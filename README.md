# Contexto del proyecto — Tesis de Maestría en Ciencias Matemáticas Aplicadas

## Propósito de este documento

Este archivo es el documento de contexto para cualquier agente (Claude Code u otro) que vaya a trabajar sobre el código de este repositorio. No es un README de instalación — es la explicación completa del problema científico, el marco matemático propuesto, el estado actual del desarrollo, y la hoja de ruta pendiente. Léelo completo antes de tocar cualquier celda del notebook o escribir código nuevo. El objetivo es que cualquier sugerencia de código respete la formulación matemática exacta que se describe aquí, no una simplificación genérica de "imputación de series de tiempo".

---

## 1. Quién soy y en qué consiste el proyecto

Soy Alejandro Enrique Aguilar Sánchez, ingeniero electrónico, actualmente cursando una maestría en Ciencias Matemáticas Aplicadas en la Universidad Nacional de Colombia (UNAL). Trabajo como científico de datos en una firma de ingeniería que hace monitoreo geotécnico, lo que me da acceso directo a los datos y al contexto operativo del problema de mi tesis.

**Directores de tesis:**
- Director: Arles Ernesto Rodríguez Portela (ingeniero de sistemas, experiencia en sistemas inteligentes y análisis de datos).
- Co-director: Juan Carlos Galvis Arrieta (Profesor Asociado, especialista en análisis numérico de EDPs y métodos multiescala).

**Contexto importante:** los jurados y revisores de esta tesis son doctores en matemáticas. Toda la formulación debe sostenerse con rigor matemático completo, no solo intuición de ingeniería. Cualquier código que se escriba debe poder justificarse matemáticamente paso a paso si un jurado lo pregunta.

---

## 2. El problema físico: el Túnel de la Faja, Mina Antamina, Perú

El túnel de la faja transporta mineral mediante una cinta transportadora, excavado en macizo rocoso. Es monitoreado continuamente por dos sistemas de instrumentación independientes:

### Sistema EPM (Extensómetros de Posición Múltiple)
- 4 sensores instalados en una misma sección transversal del túnel.
- Cada sensor mide deformación relativa del macizo rocoso, en milímetros.
- Frecuencia de muestreo original de 30 minutos (los datasets de trabajo están reprocesados a 6 horas).
- **Problema central:** dentro de una ventana de ~2 años, existe una brecha continua de más de un año sin datos, simultánea en las 4 series. Este tipo de dato faltante se clasifica como **MNAR (Missing Not At Random)** — no es dispersión aleatoria de puntos, es un tramo continuo y prolongado.

### Sistema TPM (Tunnel Profile Monitoring)
- 7 nodos distribuidos a lo largo del perfil transversal del túnel.
- Cada nodo mide dos variables: un potenciómetro de cuerda **POT(i)**, que mide desplazamiento, y un inclinómetro MEMS **Tilt(i)**, que mide inclinación. Total: 14 series de tiempo.
- **Crítico:** el TPM operó de forma continua durante todo el período en que el EPM tiene la brecha. Es la fuente auxiliar completa.

Ambos sistemas monitorean el mismo macizo rocoso, físicamente cercanos dentro del túnel. La hipótesis de la tesis es que existe una correlación física real entre ambos, no solo estadística — ambos observan la misma dinámica geotécnica subyacente desde ángulos distintos.

### El desfase estructural entre sistemas
Existe un desfase de 1 hora entre las rejillas de muestreo de EPM y TPM, que produce tres desfases temporales distintos (5h, 11h, 17h) según el bloque temporal. La recomendación de trabajo es **no forzar sincronización artificial** — usar los timestamps crudos directamente, porque el marco MOGP maneja de forma nativa datos heterotópicos (series que no comparten exactamente los mismos instantes de observación).

---

## 3. Objetivo central de la tesis

Reconstruir las cuatro series faltantes del EPM durante la brecha MNAR de más de un año, usando las catorce series del TPM como fuente auxiliar. La reconstrucción **no debe ser interpolación ciega**: debe ser una transferencia de conocimiento geotécnico — el modelo tiene que abstraer la dinámica del macizo rocoso desde las observaciones del TPM y proyectarla hacia el EPM, preservando las propiedades dinámicas reales del sistema físico y cuantificando la incertidumbre de forma probabilística.

---

## 4. Marco matemático: los cinco pilares

