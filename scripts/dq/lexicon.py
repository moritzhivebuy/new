"""Nachschlagelisten für die Namenserkennung.

Reine Daten, keine Logik. Erweitern ist der wichtigste Stellhebel für die
Trefferquote der Routine — vor allem GIVEN und ROLE_TOKENS.
"""

# ---------------------------------------------------------------------------
# Vornamen. Entscheidet, welches Token in "a.b@firma.de" der Vorname ist.
# DE/AT/CH-Schwerpunkt plus die international häufigsten Formen.
# ---------------------------------------------------------------------------
GIVEN = set("""
aaron abdul abdullah achim ada adam adelheid adem adil adnan adrian adriana adriano agnes ahmad
ahmed aida aike aileen aisha ajla aksel alain alan albert alberto albin albrecht aleksandar
aleksandra alena alessandra alessandro alex alexa alexander alexandra alexandre alexej alfons
alfred ali alia alice alicia alina aline alisa alison alissa alkan allan alma almir alois alper
alperen alvaro alwin amadeus amal amanda amel amelie amin amina amir amira amos ana anastasia
anastassija anatol anders andre andrea andreas andreea andrej andres andrew andrey andrzej andy
anette angela angelika angelina angelo anika anil anita anja anke ann anna annabel annalena
anne anneke annelie annemarie annett annette annika anny anouk anselm anthony antje anton
antonia antonio antony anuschka apostolos arda ardit ariane arif arijana aris arjan arlind
armin arnaud arne arno arnold aron arsen artem arthur artur arved arvid asen asim asli asmus
astrid atakan athanasios attila aurel aurelia aurelie aurore axel aydin ayhan ayla ayse
azra bahar balthasar barbara bardia barnabas bart bartek bartosz basil bastian beat beate
beatrice beatrix bedirhan bela belinda bella ben benedikt benjamin bennet benno bent berat
berivan berkay bernadette bernd bernhard bernt bert berta bertram bettina betty bianca bilal
bill birgit birte bjarne bjoern bjorn blanka bodo bogdan boris borja boro brandon brigitte
britta bruno bryan burak burkhard burkhardt calvin camilla camillo camilo can candy carina
carl carla carlo carlos carmen carola carolin carolina caroline carsten casper caspar
catalina catharina cathrin catrin cecilia cedric celal celina celine cem cemal cengiz cesar
chantal charles charlotte cheyenne chiara chris christa christel christian christiane
christin christina christine christof christoph christophe christopher cindy claas clara
clarissa claudia claudine claudio claus clemens colin conny conrad constantin constanze
cora corina corinna cornelia cornelius corvin curt cyril daan dagmar dalia damian damir
dana daniel daniela daniele danilo danny daria dario darius darko dave david davide dean
deborah delia demir denis denise dennis derya desiree detlef detlev diana didem diderk
diego dieter dietmar dietrich dilara dimitri dimitrios dina dino dirk ditmar dogan dominic
dominik dominique donald donata dora dorian doris dorit dorothea dorothee dragan drazen dunja
dustin dylan eberhard ecrin eda edda edgar edin edith edmund edonita edouard eduard edvin
edwin efe egon ehrenfried eik eike ekkehard ekrem elena eleni eleonora eleonore elfriede
elia elias elif elin elina elisa elisabeth elise elke ella ellen elmar eloise elsa elvira
emanuel emanuela emel emil emilia emilie emin emine emir emma emmanuel emmett emre enes engin
enis enno enrico enver eren erhard eric erich erik erika erkan ernst erol ertan erwin esat
esin esra essam esther etienne eugen eugenia eva evelin eveline evelyn ewa ewald fabian
fabienne fabio fabrice fadime fahri faisal falk falko fabiola farah farid fatih fatima fatma
faruk fedor felicia felix ferdinand ferhat fernando festim fidan filip filiz finn fiona
flavio fleur florence florent florian floris frances francesca francesco franciska franco
frank franka franz franziska frauke fred freddy frederic frederick frederieke frederik
frederike fredrik freya frida friedbert friederike friedhelm friedrich fritz gabor gabriel
gabriela gabriele gaetan galina ganesh gaston gebhard geert gennaro georg george georgia
georgios gerald gerard gerd gerda gereon gerhard gerlinde germar gernot gerold gerrit
gerritje gert gertrud gesa ghalia gian gianluca gianni gilbert gilles gina giorgio giovanni
gisela giselher giulia giuseppe glenn goran gordon gottfried grace graham gregor grete grit
gudrun guido gundula gunnar gunter guenter guenther gustav gudula hacer hadi hagen hakan
hakim halil halim halina hamid hamza hana hanan hanna hannah hannelore hannes hanno hans
hansjoerg harald hardy hariolf harm harold harri harry hartmut hartwig hasan hassan hauke
hava havva hedwig heidi heike heiko heiner heinrich heinz helen helena helene helga helge
helmut helmuth hendrik henning henri henriette henrik henry herbert herby heribert herlinde
hermann hermine hertha hicham hilal hilda hilde hildegard hilmar hisham holger horst hubert
hubertus hugo huseyin ibrahim ida idris igor ilay ilhan ilias ilie ilka ilkay ilona ilse
ilyas imke immanuel ina indira ines inga inge ingeborg ingo ingrid inken ioannis irena irene
iris irina irmgard isa isabel isabell isabella isabelle isak ismail israel iva ivan ivana
ivano ivaylo ivett ivo iwan jacek jacob jacqueline jael jakob jakub jamal james jamil jan
jana janek janina janine janis janna jannes jannik janos jaroslav jasmin jasmina jason
jasper javier jean jeanette jeanne jeff jennifer jenny jens jeremias jeremy jerome jesper
jessica jessika jim jimmy jiri joachim joan joanna jochen jodok joel joelle johann johanna
johannes john jolanda jonas jonathan joost jordan jorge joris josef josefine joseph josephine
joshua josip jost jovan juan judith judith julia julian juliane julien julius june jurgen
juergen justin justus jutta kadir kai kalle kamil karen karim karin karina karl karla
karlheinz karolina karoline karsten kaspar kasper katalin katarina katarzyna katharina
kathleen kathrin katja katrin kay kemal kenan kerem kerim kerstin kevin khaled kilian
kim kira kirsten kjell klaas klara klaus klemens knut koen konrad konstantin konstantina
kordula kornelia kristian kristin kristina kristine kurt lambert lara larissa lars lasse
laura laurent laurenz laurens lea leah leander leandro lena lene lennart lenz leo leon
leona leonard leonardo leone leonhard leonid leonie leopold leroy leslie levent levin
levke lewin liam lidia lieselotte lilian liliane lilli lina linda linus lion lionel lisa
lisbeth livia liza lofti loic lorena lorenz lorenzo lothar lotta lotte luc luca lucas
lucia lucie lucien ludger ludwig luigi luis luisa luise luitgard lukas luka lutz lydia
lynn maarten madeleine madina magdalena magnus mahmut maik maike maja majid malee malgorzata
malte mandy manfred manolis manuel manuela mara marc marcel marcello marco marcus marek
maren margarete margarethe margit margret maria mariam marian mariana marianna marianne
marie mariella marietta marija marika marina mario marion marisa marita marius marjan mark
marko markus marlen marlene marlies marnie marta marte martha martin martina marvin mascha
massimo mateo matheus mathias mathieu mathilde matias matteo matthes matthias mattis
maurice maurizio max maximilian maya mehdi mehmet meike melanie melek melina melis melisa
melissa merle merlin mert merve meryem michael michaela michal michel michele michelle
mihai mika mikael mike miklos milan milena milica milos mimi mina minfeng miran miranda
mirco mirella miriam mirjam mirko miroslav mirza mishel mohamed mohammad mohammed moises
monika monique montgomery moritz morten muhammed murat mustafa myriam nabil nadia nadine
nadja nadschana nafiseh nagy nancy naomi nasir natalia natalie natascha nathalie nazan
neele nelly nenad nermin nevin niels nick nickel niclas nico nicola nicolas nicole niels
niklas nikola nikolai nikolaos nikolaus nils nina nino noah noemi nora norbert norman
norwin nuria nurten oda odilo oguz okan oksana olaf oleg olga olivia oliver olivier omar
onur oscar oskar osman otmar otto ozan ozgur pablo pamela panagiotis paola paolo pascal
pascale patricia patrick patrik patrice paul paula pauline pavel pawel pedro peer pelin
peer per peter petra petros philip philipp philippa philippe phillip pia pierre pieter
pietro pia piotr pirmin polina radu rafael rafal ragnar rahel raif rainer raif rajko ralf
ralph rami ramona ramon randolf raoul raphael raul rebecca rebekka regina reginald regine
reiner reinhard reinhold rejhan remo rena renate rene renate ricarda riccardo richard
rico rieke rita ritva robert roberta roberto robin roderich rodrigo roger roland rolf
roman romain romana romeo romy ronald ronny rosa rosalie rose rosemarie rosina roswitha
ruben rudi rudolf rudolph rui rupa rupert ruslan ruth ryan saban sabine sabrina sacha
sadik safiye saida sait sakine salih salim sally salome sami samir samira sammy samuel
sanaz sandra sandro sanjin santiago sara sarah saskia sascha sebastian selin selim selina
selma semih semra senad serap serdar serge sergej sergio serkan sevda sevim sevgi sezer
sibel sibylle sidney siegbert siegfried siegmund sigrid sigurd silas silke silvan silvana
silvia silvio simeon simo simon simona simone sina sinan sirin siw sofia sofie sokol solveig
sonja sonya sophia sophie soraya sorin soeren stanislaw stefan stefanie steffen steffi
stella stephan stephane stephanie stephen sten sten steve steven stine stuart sujit
sultan susan susanna susanne suzanne svea sven svenja svetlana svantje sybille sylke
sylvain sylvana sylvia szymon tabea tahir tamara tamas tanja tarek tarik tatjana tayfun
tea tekin teresa tero tessa thea theo theodor theresa therese theresia thies thilo thomas
thorben thorsten tibor tilman tilo tim timm timo timon tina tino tizian tobias tolga
tom tomas tomasz tommy toni tony torben torsten tristan tufan turgay udo ugur ulf uli
ulla ulrich ulrike ulla ulrik ulla umut ursula urs ute uta uwe vahid valentin valentina
valeria valerie vanessa vasilios vedat veit velina venera vera verena veronika veit
vesna victor victoria vidal viktor viktoria vince vincent vinzenz viola violetta virginia
vitali vittoria vivian vivien volkan volker vural wadim waldemar walter waltraud wanda
weronika werner wesley wibke wieland wiktor wilfried wilhelm wilhelmine will willi william
willy wim winfried wladimir wolf wolfgang wolfram xavier xenia yannick yannic yannis
yasemin yasin yasmin yavuz yildiz ylva yoana yolanda yordan yuliya yulia yunus yusuf
yvonne zafer zana zdenko zehra zeljko zeynep zita zoe zoltan zora zoran zuzana
""".split())


