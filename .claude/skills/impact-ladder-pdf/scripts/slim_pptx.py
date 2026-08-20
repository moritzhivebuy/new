#!/usr/bin/env python3
"""Verkleinert eine von render_pptx.py erzeugte Datei.

Entfernt die von python-pptx mitgelieferten, aber nicht genutzten Slide-Layouts
sowie Thumbnail und Druckereinstellungen. Das Ergebnis ist deutlich kleiner und
laesst sich damit auch ueber Schnittstellen mit Groessenlimit hochladen.

Aufruf: python3 scripts/slim_pptx.py output/<datei>.pptx
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

KEEP_LAYOUT = "slideLayout7.xml"  # Blank, das einzige von render_pptx genutzte


def main():
    src = Path(sys.argv[1])
    tmp = src.with_suffix(".slim.pptx")
    drop_prefixes = ("docProps/thumbnail", "ppt/printerSettings/")

    with zipfile.ZipFile(src) as zin:
        names = zin.namelist()
        layouts = [n for n in names
                   if n.startswith("ppt/slideLayouts/") and n.endswith(".xml")]
        drop = {n for n in layouts if not n.endswith(KEEP_LAYOUT)}
        drop |= {n for n in names
                 if n.startswith("ppt/slideLayouts/_rels/")
                 and not n.endswith(KEEP_LAYOUT + ".rels")}
        drop |= {n for n in names if n.startswith(drop_prefixes)}

        master_rels = zin.read("ppt/slideMasters/_rels/slideMaster1.xml.rels").decode()
        keep_id = re.search(
            r'<Relationship Id="([^"]+)"[^>]*Target="\.\./slideLayouts/%s"' % KEEP_LAYOUT,
            master_rels).group(1)
        master_rels = re.sub(
            r'<Relationship Id="(?!%s")[^>]*slideLayouts/[^>]*/>' % keep_id, "",
            master_rels)

        master = zin.read("ppt/slideMasters/slideMaster1.xml").decode()
        master = re.sub(
            r'<p:sldLayoutId [^>]*r:id="(?!%s")[^>]*/>' % keep_id, "", master)

        ct = zin.read("[Content_Types].xml").decode()
        for name in drop:
            ct = ct.replace('<Override PartName="/%s" ContentType="application/'
                            'vnd.openxmlformats-officedocument.presentationml.'
                            'slideLayout+xml"/>' % name, "")
            ct = ct.replace('<Override PartName="/%s" ContentType="image/jpeg"/>'
                            % name, "")
        ct = re.sub(r'<Default Extension="bin"[^>]*/>', "", ct)
        ct = re.sub(r'<Default Extension="jpeg"[^>]*/>', "", ct)

        root_rels = zin.read("_rels/.rels").decode()
        root_rels = re.sub(r'<Relationship [^>]*thumbnail[^>]*/>', "", root_rels)

        pres_rels = zin.read("ppt/_rels/presentation.xml.rels").decode()
        pres_rels = re.sub(r'<Relationship [^>]*printerSettings[^>]*/>', "", pres_rels)

        replaced = {
            "[Content_Types].xml": ct,
            "_rels/.rels": root_rels,
            "ppt/_rels/presentation.xml.rels": pres_rels,
            "ppt/slideMasters/slideMaster1.xml": master,
            "ppt/slideMasters/_rels/slideMaster1.xml.rels": master_rels,
        }

        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            for item in zin.infolist():
                if item.filename in drop:
                    continue
                data = replaced.get(item.filename)
                zout.writestr(item.filename,
                              data.encode() if data else zin.read(item.filename))

    before, after = src.stat().st_size, tmp.stat().st_size
    shutil.move(tmp, src)
    print("verkleinert: %d -> %d Byte (%s)" % (before, after, src.name))


if __name__ == "__main__":
    main()
