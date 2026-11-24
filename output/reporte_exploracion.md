# Reporte de exploración — Scopus Yachay Tech (AF-ID 60105012)

- Archivo: `data/raw/raw.csv`
- Fecha de generación: 2026-11-24

## 1. Estructura general

- Filas: **1836**, columnas: **34**
- Columnas: `Authors`, `Author full names`, `Author(s) ID`, `Title`, `Year`, `Source title`, `Volume`, `Issue`, `Art. No.`, `Page start`, `Page end`, `Cited by`, `DOI`, `Link`, `Affiliations`, `Authors with affiliations`, `Abstract`, `Author Keywords`, `Index Keywords`, `References`, `Publisher`, `Sponsors`, `Conference name`, `Conference date`, `Conference location`, `Conference code`, `ISSN`, `ISBN`, `CODEN`, `Document Type`, `Publication Stage`, `Open Access`, `Source`, `EID`

| columna                   | tipo (lectura como texto)   |   nulos |   % nulos |   valores únicos |
|:--------------------------|:----------------------------|--------:|----------:|-----------------:|
| Authors                   | str                         |       0 |      0    |             1769 |
| Author full names         | str                         |       0 |      0    |             1784 |
| Author(s) ID              | str                         |       0 |      0    |             1756 |
| Authors with affiliations | str                         |       0 |      0    |             1826 |
| Affiliations              | str                         |       0 |      0    |             1731 |
| Year                      | str                         |       0 |      0    |               14 |
| EID                       | str                         |       0 |      0    |             1836 |
| DOI                       | str                         |     121 |      6.59 |             1713 |
| Title                     | str                         |       0 |      0    |             1830 |
| Document Type             | str                         |       0 |      0    |               12 |

## 2. Documentos por año

|   Year_int |   documentos | nota                                           |
|-----------:|-------------:|:-----------------------------------------------|
|       2014 |           17 | bajo (año de arranque)                         |
|       2015 |           52 |                                                |
|       2016 |           63 |                                                |
|       2017 |          120 |                                                |
|       2018 |          139 |                                                |
|       2019 |          189 |                                                |
|       2020 |          197 |                                                |
|       2021 |          201 |                                                |
|       2022 |          158 |                                                |
|       2023 |          177 |                                                |
|       2024 |          185 |                                                |
|       2025 |          178 |                                                |
|       2026 |          147 | AÑO EN CURSO (incompleto)                      |
|       2027 |           13 | FUTURO (publicación con fecha posterior a hoy) |

### Etapa de publicación por año (años atípicos)

|   Year_int |   Article in press |   Final |
|-----------:|-------------------:|--------:|
|       2014 |                  0 |      17 |
|       2015 |                  0 |      52 |
|       2016 |                  0 |      63 |
|       2017 |                  0 |     120 |
|       2018 |                  0 |     139 |
|       2019 |                  0 |     189 |
|       2020 |                  0 |     197 |
|       2021 |                  0 |     201 |
|       2022 |                  0 |     158 |
|       2023 |                  0 |     177 |
|       2024 |                  0 |     185 |
|       2025 |                  1 |     177 |
|       2026 |                  9 |     138 |
|       2027 |                  0 |      13 |

### Tipos de documento

| tipo             |   documentos |
|:-----------------|-------------:|
| Article          |         1198 |
| Conference paper |          390 |
| Review           |          133 |
| Book chapter     |           59 |
| Editorial        |           16 |
| Note             |           14 |
| Letter           |           10 |
| Erratum          |            8 |
| Book             |            5 |
| Data paper       |            1 |
| Short survey     |            1 |
| Retracted        |            1 |

### Documentos con año > 2026

| EID                 |   Year | Document Type    | Publication Stage   | Source title                                       |
|:--------------------|-------:|:-----------------|:--------------------|:---------------------------------------------------|
| 2-s2.0-105052721345 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |
| 2-s2.0-105055118465 |   2027 | Conference paper | Final               | Communications in Computer and Information Science |
| 2-s2.0-105045962718 |   2027 | Conference paper | Final               | Lecture Notes in Computer Science                  |
| 2-s2.0-105045955173 |   2027 | Conference paper | Final               | Lecture Notes in Computer Science                  |
| 2-s2.0-105052676400 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |
| 2-s2.0-105052656939 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |
| 2-s2.0-105055091534 |   2027 | Conference paper | Final               | Communications in Computer and Information Science |
| 2-s2.0-105052698829 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |
| 2-s2.0-105055113103 |   2027 | Conference paper | Final               | Communications in Computer and Information Science |
| 2-s2.0-105055082643 |   2027 | Conference paper | Final               | Communications in Computer and Information Science |
| 2-s2.0-105045994357 |   2027 | Conference paper | Final               | Lecture Notes in Computer Science                  |
| 2-s2.0-105052668596 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |
| 2-s2.0-105052692785 |   2027 | Conference paper | Final               | Lecture Notes in Networks and Systems              |

## 3. Documentos duplicados

- Duplicados por `EID`: **0**
- Duplicados por `DOI` (sin contar nulos): **2** (4 filas implicadas)
- Duplicados por título normalizado: **7** (12 filas); por título normalizado + año: **3**

### Casos por DOI