# ---------------------------------------------------------------------------
# Rollen-/Funktionspostfächer. Ein Treffer hier verhindert, dass ein
# Personenname erfunden wird -- die wichtigste Leitplanke der Routine.
# ---------------------------------------------------------------------------
ROLE_TOKENS = set("""
info kontakt contact office service services kundenservice customerservice kundendienst
support helpdesk help hilfe team teams zentrale central empfang reception sekretariat
mail email emails post posteingang inbox mailbox webmaster admin administrator root
noreply no-reply donotreply nichtantworten postmaster abuse hostmaster
bestellung bestellungen besteller order orders ordering purchase purchasing purchases
einkauf zentraleinkauf eeinkauf ekeinkauf beschaffung procurement eprocure eprocurement
edi ek zek disposition dispo materialwirtschaft warenwirtschaft
buchhaltung accounting rechnung rechnungen rechnungseingang invoice invoices invoicing
billing finance finanzen kreditoren debitoren mahnwesen zahlung payments ap ar
vertrieb sales verkauf verkoop presales aftersales
marketing presse press pr kommunikation communications newsletter abo
hr personal personalabteilung jobs job bewerbung bewerbungen karriere career careers
recruiting recruitment ausbildung
it edv itsupport ithelpdesk technik technical technicalsupport engineering
logistik logistics versand shipping spedition lager warehouse fuhrpark fleet
qm qs qualitaet quality
scm adminscm supplychain
datenschutz privacy dsgvo gdpr legal recht compliance revision
gf geschaeftsfuehrung geschaeftsleitung vorstand board management direktion
buero bureau shop web online webshop store
ticket tickets anfrage anfragen request requests enquiry enquiries
crm erp sap system systems noc ops operations
test testing demo dummy sample beispiel noname unknown nobody
public general allgemein alle all group gruppe konzern
www ftp smtp imap
""".split())

