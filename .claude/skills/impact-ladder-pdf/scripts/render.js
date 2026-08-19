const fs = require('fs');
const path = require('path');
const Handlebars = require('handlebars');
const puppeteer = require('puppeteer');

const jsonPath = process.argv[2];
if (!jsonPath) {
  console.error('Nutzung: node scripts/render.js <pfad-zur-json>');
  process.exit(1);
}
const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
if (!Array.isArray(data.ladder) || data.ladder.length !== 4) {
  console.error('Fehler: ladder muss genau 4 Ebenen enthalten.');
  process.exit(1);
}
const templateDir = path.join(__dirname, '..', 'template');
const templateSrc = fs.readFileSync(path.join(templateDir, 'template.html'), 'utf8');
const html = Handlebars.compile(templateSrc)(data);

// Kompiliertes HTML im template-Ordner ablegen, damit relative Pfade
// zu Fonts und Logo (../assets/...) korrekt aufgeloest werden.
const tmpHtml = path.join(templateDir, '_compiled.html');
fs.writeFileSync(tmpHtml, html, 'utf8');

const slug = data.customer.name
  .toLowerCase()
  .replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue').replace(/ß/g, 'ss')
  .replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const dateStr = new Date().toISOString().slice(0, 10);
const outPath = path.join(__dirname, '..', 'output', `${dateStr}-impact-ladder-${slug}.pdf`);

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  await page.goto('file://' + tmpHtml, { waitUntil: 'networkidle0' });
  await page.evaluateHandle('document.fonts.ready');
  await page.pdf({
    path: outPath,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: `
      <div style="width:100%;font-size:7px;color:#204540;padding:0 16mm;
                  display:flex;justify-content:space-between;font-family:Helvetica,Arial,sans-serif;">
        <span>Hivebuy GmbH · Invalidenstraße 35 · 10115 Berlin · hivebuy.com</span>
        <span>Seite <span class="pageNumber"></span> von <span class="totalPages"></span></span>
      </div>`,
    margin: { top: '0mm', bottom: '16mm', left: '0mm', right: '0mm' }
  });
  await browser.close();
  fs.unlinkSync(tmpHtml);
  console.log('PDF erstellt: ' + outPath);
})();