| DOI                                | EID                 |   Year | Document Type   | Title                                          |
|:-----------------------------------|:--------------------|-------:|:----------------|:-----------------------------------------------|
| 10.1016/B978-0-12-818731-9.00140-3 | 2-s2.0-85152828758  |   2022 | Book chapter    | Urinary Tract Infections: Fungi (Candida spp.) |
| 10.1016/B978-0-12-818731-9.00140-3 | 2-s2.0-85216396378  |   2022 | Book chapter    | Urinary Tract Infections: Fungi (Candida spp.) |
| 10.1515/9783110546163              | 2-s2.0-105052400880 |   2017 | Book            | Free Boundaries in Rock Mechanics              |
| 10.1515/9783110546163              | 2-s2.0-85046567875  |   2017 | Book            | Free boundaries in rock mechanics              |

### Casos por título normalizado

| EID                 |   Year | Document Type    | DOI                                | Title                                                                  |
|:--------------------|-------:|:-----------------|:-----------------------------------|:-----------------------------------------------------------------------|
| 2-s2.0-85070569803  |   2019 | Conference paper | nan                                | Applications of self-assembling ultrashort peptides in bionanotechnol… |
| 2-s2.0-85059843316  |   2019 | Review           | 10.1039/C8RA07533F                 | Applications of self-assembling ultrashort peptides in bionanotechnol… |
| 2-s2.0-105052400880 |   2017 | Book             | 10.1515/9783110546163              | Free Boundaries in Rock Mechanics                                      |
| 2-s2.0-85046567875  |   2017 | Book             | 10.1515/9783110546163              | Free boundaries in rock mechanics                                      |
| 2-s2.0-85199381829  |   2024 | Editorial        | 10.1088/1742-6596/2796/1/011001    | Preface                                                                |
| 2-s2.0-85053238286  |   2018 | Editorial        | 10.1080/10556788.2018.1486553      | Preface                                                                |
| 2-s2.0-85084629961  |   2019 | Editorial        | nan                                | Preface                                                                |
| 2-s2.0-85101181904  |   2017 | Editorial        | nan                                | Preface                                                                |
| 2-s2.0-85082713235  |   2020 | Article          | 10.19139/soic-2310-5070-488        | Stochastic models to estimate population dynamics                      |
| 2-s2.0-85065976591  |   2019 | Article          | 10.19139/soic.v7i2.538             | Stochastic models to estimate population dynamics                      |
| 2-s2.0-85152828758  |   2022 | Book chapter     | 10.1016/B978-0-12-818731-9.00140-3 | Urinary Tract Infections: Fungi (Candida spp.)                         |
| 2-s2.0-85216396378  |   2022 | Book chapter     | 10.1016/B978-0-12-818731-9.00140-3 | Urinary Tract Infections: Fungi (Candida spp.)                         |

## 4. Autores

- Firmas autor–documento: **12041**; `Author(s) ID` únicos: **5915**
- Entradas de `Author full names` sin el formato `Nombre (ID)`: **0**
- Documentos donde #IDs, #nombres completos, #nombres cortos y #entradas de `Authors with affiliations` no coinciden: **2**

### 4.1 IDs con varias variantes de nombre: 687