# Strukturelle Nicht-Personen-Marker im Local Part. Als eigenständiges Token.
STRUCT_BLOCK = set("ext extern external intern internal temp tmp alt old neu new "
                   "de en fr it es at ch uk us eu global".split())


# ---------------------------------------------------------------------------
# Namenspartikel: bleiben klein und zählen nicht als eigener Namensbestandteil.
# ---------------------------------------------------------------------------
PARTICLES = set("von vom van de del della der den des di da do du la le les zu zur "
                "am an auf im in ter te ten bin ibn al el".split())

# Akademische Titel und Anreden, die nicht ins Namensfeld gehören.
TITLES = set("dr dr. prof prof. dipl dipl. ing ing. mag mag. med med. rer nat habil "
             "mba msc bsc ba ma llm phd dipl.-ing dipl.-kfm kfm bsc. msc. "
             "herr frau hr fr mr mr. mrs mrs. ms ms. miss madame monsieur".split())


# ---------------------------------------------------------------------------
# Geschlechtsindikatoren für den Anrede-Abgleich. Nur als Prüfhinweis
# verwenden, nie als Urteil -- bei international besetzten Vornamen unscharf.
# ---------------------------------------------------------------------------
FEMALE = set("""
ada adelheid agnes aida aileen aisha alena alessandra alexa alexandra alice alicia alina
aline alisa alison alissa alma amanda amelie amina amira ana anastasia anastassija andrea
andreea anette angela angelika angelina anika anita anja anke anna annabel annalena anne
anneke annelie annemarie annett annette annika anny anouk antje antonia anuschka ariane
arijana arlind asli astrid aurelia aurelie aurore ayla ayse azra bahar barbara beate
beatrice beatrix belinda bella berivan berta bettina betty bianca birgit birte blanka
brigitte britta camilla carina carla carmen carola carolin carolina caroline catalina
catharina cathrin catrin cecilia celina celine chantal charlotte cheyenne chiara christa
christel christiane christin christina christine cindy clara clarissa claudia claudine
cora corina corinna cornelia dagmar dalia dana daniela daniele daria delia denise derya
desiree diana didem dilara dina doris dorit dorothea dorothee dunja edda edith edonita
eda elena eleni eleonora eleonore elfriede elif elin elina elisa elisabeth elise elke
ella ellen eloise elsa elvira emel emilia emilie emine emma esin esra esther eugenia
eva evelin eveline evelyn ewa fabienne fadime fatima fatma felicia fidan filiz fiona
fleur florence frances francesca franciska franka franziska frauke frederieke frederike
freya frida friederike gabriela gabriele galina georgia gerda gerlinde gerritje gertrud
gesa ghalia gina gisela giulia grace grete grit gudrun gundula hacer halina hana hanan
hanna hannah hannelore hava havva hedwig heidi heike helen helena helene helga henriette
herlinde hermine hertha hilal hilda hilde hildegard ilka ilona ilse imke ina indira ines
inga inge ingeborg ingrid inken irena irene iris irina irmgard isa isabel isabell isabella
isabelle iva ivana ivett jacqueline jael jana janina janine janna jasmin jasmina jeanette
jeanne jennifer jenny jessica jessika jolanda joanna johanna josefine josephine judith
julia juliane june jutta karen karin karina karla karolina karoline katalin katarina
katarzyna katharina kathleen kathrin katja katrin kim kira kirsten klara kordula kornelia
kristin kristina kristine lara larissa laura lea leah lena lene leona leonie leslie levke
lidia lieselotte lilian liliane lilli lina linda lisa lisbeth livia liza lorena lotta
lotte lucia lucie luisa luise luitgard lydia lynn madeleine madina magdalena maja malee
malgorzata mandy manuela mara maren margarete margarethe margit margret maria mariam
mariana marianna marianne marie mariella marietta marija marika marina marion marisa
marita marlen marlene marlies marnie marta marte martha martina mascha maya meike melanie
melek melina melis melisa melissa merle merve meryem michaela michelle milena milica mina
miranda mirella miriam mirjam monika monique myriam nadia nadine nadja nancy naomi natalia
natalie natascha nathalie nazan neele nelly nermin nevin nicola nicole nina noemi nora
nuria nurten oda oksana olga olivia pamela paola patricia paula pauline pelin petra pia
polina rahel ramona rebecca rebekka regina regine rena renate ricarda rieke rita ritva
romana romy rosa rosalie rose rosemarie rosina roswitha ruth sabine sabrina safiye saida
sakine sally salome samira sanaz sandra sanjin sara sarah saskia selin selina selma semra
senad serap sevda sevim sevgi sibel sibylle sigrid silke silvana silvia simona simone
sina sofia sofie solveig sonja sonya sophia sophie soraya stefanie steffi stella stephanie
stine sultan susan susanna susanne suzanne svea svenja svetlana svantje sybille sylke
sylvana sylvia tabea tamara tanja tatjana tea teresa tessa thea theresa therese theresia
tina ulla ulrike ursula ute uta valentina valeria valerie vanessa velina venera vera
verena veronika vesna victoria viktoria viola violetta virginia vittoria vivian vivien
waltraud wanda weronika wibke wilhelmine xenia yasemin yasmin yildiz ylva yoana yolanda
yuliya yulia yvonne zehra zeynep zita zoe zora zuzana
""".split())

