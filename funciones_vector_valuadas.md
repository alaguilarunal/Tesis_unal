# Funciones Vector-Valuadas — Extensión a Procesos Gaussianos Multisalida (MOGP)

## Propósito de este documento

Este archivo es contexto para el agente de Claude Code que trabaja sobre `libro_1.ipynb`. Explica qué extensión matemática se va a implementar, por qué, y cómo conecta con lo que ya existe en el notebook. Léelo completo antes de escribir código nuevo — el objetivo no es "hacer un GP multisalida genérico", sino implementar exactamente el Paso 2 del estudio de ablación de la tesis, con la formulación que se describe aquí.

---

## 1. De dónde venimos: qué ya existe en el notebook

`libro_1.ipynb` ya contiene el **Paso 1 del ablation study**: un GP univariado (una sola serie a la vez, kernel RBF y también Matérn52 probado) sobre EPM Sensor 4, con una ventana artificialmente enmascarada (`gap_start=200`, `gap_len=100`) simulando la brecha real. El resultado documentado de este paso: el RMSE del GP prácticamente iguala al de interpolación lineal — evidencia deliberada de que un GP univariado con kernel genérico no logra superar la interpolación simple, lo cual motiva el siguiente paso.

**No se modifica el Paso 1 existente.** La nueva sección se agrega como celdas nuevas, después de la sección "Con kernel Matérn", en una nueva sección markdown titulada algo como `# MOGP — Funciones Vector-Valuadas (Paso 2 del ablation)`.

---

## 2. Qué es una función vector-valuada, en el contexto de esta tesis

En el Paso 1, el proceso gaussiano modelaba una sola serie: $f(t)\sim\mathcal{GP}(0,k(t,t'))$, donde $f(t)$ es un número (la deformación de un solo sensor EPM en el instante $t$).

Ahora se extiende a un **vector de salidas simultáneas**:

$$\mathbf{f}(t) = \big(f_1(t), \dots, f_D(t)\big) \sim \mathcal{GP}(\mathbf{0}, K(t,t'))$$

- $D$: número total de series modeladas juntas. En la implementación inicial, $D=2$ (una serie EPM + una serie MPT, el par con mejor cross-mapping skill según el análisis CCM ya hecho — no las 18 series completas todavía).
- $K(t,t') \in \mathbb{R}^{D\times D}$: la matriz de covarianza en bloques, donde la entrada $(d,d')$ es la covarianza entre la serie $d$ en el tiempo $t$ y la serie $d'$ en el tiempo $t'$.
- El bloque $K_{TE}(t,t')$ (covarianza cruzada MPT-EPM) es la pieza que en el Paso 3 se reemplazará por la derivación analítica de Nishihara. En este Paso 2, se usa un kernel genérico compartido.

---

## 3. El modelo a implementar: ICM (Intrinsic Coregionalization Model)

Este paso NO usa todavía el kernel de Nishihara. Usa la forma **separable** más simple de $K(t,t')$:

$$K(t,t') = B \cdot k(t,t')$$

- $B \in \mathbb{R}^{D\times D}$: la matriz de corregionalización, aprendida desde los datos (codifica qué tan correlacionadas están las series entre sí, independiente del tiempo). GPy la parametriza como $B = W W^\top + \kappa I$, donde $W$ y $\kappa$ son los hiperparámetros libres.
- $k(t,t')$: un kernel escalar estándar, **compartido por todas las series**, que describe cómo decae la similitud con la distancia temporal. Aquí es donde entran las dos variantes pedidas: RBF y Matérn.

**Limitación conocida de este modelo, documentada a propósito:** al ser separable, obliga a que la covarianza cruzada MPT-EPM decaiga en el tiempo con la misma forma que las covarianzas EPM-EPM o MPT-MPT — solo cambia la magnitud ($B_{d,d'}$), nunca la forma. Esta limitación es exactamente la motivación del Paso 3 (kernel de Nishihara, no separable), y debe quedar mencionada en cualquier conclusión que el agente escriba sobre los resultados de este paso.

---

## 4. Las dos integraciones pedidas: RBF e ICM-Matérn

Se implementan dos variantes del mismo modelo ICM, cambiando solo el kernel base $k(t,t')$:

### Variante A — ICM con kernel base RBF
```python
kernel_rbf = GPy.kern.RBF(input_dim=1)
icm_rbf = GPy.util.multioutput.ICM(input_dim=1, num_outputs=2, kernel=kernel_rbf)
```

### Variante B — ICM con kernel base Matérn (usar Matern32 o Matern52, igual que en el Paso 1)
```python
kernel_matern = GPy.kern.Matern52(input_dim=1)
icm_matern = GPy.util.multioutput.ICM(input_dim=1, num_outputs=2, kernel=kernel_matern)
```

Ambas variantes se entrenan y evalúan igual que el Paso 1 (normalización, máscara de la brecha, RMSE/MAE, cobertura del intervalo al 95%), para que los resultados sean directamente comparables entre Paso 1, Variante A y Variante B.

---

## 5. Requisito técnico específico de GPy: codificación del índice de salida

A diferencia del GP univariado del Paso 1, GPy necesita saber **a qué serie pertenece cada observación**. Esto se hace agregando una columna extra de índice a `X`, y usando `GPy.util.multioutput.LCM`/`ICM` con `GPy.models.GPCoregionalizedRegression`, que arma internamente los datos en el formato heterotópico:

```python
X_list = [t_train_MPT, t_train_EPM]   # cada serie con su propio vector de tiempo — heterotópico, no forzar el mismo grid
Y_list = [y_train_MPT, y_train_EPM]
modelo = GPy.models.GPCoregionalizedRegression(X_list, Y_list, kernel=icm_rbf)
```

**Importante — no forzar sincronización de timestamps.** El MPT y el EPM tienen grillas de tiempo con un desfase estructural de ~1 hora entre sí (ya documentado en la limpieza de datos). El formato heterotópico de GPy maneja esto de forma nativa: cada lista de `X` conserva su propio vector de tiempos, sin necesidad de interpolar o alinear artificialmente los relojes.

---

## 6. Selección del par MPT-EPM para esta primera implementación

No implementar con las 18 series de una vez. Usar el par con mejor evidencia de acoplamiento del análisis CCM ya completado: **EPM Sensor 1 (5m)** con la serie MPT que dio mayor skill de cross-mapping (0.66–0.90 según el análisis previo). Esto aísla el experimento a $D=2$, permitiendo verificar que el mecanismo funciona antes de escalar.

---

## 7. Qué comparar al final de este paso

- RMSE/MAE del MOGP-ICM (Variante A y B) contra el RMSE/MAE del GP univariado del Paso 1, sobre la misma ventana enmascarada.
- Expectativa razonada (no garantizada): el MOGP debería mejorar sobre el Paso 1, porque ahora tiene acceso a información del MPT durante la brecha simulada — algo que el GP univariado no tenía.
- Si el MOGP-ICM no mejora sustancialmente, no es necesariamente un error de código: puede ser evidencia adicional de que se necesita el kernel no separable de Nishihara (Paso 3), no solo la estructura de corregionalización genérica.

---

## 8. Lo que este documento NO cubre todavía

- La derivación del kernel de Nishihara (Paso 3) — eso viene después, en un documento separado.
- El uso de las 18 series completas — se deja para una vez validado el caso $D=2$.
- Kennedy-O'Hagan multi-fidelidad — es un marco relacionado pero distinto del ICM, se documentará aparte si se decide implementarlo explícitamente en vez de usarlo solo como justificación teórica.
