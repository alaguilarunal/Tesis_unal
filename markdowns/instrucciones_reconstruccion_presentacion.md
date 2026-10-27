# Instrucciones para reconstruir la presentación del Seminario 4

Archivo base: `presentacion_seminario_4.tex` (Beamer, tema UNAL).
Fecha de la presentación: **21 de octubre de 2026, 7:00 am**. Audiencia: matemáticos (doctores). El autor es ingeniero electrónico y no domina varias herramientas matemáticas, así que **todo lo que quede en las diapositivas debe poder explicarlo él en lenguaje simple**.

---

## 0. Reglas de trabajo

1. Esta es una **presentación de avance**. No existe un MOGP implementado ni el kernel físico completo. Eso se dice al principio y no se oculta.
2. **Regla principal:** si una diapositiva contiene matemática que el autor no puede explicar hoy, se quita del cuerpo. No se borra: se mueve a `respaldo_slides_removidos.tex` (comentada o dentro de `\iffalse ... \fi`) para recuperarla después.
3. Poco texto por diapositiva, lenguaje simple. Cada diapositiva nueva o modificada lleva `\note{...}` con un guion oral de 3 a 4 frases en lenguaje simple.
4. **No inventar cifras, citas ni datos.** Si falta un dato, escribir `[PENDIENTE: ...]` en el texto de la diapositiva y listarlo en el resumen final.
5. No usar la raya larga (`---` o el carácter largo) en el texto de las diapositivas. Usar coma, punto o dos puntos.
6. No afirmar: "significativo", "causalidad", "retardo físico de propagación", "no mejora a la interpolación lineal", "no se ha hecho antes en el mundo". Detalle en la sección 7.
7. Terminología: unificar a **TPM** (así lo usan el anteproyecto, los CSV y el cuaderno). Hoy el `.tex` usa MPT. Reemplazar en todo el documento. Si el autor prefiere MPT, es un cambio global igual de simple.
8. Notación del modelo físico: usar la que ya tiene la presentación (**E0, E1, η1**), no mezclarla con la del documento de estado del arte (E1, E2, η1, η2).

Entrega esperada: el `.tex` corregido, el PDF compilado sin errores, `respaldo_slides_removidos.tex`, y un resumen corto con (a) cambios hechos, (b) lista de `[PENDIENTE]`, (c) decisiones que debe tomar el autor.

---

## 1. Orden final propuesto

La barra de secciones queda: **Problema, Datos, Hipótesis, Dependencia, Procesos Gaussianos, Modelo físico, Pasos siguientes, Conclusiones.** (Se elimina "Resultados".)

| Sección | Diapositivas |
|---|---|
| Inicio | Portada, **Alcance (NUEVA)**, Sumario |
| Problema | Túnel y sistemas (con imagen), EPM, TPM, El problema (brecha de 681 días), Motivación práctica |
| Datos | Los datos, Las cuatro series EPM, Series TPM seleccionadas |
| Hipótesis | Hipótesis de trabajo, **Artículo de referencia: Dalmasso (NUEVA, reemplaza el estado del arte)**, **ML frente a procesos gaussianos (NUEVA)**, Aporte propuesto |
| Dependencia | Herramientas, Pearson, Distance correlation, Transfer entropy (conceptual), CCM (conceptual, NUEVA), Síntesis |
| Procesos Gaussianos | **Qué es un proceso gaussiano (NUEVA)**, Definición formal, Distribución posterior, Hiperparámetros (simplificada) |
| Modelo físico | **Modelo de Nishihara (con diagrama)** |
| Pasos siguientes | **2 diapositivas conceptuales (NUEVAS)** |
| Cierre | Conclusiones, Gracias |
| Anexos | Pearson, dCor (construcción), TE formal, CCM formal, GP/MOGP formal, pipeline, series TPM, referencias |

---

## 2. Diapositivas NUEVAS: contenido

### 2.1 Alcance (después de la portada)

Título: **Alcance de esta presentación**

