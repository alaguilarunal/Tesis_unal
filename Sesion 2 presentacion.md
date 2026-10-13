# Estructura de sección — Seminario 4
## Evidencia estadística previa a MOGP (TE + CCM + Pearson + Distance Correlation)

**Contexto para el agente local:** esto es una sección para insertar en `presentacion_seminario_4.tex`
(plantilla UFC Overleaf, Beamer, bibliografía con Biber). El documento ya tiene contexto físico,
problema MNAR y pregunta de investigación definidos en secciones anteriores; esta sección
retoma desde la motivación.

**Regla de espacio vertical (aplicar a TODAS las diapositivas de abajo):**
- Máximo 5-6 líneas de texto por frame, o un itemize de máximo 5 bullets cortos.
- Si un frame tiene título + itemize + ecuación, usar `\small` o `\footnotesize`.
- Si el contenido no cabe, dividir en dos frames con el mismo título y `\framesubtitle{1/2}`, `\framesubtitle{2/2}`.
- Nunca meter una demostración completa en una sola diapositiva: la ecuación va sola, con su
  interpretación verbal en máximo 2 líneas debajo.
- Ajustar las claves `\cite{...}` de abajo para que coincidan con las claves reales del `.bib`.

---

## ⚠️ CHECKLIST DE PREINTEGRACIÓN — leer antes de tocar el .tex

Este archivo fue generado sin ver el `.tex` ni el `.bib` reales. Antes de integrar, el agente
debe resolver estos cuatro puntos. Si alguno no se puede resolver con certeza, **preguntar al
usuario en vez de adivinar**:

1. **Buscar si ya existe una sección de evidencia estadística.** `presentacion_seminario_4.tex`
   probablemente ya tiene frames de Pearson / Distance Correlation / TE / CCM. Buscar con
   `\section{` o `\subsection{` cerca de esos términos. Si existe: **reemplazar/actualizar esa
   sección**, no crear una segunda en paralelo. Si no existe: insertarla después de la sección
   de "pregunta de investigación" y antes de la sección de MOGP.

2. **Verificar las claves de cita contra `references.bib`.** Se confirmó contra
   `anteproyecto_corregido.tex` que las claves `dalmasso2025`, `alvarez2012`, `kennedy2000`,
   `szekely2007` y `schreiber2000` existen con esa forma exacta (el anteproyecto usa
   `thebibliography`/`\bibitem`, no `references.bib`). **Falta confirmar si `references.bib`
   usa las mismas claves** — el usuario debe subir ese archivo o el agente debe abrirlo
   localmente y verificar antes de compilar.

   Tres referencias necesarias para esta sección **no existen todavía en ninguna
   bibliografía del proyecto** y hay que agregarlas completas a `references.bib`:

   ```bibtex
   @article{sugihara2012,
     author  = {Sugihara, George and May, Robert and Ye, Hao and Hsieh, Chih-hao
                and Deyle, Ethan and Fogarty, Michael and Munch, Stephan},
     title   = {Detecting Causality in Complex Ecosystems},
     journal = {Science},
     volume  = {338},
     number  = {6106},
     pages   = {496--500},
     year    = {2012},
     doi     = {10.1126/science.1227079}
   }

   @article{li2021dam,
     author  = {Li, Chunxu and Bao, Yuequan and Chen, Zhicheng and Gao, Yu
                and Shu, Jiang and Zhang, Lei},
     title   = {Multi-task {G}aussian process regression for missing sensor
                data in dam structural health monitoring},
     journal = {Measurement},
     volume  = {186},
     pages   = {110085},
     year    = {2021},
     doi     = {10.1016/j.measurement.2021.110085}
   }

   @article{zhou2022canton,
     author  = {Zhou, Ke and others},
     title   = {Probabilistic reconstruction for spatiotemporal sensor data
                integrated with Gaussian process regression},
     journal = {Measurement},
     volume  = {193},
     pages   = {110970},
     year    = {2022},
     doi     = {10.1016/j.measurement.2022.110970}
   }
   ```

   Nota: la lista completa de autores de `zhou2022canton` no se pudo verificar con
   certeza en la búsqueda previa. Confirmar autores exactos antes de usarla como cita
   formal en la tesis (no solo en la presentación).

