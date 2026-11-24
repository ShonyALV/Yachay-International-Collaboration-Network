# Hallazgos — Red de colaboración internacional de Yachay Tech (2014–2026)

**Pregunta analítica.** ¿Cómo ha evolucionado la red de colaboración internacional de Yachay Tech
desde 2014? ¿Su alcance geográfico acumulado sigue creciendo mientras la colaboración de cada año
se concentra en menos socios y una menor proporción de documentos internacionales?

**Respuesta corta.** Sí en las dos partes, con matices:

- **Alcance acumulado.** Creció rápido hasta 2018–2021 y ahora está **casi saturado**: 104 países, solo 9 nuevos desde 2022.
- **Colaboración anual.** Es **menos internacional**: del 81–86 % al 63–68 % de los documentos. Además trabaja con **menos socios por año**, sin que un solo país llegue a dominar.

Datos: Scopus, afiliación Yachay Tech (AF-ID 60105012). 1.811 documentos tras la limpieza, 105 países
(104 socios más Ecuador) en 6 regiones. 2026 es un año parcial, con datos hasta noviembre de 2026.
Las cifras salen de `output/metricas_por_anio.csv` y `output/json/metricas.json`.

---

## 1. Hallazgos principales

### H1. El alcance acumulado creció rápido y luego se estancó
- **Crecimiento.** Los socios acumulados pasan de **18 en 2014** a **56 en 2015**, 72 en 2017, 95 en 2021 y **104 en 2026**.
- **Concentración en los primeros años.** El 69 % de todos los socios (72 de 104) ya había aparecido en 2017. Entre 2015 y 2017 entraron 54 países nuevos, sobre todo de Europa (19) y Asia (18).
- **Desde 2022 entran muy pocos.** Solo 9 países nuevos en cinco años: Islandia, Georgia, Honduras (2022); Burkina Faso, Bahamas, Paraguay (2023); Bulgaria, Irak (2025) y Guatemala (2026). En **2024 no entró ninguno**.
- **La diversidad acumulada no cambia desde 2016.** El índice de Shannon se mantiene entre 3,50 y 3,56, y el número efectivo de socios en torno a 19.
- 📍 **En la visualización:** *Mapa → Cumulative → Play*. En 2015 el mapa "explota" con 38 pulsos de países nuevos. Desde 2022 casi no aparecen pulsos y la tarjeta *New partner countries* marca 0–3.

### H2. La colaboración anual es cada vez menos internacional
- **Caída del porcentaje.** Los documentos con al menos un país extranjero bajan de **81–86 % (2016–2018)** a **62,7–68,1 % (2021–2026)**.
- **En números absolutos.** Los documentos internacionales tocan techo en **2020 (150)** y luego bajan a 104–126 por año. Los documentos solo con Ecuador se triplican: de **22 en 2017** a **65–66 en 2021 y 2023**.
- **El resultado no depende de las megacolaboraciones.** Con el filtro activado, el porcentaje es prácticamente igual: 85,3 % en 2018 y 62,3 % en 2023.
- 📍 **En la visualización:** sparkline *% international documents* y tarjeta *International documents* en modo **Annual**, de 2018 a 2023.

### H3. Menos socios por año, concentración moderada y sin un socio dominante
- **Menos socios.** Los países socios por año bajan de 47–54 (2018–2023) a **34 en 2024**, el mínimo desde 2014, y a 43 en 2025.
- **Menor número efectivo de socios** (1/HHI): de 18,1–18,6 en 2021–2022 a **12,3 en 2024**, y 15,6 en 2025. El HHI sube de 0,054 (2021) a **0,081 (2024)**.
- **El reparto entre los socios no cambia.** La equitatividad de Pielou se mantiene entre 0,82 y 0,90 todos los años. La concentración viene de tener **menos** socios, no de que uno acapare la colaboración.
- **España** es el primer socio en 10 de 13 años, pero desde 2016 nunca supera el 18 % de las colaboraciones del año.
- 📍 **En la visualización:** sparklines *Partner countries* y *HHI concentration* en modo **Annual**. En 2024 se ve la caída de socios (▼13 frente a 2023) y el pico del HHI.

### H4. Un núcleo estable de socios y una periferia ocasional
- **Núcleo de 11 países** presentes los 13 años: España, Estados Unidos, Venezuela, México, Brasil, Argentina, Chile, Francia, Países Bajos, China y Sudáfrica.
- **Otros 12 países** colaboran 10 años o más, entre ellos Colombia, Alemania, Italia, Reino Unido, Canadá, Suiza, Australia, Japón y Austria.
- **Periferia ocasional.** **25 socios aparecen en un solo año** y 38 en dos o menos, sobre todo de Asia (7) y África (5). Suelen llegar con un único artículo de muchos países.
- **Top acumulado (2014–2026):** España 369 documentos, Estados Unidos 271, Venezuela 185, México 146 y Colombia 144.
- 📍 **En la visualización:** *Network → Cumulative 2026*. Los nodos grandes junto a Ecuador forman el núcleo. *Network → Annual*, avanzando año a año: los nodos pequeños de la periferia aparecen y desaparecen.