Texto (corto):
- Estos son **resultados preliminares** del trabajo hasta la fecha.
- El trabajo realizado: **exploración de la dependencia entre las series del EPM y del TPM**, probando distintas herramientas para analizarla.
- **No está resuelto** el problema de imputación: todavía no hay un modelo de proceso gaussiano de salida múltiple ni el kernel físico completo.
- Lo que sigue: construir el modelo (ver "Pasos siguientes").

Nota oral: "Antes de empezar quiero ser claro con el alcance. Lo que voy a mostrar es la exploración de dependencia entre las series. El problema de imputación todavía no está resuelto y al final muestro los pasos que siguen."

### 2.2 Túnel y sistemas: agregar imagen

- Insertar `tunel.jpg` (carpeta de imágenes; confirmar el nombre exacto del archivo).
- Indicar sobre la imagen o en el texto la **ubicación** de los dos monitoreos y la **distancia que los separa**: `[PENDIENTE: distancia entre el monitoreo TPM y el EPM, en metros. La debe dar el autor]`.
- No inventar la distancia.

### 2.3 Motivación práctica (modificar, no es nueva)

Dejar solo dos viñetas (quitar "Incertidumbre propagada"):
- **Alertas:** la vigilancia se define sobre umbrales de deformación y de velocidad de deformación. Un hueco en el EPM deja sin vigilar el interior del macizo, y una reconstrucción con incertidumbre permite estimar la probabilidad de superar un umbral.
- **Modelos predictivos:** los modelos de pronóstico y de alerta temprana se entrenan con ventanas de datos consecutivos, y toda ventana que toca la brecha se descarta. Aquí la brecha abarca cerca del 65 % del período EPM (681 de unos 1041 días), e imputar recupera esa información.

No mencionar calibración ni instrumentos no reemplazables (el autor lo descartó).

### 2.4 Artículo de referencia: Dalmasso et al. (2025) (reemplaza las 3 diapositivas "Estado del arte")

Eliminar las diapositivas "Estado del arte (1/3), (2/3), (3/3)" y todo lo relacionado con **Kennedy y O'Hagan** (incluida la diapositiva "Kennedy y O'Hagan como caso particular"). Pasarlas al respaldo.

Contenido de la diapositiva:
- Título: **Artículo de referencia**
- Referencia: Dalmasso, Civera, De Biagi y Chiaia (2025). *Gaussian Process Regression (GPR)-based missing data imputation and its uses for bridge structural health monitoring.* Advances in Bridge Engineering, 6:23. DOI: 10.1186/s43251-025-00169-1
- Qué hacen (parafraseado, en español): aplican GPR univariado (kernel exponencial cuadrático) a frecuencias modales de un puente ferroviario (KW51), con huecos puntuales y con brechas prolongadas.
- Hallazgo: en brechas largas la predicción tiende a la media a priori (cero) y pierde información.
- **Cita en inglés (usar exactamente este fragmento, es el único que se cita textualmente):**
  > "integrating physical models and external covariates may lead to better results"
  
  Colocarla entre comillas, con "(Dalmasso et al., 2025)". Todo lo demás en español y parafraseado. Verificar el fragmento contra el PDF del proyecto (`s43251025001691.pdf`, discusión de los casos con brecha larga) y anotar la página.
- Cierre de la diapositiva (una línea): "Esta es la motivación de la tesis: incorporar información física y variables auxiliares."

Nota oral: "Este es el artículo de referencia. Muestra que un proceso gaussiano simple, en brechas largas, vuelve a la media. Los propios autores proponen incorporar modelos físicos y variables externas, y eso es lo que propone esta tesis."

### 2.5 Machine learning frente a procesos gaussianos (NUEVA)

Fuente: documento `Imputación_de_series_temporales__estado_del_arte_y_MOGP_informado_por_Nishihara_para_el_túnel_de_Antamina.md`. **Usar solo lo que sigue y verificar cada cita antes de incluirla** (el propio documento advierte que varias referencias no están verificadas, ver sección 8).

Dos columnas.

Columna izquierda, "Arquitecturas de machine learning para imputación":
- Redes recurrentes: LSTM, GRU, GRU-D, BRITS
- Transformers: SAITS, ImputeFormer
- Modelos de difusión: CSDI, SSSD
- GAN: GAIN y variantes
- Redes de grafos: GRIN
- Redes informadas por física (PINN)