3. **Las cifras de la Sección 6 (síntesis) ya son resultados finales, no placeholders.**
   55/56, 45/56, POT(1)-Sensor1 con skill 0.898 y Tilt(5)-Sensor2 como único par negativo
   vienen del análisis TE/CCM ya completado sobre las 56 combinaciones TPM-EPM. **No
   reemplazar estos números por otros ni inventar cifras nuevas.** Si el usuario tiene una
   corrida más reciente con números distintos, debe decírselo explícitamente al agente.

4. **El contenido de abajo está en bullets/prosa, no en código Beamer terminado.** Se incluyen
   esqueletos de `\begin{frame}` en cada sección como punto de partida, pero hay que adaptarlos
   a los comandos y estilos ya definidos en la plantilla UFC (por ejemplo, si la plantilla ya
   tiene un comando personalizado para tarjetas o cajas destacadas, usar ese en vez de
   `tcolorbox` genérico).

---

## 1. Diapositiva — Descripción del problema

Contenido (bullets, no ecuaciones):
- Túnel de la Faja, Mina Antamina (Perú): monitoreo geotécnico continuo del macizo rocoso.
- Sistema EPM: 4 sensores de deformación (mm), brecha continua MNAR de más de un año.
- Sistema TPM/MPT: 14 series (7 nodos × POT + Tilt), con datos completos durante la brecha del EPM.
- Pregunta operativa: ¿puede el TPM aportar la información necesaria para reconstruir el EPM?

---

## 2. Diapositiva — Motivación

Contenido:
- Completar el EPM no es solo "rellenar huecos": permite construir datasets continuos para
  entrenar modelos de predicción y alerta temprana de inestabilidad del macizo rocoso.
- Una brecha de más de un año en la variable de deformación deja al sistema de monitoreo ciego
  justo en la ventana temporal más relevante para detectar tendencias de fluencia (creep).
- Precedentes que resuelven problemas similares con Procesos Gaussianos:

| Referencia | Qué hace | Por qué es precedente |
|---|---|---|
| Dalmasso et al. (2025), *Advances in Bridge Engineering* | GPR para imputar brechas MNAR/MAR en monitoreo de un puente; identifica el caso de brecha larga (Case 2.b) como el más difícil, y señala MOGP con covariable auxiliar como trabajo futuro | Es el antecedente directo del problema (brecha MNAR larga) y el hueco que la tesis llena |
| Li, Bao, Chen, Gao, Shu, Zhang (2021), *Measurement* | MOGP para reconstruir segmentos faltantes en deformación de dos presas de hormigón | Aplicación de MOGP a estructura geotécnica análoga (presa ≈ túnel), con ganancias cuando faltan datos al inicio/final del registro |
| Zhou et al. (2022), *Measurement* | Reconstrucción probabilística de datos faltantes en acelerómetros (Torre Cantón) integrando correlación espacio-temporal entre sensores con GPR | Valida el uso de sensores auxiliares correlacionados para reconstruir el sensor objetivo |

```latex
% Claves verificadas contra tu anteproyecto (anteproyecto_corregido.tex).
% PENDIENTE: confirmar que references.bib usa las MISMAS claves (puede diferir).
\cite{dalmasso2025}
\cite{li2021dam}       % NO EXISTE aún en tu bibliografía — ver entrada BibTeX abajo
\cite{zhou2022canton}  % NO EXISTE aún en tu bibliografía — ver entrada BibTeX abajo
```

---

## 3. Diapositiva — Hipótesis (una sola diapositiva, texto grande y centrado)

Texto sugerido:

> ¿Existe información geotécnica embebida en las series del sistema TPM que permita
> reconstruir, con cuantificación de incertidumbre, la dinámica de deformación del
> sistema EPM durante su brecha de monitoreo?