MALE = set("""
aaron abdul abdullah achim adam adem adil adnan adrian adriano ahmad ahmed aike ajla aksel
alain alan albert alberto albin albrecht aleksandar alex alexander alexandre alexej alfons
alfred ali alkan alois alper alperen alvaro alwin amadeus amin amir amos anatol anders
andre andreas andrej andres andrew andrey andrzej andy anil anselm anton antonio antony
apostolos arda ardit arif aris arjan armin arnaud arne arno arnold aron arsen artem arthur
artur arved arvid asen asim asmus atakan athanasios attila aurel axel aydin ayhan bahar
balthasar bardia barnabas bart bartek bartosz basil bastian beat bedirhan bela ben benedikt
benjamin bennet benno bent berat berkay bernd bernhard bernt bert bertram bilal bill bjarne
bjoern bjorn bodo bogdan boris borja boro brandon bruno bryan burak burkhard burkhardt
calvin camillo camilo can cedric celal cem cemal cengiz cesar charles chris christian
christof christoph christophe christopher claas claudio claus clemens colin conny conrad
constantin cornelius corvin curt cyril daan damian damir daniel danilo danny dario darius
darko dave david davide dean denis dennis detlef detlev diderk diego dieter dietmar dietrich
dimitri dimitrios dino dirk ditmar dogan dominic dominik donald dorian dragan drazen dustin
dylan eberhard edgar edin edmund edouard eduard edvin edwin efe egon ehrenfried eik eike
ekkehard ekrem elia elias elmar emanuel emil emin emir emmanuel emmett emre enes engin
enis enno enrico enver eren erhard eric erich erik erkan ernst erol ertan erwin esat
essam etienne eugen fabian fabio fabrice fahri faisal falk falko farid fatih faruk fedor
felix ferdinand ferhat fernando festim filip finn flavio florent florian floris franco
frank franz fred freddy frederic frederick frederik fredrik friedbert friedhelm friedrich
fritz gabor gabriel gaetan ganesh gaston gebhard geert gennaro georg george georgios gerald
gerard gerd gereon gerhard germar gernot gerold gerrit gert gian gianluca gianni gilbert
gilles giorgio giovanni giselher giuseppe glenn goran gordon gottfried gregor guido gunnar
gunter guenter guenther gustav hadi hagen hakan hakim halil halim hamid hamza hannes hanno
hans hansjoerg harald hardy hariolf harm harold harri harry hartmut hartwig hasan hassan
hauke heiko heiner heinrich heinz helge helmut helmuth hendrik henning henri henrik henry
herbert herby heribert hermann hicham hilmar hisham holger horst hubert hubertus hugo
huseyin ibrahim idris igor ilhan ilias ilie ilkay ilyas immanuel ingo ioannis isak ismail
israel ivan ivano ivaylo ivo iwan jacek jacob jakob jakub jamal james jamil jan janek
janis jannes jannik janos jaroslav jason jasper javier jean jeff jens jeremias jeremy
jerome jesper jim jimmy jiri joachim joan jochen jodok joel johann johannes john jonas
jonathan joost jordan jorge joris josef joseph joshua josip jost jovan juan julian julien
julius jurgen juergen justin justus kadir kai kalle kamil karim karl karlheinz karsten
kaspar kasper kay kemal kenan kerem kerim kevin khaled kilian kjell klaas klaus klemens
knut koen konrad konstantin kristian kurt lambert lars lasse laurent laurenz laurens
leander leandro lennart lenz leo leon leonard leonardo leone leonhard leonid leopold leroy
levent levin lewin liam lion lionel lofti loic lorenz lorenzo lothar luc luca lucas lucien
ludger ludwig luigi luis luka lukas lutz maarten magnus mahmut maik majid malte manfred
manolis manuel marc marcel marcello marco marcus marek mario marius marjan mark marko
markus martin marvin massimo mateo matheus mathias mathieu matias matteo matthes matthias
mattis maurice maurizio max maximilian mehdi mehmet mert michael michal michel michele
mihai mika mikael mike miklos milan milos minfeng miran mirco mirko miroslav mirza mishel
mohamed mohammad mohammed moises moritz morten muhammed murat mustafa nabil nagy nasir
nenad niels nick nickel niclas nico nicolas niklas nikola nikolai nikolaos nikolaus nils
noah norbert norman norwin oguz okan oleg oliver olivier omar onur oscar oskar osman otmar
otto ozan ozgur pablo panagiotis paolo pascal patrick patrik patrice paul pavel pawel pedro
peer per peter petros philip philipp philippe phillip pierre pieter pietro piotr pirmin
radu rafael rafal ragnar rainer raif rajko ralf ralph rami ramon randolf raoul raphael
raul reiner reinhard reinhold rejhan remo rene riccardo richard rico robert roberto robin
roderich rodrigo roger roland rolf roman romain romeo ronald ronny ruben rudi rudolf
rudolph rui rupert ruslan ryan saban sacha sadik sait salih salim sami samir sammy samuel
sandro santiago sascha sebastian selim semih serdar serge sergej sergio serkan sezer
sidney siegbert siegfried siegmund sigurd silas silvan silvio simeon simo simon sinan
sokol sorin soeren stanislaw stefan steffen stephan stephane stephen sten steve steven
stuart sujit sven szymon tahir tamas tarek tarik tayfun tekin tero theo theodor thies
thilo thomas thorben thorsten tibor tilman tilo tim timm timo timon tino tizian tobias
tolga tom tomas tomasz tommy toni tony torben torsten tristan tufan turgay udo ugur ulf
uli ulrich ulrik umut urs uwe vahid valentin vasilios vedat veit velina victor vidal
viktor vince vincent vinzenz vitali volkan volker vural wadim waldemar walter wesley
wieland wiktor wilfried wilhelm will willi william willy wim winfried wladimir wolf
wolfgang wolfram xavier yannick yannic yannis yasin yavuz yordan yunus yusuf zafer zdenko
zeljko zoltan zoran
""".split())