### Pilar 1 — Procesos Gaussianos (GP) para imputación univariada
Un GP es un modelo probabilístico sobre funciones: en vez de ajustar parámetros de una forma funcional fija, se coloca una distribución de probabilidad directamente sobre el espacio de funciones posibles, definida por una función media $m(t)$ (usualmente cero) y una función de covarianza (kernel) $k(t,t')$. La literatura (Rasmussen & Williams 2006; Dalmasso et al. 2025) confirma que es una herramienta válida y competitiva para imputar brechas prolongadas en series de monitoreo estructural y geotécnico, aunque con limitaciones serias cuando el hueco es muy largo (ver sección 7).

### Pilar 2 — Procesos Gaussianos de Salida Múltiple (MOGP)
Extensión del GP univariado para modelar conjuntamente múltiples series correlacionadas. Aquí se modelan simultáneamente las 14 series del TPM y las 4 del EPM (18 salidas totales), capturando la covarianza cruzada entre ambos sistemas mediante una función $K_{TE}(t,t')$ — **esta función es la contribución matemática central de la tesis**. El problema se formula como un **MOGP asimétrico** (multi-fidelidad): el EPM es la salida objetivo de alta importancia con datos incompletos, y el TPM es la fuente auxiliar completa.

### Pilar 3 — Kernels informados por física
En vez de un kernel genérico (RBF, Matérn), la covarianza se deriva directamente del modelo constitutivo del macizo rocoso. La idea formal (Raissi, Perdikaris & Karniadakis 2017): si $u \sim \mathcal{GP}(0, k)$ y $\mathcal{L}u = f$, donde $\mathcal{L}$ es un operador diferencial lineal que describe la física del sistema, entonces $f \sim \mathcal{GP}(0, \mathcal{L}\mathcal{L}^* k)$. Aplicar el operador del modelo de Nishihara a esta receta produce un kernel físicamente consistente para las correlaciones entre deformaciones. Los Modelos de Fuerzas Latentes de Álvarez, Luengo y Lawrence (2009/2013) son el precedente directo: construyen kernels MOGP a partir de ecuaciones diferenciales masa-resorte-amortiguador, análogas mecánicamente al Kelvin-Voigt de Nishihara.

### Pilar 4 — Modelo constitutivo de Nishihara
Modelo estándar para el comportamiento viscoelástico-viscoplástico del macizo rocoso bajo fluencia (creep). Conecta en serie tres elementos mecánicos:
1. Un resorte elástico instantáneo (rigidez $E_0$).
2. Un elemento de Kelvin-Voigt para fluencia primaria (rigidez $E_1$, viscosidad $\eta_1$, en paralelo).
3. Un amortiguador viscoplástico de Bingham (viscosidad $\eta_2$), activo solo cuando el esfuerzo supera un umbral $\sigma_s$.

**Decisión de alcance importante:** la tesis trabaja **exclusivamente con las Fases I y II** (resorte + Kelvin-Voigt), porque el macizo rocoso de Antamina no alcanza plastificación bajo condiciones normales de operación. Esto mantiene las ecuaciones lineales y analíticamente tratables. La Fase III (Bingham) queda excluida del alcance. El tiempo de retardo $\tau = \eta_1/E_1$ es el parámetro de longitud de escala del kernel, con interpretación física directa.

### Pilar 5 — Estructura multi-fidelidad de Kennedy-O'Hagan
El marco de Kennedy y O'Hagan (2000) es la justificación matemática más sólida para usar el TPM como fuente auxiliar de un sistema distinto pero correlacionado: TPM cumple el rol de fuente completa, EPM el de fuente objetivo incompleta, y la discrepancia entre ambos se modela como un GP adicional aprendido desde los datos ($Z_2 = \rho Z_1 + \delta$).

---

## 5. La novedad exacta de la tesis

No existe ningún trabajo publicado que derive analíticamente la función de covarianza cruzada del modelo de Nishihara y la use dentro de un MOGP asimétrico para imputar una brecha MNAR de largo plazo entre dos sistemas de monitoreo heterogéneos del mismo macizo rocoso. La contribución específica es derivar el bloque cruzado $K_{TE}(t,t')$ a partir de la función de Green de Nishihara, convirtiendo la estructura de su operador diferencial en una función de covarianza válida para inferencia probabilística — distinto de trabajos previos (Hu et al. 2022, Zhao et al. 2023) que usan Nishihara como predictor determinístico hacia adelante, no como prior probabilístico.

**Punto de derivación clave:** el objeto que entra en la integral de convolución es la función de Green $G(t,s)$ (respuesta al impulso), no la solución general de creep $\varepsilon(t)$. La función de Green de Nishihara (Fases I-II) es un decaimiento exponencial parametrizado por $E_1/\eta_1$. $E_0$, $E_1$, $\eta_1$ se aprenden como hiperparámetros desde los datos de monitoreo, no se miden en laboratorio.

---

## 6. Estructura tentativa de la tesis (8 capítulos)

1. Introducción y contexto — problema geotécnico, motivación, objetivos, hipótesis.
2. Marco teórico: Procesos Gaussianos univariados — gaussianas multivariadas, definición formal de GP, kernels, inferencia bayesiana, posterior, verosimilitud marginal, optimización de hiperparámetros.
3. Procesos Gaussianos de Salida Múltiple — kernel matricial $K_M$, covarianzas cruzadas, datos heterotópicos, LMC y variantes, MOGP asimétrico, Kennedy-O'Hagan.
4. El modelo constitutivo de Nishihara — mecánica, ecuaciones, interpretación física, solución analítica bajo carga constante, calibración desde datos de monitoreo.
5. Derivación del kernel informado por física — formulación EDE, solución vía espacio de estados, extracción de la covarianza, derivación de $K_{TE}$.
6. Análisis estadístico y de correlación — exploratorio EPM/TPM, correlación empírica, justificación estadística.
7. **Imputación de la brecha EPM** — formulación MOGP asimétrico + kernel Nishihara, entrenamiento, reconstrucción, cuantificación de incertidumbre, validación. **Este es el capítulo donde vive el código de este repositorio.**
8. Conclusiones y trabajo futuro.

---

## 7. Estado actual del trabajo (lo que ya está hecho)

### 7.1 Limpieza de datos — completada
Dos datasets limpios y verificados:
- `EPMDATA_INTERPOLATED_v2.csv` — 885 filas, ~221 días, muestreo cada 6 horas. Columnas: `date`, `Sensor 1 (5m)`, `Sensor 2 (10m)`, `Sensor 3 (5m)`, `Sensor 4 (10m)`.
- `TPMDATA_CLEANED.csv` — 884 filas, mismo período. Columnas: `date`, `POT(1..7)`, `Tilt(1..7)`, `freq`.

Problemas ya corregidos: NaNs dispersos y 4 timestamps faltantes en EPM (huecos de 12h); errores de separador decimal en columnas POT que inflaban valores ×1000, más 3 timestamps faltantes en TPM. Todas las interpolaciones fueron verificadas manualmente; un error intermedio (NaN de frontera resuelto con forward-fill en vez de interpolación real) fue detectado y corregido.

**Nota sobre EPM Sensor 1:** tiene solo ~15 valores únicos en 885 lecturas — verificado con herramientas de línea de comandos, saltando pandas. Esto es consistente con el límite de resolución mecánica del instrumento extensométrico, no es corrupción de datos. Esta cuantización afecta los supuestos de modelado GP y debe tenerse en cuenta al interpretar hiperparámetros de longitud de escala para este sensor específico.

### 7.2 Validación de causalidad — completada
- **Transfer Entropy (TE):** 55/56 pares TPM→EPM y 45/56 pares EPM→TPM estadísticamente significativos (p<0.05, test de permutación con 199 surrogates, umbral: el valor TE observado debe estar *por encima* del percentil 95 de la distribución nula, no simplemente fuera de rango). Los sensores POT muestran fuerte asimetría TPM→EPM; los Tilt muestran acoplamiento más bidireccional. **EPM Sensor 1 (5m) mostró la mayor habilidad de cross-mapping a pesar de tener pobre auto-predictibilidad** — este es el argumento empírico más fuerte a favor de MOGP sobre GP univariado.
- **CCM (Convergent Cross Mapping):** optimización de dimensión de embebido completada para las 18 series; CCM corrido para los 56 pares TPM-EPM. La alta habilidad bidireccional en la mayoría de los pares es consistente con la interpretación de **variable latente compartida (forzamiento común)** — esta es la lectura correcta para la defensa de tesis, no causalidad estricta unidireccional.
- Tres pares mostraron CCM skill negativo (Tilt(5)-Sensor2, POT(2)-Sensor3, POT(4)-Sensor2) — candidatos a exclusión del conjunto auxiliar MOGP, pendiente de confirmar.

### 7.3 Primer experimento de GP — completado (ver `libro_1.ipynb`)
El notebook actual contiene el **primer peldaño del ablation study**: un GP univariado (kernel RBF genérico) sobre EPM Sensor 2 (10m), con una ventana de 400 puntos artificialmente enmascarada (gap_start=200, gap_len=400) simulando una brecha. Detalles de implementación:
- Normalización estándar de la serie (media/desviación) antes de entrenar.
- `GPy.kern.RBF(input_dim=1, variance=1.0, lengthscale=10.0)` + `GPy.models.GPRegression`, optimizado por máxima verosimilitud marginal.
- Evaluación: RMSE, MAE en escala original (mm), y cobertura del intervalo de confianza al 95%.

**Resultado esperado y su interpretación correcta:** en un experimento previo con Sensor 1, el RMSE del GP prácticamente igualó al de interpolación lineal simple, con un lengthscale óptimo de ~360 horas. **Esto no es un fracaso del experimento — es evidencia deliberada de ablación**: demuestra que un GP univariado con kernel genérico no logra superar la interpolación simple durante transiciones de nivel, lo cual justifica empíricamente la necesidad de traer al TPM como fuente auxiliar. Cualquier código nuevo que trabaje sobre este notebook debe preservar esta interpretación — no se está buscando "mejorar" este resultado con trucos de tuning; se está usando como línea base documentada del Capítulo 7.

### 7.4 Estructura del ablation study (Capítulo 7)
1. GP univariado, kernel genérico — completado (sección 7.3 arriba).
2. MOGP con kernel genérico (ICM — Bonilla, Chai & Williams 2007) — **siguiente paso, aún no implementado en código**.
3. MOGP con kernel de Nishihara (físicamente informado) — pendiente, es la contribución original.

---

## 8. Lo que sigue (pendiente de implementar)

1. **MOGP con kernel genérico (ICM).** En GPy: `GPy.util.multioutput.ICM(input_dim=1, num_outputs=18, kernel=GPy.kern.RBF(1))`. El kernel tiene la forma $K_{\text{ICM}}((t,d),(t',d')) = B_{d,d'} \cdot k(t,t')$, donde $B$ es la matriz de corregionalización de 18×18 (aprendida) que codifica qué tan correlacionada está cada par de series entre sí, independiente del tiempo, y $k(t,t')$ captura la correlación temporal de cada serie consigo misma. **Recomendación de implementación:** empezar con el caso más simple — 1 serie TPM + 1 serie EPM (2 salidas) — usando el par con mejor cross-mapping skill de CCM antes de escalar a las 18 series completas.
2. **Derivación e implementación del kernel de Nishihara** subclasificando `GPy.kern.Kern`.
3. Completar el ablation study y generar resultados del Capítulo 7.
4. Tareas pendientes de CCM: tests de surrogates para significancia estadística, curvas de convergencia para los pares top, exclusionRadius justificado desde análisis de autocorrelación, optimización de $\tau$, validación operacional leave-one-sensor-out.
5. Posible reformulación en espacio de estados de la inferencia GP con el kernel de Nishihara, para reducir el costo computacional de $O(N^3)$ a $O(N)$.
6. Pregunta abierta: qué series TPM con $E$ óptimo alto y baja auto-predictibilidad deberían excluirse del conjunto auxiliar MOGP (a confirmar contra los resultados cruzados de CCM).

---

## 9. Principios y aprendizajes clave (para no repetir errores conceptuales)

- **La heterogeneidad EPM-TPM es real y debe abordarse explícitamente en la defensa:** TPM y EPM miden cantidades físicamente distintas — a diferencia de la multi-fidelidad homogénea clásica de Kennedy-O'Hagan (donde ambos niveles miden la misma variable a distinta resolución).
- La etiqueta "autoregresivo" de Kennedy-O'Hagan se refiere a niveles de fidelidad, no a tiempo — es distinta de formulaciones verdaderamente recursivas como el filtro de Kalman.
- Dalmasso et al. (2025), Caso 2.b (brecha MNAR larga en zona variable) muestra al GP colapsando hacia media cero — el paper identifica explícitamente el MOGP con covariables auxiliares como trabajo futuro, lo cual posiciona directamente la contribución de esta tesis.
- El entrenamiento de un MOGP no es como entrenar una red neuronal: la predicción es una operación algebraica cerrada; el entrenamiento es ascenso de gradiente sobre la verosimilitud marginal logarítmica respecto a los hiperparámetros del kernel (las constantes físicas de Nishihara). No se requiere iteración para la predicción en sí.
- En el test de surrogates de TE, el valor observado debe estar *por encima* (no simplemente fuera) del percentil 95 de la distribución nula para confirmar significancia.
- La alta habilidad bidireccional de CCM es consistente con variable latente compartida, no necesariamente causalidad estricta unidireccional — este es el framing correcto para la defensa.

---

## 10. Librería y decisiones de herramientas

- **GPy fue elegido sobre GPflow** por: soporte nativo de modelos multi-fidelidad Kennedy-O'Hagan vía Emukit, linaje directo con el módulo ICM/LCM de Álvarez et al., y la posibilidad de subclasificar `GPy.kern.Kern` para el kernel custom de Nishihara.
- Entorno de cómputo: Google Colab y VS Code (notebooks Jupyter); Python con `pandas`, `numpy`, `GPy`, `pyEDM`, `dcor`.
- Entorno de documento: Overleaf (LaTeX); paquetes `booktabs`, `longtable`, `multirow`, `enumitem`, `tcolorbox`, `titlesec`, `pdflscape`.

---

## 11. Bibliografía — pilares y artículos de trabajo

### Núcleo innegociable (10 artículos — deben poder defenderse ante el jurado sin titubeos)

| # | Referencia | Qué sostiene en la tesis |
|---|---|---|
| 1 | Rasmussen & Williams (2006), *Gaussian Processes for Machine Learning* | Deducción completa de la posterior GP (Capítulo 2) |
| 2 | Álvarez, Rosasco & Lawrence (2012), *Kernels for Vector-Valued Functions* | Por qué la matriz de bloques $K(t,t')$ es semidefinida positiva |
| 3 | Kennedy & O'Hagan (2000) | Marco multi-fidelidad; por qué TPM es fuente completa y EPM objetivo incompleto |
| 4 | Raissi, Perdikaris & Karniadakis (2017) | La receta $\mathcal{L}u=f \Rightarrow f\sim\mathcal{GP}(0,\mathcal{LL}^*k)$, aplicada a Nishihara |
| 5 | Álvarez, Luengo & Lawrence (2009/2013), Latent Force Models | Ejemplo masa-resorte-amortiguador, análogo directo de Kelvin-Voigt |
| 6 | Bonilla, Chai & Williams (2007), ICM | Autokrigeabilidad — cuándo TPM realmente aporta información al EPM |
| 7 | Dalmasso et al. (2025), *GPR-based missing data imputation* (bridge SHM) | Caso 2.b de colapso del GP univariado en brechas largas — ya replicado con datos reales propios |
| 8 | Hu et al. (2022) / Zhao et al. (2023) | Ecuación constitutiva completa de Nishihara con calibración desde monitoreo |
| 9 | Le Gratiet & Garnier (2014), *Recursive co-kriging* | Implementación práctica de Kennedy-O'Hagan sin explosión de costo computacional |
| 10 | Liu, Cai & Ong (2018), *Remarks on multi-output GP regression* | Mapa MOGP simétrico vs. asimétrico — justificación de la elección |

### Segundo círculo (contexto de apoyo, 8 artículos)

11. Boyle & Frean (2005) — procesos de convolución, alternativa al ICM.
12. Perdikaris et al. (2017), NARGP — qué hacer si la relación TPM→EPM no es lineal.
13. Titsias (2009), puntos inductores — escalamiento a miles de datos.
14. Hartikainen & Särkkä (2010) — formulación Kalman / espacio de estados.
15. Särkkä & Solin (2019), *Applied Stochastic Differential Equations* — receta formal EDE→GP para el Capítulo 5.
16. Avendaño-Valencia et al. (2021) — precedente de "sensor virtual" en otra industria.
17. Swiler et al. (2020) — panorama de GPs restringidos por física.
18. Li et al. (2021), MOGP en presas — precedente geotécnico más cercano al caso de estudio.

### Bibliografía adicional confirmada
Claves de citación disponibles en Overleaf: `schreiber2000`, `vicente2011`, `theiler1992` (TE/CCM). Referencias core adicionales ya integradas en el mapa de literatura: Dai-Álvarez-Lawrence (2017), Liu-Cai-Ong (2018).

---

## 12. Convención de trabajo para el agente

- Nunca inventes variables, funciones o nombres de columnas que no existan en el código ya escrito o en los CSV descritos arriba. Si necesitas una variable nueva, defínela explícitamente en una celda nueva, nunca la asumas.
- Cuando el resultado de un experimento parezca "malo" (por ejemplo, RMSE alto, GP colapsando a media), no lo trates como un bug a arreglar sin preguntar primero — puede ser evidencia deliberada de ablación, como ocurrió con el Sensor 1. Confirma la interpretación antes de "arreglar" resultados.
- Todo el código de imputación final debe trabajar sobre los timestamps crudos de cada sistema (EPM y TPM), no forzar una sincronización artificial entre las dos rejillas temporales.
- El alcance matemático de Nishihara en este proyecto se limita a las Fases I y II (lineal). No introduzcas el término de Bingham (Fase III) salvo que se indique explícitamente lo contrario.

#DATA
La encuentras en la ruta data