Nota para el agente: usar un frame simple, sin itemize, texto centrado, quizás en un
`tcolorbox` (paquete ya cargado en la plantilla) para destacarlo visualmente.

Esqueleto de referencia (adaptar colores/estilo a la plantilla UFC si ya tiene uno definido):

```latex
\begin{frame}{Hipótesis de trabajo}
\centering
\begin{tcolorbox}[colback=blue!5, colframe=blue!40, width=0.9\textwidth]
\large
¿Existe información geotécnica embebida en las series del sistema TPM que permita
reconstruir, con cuantificación de incertidumbre, la dinámica de deformación del
sistema EPM durante su brecha de monitoreo?
\end{tcolorbox}
\end{frame}
```

---

## 4. Diapositiva — Los cuatro pilares de evidencia estadística

Formato sugerido: 4 tarjetas (2x2) usando `tcolorbox` o `minipage`, cada una con nombre + 1-2 líneas.

| Pilar | Qué mide | Por qué se usa aquí |
|---|---|---|
| **Correlación de Pearson** | Dependencia lineal entre dos variables | Primer filtro, línea base de comparación |
| **Distance Correlation (dCor)** | Dependencia estadística general (vale 0 si y solo si son independientes) | Detecta dependencia no lineal que Pearson no ve; relevante porque el comportamiento del macizo es elastoplástico |
| **Transfer Entropy (TE)** | Transferencia dirigida de información entre series temporales | Establece direccionalidad estadística (¿TPM→EPM?), más allá de correlación simétrica |
| **Convergent Cross Mapping (CCM)** | Si dos series pertenecen al mismo sistema dinámico acoplado | Evidencia de que TPM y EPM comparten la dinámica del macizo, habilitando el MOGP |

```latex
% Nota: Distance Correlation NO es "más probabilística" que Pearson.
% Es una medida basada en distancias (no en momentos) que detecta
% cualquier tipo de dependencia, lineal o no lineal.
```

Esqueleto de referencia (grid 2x2 con `tcolorbox`; ajustar a estilo de la plantilla si aplica):

```latex
\begin{frame}{Cuatro pilares de evidencia estadística}
\begin{columns}[t]
\begin{column}{0.48\textwidth}
\begin{tcolorbox}[title=Pearson, colback=gray!5]
\footnotesize Dependencia \textbf{lineal}. Primer filtro y línea base de comparación.
\end{tcolorbox}
\vspace{0.3cm}
\begin{tcolorbox}[title=Distance Correlation, colback=gray!5]
\footnotesize Dependencia estadística general (vale 0 sii independencia). Detecta no
linealidad que Pearson no ve.
\end{tcolorbox}
\end{column}
\begin{column}{0.48\textwidth}
\begin{tcolorbox}[title=Transfer Entropy, colback=gray!5]
\footnotesize Transferencia \textbf{dirigida} de información. Establece direccionalidad
TPM$\to$EPM.
\end{tcolorbox}
\vspace{0.3cm}
\begin{tcolorbox}[title=CCM, colback=gray!5]
\footnotesize ¿Pertenecen al mismo sistema dinámico? Evidencia de dinámica compartida
del macizo.
\end{tcolorbox}
\end{column}
\end{columns}
\end{frame}
```

---

## 5. Diapositivas — Ecuaciones (una por pilar, o agrupadas si el espacio lo permite)

### 5.1 Pearson

```latex
\begin{equation}
\rho_{XY} = \frac{\mathrm{Cov}(X,Y)}{\sigma_X \sigma_Y}
= \frac{\sum_{i=1}^{n}(x_i - \bar{x})(y_i - \bar{y})}
       {\sqrt{\sum_{i=1}^{n}(x_i-\bar{x})^2}\sqrt{\sum_{i=1}^{n}(y_i-\bar{y})^2}}
\label{eq:pearson}
\end{equation}
```

