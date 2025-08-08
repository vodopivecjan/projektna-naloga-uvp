# Analiza podatkov o IMDB-jevi lestvici najboljših 250 serij po ocenah ljudi
V tej projektni nalogi, narejeni pri predmetu Uvod v programiranje,
sem se odlocil za analizo top 250 serij vseh časov saj tudi sam rad gledam serije in
sem jih tudi pogledal nekaj iz tega seznama.
Obenem se mi pa zdi, da redko primerjam tako res podatkovno,
kdo se kje večkrat pojavi od igralcev, režiserjev, ustvarjalcev serij,
kateriji medijski kanali največ najboljših serij zakupijo pravice in prenašajo,
katera prudukcijska podjetja so zadaj in koliko dominirajo, itd.
Potem pa tudi potem malo bolj na splošno, kateri žanri so najpogostejši po letih,
iz katerih držav je največ teh res dobrih serij, zlata leta serij in še kaj...

Ta analiza ponuja majhno zbirko povezav med podatki o serijah in morda razkriva kakšne zanimive vzorce.
Upam, da bo ta projekt koristen ali pa vsaj zanimiv za koga, ki ga zanima web scraping in
preprosta analiza podatkov, obenem pa tudi sam občasno rad pogleda kakšno serijo.

# Knjižnice in postavitev okolja
Ta projekt uporablja uv, zato je vsa konfiguracija v pyproject.toml datoteki,
ki jo lahko samo prenesemo v drugo mapo, poženemo ukaz 'uv sync' in to je to,
če pa hočemo manualno, so pa naslednje nujne knjiznice:
```
dependencies = [
    "beautifulsoup4>=4.13.4",
    "jupyter>=1.1.1",
    "matplotlib>=3.10.5",
    "matplotlib-venn>=1.1.2",
    "pandas>=2.3.1",
    "playwright>=1.53.0",
    "plotly>=6.2.0",
    "requests>=2.32.4",
    "seaborn>=0.13.2",
]
```

# Uporaba
Projekt naj bi deloval tako, da se najprej pridobi podatke, zato se gre v mapo ./src/get_data/ in se tam samo požene "app.py"
Ta program vzame priblizno 8 minut da pobere vse podatke iz spleta in jih sam spravi v csv in json datoteke v ./output/

Ko program zaključi pa gremo lahko v mapo .src/parse_data in tam odpremo jupyter_notebook datoteko "parse_data.ipzynb" in izvedemo analizo 