### H5. La red se reorientó hacia América Latina
- **América Latina y el Caribe** pasa del **16–20 % de las colaboraciones (2014–2017)** al **31–40 % (2018–2026)**. Colombia es el primer socio en 2018–2019, y México el segundo en 2024 y 2026.
- **Europa** sigue siendo la primera o segunda región todos los años (34–52 %).
- **África** cae del **29 % (2014)** al 1–4 %, porque el peso inicial venía de Sudáfrica y de proyectos puntuales.
- **Norteamérica y Oceanía** crecen en 2025: 19,8 % y 6,5 %, con Canadá y Australia.
- **Cobertura regional completa desde el inicio.** Ya en 2014 había socios en las 6 regiones. La expansión posterior ocurre **dentro** de cada región, no hacia regiones nuevas.
- 📍 **En la visualización:** *Map → Annual*, comparando 2016 con 2019. En 2016 los arcos van sobre todo a Europa; en 2019 se ven arcos más gruesos hacia Colombia, Venezuela y México. Lo confirman las barras del *Top 5*.

### H6. Las megacolaboraciones inflan algunos años, pero no cambian la tendencia
- **Pocos documentos.** Hay **15 documentos (0,8 %)** con 10 países o más, casi todos de ecología, biogeografía o astrofísica. El mayor es un artículo de PNAS de 2015 con 43 países y 173 autores.
- **Mucho efecto en el recuento anual de socios:**

  | Año | Con megacolaboraciones | Sin ellas |
  |---|---|---|
  | 2015 | 56 | 27 |
  | 2016 | 47 | 29 |
  | 2018 | 54 | 39 |
  | 2022 | 47 | 36 |

- **Las tendencias se mantienen sin ellas:** la caída del % internacional, el estancamiento acumulado y la reorientación latinoamericana.
- 📍 **En la visualización:** activar *Exclude mega-collaborations* en *Network → Annual 2015*. La red pasa de 57 nodos a 28.

---

## 2. Qué revela la vista anual frente a la acumulada

| | Vista **acumulada** | Vista **anual** |
|---|---|---|
| Socios | Crece siempre: 18 → 104. Cuenta una historia de expansión continua. | Sube y baja (18, 56, 47, 40, 54 … 34, 43, 38). Muestra cuántos socios están activos cada año. |
| Diversidad | Shannon ≈ 3,5 y HHI ≈ 0,052, estables desde 2016: el pasado amortigua los cambios. | Desde 2015 el HHI se mueve entre 0,047 y 0,081 (0,14 en 2014), con un pico en 2024: muestra los cambios de cada año. |
| % internacional | Baja despacio, de 94 % a 72 %, porque arrastra los primeros años. | Baja con claridad: de 85 % (2018) a 63–68 %. |
| Nuevos países | Se ven como "llegadas" que se acumulan. | Se ven también los países que **no vuelven**: 25 socios aparecen un solo año. |
| Megacolaboraciones | Su efecto se diluye con el tiempo. | Dominan años concretos (2015, 2016, 2018, 2022). |

**Conclusión.** La vista acumulada sola haría creer que la red sigue expandiéndose. La vista anual
muestra que esa expansión ya ocurrió y que la colaboración actual es más doméstica y con menos
socios. Por eso hay que mostrar las dos.

---

## 3. Limitaciones

- **Cobertura de Scopus.** Faltan revistas regionales, en español y no indexadas, lo que probablemente subestima la colaboración latinoamericana. Las actas de congreso dependen de la indexación de cada serie.
- **Conteo completo.** Cada documento suma 1 a cada par de países sin importar cuántos autores aporta cada uno. Un artículo con 43 países pesa lo mismo, por arista, que uno bilateral. El filtro de megacolaboraciones mitiga, pero no corrige, este sesgo.
- **El país se toma de la afiliación.** Un autor extranjero con afiliación ecuatoriana cuenta como Ecuador, y una afiliación doble cuenta para ambos países. 6 afiliaciones sin país recuperable se descartaron. A 5 documentos se les añadió Ecuador por venir de la afiliación de Yachay Tech.
- **2026 es parcial** (hasta noviembre). Sus valores, como 38 socios o 63 % internacional, no son comparables con años completos. Se excluyeron 13 documentos fechados en 2027.
- **Desambiguación de autores.** El conteo de investigadores únicos depende de los IDs de Scopus. Solo se unieron 16 perfiles evidentes y pueden quedar duplicados u homónimos.
- **Territorios.** Hong Kong se agregó a China y la Guayana Francesa a Francia.
- **Comunidades Louvain.** Tienen modularidad baja (0,156) porque Ecuador conecta con todos. Solo se usan como apoyo visual, no como hallazgo.
- **Atribución institucional.** La red mide coautoría, no la intensidad ni el origen de cada colaboración (proyectos, movilidad, personal docente extranjero de Yachay Tech, etc.).