Interpretación verbal (máximo 2 líneas en el frame): $\rho_{XY}\in[-1,1]$ mide qué tan bien
una relación lineal describe la co-variación entre $X$ y $Y$.

### 5.2 Distance Correlation

```latex
\begin{equation}
A_{jk} = a_{jk} - \bar{a}_{j\cdot} - \bar{a}_{\cdot k} + \bar{a}_{\cdot\cdot}, \qquad
B_{jk} = b_{jk} - \bar{b}_{j\cdot} - \bar{b}_{\cdot k} + \bar{b}_{\cdot\cdot}
\label{eq:dcor-centering}
\end{equation}

\begin{equation}
\mathrm{dCov}^2(X,Y) = \frac{1}{n^2}\sum_{j,k} A_{jk}B_{jk}
\label{eq:dcov}
\end{equation}

\begin{equation}
\mathrm{dCor}(X,Y) = \frac{\mathrm{dCov}(X,Y)}{\sqrt{\mathrm{dVar}(X)\,\mathrm{dVar}(Y)}}
\label{eq:dcor}
\end{equation}
```

donde $a_{jk}=\|x_j-x_k\|$, $b_{jk}=\|y_j-y_k\|$ son distancias euclidianas por pares, y
$\bar a_{j\cdot}, \bar a_{\cdot k}, \bar a_{\cdot\cdot}$ son promedios de fila, columna y total
(doble centrado). $\mathrm{dVar}(X) = \mathrm{dCov}(X,X)$.

Interpretación verbal: $\mathrm{dCor}(X,Y)=0$ si y solo si $X$ y $Y$ son estadísticamente
independientes, sin importar la forma de la relación (Székely, Rizzo & Bakirov, 2007).

### 5.3 Transfer Entropy

```latex
\begin{equation}
T_{X\to Y} = H\!\left(Y_{t+1} \mid Y_t^{(k)}\right) - H\!\left(Y_{t+1}\mid Y_t^{(k)}, X_t^{(l)}\right)
\label{eq:te}
\end{equation}
```

donde $H(\cdot\mid\cdot)$ es la entropía condicional de Shannon y
$Y_t^{(k)}=(Y_t,Y_{t-1},\dots,Y_{t-k+1})$ es el pasado de orden $k$ de $Y$.

Interpretación verbal: $T_{X\to Y}>0$ indica que el pasado de $X$ reduce la incertidumbre
sobre el futuro de $Y$ más allá de lo que ya predice el propio pasado de $Y$ (Schreiber, 2000).

### 5.4 Convergent Cross Mapping

```latex
\begin{equation}
M_X(t) = \big(x(t),\, x(t-\tau),\, x(t-2\tau),\, \dots,\, x(t-(E-1)\tau)\big)
\label{eq:ccm-embedding}
\end{equation}

\begin{equation}
\widehat{Y}(t)\mid M_X = \sum_{i=1}^{E+1} w_i\, Y(t_i), \qquad
w_i = \frac{u_i}{\sum_{j=1}^{E+1} u_j}, \qquad
u_i = \exp\!\left(-\frac{d\big(M_X(t), M_X(t_i)\big)}{d\big(M_X(t), M_X(t_1)\big)}\right)
\label{eq:ccm-crossmap}
\end{equation}

\begin{equation}
\rho = \mathrm{corr}\Big(Y(t),\, \widehat{Y}(t)\mid M_X\Big)
\label{eq:ccm-skill}
\end{equation}
```

donde $M_X(t)$ es el manifold reconstruido (embedding de Takens) de $X$ con dimensión $E$ y
retardo $\tau$, y $t_1,\dots,t_{E+1}$ son los $E+1$ vecinos más cercanos de $M_X(t)$.

Interpretación verbal: si $X$ causa/fuerza a $Y$ dentro del mismo sistema dinámico, $\rho$
(el "skill" de cross-mapping) aumenta y converge conforme crece la longitud de la librería $L$
(Sugihara et al., 2012).