Columna derecha, "Ventajas de los procesos gaussianos":
1. **Funcionan con pocos datos.** Los modelos profundos necesitan muchas ventanas completas para entrenarse.
2. **Dan incertidumbre:** una media y una varianza en cada punto faltante, de forma nativa.
3. **Permiten incorporar la física** en la función de covarianza (el kernel).
4. Son interpretables.

Línea al pie, con honestidad: ningún método gana en todos los escenarios (Du et al., 2024, TSI-Bench), y cuando todos los sensores de un sistema fallan a la vez pocas técnicas se recuperan (Khayati et al., 2020, Mind the Gap).

Nota oral: "Hoy lo dominante en imputación son modelos profundos. Para una brecha larga con pocos datos y necesidad de incertidumbre, un proceso gaussiano tiene ventajas. No digo que gane siempre: ningún método lo hace."

No incluir la tabla completa del documento ni los conteos de familias (el documento aclara que sesgan hacia GP).

### 2.6 Qué es un proceso gaussiano (antes de la "Definición formal")

Título: **¿Qué es un proceso gaussiano?**

Texto:
- Describe una **curva desconocida**, por ejemplo la deformación del macizo en el tiempo.
- Se define con dos cosas: una **curva promedio** y un **kernel**, que dice qué tanto se parecen las lecturas de dos instantes. Si están cerca en el tiempo se parecen mucho, si están lejos casi nada.
- Permite estimar la curva donde no hay datos, **y qué tan incierta es esa estimación**.

Nota oral: "Un proceso gaussiano describe una curva que no conocemos. Se define con una curva promedio y un kernel que dice qué tanto se parecen las lecturas de dos instantes. Con eso estimo la curva donde no hay datos y también qué tan incierta es esa estimación."

### 2.7 CCM (conceptual, sin resultados)

Título: **Convergent Cross Mapping (CCM): en exploración**

Texto:
- Idea: con la historia de una serie se reconstruye la dinámica del sistema que la genera. Si esa reconstrucción permite predecir bien a la otra serie, **las dos series comparten dinámica**.
- Si la capacidad de predicción mejora al usar más datos, es evidencia de acoplamiento.
- Referencia: Sugihara et al. (2012), clave `sugihara2012`.
- **Estado: en exploración. Sin resultados validados.**

Quitar todo conteo ("53 de 56") y toda tabla de resultados de CCM. Mover la formulación formal al anexo.

### 2.8 Pasos siguientes (2 diapositivas, poco texto)

Referencias a citar, en el pie de cada diapositiva, con la clave del `.bib` que exista: Raissi et al. (2017), Álvarez et al. (2012, 2013), Hartikainen y Särkkä (2010), Liu et al. (2018). **No explicar ni usar los términos "función de Green" ni "fuerzas latentes" en el texto**, el autor no los va a defender.

**Diapositiva 1: Construir el kernel informado por la física**
1. Tratar el esfuerzo sobre el macizo, que no se mide, como una entrada desconocida modelada con un proceso gaussiano.
2. Usar el modelo de Nishihara para describir cómo responde la roca a ese esfuerzo.
3. Calcular la covarianza entre las lecturas del EPM y del TPM a partir de esa respuesta, en vez de elegirla de forma genérica.
4. Referencias: Raissi et al. (2017); Álvarez, Luengo y Lawrence (2013).

**Diapositiva 2: Estimar, imputar y validar**
1. Ajustar los parámetros del modelo con los datos anteriores a la brecha.
2. Estimar el EPM en la brecha, con su incertidumbre, usando el TPM como información auxiliar.
3. Validar con brechas artificiales de longitud conocida, midiendo error y cobertura de los intervalos.
4. Referencias: Liu, Cai y Ong (2018) (procesos gaussianos de salida múltiple asimétricos); Hartikainen y Särkkä (2010) (cálculo eficiente).

No poner fechas ni "cronograma" salvo que el autor las entregue (`[PENDIENTE: cronograma]`). Retirar de las conclusiones el título "y cronograma" si no hay tabla.

---

## 3. Diapositivas a MODIFICAR