---

## 4. Guion del video (máx. 5:00)

Preparación: `python -m http.server 8000` en la raíz del proyecto y abrir `http://localhost:8000/viz/`
a pantalla completa (F11) en 1920×1080. Tema oscuro. Cada estado se puede abrir directamente con su `#hash`.

### 0:00 – 0:30 · Pregunta y relevancia
- **Estado:** `#mapa-acumulado-2026`, sin tocar nada.
- **Narración:** "Yachay Tech nació en 2014 como universidad de investigación con mucho personal internacional. Nos preguntamos si su red de colaboración internacional sigue expandiéndose o si, con el tiempo, la colaboración de cada año se ha concentrado en menos socios y se ha vuelto más doméstica. Para un proyecto así, la colaboración internacional es un indicador clave de visibilidad y de capacidad de investigación."

### 0:30 – 1:30 · Construcción del grafo
- **Estado:** seguir en el mapa y señalar con el cursor la leyenda y un arco (tooltip).
- **Narración:**
  - Partimos de 1.836 registros de Scopus con la afiliación de Yachay Tech.
  - Tras limpiar duplicados, fechas futuras, erratas y retractaciones quedan 1.811 documentos entre 2014 y 2026.
  - Para cada afiliación extrajimos y normalizamos el país (código ISO y región).
  - **Nodos** = países; **aristas** = dos países firman juntos un mismo documento. El grafo es no dirigido y ponderado por el número de documentos (conteo completo). Ecuador es el nodo central.
  - Construimos dos grafos temporales: **anual**, solo con los documentos de cada año, y **acumulado**, desde 2014 hasta ese año.
  - Calculamos métricas por año: socios, % internacional, Shannon, HHI y comunidades Louvain.
- Pasar a `#red-acumulado-2026` y mostrar un instante la vista Red (Ecuador al centro, tamaño = grado ponderado).

### 1:30 – 3:30 · Demostración temporal
1. **(1:30) Expansión acumulada.** `#mapa-acumulado-2014` → **Play**.
   - Señalar el "estallido" de 2015: 38 pulsos y 56 socios.
   - Hacia 2021 el mapa está casi completo (95 socios).
   - Pausar en **2024**: *New partner countries = 0*. Apuntar al sparkline de socios, que se aplana.
2. **(2:10) Vista anual.** Cambiar a **Annual** y poner `#mapa-anual-2016` → avanzar con `→` hasta 2019.
   - En 2016 los arcos van sobre todo a Europa; en 2019, Colombia y Venezuela suben al Top 5.
   - Seguir a 2024: 34 socios (▼13) y México segundo.
3. **(2:45) Concentración.** Apuntar a los sparklines en Annual:
   - *% international* baja de 85 % a 63–68 %.
   - *HHI* hace un pico en 2024.
   - *Partner countries* baja.
4. **(3:05) Robustez.** `#red-anual-2015` → activar *Exclude mega-collaborations*.
   - La red de 2015 pasa de 57 a 28 nodos.
   - Volver a 2023: el % internacional casi no cambia.
5. **(3:20) Núcleo.** `#red-acumulado-2026`, zoom con la rueda sobre Ecuador: el núcleo de socios estables (España, EE. UU., Venezuela, México, Colombia).

### 3:30 – 5:00 · Hallazgos (pantalla: `#mapa-acumulado-2026`, o un zoom a América Latina)
1. **Expansión y saturación.** De 18 a 104 países; el 69 % ya había aparecido en 2017 y solo entran 9 desde 2022.
2. **Menos internacional.** Del 81–86 % al 63–68 % de los documentos. Los internacionales tocan techo en 2020 y los domésticos se triplican.
3. **Menos socios, sin dominancia.** Socios por año de unos 50 a 34–43, número efectivo de socios de 18 a 12–16, pero con un reparto estable (Pielou 0,82–0,90).
4. **Núcleo y periferia.** 11 países presentes todos los años frente a 25 que aparecen una sola vez.
5. **Giro latinoamericano.** América Latina pasa del 16–20 % al 31–40 % de las colaboraciones; África cae del 29 % al 1–4 %.
6. **Cierre:** "La red ya alcanzó su amplitud geográfica. El reto ahora no es sumar países, sino sostener y profundizar la colaboración con un núcleo estable. Esto se ve solo al comparar la vista anual con la acumulada." Mencionar en una frase las limitaciones: Scopus, conteo completo y 2026 parcial.