```latex
% Citas sugeridas para esta sección de ecuaciones
% Pearson: normalmente no se cita formalmente, se puede omitir el \cite.
\cite{szekely2007}      % Distance Correlation — verificada contra el anteproyecto
\cite{schreiber2000}    % Transfer Entropy — verificada contra el anteproyecto
\cite{sugihara2012}     % CCM — NO EXISTE en tu bibliografía actual, ver entrada BibTeX abajo
```

---

## 6. Diapositiva — Síntesis de los 4 pilares (AGREGAR — no estaba en el orden original)

Sugerencia: una tabla o gráfico de barras resumen antes de pasar a MOGP, para que el salto
argumentativo no sea abrupto.

Contenido sugerido (ajustar cifras a los resultados finales):
- 55/56 pares MPT→EPM estadísticamente significativos (TE, test de permutación).
- 45/56 pares EPM→MPT significativos (evidencia de bidireccionalidad → forzamiento común del macizo).
- CCM: solo Tilt(5)-Sensor2 con skill negativo en dirección TPM→EPM.
- Mejor par para el primer experimento MOGP: POT(1)-Sensor1 (CCM skill = 0.898).
- Conclusión de la diapositiva: los 4 pilares convergen en la misma señal → dinámica compartida
  entre TPM y EPM → justifica tratar TPM como fuente auxiliar en un MOGP.

Esqueleto de referencia (usa `booktabs`, ya cargado en la plantilla):

```latex
\begin{frame}{Síntesis: los 4 pilares convergen}
\small
\begin{table}
\begin{tabular}{@{}lc@{}}
\toprule
Resultado & Valor \\
\midrule
Pares TPM$\to$EPM significativos (TE) & 55/56 \\
Pares EPM$\to$TPM significativos (TE) & 45/56 \\
Pares con CCM skill negativo (TPM$\to$EPM) & 1/56 (Tilt(5)-Sensor2) \\
Mejor par para primer experimento MOGP & POT(1)-Sensor1 ($\rho=0.898$) \\
\bottomrule
\end{tabular}
\end{table}
\vspace{0.2cm}
\centering \footnotesize Los 4 pilares apuntan en la misma dirección: TPM y EPM comparten
la dinámica del macizo rocoso.
\end{frame}
```

---

## 7. Diapositiva(s) — Procesos Gaussianos de Salida Múltiple (MOGP)

Contenido (mantener breve, esto ya debería tener su propia sección más extensa después):
- Extensión del GP univariado a salidas múltiples correlacionadas.
- Formulación asimétrica / multi-fidelidad: TPM como fuente completa, EPM como fuente objetivo incompleta.
- Referenciar marco teórico:

```latex
% Claves verificadas contra tu anteproyecto (anteproyecto_corregido.tex)
\cite{alvarez2012}     % Álvarez, Rosasco & Lawrence (2012)
\cite{kennedy2000}     % Kennedy & O'Hagan (2000)
```

---

## 8. Diapositiva(s) — Resultados actuales

Incluir (ya calculado según tu proyecto):
- Resultado del ablation study: GP univariado con kernel genérico (RBF) sobre un hueco
  artificial de 60 puntos en EPM Sensor 1 no supera a interpolación lineal
  (RMSE ~0.26–0.47 mm) → evidencia de que se necesita información auxiliar (TPM).
- Esto cierra el argumento: pilares estadísticos → TPM comparte dinámica con EPM →
  GP univariado no basta → siguiente paso es MOGP con TPM como auxiliar.

---

## Nota final para el agente local

El orden completo queda:

1. Descripción del problema
2. Motivación (+ 3 papers precedentes)
3. Hipótesis (1 diapositiva)
4. Cuatro pilares (tarjetas)
5. Ecuaciones (una por pilar)
6. **Síntesis de los 4 pilares** (agregada — ver sección 6 arriba)
7. MOGP (marco teórico, breve)
8. Resultados actuales (incluye ablation study)

Si el tiempo total de la sección es limitado, los pasos 6 y 8 son los que menos se pueden
recortar: son los que cierran el argumento ante el jurado.