|   Author ID |   documentos |   n variantes | variantes (frecuencia)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
|------------:|-------------:|--------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 57200308316 |          100 |             8 | Almeida-Galárraga, Diego (76) / Almeida-Galárraga, Diego A. (7) / Almeida-Galarraga, Diego (6) / Almeida, Diego (5) / Almeida-Galárraga, D. (3) / Almeida-Gallaraga, Diego (1) / Almeida, Diego A. (1) / Almeida Galarraga, Diego A. (1)                                                                                                                                                                                                                                                                                                                                                                                                    |
| 35746975300 |           94 |            20 | Peluffo-Ordóñez, Diego H. (40) / Peluffo-Ordóñez, D.H. (17) / Peluffo-Ordóñez, Diego Hernán (10) / Peluffo-Ordoñez, Diego H. (3) / Peluffo-Ordóñez, Diego (3) / Peluffo-Ordonez, Diego Hernan (2) / Peluffo-Ordonez, Diego H. (2) / Peluffo-Ordoñez, Diego (2) / Peluffo-Ordonez, D.H. (2) / Peluffo-Ordoñez, Diego Hernán (2) / Peluffo-Ordoñez, D.H. (2) / H. Peluffo-Ordóñez, Diego (1) / Peluffo-Ordóñez, D. (1) / H.peluffo-Ordoñez, Diego (1) / Peluffo, Diego (1) / Peluffo Ordoñez, Diego Hernán (1) / Ordoñez, Diego Peluffo (1) / Peluffo-Ordonez, Diego Hernn (1) / Peluffo-Ordónez, Diego H. (1) / Peluffo-Ordóñez, Diego H (1) |
| 57219521008 |           79 |             8 | Villalba-Meneses, Fernando (57) / Villalba-Meneses, Gandhi (6) / Villalba Meneses, Fernando (5) / Meneses, Fernando Villalba (4) / Villalba-Meneses, Gandhi F. (3) / Villalba-Meneses, G.F. (2) / Villalba-Meneses, Gandhi Fernando (1) / Villalba, Fernando (1)                                                                                                                                                                                                                                                                                                                                                                            |
| 57219655742 |           72 |             4 | Tirado-Espín, Andrés (66) / Tirado-Espin, Andres (3) / Tirado-Espín, Andres (2) / Tirado-Espin, Andrés (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
|  7202571211 |           56 |             3 | González, Gema (42) / Gonzalez, Gema (8) / González, G. (6)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 55893790300 |           56 |             2 | Alexis, Frank (55) / Alexis, F. (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
|  7004521635 |           55 |             2 | Leiva, Hugo (48) / Leiva, H. (7)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|  7005138070 |           50 |             2 | Albericio, Fernando (48) / Alberício, Fernando (2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
|  6603163202 |           49 |             2 | Debut, Alexis (48) / Debut, A. (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 58202302000 |           48 |            12 | Ramírez-Cando, Lenin (24) / Ramirez-Cando, Lenin J. (8) / Ramírez-Cando, Lenin J. (3) / Ramirez-Cando, Lenin Javier (3) / Ramirez-Cando, Lenin (2) / Ramírez, Lenin (2) / Cando, L.J. Ramirez (1) / Ramirez-Cando, Lenín (1) / Cando, Lenin Javier Ramirez (1) / Ramirez-Cando, L. (1) / Cando, Lenin Javier Ramírez (1) / Ramiréz-Cando, Lenín (1)                                                                                                                                                                                                                                                                                         |
| 57580879100 |           47 |             3 | Cadena-Morejón, Carolina (39) / Cadena-Morejon, Carolina (7) / Cadena, Carolina (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 57202499664 |           43 |             3 | Morocho-Cayamcela, Manuel Eugenio (40) / Eugenio Morocho-Cayamcela, Manuel (2) / Morocho-Cayamcela, Manuel E. (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 58095317100 |           39 |             7 | Rodríguez, Hortensia (28) / Rodriguez, Hortensia (5) / Rodríguez Cabrera, Hortensia M. (2) / Rodríguez-Cabrera, Hortensia María (1) / Cabrera, Hortensia Rodriguez (1) / Rodriguez, Hortencia (1) / Cabrera, Hortensia Maria Rodriguez (1)                                                                                                                                                                                                                                                                                                                                                                                                  |
| 54784002000 |           36 |             2 | Briceño, Sarah (34) / Briceño, S. (2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 55798569000 |           34 |             3 | Dénes, H. (16) / Dénes, Helga (16) / Denes, H. (2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 59073365600 |           33 |             5 | Vizcaíno-Imacaña, Paulina (19) / Vizcaino-Imacaña, Paulina (7) / Vizcaíno, Paulina (4) / Vizcaino, Paulina (2) / Vizcaíno-Imacaňa, Paulina (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
|  6505827132 |           32 |             5 | Amaro, Isidro R. (24) / Amaro, Isidro (5) / Amaro, Isidro-R. (1) / Amaro, I.R. (1) / Amaro-Martín, Isidro (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 24299445000 |           31 |             3 | Mowbray, Duncan John (20) / Mowbray, Duncan J. (9) / Mowbray, D.J. (2)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 23397443400 |           30 |             2 | Infante, Saba (27) / Saba, Infante (3)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 57189729597 |           29 |             2 | Vizuete, Karla (28) / Vizuete, Karla Sofía (1)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

_… 667 filas más no mostradas._

### 4.2 Nombres (normalizados) con varios IDs — posibles perfiles duplicados: 52

| nombre                     |   documentos |   n IDs | IDs (documentos)                                   |
|:---------------------------|-------------:|--------:|:---------------------------------------------------|
| Ni, Ming                   |           14 |       3 | 34979024800 (12), 57206176151 (1), 59861773000 (1) |
| León, Juan Pablo Astudillo |           12 |       2 | 57204736794 (11), 61007805300 (1)                  |
| Hibino, K.                 |            9 |       2 | 7006554782 (8), 57202843809 (1)                    |
| Brämer-Escamilla, Werner   |            8 |       2 | 8853896400 (7), 60136068900 (1)                    |
| Vanegas, Judith            |            8 |       2 | 55895179500 (5), 58926399500 (3)                   |
| Nakamura, Y.               |            8 |       2 | 59591571300 (5), 59110868900 (3)                   |
| Saito, T.                  |            8 |       3 | 59038595500 (4), 59999709500 (3), 59628697100 (1)  |
| Vizcaino, Paulina          |            7 |       2 | 59073365600 (6), 60980170200 (1)                   |
| Zhang, Y.                  |            7 |       3 | 56127227400 (5), 23092555200 (1), 59663111600 (1)  |
| Córdova, Vivian Morera     |            6 |       2 | 59511590800 (3), 6602635796 (3)                    |
| Nakajima, T.               |            6 |       2 | 59584315600 (3), 59589453900 (3)                   |
| Qu, X.B.                   |            6 |       2 | 59100331000 (4), 55606870100 (2)                   |
| Yamamoto, Y.               |            6 |       2 | 57214210329 (4), 59079118000 (2)                   |
| Yamauchi, K.               |            6 |       2 | 56973280300 (4), 59579049200 (2)                   |
| Alvarez, Francisco J.      |            5 |       2 | 57196863407 (3), 59185416500 (2)                   |
| Morales, Diego             |            5 |       2 | 57113132900 (4), 57224571557 (1)                   |
| Sandoya, Verónica          |            5 |       2 | 57195981029 (4), 60582756300 (1)                   |
| Rivera, Ariana             |            5 |       2 | 57211622161 (4), 59842098900 (1)                   |
| van der Hulst, J.M.        |            4 |       2 | 7003809007 (3), 60132551700 (1)                    |
| Wang, J.                   |            4 |       2 | 59864232700 (3), 7701339230 (1)                    |
| Leszczynski, Jerzy         |            4 |       2 | 57203195572 (3), 36012975000 (1)                   |
| Davalos, Raul              |            3 |       2 | 58355942400 (2), 60979783200 (1)                   |
| Vargas, Franklin           |            3 |       2 | 57125585900 (2), 56234575600 (1)                   |
| Ariza García, Eusebio      |            3 |       2 | 55749064000 (2), 58279834400 (1)                   |
| Wang, Heng                 |            2 |       2 | 57209105089 (1), 57155752300 (1)                   |

_… 27 filas más no mostradas._

_Nota: un mismo nombre con varios IDs puede ser un perfil duplicado de Scopus o dos personas homónimas; no se unifican sin evidencia (p. ej., misma afiliación)._

## 5. Formato de las afiliaciones

- `Affiliations` separa instituciones con `;` y los niveles de cada institución con `,`.
- Documentos con entidades HTML (`&#x..;`, `& amp;`) que rompen la separación por `;` si no se decodifican antes: **4**
- Afiliaciones (instancias documento–institución): **8224**; el último segmento es un país reconocido en **8207** (**99.79 %**).
- Afiliaciones por documento: mediana 3, máx. 127

### 5.1 Afiliaciones cuyo último segmento NO es un país

| EID                | último segmento                          | país en otro segmento   | menciona Yachay/Urcuquí   | afiliación                                                                       |
|:-------------------|:-----------------------------------------|:------------------------|:--------------------------|:---------------------------------------------------------------------------------|
| 2-s2.0-85205807219 | Edificio de Especialidades Médicas       | —                       | no                        | Universidad San Francisco de Quito (USFQ), Grupo de Medicina Molecular y Trasla… |
| 2-s2.0-85115450734 | Brazil. Electronic address: roliveira@i… | —                       | no                        | Zona Oeste State University, Laboratory of Nanoradiopharmaceuticals and Radioph… |
| 2-s2.0-85125245616 | Yachay Tech University                   | —                       | sí                        | Yachay Tech University                                                           |
| 2-s2.0-85125245616 | CELEC EP                                 | —                       | no                        | CELEC EP                                                                         |
| 2-s2.0-85095771040 | SDAS Research Group                      | —                       | no                        | SDAS Research Group                                                              |
| 2-s2.0-85108018840 | SDAS Research Group                      | —                       | no                        | SDAS Research Group                                                              |
| 2-s2.0-85080144985 | Universidad de Investigación de Tecnolo… | —                       | sí                        | School of Biological and Applied, Biomedical Engineering Department, Universida… |
| 2-s2.0-85080104468 | Vice Chancellor Of Research and Innovat… | —                       | sí                        | Vice Chancellor Of Research and Innovation Yachay Tech University School of Bio… |
| 2-s2.0-85080128342 | SDSN Andes Youth Network                 | —                       | no                        | SDSN Andes Youth Network                                                         |
| 2-s2.0-85101345436 | Universidad de Investigación de Tecnolo… | —                       | sí                        | Universidad de Investigación de Tecnología Experimental Yachay Tech              |
| 2-s2.0-85114001112 | Universidad YachayTech                   | —                       | sí                        | Escuela de Ciencias Biológicas e Ingeniería Carrera de Biología, Universidad Ya… |
| 2-s2.0-85114001112 | Universidad Yachay Tech                  | —                       | sí                        | Estudiante de pregrado de Biología, Escuela de Ciencias Biológicas e Ingeniería… |
| 2-s2.0-85114001112 | Universidad Yachay Tech                  | —                       | sí                        | Escuela de Ciencias Matemáticas y Computacionales Carrera de Matemáticas, Unive… |
| 2-s2.0-85114001112 | Fondo Para la Protección del Agua (FONA… | —                       | no                        | Área de Conservación Hídrica Antisana, Fondo Para la Protección del Agua (FONAG) |
| 2-s2.0-85084110357 | Universidad de Investigación de Tecnolo… | —                       | sí                        | Universidad de Investigación de Tecnología Experimental Yachay Tech              |
| 2-s2.0-85084114334 | School of Biological Sciences and Engin… | —                       | sí                        | School of Biological Sciences and Engineering Yachay Tech                        |
| 2-s2.0-85084115743 | Universidad de Investigación de Tecnolo… | —                       | sí                        | Universidad de Investigación de Tecnología Experimental Yachay Tech              |

### 5.2 Alineación de `Authors with affiliations` con `Author(s) ID`

- Entradas de `Authors with affiliations` que empiezan con el nombre corto del autor en la misma posición de `Authors`: **12041 / 12041** (100.00 %) → el orden está alineado con `Author(s) ID`.
- Formato de cada entrada: `Apellido I., Inst1 nivel, …, País1, Inst2 …, País2`. Un autor con varias afiliaciones las tiene **unidas por comas** dentro de la misma entrada, así que el último segmento NO basta: hay que buscar países en todos los segmentos.
- Entradas autor–documento con más de un país: **1060**

Documentos con conteos desalineados (EID, #IDs, #nombres completos, #nombres cortos, #entradas con afiliación):

| EID                |   IDs |   full names |   Authors |   AwA |
|:-------------------|------:|-------------:|----------:|------:|
| 2-s2.0-85205807219 |     8 |            8 |         8 |     9 |
| 2-s2.0-85115450734 |    12 |           12 |        12 |    13 |

### 5.3 Consistencia de países entre `Affiliations` y `Authors with affiliations`

- Documentos cuyo conjunto de países difiere entre ambas columnas: **4**
  (los países 'solo en AwA' pueden ser falsos positivos, p. ej. un segmento 'Georgia' que es un estado de EE. UU., o recuperaciones válidas de afiliaciones sin país).

| EID                 | solo en Affiliations   | solo en AwA   |
|:--------------------|:-----------------------|:--------------|
| 2-s2.0-105053573709 | —                      | PRI           |
| 2-s2.0-85199657612  | —                      | SMR           |
| 2-s2.0-85049590326  | —                      | ARM           |
| 2-s2.0-85076861121  | —                      | HKG           |

## 6. Países detectados

- Países únicos reconocidos: **107** (incluido Ecuador); socios: **106**
- Continentes presentes: Africa, Asia, Europe, North America, Oceania, South America

| texto en Scopus           | nombre ISO                            | ISO3   |   ISO num | continente    |   documentos |   afiliaciones | revisar   |
|:--------------------------|:--------------------------------------|:-------|----------:|:--------------|-------------:|---------------:|:----------|
| Ecuador                   | Ecuador                               | ECU    |       218 | South America |         1823 |           3373 |           |
| Spain                     | Spain                                 | ESP    |       724 | Europe        |          375 |            627 |           |
| United States             | United States                         | USA    |       840 | North America |          272 |            610 |           |
| Venezuela                 | Venezuela, Bolivarian Republic of     | VEN    |       862 | South America |          185 |            267 | sí        |
| Mexico                    | Mexico                                | MEX    |       484 | North America |          149 |            235 |           |
| Colombia                  | Colombia                              | COL    |       170 | South America |          145 |            252 |           |
| Germany                   | Germany                               | DEU    |       276 | Europe        |          138 |            230 |           |
| Chile                     | Chile                                 | CHL    |       152 | South America |           89 |            188 |           |
| Brazil                    | Brazil                                | BRA    |       076 | South America |           88 |            208 |           |
| France                    | France                                | FRA    |       250 | Europe        |           84 |            124 |           |
| Canada                    | Canada                                | CAN    |       124 | North America |           79 |            111 |           |
| Italy                     | Italy                                 | ITA    |       380 | Europe        |           69 |            131 |           |
| United Kingdom            | United Kingdom                        | GBR    |       826 | Europe        |           61 |            100 |           |
| China                     | China                                 | CHN    |       156 | Asia          |           60 |            161 |           |
| South Africa              | South Africa                          | ZAF    |       710 | Africa        |           55 |             78 |           |
| Australia                 | Australia                             | AUS    |       036 | Oceania       |           52 |            213 |           |
| Austria                   | Austria                               | AUT    |       040 | Europe        |           50 |             56 |           |
| Argentina                 | Argentina                             | ARG    |       032 | South America |           49 |            101 |           |
| Netherlands               | Netherlands                           | NLD    |       528 | Europe        |           38 |             71 |           |
| Belgium                   | Belgium                               | BEL    |       056 | Europe        |           30 |             54 |           |
| Switzerland               | Switzerland                           | CHE    |       756 | Europe        |           30 |             47 |           |
| Japan                     | Japan                                 | JPN    |       392 | Asia          |           29 |            158 |           |
| Sweden                    | Sweden                                | SWE    |       752 | Europe        |           25 |             34 |           |
| South Korea               | Korea, Republic of                    | KOR    |       410 | Asia          |           24 |             32 | sí        |
| Saudi Arabia              | Saudi Arabia                          | SAU    |       682 | Asia          |           24 |             26 |           |
| Cuba                      | Cuba                                  | CUB    |       192 | North America |           23 |             29 |           |
| Portugal                  | Portugal                              | PRT    |       620 | Europe        |           23 |             39 |           |
| Morocco                   | Morocco                               | MAR    |       504 | Africa        |           19 |             28 |           |
| India                     | India                                 | IND    |       356 | Asia          |           18 |             35 |           |
| Denmark                   | Denmark                               | DNK    |       208 | Europe        |           17 |             26 |           |
| Hungary                   | Hungary                               | HUN    |       348 | Europe        |           17 |             19 |           |
| Russian Federation        | Russian Federation                    | RUS    |       643 | Europe        |           17 |             31 |           |
| United Arab Emirates      | United Arab Emirates                  | ARE    |       784 | Asia          |           15 |             18 |           |
| Czech Republic            | Czechia                               | CZE    |       203 | Europe        |           15 |             20 | sí        |
| Peru                      | Peru                                  | PER    |       604 | South America |           15 |             28 |           |
| Poland                    | Poland                                | POL    |       616 | Europe        |           15 |             45 |           |
| Norway                    | Norway                                | NOR    |       578 | Europe        |           13 |             14 |           |
| Algeria                   | Algeria                               | DZA    |       012 | Africa        |           12 |             15 |           |
| Malaysia                  | Malaysia                              | MYS    |       458 | Asia          |           12 |             16 |           |
| Bolivia                   | Bolivia, Plurinational State of       | BOL    |       068 | South America |           11 |             18 | sí        |
| Egypt                     | Egypt                                 | EGY    |       818 | Africa        |           11 |             13 |           |
| Finland                   | Finland                               | FIN    |       246 | Europe        |           10 |             15 |           |
| Panama                    | Panama                                | PAN    |       591 | North America |           10 |             10 |           |
| Singapore                 | Singapore                             | SGP    |       702 | Asia          |           10 |             32 |           |
| Israel                    | Israel                                | ISR    |       376 | Asia          |            9 |             13 |           |
| Greece                    | Greece                                | GRC    |       300 | Europe        |            8 |             12 |           |
| New Zealand               | New Zealand                           | NZL    |       554 | Oceania       |            8 |             12 |           |
| Armenia                   | Armenia                               | ARM    |       051 | Asia          |            7 |             13 |           |
| Costa Rica                | Costa Rica                            | CRI    |       188 | North America |            7 |              8 |           |
| Uruguay                   | Uruguay                               | URY    |       858 | South America |            7 |              8 |           |
| Dominican Republic        | Dominican Republic                    | DOM    |       214 | North America |            6 |              8 |           |
| Indonesia                 | Indonesia                             | IDN    |       360 | Asia          |            6 |             23 |           |
| Croatia                   | Croatia                               | HRV    |       191 | Europe        |            5 |              7 |           |
| Philippines               | Philippines                           | PHL    |       608 | Asia          |            5 |              7 |           |
| Romania                   | Romania                               | ROU    |       642 | Europe        |            5 |              9 |           |
| Slovakia                  | Slovakia                              | SVK    |       703 | Europe        |            5 |              9 |           |
| Turkey                    | Türkiye                               | TUR    |       792 | Asia          |            5 |              7 | sí        |
| Congo                     | Congo                                 | COG    |       178 | Africa        |            4 |              5 |           |
| Ireland                   | Ireland                               | IRL    |       372 | Europe        |            4 |              5 |           |
| Kazakhstan                | Kazakhstan                            | KAZ    |       398 | Asia          |            4 |              4 |           |
| Madagascar                | Madagascar                            | MDG    |       450 | Africa        |            4 |              4 |           |
| Pakistan                  | Pakistan                              | PAK    |       586 | Asia          |            4 |              4 |           |
| Tanzania                  | Tanzania, United Republic of          | TZA    |       834 | Africa        |            4 |              8 | sí        |
| Cameroon                  | Cameroon                              | CMR    |       120 | Africa        |            3 |              7 |           |
| Iran                      | Iran, Islamic Republic of             | IRN    |       364 | Asia          |            3 |              3 | sí        |
| Iraq                      | Iraq                                  | IRQ    |       368 | Asia          |            3 |             18 |           |
| Puerto Rico               | Puerto Rico                           | PRI    |       630 | North America |            3 |              5 |           |
| Thailand                  | Thailand                              | THA    |       764 | Asia          |            3 |              3 |           |
| Uganda                    | Uganda                                | UGA    |       800 | Africa        |            3 |              3 |           |
| Brunei Darussalam         | Brunei Darussalam                     | BRN    |       096 | Asia          |            2 |              2 |           |
| Cote d'Ivoire             | Côte d'Ivoire                         | CIV    |       384 | Africa        |            2 |              2 | sí        |
| Fiji                      | Fiji                                  | FJI    |       242 | Oceania       |            2 |              2 |           |
| French Guiana             | French Guiana                         | GUF    |       254 | South America |            2 |              2 |           |
| Hong Kong                 | Hong Kong                             | HKG    |       344 | Asia          |            2 |              2 |           |
| Iceland                   | Iceland                               | ISL    |       352 | Europe        |            2 |              2 |           |
| Laos                      | Lao People's Democratic Republic      | LAO    |       418 | Asia          |            2 |              2 | sí        |
| Lithuania                 | Lithuania                             | LTU    |       440 | Europe        |            2 |              3 |           |
| Nigeria                   | Nigeria                               | NGA    |       566 | Africa        |            2 |              2 |           |
| El Salvador               | El Salvador                           | SLV    |       222 | North America |            2 |              2 |           |
| Serbia                    | Serbia                                | SRB    |       688 | Europe        |            2 |              2 |           |
| Suriname                  | Suriname                              | SUR    |       740 | South America |            2 |              3 |           |
| Slovenia                  | Slovenia                              | SVN    |       705 | Europe        |            2 |              2 |           |
| Taiwan                    | Taiwan, Province of China             | TWN    |       158 | Asia          |            2 |              3 | sí        |
| Viet Nam                  | Viet Nam                              | VNM    |       704 | Asia          |            2 |              3 |           |
| Burkina Faso              | Burkina Faso                          | BFA    |       854 | Africa        |            1 |              1 |           |
| Bangladesh                | Bangladesh                            | BGD    |       050 | Asia          |            1 |              1 |           |
| Bulgaria                  | Bulgaria                              | BGR    |       100 | Europe        |            1 |              1 |           |
| Bahamas                   | Bahamas                               | BHS    |       044 | North America |            1 |              1 |           |
| Democratic Republic Congo | Congo, The Democratic Republic of the | COD    |       180 | Africa        |            1 |              2 | sí        |
| Djibouti                  | Djibouti                              | DJI    |       262 | Africa        |            1 |              1 |           |
| Estonia                   | Estonia                               | EST    |       233 | Europe        |            1 |              1 |           |
| Georgia                   | Georgia                               | GEO    |       268 | Asia          |            1 |              2 |           |
| Guatemala                 | Guatemala                             | GTM    |       320 | North America |            1 |              1 |           |
| Guyana                    | Guyana                                | GUY    |       328 | South America |            1 |              1 |           |
| Honduras                  | Honduras                              | HND    |       340 | North America |            1 |              1 |           |
| Lebanon                   | Lebanon                               | LBN    |       422 | Asia          |            1 |              1 |           |
| Sri Lanka                 | Sri Lanka                             | LKA    |       144 | Asia          |            1 |              2 |           |
| Luxembourg                | Luxembourg                            | LUX    |       442 | Europe        |            1 |              1 |           |
| Latvia                    | Latvia                                | LVA    |       428 | Europe        |            1 |              1 |           |
| Myanmar                   | Myanmar                               | MMR    |       104 | Asia          |            1 |              1 |           |
| Nepal                     | Nepal                                 | NPL    |       524 | Asia          |            1 |              1 |           |
| Papua New Guinea          | Papua New Guinea                      | PNG    |       598 | Oceania       |            1 |              1 |           |
| Paraguay                  | Paraguay                              | PRY    |       600 | South America |            1 |              4 |           |
| Qatar                     | Qatar                                 | QAT    |       634 | Asia          |            1 |              1 |           |
| Sudan                     | Sudan                                 | SDN    |       729 | Africa        |            1 |              1 |           |
| Tunisia                   | Tunisia                               | TUN    |       788 | Africa        |            1 |              2 |           |
| Vanuatu                   | Vanuatu                               | VUT    |       548 | Oceania       |            1 |              1 |           |

Variantes sospechosas (columna *revisar* = sí): el texto de Scopus difiere del nombre ISO, o es un territorio (Hong Kong, Puerto Rico, Guayana Francesa, Taiwán) que puede no existir como polígono propio en `world-atlas` 110m.

## 7. Variantes del nombre de Yachay Tech

| segmento con 'Yachay'                                                    |   frecuencia |
|:-------------------------------------------------------------------------|-------------:|
| Yachay Tech University                                                   |         1296 |
| Universidad Yachay Tech                                                  |          246 |
| Yachay Tech                                                              |          243 |
| Hda. San José s/n y Proyecto Yachay                                      |          101 |
| Yachay City of Knowledge                                                 |           80 |
| Universidad de Investigación de Tecnología Experimental Yachay           |           73 |
| Yachay University for Experimental Technology and Research (Yachay Tech) |           22 |
| Hacienda San José s/n y Proyecto Yachay                                  |           17 |
| University Yachay Tech                                                   |           15 |
| University of Yachay Tech                                                |           15 |
| Yachay-Tech University                                                   |           12 |
| University YachayTech                                                    |           10 |
| YachayTech University                                                    |            9 |
| YachayTech                                                               |            9 |
| Yachay Tech.                                                             |            9 |
| Proyecto Yachay                                                          |            8 |
| University of Investigation and Experimental Technology Yachay           |            8 |
| Universidad de Investigación de Tecnología Experimental Yachay Tech      |            8 |
| Yachay Experimental Technology Research University                       |            7 |
| Yachay Tech Medicinal Chemistry Research Group (MedChem-YT)              |            7 |
| Yachay Tech. University                                                  |            7 |
| Hda. San José S/N y Proyecto Yachay                                      |            6 |
| Yachay                                                                   |            6 |
| Universidad Yachay                                                       |            6 |
| Yachaytech                                                               |            6 |
| Hacienda San José s/n Proyecto Yachay                                    |            5 |
| Hacienda San José s/n y Proyecto Yachay (Ciudad del Conocimiento Yachay) |            5 |
| Yachay University for Experimental Technology and Research               |            4 |
| Hcda San José y Proyecto Yachay                                          |            4 |
| Universidad Yachay-Tech                                                  |            4 |
| Yachay Botanical Garden                                                  |            4 |
| Universidad de Investigación de Tecnología Experimental YACHAY           |            4 |
| Ciudad Del Conocimiento Yachay                                           |            4 |
| Universidad de Tecnología Experimental Yachay Tech                       |            3 |
| Yachay Tech Language Center                                              |            3 |
| Yachay Tech University of Technology and Research                        |            3 |
| Yachay Scientific Computing Group (SCG)                                  |            3 |
| Yachay-Tech University Hacienda San José                                 |            3 |
| Yachay University                                                        |            3 |
| Universidad de Yachay Tech                                               |            3 |

_… 101 filas más no mostradas._

- Documentos cuyo campo `Affiliations` no menciona 'Yachay': **1**

| EID                |   Year | Title                                                                                      | Affiliations                      |
|:-------------------|-------:|:-------------------------------------------------------------------------------------------|:----------------------------------|
| 2-s2.0-85026783023 |   2017 | Acquired Character, Self-Control and Morality: Towards a Comprehensive View of Schopenhau… | Universidad Yachai Tech., Ecuador |

## 8. Documentos sin país identificable y sin Ecuador

- Documentos sin ningún país identificable (regla del último segmento): **8**

| EID                |   Year | Affiliations                                                                                                                                 |
|:-------------------|-------:|:---------------------------------------------------------------------------------------------------------------------------------------------|
| 2-s2.0-85125245616 |   2021 | Yachay Tech University; CELEC EP                                                                                                             |
| 2-s2.0-85080144985 |   2019 | School of Biological and Applied, Biomedical Engineering Department, Universidad de Investigación de Tecnología Experimental Yachay Tech     |
| 2-s2.0-85080104468 |   2019 | Vice Chancellor Of Research and Innovation Yachay Tech University School of Biological Sciences & Engineering                                |
| 2-s2.0-85101345436 |   2019 | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                                          |
| 2-s2.0-85114001112 |   2019 | Escuela de Ciencias Biológicas e Ingeniería Carrera de Biología, Universidad YachayTech; Estudiante de pregrado de Biología, Escuela de Cie… |
| 2-s2.0-85084110357 |   2017 | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                                          |
| 2-s2.0-85084114334 |   2017 | School of Biological Sciences and Engineering Yachay Tech                                                                                    |
| 2-s2.0-85084115743 |   2017 | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                                          |

- Documentos donde Ecuador no aparece como país: **13**

| EID                |   Year | Title                                                        | Affiliations                                                                                                             |
|:-------------------|-------:|:-------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------|
| 2-s2.0-85125245616 |   2021 | Magnetometry survey applied to geothermal exploration in Ch… | Yachay Tech University; CELEC EP                                                                                         |
| 2-s2.0-85080144985 |   2019 | The structure of neurexin 1α (n1α) and its role as synaptic… | School of Biological and Applied, Biomedical Engineering Department, Universidad de Investigación de Tecnología Experim… |
| 2-s2.0-85080104468 |   2019 | Bionatura journal enters scopus database                     | Vice Chancellor Of Research and Innovation Yachay Tech University School of Biological Sciences & Engineering            |
| 2-s2.0-85056169734 |   2018 | Topological 3D elevation data interpolation of ASTER GDEM b… | Universiti Teknologi Malaysia (UTM), Faculty of Geoinformation and Real Estate, Malaysia; Yachay Tech University, Schoo… |
| 2-s2.0-85101345436 |   2019 | Enzyme replacement therapy with pegademase bovine for human… | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                      |
| 2-s2.0-85114001112 |   2019 | Population estimates and habitat selection of white-tailed … | Escuela de Ciencias Biológicas e Ingeniería Carrera de Biología, Universidad YachayTech; Estudiante de pregrado de Biol… |
| 2-s2.0-85062673161 |   2018 | Methodology for the design and sim…                          | Grupo de Investigación Eslinga, Universidad Cooperativa de Colombia-Pasto, Colombia; Grupo de Investigación CIGIP, Univ… |
| 2-s2.0-85084110357 |   2017 | Lycalopex culpaeus reissii , the second largest canid in So… | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                      |
| 2-s2.0-84946780778 |   2015 | Doping Carbon Nanomaterials with Heteroatoms                 | Faculty of Physics, University of Vienna, Vienna, Austria; Yachay Tech University, School of Physical Sciences and Nano… |
| 2-s2.0-85084114334 |   2017 | DNA microarrays: Recent Advances                             | School of Biological Sciences and Engineering Yachay Tech                                                                |
| 2-s2.0-85022221871 |   2017 | Contact angle entropy and macroscopic friction in noncohesi… | Laboratorio de Física Estadística de Sistemas Desordenados, Centro de Física, Instituto Venezolano de Investigaciones C… |
| 2-s2.0-84911409572 |   2016 | Pre-service teacher perspectives towards pedagogical uses o… | Kansas State University / Yachay Tech, United States                                                                     |
| 2-s2.0-85084115743 |   2017 | Coordinated hunting; [Caza coordinada]                       | Universidad de Investigación de Tecnología Experimental Yachay Tech                                                      |

## 9. Vista previa (sin limpiar) de la colaboración internacional por año

|   año |   documentos |   docs internacionales |   % internacional |   países socios |   continentes socios |
|------:|-------------:|-----------------------:|------------------:|----------------:|---------------------:|
|  2014 |           17 |                     14 |              82.4 |              18 |                    6 |
|  2015 |           52 |                     51 |              98.1 |              56 |                    6 |
|  2016 |           63 |                     52 |              82.5 |              48 |                    6 |
|  2017 |          120 |                     98 |              81.7 |              40 |                    5 |
|  2018 |          139 |                    119 |              85.6 |              55 |                    6 |
|  2019 |          189 |                    147 |              77.8 |              47 |                    6 |
|  2020 |          197 |                    151 |              76.6 |              51 |                    6 |
|  2021 |          201 |                    136 |              67.7 |              50 |                    6 |
|  2022 |          158 |                    107 |              67.7 |              47 |                    6 |
|  2023 |          177 |                    111 |              62.7 |              47 |                    6 |
|  2024 |          185 |                    126 |              68.1 |              34 |                    6 |
|  2025 |          178 |                    111 |              62.4 |              43 |                    6 |
|  2026 |          147 |                     93 |              63.3 |              39 |                    6 |
|  2027 |           13 |                      6 |              46.2 |               4 |                    3 |