# ---------------------------------------------------------------------------
# Freemail-Domains: kein Firmenkontext, Domain-Konvention nicht lernbar.
# ---------------------------------------------------------------------------
FREEMAIL = set("""
gmail.com googlemail.com gmx.de gmx.net gmx.at gmx.ch web.de yahoo.com yahoo.de yahoo.co.uk
hotmail.com hotmail.de hotmail.co.uk outlook.com outlook.de live.com live.de msn.com
icloud.com me.com mac.com aol.com aol.de t-online.de freenet.de mail.de posteo.de
protonmail.com proton.me mailbox.org bluewin.ch hispeed.ch sunrise.ch gmx.co.uk
online.de arcor.de vodafone.de 1und1.de tutanota.com yandex.ru mail.ru
""".split())


# ---------------------------------------------------------------------------
# TLD -> Ländervorwahl und ISO-Land, für die E.164-Normalisierung.
# ---------------------------------------------------------------------------
TLD_COUNTRY = {
    "de": ("+49", "Germany"),   "at": ("+43", "Austria"),      "ch": ("+41", "Switzerland"),
    "li": ("+423", "Liechtenstein"), "lu": ("+352", "Luxembourg"), "nl": ("+31", "Netherlands"),
    "be": ("+32", "Belgium"),   "fr": ("+33", "France"),        "it": ("+39", "Italy"),
    "es": ("+34", "Spain"),     "pt": ("+351", "Portugal"),     "dk": ("+45", "Denmark"),
    "se": ("+46", "Sweden"),    "no": ("+47", "Norway"),        "fi": ("+358", "Finland"),
    "pl": ("+48", "Poland"),    "cz": ("+420", "Czechia"),      "sk": ("+421", "Slovakia"),
    "hu": ("+36", "Hungary"),   "si": ("+386", "Slovenia"),     "hr": ("+385", "Croatia"),
    "ro": ("+40", "Romania"),   "bg": ("+359", "Bulgaria"),     "gr": ("+30", "Greece"),
    "uk": ("+44", "United Kingdom"), "ie": ("+353", "Ireland"), "tr": ("+90", "Turkey"),
}

# Nationale Präfixe, die beim Umbau auf E.164 entfallen.
NATIONAL_TRUNK = "0"