### 3.1 Aporte propuesto
Texto corto, sin función de Green, sin fuerzas latentes, sin Kennedy y O'Hagan:

> **Propuesta:** un esquema basado en procesos gaussianos, enriquecido con el modelo de Nishihara del macizo rocoso, que usa las series del TPM como información auxiliar para imputar las series del EPM.
> - El esfuerzo no se mide: se trata como una entrada desconocida.
> - El modelo de Nishihara relaciona ese esfuerzo con la deformación que registran los dos sistemas.
> - De ahí sale la covarianza entre ambos, con parámetros con significado físico, en vez de un kernel genérico.
> - **Estado: propuesta en desarrollo.**

Colocarla después de "Artículo de referencia" y de "ML frente a procesos gaussianos".

### 3.2 Hipótesis de trabajo
Reformular la pregunta 1: no prometer dependencia "no explicada por tendencias comunes" (todo está calculado en niveles). Escribir: "¿Hay indicios de dependencia entre las series EPM y TPM?" y dejar el control por tendencias como pendiente.

### 3.3 Herramientas de dependencia
- Corregir el título: "Herramientas para el análisis de dependencia" (hoy dice "anaaisis").
- Dejar con resultados solo **Pearson** y **distance correlation**.
- **Transfer entropy y CCM: conceptuales, en exploración, sin resultados.**

### 3.4 Pearson
Reemplazar el recuadro "La idea" por:
> "Pearson responde una sola pregunta: cuando una variable está por encima de su promedio, ¿la otra también? Mide qué tan bien se parecen dos variables a una línea recta, de −1 a 1."

### 3.5 Transfer entropy (conceptual, sin resultados)
- Definición en palabras: cuánto reduce el pasado de una serie la incertidumbre sobre el futuro de la otra, más allá del propio pasado de esta. Es direccional y **no implica causalidad física**.
- Referencias: Schreiber (2000). Para la versión efectiva con fuente barajada: Marschinski y Kantz (2002), descrita en Behrendt et al. (2019), sección 2.2, ecuación 5.
- **Estado: en exploración. La prueba de significancia está pendiente.** No mostrar conteos de pares "significativos" ni figuras de TE vs rezago.
- Si en algún lugar queda una figura de TE: el eje en horas es **pasos × 6 h** (la rejilla es de 6 h, no de 30 min), de modo que τ = 3 pasos son 18 h. Cambiar "asimetría causal" por "asimetría direccional".
- Definición del rezago τ (para la nota): en el código, el valor de la serie fuente está τ pasos antes de y_t. Los rezagos empiezan en 1.

### 3.6 Síntesis de la evidencia
Reducir a Pearson y dCor, con los rangos que salgan de los resultados (en las diapositivas actuales: |r| hasta 0.99 y dCor hasta 0.7; **verificar contra los datos**). Agregar una línea: "Calculado sobre niveles; el efecto de las tendencias comunes queda por controlar." Quitar las cifras 55/56 y 53/56.

### 3.7 Estimación de hiperparámetros (simplificar)
Quitar la fórmula del gradiente y toda la notación (van al anexo). Dejar:
- Los parámetros del kernel (escala, alcance, ruido) se escogen para que el modelo explique lo mejor posible los datos observados.
- Es un problema de optimización que puede tener varios mínimos locales (limitación que se declara).
- Se hace con los datos antes de la brecha.

### 3.8 Proceso gaussiano de salida múltiple y kernels genéricos
- Dejar el MOGP como diapositiva **conceptual** (qué es, en palabras: modelar varias series juntas con una covarianza entre ellas). Estado: **propuesta, no implementado.**
- Si se conserva alguna fórmula, corregir `K_ET = K_TE^T` por `K_ET(t,t') = K_TE(t',t)^T` y dar las dimensiones de los bloques (K_TT 14x14, K_EE 4x4, K_TE 14x4).
- La diapositiva de kernels genéricos (RBF, Matérn) pasa al anexo.

### 3.9 Los datos (rediseñar y corregir cifras)
Aplicar el diseño de dos partes: tabla EPM contra TPM arriba, tres cajas abajo (tramo simultáneo, brecha, razón). Cifras verificadas con `EPM_completo.csv` y `TPM_completo.csv`:

| Dato | Valor |
|---|---|
| Registros EPM | 7 245 por sensor, sin NaN |
| Antes de la brecha | **886** lecturas; la última es 2023-06-20 01:00 (hoy el `.tex` dice 885) |
| Después de la brecha | **6 359** lecturas desde 2025-05-01 00:00 (hoy dice 6 360) |
| Brecha | 680.96 días (≈ 681) |
| Tramo con ambos sistemas | **≈ 222 días** (hoy dice 221; entre las fechas hay 223 días de calendario) |
| Razón brecha / tramo | **≈ 3.06** (hoy 3.08) |
| TPM | 10 379 registros, del 2017-12-04 al 2025-10-10 |
| Lecturas TPM en la brecha | 2 733 (intervalo [2023-06-20 00:00, 2025-05-01)); 2 732 estrictamente dentro |
| Frecuencia EPM | 6 h antes de la brecha, aproximadamente 30 min después |
| Unidad EPM | Digits (no mm) |

Nota oral (alineación): antes de la brecha el EPM se lee a las 01, 07, 13 y 19 h y el TPM a las 00, 06, 12 y 18 h: hay un desfase constante de 1 h. Después de la brecha el EPM es cada 30 min y el TPM cada 6 h. Para el análisis se trabaja sobre una rejilla de 6 h.

### 3.10 Las cuatro series EPM (cambios de nivel al reanudar)
Corregir la frase que dice que los Sensores 3 y 4 muestran un cambio de nivel. Los saltos medidos al reanudar son:

| Sensor | Salto (digits) | En desviaciones estándar previas |
|---|---|---|
| 1 | +33.5 | ≈ 27 |
| 2 | +5.7 | ≈ 2.3 |
| 3 | +1.2 | ≈ 1.3 |
| 4 | +2.2 | ≈ 5 |

Escribir "causa no confirmada". El Sensor 1 es el de mayor salto.

### 3.11 Puntos a reconstruir
Simplificar a una línea o llevar al anexo: la fila dice "6 h" y el texto de abajo habla de 3 000 puntos, es contradictorio.

### 3.12 Conclusiones
Reescribir, sin afirmaciones no sostenidas:
1. Hay **indicios de dependencia** entre el EPM y el TPM (Pearson, distance correlation, en niveles). El control por tendencias comunes está pendiente.
2. Transfer entropy y CCM están en exploración.
3. Los procesos gaussianos son un candidato por su manejo de pocos datos y de la incertidumbre.
4. Siguiente paso: construir el kernel informado por el modelo de Nishihara.

---

## 4. Modelo de Nishihara (reemplaza "sólido de Kelvin generalizado" y las 4 diapositivas matemáticas)

Título: **Modelo de Nishihara**. No usar el nombre "sólido de Kelvin generalizado".

Contenido:
- **Diagrama** de resortes y amortiguadores en serie. Buscar la imagen en la carpeta de imágenes; si no existe, dibujarla en TikZ. Elementos:
  1. **Resorte de Hooke (E0):** deformación instantánea, elástica.
  2. **Elemento de Kelvin-Voigt (resorte E1 en paralelo con amortiguador η1):** fluencia primaria, la deformación lenta de los primeros tiempos.
  3. **Elemento viscoplástico (Bingham):** fluencia secundaria; solo se activa si el esfuerzo supera un umbral.
- Etiquetar cada elemento y decir qué representa físicamente.
- **El tercer elemento probablemente no se usará:** según conversación con un experto, en este túnel no se ha observado un nivel de plasticidad, así que ese componente se toma como cero. Presentarlo como **hipótesis de trabajo**. `[PENDIENTE: nombre o cargo del experto, si el autor quiere citarlo]`.
- Opcional: la respuesta bajo esfuerzo constante σ0 de los dos primeros elementos, ε(t) = σ0/E0 + (σ0/E1)(1 − e^(−t/τ1)), con τ1 = η1/E1. Solo si el autor puede explicarla.

Nota oral: "El modelo de Nishihara tiene tres elementos en serie. Para este túnel uso los dos primeros, porque según un experto no se ha observado plasticidad, y el tercero solo actúa si el esfuerzo supera un umbral."

Mover al respaldo: "Fuerzas latentes", "Validez del kernel conjunto", "Un resultado analítico", "Kennedy y O'Hagan como caso particular" y "Alcance y supuestos" (mecanismo de faltante). `[DECISIÓN del autor: si quiere conservar el mecanismo de faltante en una línea. El anteproyecto dice MNAR y la presentación decía "ignorable", hay que reconciliarlos antes de mostrarlo.]`

---

## 5. Diapositivas a QUITAR (mover al respaldo, no borrar)

- Diseño de los experimentos, E1, E2 (las dos), E3 (las dos) y "Lo que falta". Los experimentos no están bien ordenados; se reponen cuando se corrija la prueba de transfer entropy.
- Estado del arte (1/3, 2/3, 3/3) y todo lo de Kennedy y O'Hagan.
- Fuerzas latentes, validez del kernel conjunto, resultado analítico.
- La diapositiva "Trabajos en los que se apoya" antigua, si todavía existe.

---

## 6. Anexos

Conservar o crear (ya hay texto redactado para varios): Pearson, distance correlation (construcción paso a paso y por qué da cero con independencia), transfer entropy (definición formal, k y l como tamaño de historia, τ como rezago), CCM (definición formal), definición de proceso gaussiano y posterior, gradiente de la verosimilitud, MOGP formal, kernels genéricos, pipeline completo, las 14 series TPM, referencias. Cada diapositiva del cuerpo debe tener una referencia visible "ver Anexo" cuando corresponda.

---

## 7. Qué NO afirmar (y qué decir en su lugar)

| No decir | Decir |
|---|---|
| "55 de 56 pares significativos" | "Evidencia preliminar de dependencia dirigida; prueba de significancia pendiente" |
| "τ* es el retardo físico de propagación" | Quitar. Los τ* varían entre pares sin patrón |
| "Evidencia de causalidad" | "Dependencia estadística dirigida, no causalidad física" |
| "El GP no mejora a la interpolación lineal" | Quitar (con una sola corrida, 2.42 contra 2.72, no es concluyente) |
| "No se ha reportado antes" (como hecho) | "Hasta donde alcanza la revisión, no encontré esta combinación" |

Contexto: la prueba de transfer entropy usa sustitutos barajados, que corrigen el sesgo del estimador pero con series con tendencia sobrestiman la significancia. Detalle y plan de corrección en el prompt de arreglo del cuaderno `tpm_y_ccm.ipynb` (aparte).

---

## 8. Advertencias sobre referencias

- **Verificadas:** Dalmasso et al. (2025), contra el PDF del proyecto; Raissi et al. (2017), PDF del proyecto; Behrendt et al. (2019), PDF; Theiler et al. (1992), Physica D 58, 77-94.
- **Por verificar antes de citar:** Marschinski y Kantz (2002, Eur. Phys. J. B 30, 275-281; solo se conoce por el resumen y descripciones), Álvarez et al. (2012, 2013), Hartikainen y Särkkä (2010), Wan y Ni (2019), Du et al. (2024) y Khayati et al. (2020).
- El documento de estado del arte indica que varias de sus referencias (6, 13, 14, 15, 46, 53-57, 59-61, 63, 66) se identificaron solo por título y DOI. No citar de ahí nada que el autor no pueda abrir y leer.
- La afirmación de vacío en la literatura ("no hay kernels GP derivados de Nishihara") se basa en búsquedas web dirigidas y debe confirmarse en Scopus o Web of Science.

---

## 9. Lista de verificación final

- [ ] Compila sin errores ni "overfull" graves.
- [ ] MPT cambiado a TPM en todo el documento.
- [ ] Ninguna diapositiva afirma "significativo", "causalidad" o cifras 55/56 y 53/56.
- [ ] Cada diapositiva nueva o modificada tiene `\note{}` con guion oral simple.
- [ ] Los `[PENDIENTE]` están listados en el resumen final.
- [ ] `respaldo_slides_removidos.tex` contiene todo lo retirado.
- [ ] Cifras de "Los datos" coinciden con la tabla de la sección 3.9.
