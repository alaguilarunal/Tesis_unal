# Instrucciones de integración — libro_1.ipynb

**Contexto para el agente (leer antes de tocar nada):**

Hay dos notebooks. `libro_1.ipynb` es el vigente y local — usa `data/EPMDATA_INTERPOLATED_v2.csv`
y `data/TPMDATA_CLEANED.csv`, que están limpios (sin NaNs, sin el bug de escala de las
columnas POT, muestreo uniforme cada 6 horas, 884-885 filas). `tpm_y_ccm.ipynb` es un
notebook de Colab **deprecado** que calculó Transfer Entropy sobre un archivo distinto
(`EPMDATA-FIXED.csv`/`TPMDATA-FIXED.csv`, 881 filas) que tenía NaNs y un bug de escala en
las columnas POT (valores que perdieron el punto decimal, ej. `8.129` guardado como `8129`).
Ese notebook también asumía mal la unidad de tiempo: multiplicaba los pasos por 30 minutos,
cuando el paso real confirmado es de **6 horas** (verificado con la columna `freq` de los
datos crudos, que reporta el intervalo en minutos: 360/720/1080 = 6h/12h/18h).

**Regla general: todo el trabajo nuevo usa `EPMDATA_INTERPOLATED_v2.csv` y
`TPMDATA_CLEANED.csv` exclusivamente. No usar `EPMDATA-FIXED.csv`, `TPMDATA-FIXED.csv`, ni
rutas de Google Drive. `tpm_y_ccm.ipynb` no se modifica — solo se reutiliza su función
`transfer_entropy()`, corrigiendo lo que se indica abajo.**

---

## PARTE A — Correcciones en celdas existentes de `libro_1.ipynb`

### A.1 — Etiquetas incorrectas en los gráficos (celdas 6 y 8)

**Problema:** el título y el eje Y dicen `"Sensor 1 (5m)"` en texto fijo, pero la variable
`serie` está fijada a `'Sensor 2 (10m)'`. El gráfico usa el dato correcto pero el texto miente.

**En la celda 6**, buscar:
```python
ax.set_ylabel('Sensor 1 (5m) [mm]')
ax.set_title(f'GP con kernel RBF - RMSE={rmse:.3f} mm')
```
Reemplazar por:
```python
ax.set_ylabel(f'{serie} [mm]')
ax.set_title(f'GP con kernel RBF - {serie} - RMSE={rmse:.3f} mm')
```

**En la celda 6**, además, agregar (después de `modelo.optimize(messages=False)`, antes del
comentario `#---`) esta línea que falta — sin ella no se puede verificar el lengthscale
óptimo del RBF, que es justo el número que se necesita para la diapositiva de ablación:
```python
print(modelo.kern)
```

**En la celda 8**, buscar el mismo par de líneas y reemplazar por:
```python
ax.set_ylabel(f'{serie} [mm]')
ax.set_title(f'GP con kernel Matérn 5/2 - {serie} - RMSE={rmse:.3f} mm')
```

### A.2 — Celda 18 rota (`NameError: name 'n' is not defined`)

**Problema:** esta celda usa la variable `n`, definida en la celda 12 (`n = len(df_ccm)`).
Si el kernel se reinicia y esta celda se corre sin volver a correr la celda 12 antes, truena.
No es un error del algoritmo — es una dependencia de estado entre celdas no protegida.

**Fix:** agregar esta línea al inicio de la celda 18 (antes de `N_PERMUTACIONES = 99`), para
que la celda sea autosuficiente sin importar el orden de ejecución previo:
```python
n = len(df_ccm)   # recalculado aquí por seguridad, independiente del orden de ejecución de celdas previas
```

Después de este fix, correr la celda 18 completa. Con `N_PERMUTACIONES=99` y
`SAMPLE_SURROGATE=30` sobre 56 pares, el propio comentario de la celda ya advierte
~2.5 horas de cómputo — es esperado, no es un error si tarda.

### A.3 — Falta el baseline de interpolación lineal

**Problema:** la diapositiva de ablación afirma "RMSE ≈ RMSE de interpolación lineal" pero
ningún cálculo de interpolación lineal existe en el notebook. Sin este número, esa frase de
la presentación no tiene respaldo.

**Fix:** agregar una celda nueva **inmediatamente después de la celda 6** (reutiliza
`y_norm`, `mask_hidden`, `y_mean`, `y_std`, `y_hidden_true_mm` ya definidas ahí):
```python
# Baseline de interpolación lineal — para poder verificar la afirmación
# "RMSE del GP univariado ≈ RMSE de interpolación lineal" antes de reportarla.
y_norm_series = pd.Series(y_norm)
y_norm_series[mask_hidden] = np.nan
y_interp_norm = y_norm_series.interpolate(method='linear').values
y_interp_mm = y_interp_norm * y_std + y_mean

rmse_interp = np.sqrt(np.mean((y_interp_mm[mask_hidden] - y_hidden_true_mm) ** 2))
mae_interp = np.mean(np.abs(y_interp_mm[mask_hidden] - y_hidden_true_mm))
print(f"RMSE interpolación lineal: {rmse_interp:.4f} mm")
print(f"MAE interpolación lineal:  {mae_interp:.4f} mm")
```

### A.4 — Confirmar parámetros del hueco sintético (documentación, no código)

Agregar una celda markdown antes de la celda 6 con este texto exacto (para que quede
registrado y no se vuelva a cuestionar en el futuro):
```markdown
**Parámetros del hueco sintético (confirmados como definitivos para el Paso 1 del ablation study):**
`gap_start=200`, `gap_len=500` → 500 puntos × 6h = 125 días de hueco simulado sobre
`Sensor 2 (10m)`.
```

---

## PARTE B — Exploración de kernels adicionales (Matérn 3/2 y compuesto)

**Contexto:** ya se corrieron RBF (RMSE=2.42mm) y Matérn 5/2 (RMSE=1.75mm) sobre el mismo
hueco. Faltan dos kernels adicionales acordados: Matérn 3/2 solo (misma familia que el
kernel de Nishihara ya derivado, para comparación directa), y un compuesto Matérn 3/2 +
Periódico (para capturar el ciclo diario de voladuras/tráfico/variación térmica que ya se
identificó en el análisis exploratorio).

**Antes de escribir más código duplicado**, refactorizar el patrón repetido (entrenar,
predecir, medir, graficar) en una función reutilizable. Agregar esta celda **antes de la
celda 6** (o convertir la celda 6 en esta función y luego llamarla):

```python
def evaluar_kernel(kernel, nombre_kernel, t_train, y_train, t_hidden, y_hidden_true,
                    y_mean, y_std, t, mask_hidden, serie):
    """
    Entrena un GP univariado con el kernel dado sobre el hueco sintético ya definido
    (t_train/y_train excluyen el hueco; t_hidden/y_hidden_true son los puntos ocultos),
    calcula RMSE/MAE/cobertura al 95%, grafica, y devuelve las métricas para comparar
    entre kernels.
    """
    modelo = GPy.models.GPRegression(t_train, y_train, kernel)
    modelo.optimize(messages=False)
    print(modelo.kern)

    y_pred_norm, y_var_norm = modelo.predict(t_hidden)
    y_pred_norm = y_pred_norm.flatten()
    y_std_pred_norm = np.sqrt(y_var_norm.flatten())

    y_pred_mm = y_pred_norm * y_std + y_mean
    y_hidden_true_mm = y_hidden_true * y_std + y_mean
    y_std_pred_mm = y_std_pred_norm * y_std

    rmse = np.sqrt(np.mean((y_pred_mm - y_hidden_true_mm) ** 2))
    mae = np.mean(np.abs(y_pred_mm - y_hidden_true_mm))
    z95_lo = y_pred_mm - 1.96 * y_std_pred_mm
    z95_hi = y_pred_mm + 1.96 * y_std_pred_mm
    cobertura = np.mean((y_hidden_true_mm >= z95_lo) & (y_hidden_true_mm <= z95_hi))

    print(f"[{nombre_kernel}] RMSE: {rmse:.4f} mm | MAE: {mae:.4f} mm | Cobertura 95%: {cobertura*100:.1f}%")

    t_dias = t / 24
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(t_dias[~mask_hidden], y_norm[~mask_hidden] * y_std + y_mean, '-', color='steelblue', linewidth=1, label='Datos de entrenamiento')
    ax.plot(t_dias[mask_hidden], y_hidden_true_mm, '-o', color='black', linewidth=1.5, markersize=4, label='Valor real (oculto)')
    ax.plot(t_dias[mask_hidden], y_pred_mm, '-', color='crimson', linewidth=2, label=f'Predicción GP ({nombre_kernel})')
    ax.fill_between(t_dias[mask_hidden], z95_lo, z95_hi, color='crimson', alpha=0.2, label='Intervalo 95%')
    ax.set_xlabel('Tiempo (días desde el inicio)')
    ax.set_ylabel(f'{serie} [mm]')
    ax.set_title(f'GP con kernel {nombre_kernel} - {serie} - RMSE={rmse:.3f} mm')
    ax.legend()
    plt.tight_layout()
    plt.show()

    return {'kernel': nombre_kernel, 'rmse': rmse, 'mae': mae, 'cobertura_95': cobertura}
```

Agregar una celda nueva **después de la celda 8**, llamando la función para los dos kernels
faltantes (nota: `t` está en horas desde el inicio, por eso el período diario del kernel
periódico es `period=24.0`):

```python
resultados_kernels = []

# Matérn 3/2 solo — misma familia de suavidad que el kernel de Nishihara ya derivado
kernel_m32 = GPy.kern.Matern32(input_dim=1, variance=1.0, lengthscale=100.0)
resultados_kernels.append(
    evaluar_kernel(kernel_m32, "Matérn 3/2", t_train, y_train, t_hidden, y_hidden_true,
                   y_mean, y_std, t, mask_hidden, serie)
)

# Matérn 3/2 + Periódico — separa la tendencia de fluencia del ciclo diario
kernel_compuesto = (
    GPy.kern.Matern32(input_dim=1, variance=1.0, lengthscale=100.0)
    + GPy.kern.StdPeriodic(input_dim=1, variance=0.5, period=24.0, lengthscale=24.0)
)
resultados_kernels.append(
    evaluar_kernel(kernel_compuesto, "Matérn 3/2 + Periódico", t_train, y_train, t_hidden,
                   y_hidden_true, y_mean, y_std, t, mask_hidden, serie)
)

print(pd.DataFrame(resultados_kernels))
```

---

## PARTE C — Recalcular Transfer Entropy (nueva sección, al final de `libro_1.ipynb`)

Agregar una celda markdown nueva al final del notebook:

```markdown
# Transfer Entropy — recalculada sobre datos corregidos

Esta sección reemplaza el cálculo de `tpm_y_ccm.ipynb`, que usaba `EPMDATA-FIXED.csv`/
`TPMDATA-FIXED.csv` (con NaNs, bug de escala en POT, y una conversión de unidades
incorrecta: asumía pasos de 30 minutos cuando el paso real es de 6 horas). Aquí se
recalcula todo sobre `epm`/`tpm` (las variables ya cargadas en las celdas 3 y 12,
provenientes de `EPMDATA_INTERPOLATED_v2.csv`/`TPMDATA_CLEANED.csv`), reutilizando la
función `transfer_entropy()` original de Schreiber (2000) sin cambios — el bug estaba en
la conversión a horas/minutos y en el rango de rezagos probado, no en la fórmula.
```

Luego, una celda de código con la función (copiada tal cual de `tpm_y_ccm.ipynb`, celda 10,
sin modificar — la fórmula está correcta):

```python
from collections import Counter

def transfer_entropy(fuente, objetivo, tau, bins=5):
    """
    Calcula T(fuente -> objetivo) al rezago tau, en bits, por el estimador de
    histograma de Schreiber (2000). Copiado sin cambios de tpm_y_ccm.ipynb — la
    fórmula nunca tuvo el bug, solo la interpretación de las unidades de tau.
    """
    def discretizar(x):
        x = np.asarray(x)
        mn, mx = x.min(), x.max()
        idx = np.floor((x - mn) / (mx - mn + 1e-12) * bins).astype(int)
        return np.clip(idx, 0, bins - 1)

    X = discretizar(fuente)
    Y = discretizar(objetivo)
    n = len(Y)

    c_xyz, c_yz, c_xz, c_z = Counter(), Counter(), Counter(), Counter()
    for i in range(tau, n - 1):
        y_futuro, y_pasado, x_pasado = Y[i + 1], Y[i], X[i - tau]
        c_xyz[(y_futuro, y_pasado, x_pasado)] += 1
        c_yz[(y_futuro, y_pasado)] += 1
        c_xz[(y_pasado, x_pasado)] += 1
        c_z[(y_pasado,)] += 1

    total = sum(c_xyz.values())
    if total == 0:
        return 0.0

    te = 0.0
    for (yf, yp, xp), n_xyz in c_xyz.items():
        n_yz, n_xz, n_z = c_yz[(yf, yp)], c_xz[(yp, xp)], c_z[(yp,)]
        if n_yz > 0 and n_xz > 0 and n_z > 0:
            te += (n_xyz / total) * np.log2((n_xyz * n_z) / (n_yz * n_xz))
    return max(0.0, te)
```

**Celda siguiente — confirmar el paso temporal real (no volver a asumirlo):**
```python
paso_horas = (epm['date'].iloc[1] - epm['date'].iloc[0]).total_seconds() / 3600
print(f"Paso temporal detectado entre filas consecutivas: {paso_horas} horas")
# Debe imprimir 6.0. Si imprime otra cosa, DETENERSE — algo cambió en los datos
# y hay que revisar antes de seguir, no asumir ningún valor.
assert paso_horas == 6.0, "El paso temporal no es el esperado (6 horas) — revisar antes de continuar"
```

**Celda siguiente — calcular TE para los 56 pares, rango de rezagos ampliado
(el rango anterior de 1 a 12 pasos pegaba contra el techo en todos los pares, señal
de que el verdadero óptimo estaba más allá; se amplía a 1–28 pasos = hasta 7 días):**
```python
tpm_cols = [c for c in tpm.columns if 'freq' not in c]
epm_cols = [c for c in epm.columns if 'Sensor' in c]

te_tpm_epm_dict = {}
te_epm_tpm_dict = {}

for tpm_col in tpm_cols:
    print("=" * 50, f"Serie: {tpm_col}")
    for epm_col in epm_cols:
        lags = np.arange(1, 29)   # 1 a 28 pasos = hasta 7 días (6h x 28), antes era 1-12
        te_tpm_epm = [transfer_entropy(tpm[tpm_col], epm[epm_col], tau=int(lag)) for lag in lags]
        te_epm_tpm = [transfer_entropy(epm[epm_col], tpm[tpm_col], tau=int(lag)) for lag in lags]

        tau_optimo = int(lags[np.argmax(te_tpm_epm)])
        tau_optimo_epm_tpm = int(lags[np.argmax(te_epm_tpm)])
        te_max = max(te_tpm_epm)
        te_max_epm_tpm = max(te_epm_tpm)

        te_tpm_epm_dict.setdefault(tpm_col, {})[epm_col] = {
            "tau_optimo": tau_optimo, "te_max": te_max, "lags": lags,
            "lag_horas": lags * paso_horas,
            "te_tpm_epm": te_tpm_epm, "te_epm_tpm": te_epm_tpm,
            "te_max_epm_tpm": te_max_epm_tpm, "tau_optimo_epm_tpm": tau_optimo_epm_tpm,
        }
        te_epm_tpm_dict.setdefault(tpm_col, {})[epm_col] = {
            "tau_optimo": tau_optimo_epm_tpm, "te_max": te_max_epm_tpm, "lags": lags,
        }

        # Alerta si el óptimo sigue pegado al techo del rango — ya no debería pasar,
        # pero si pasa, hay que ampliar el rango de nuevo antes de reportar el resultado.
        if tau_optimo == lags[-1]:
            print(f"  ADVERTENCIA: tau_optimo pegado al techo del rango para {tpm_col}->{epm_col}, ampliar 'lags'")

        print(f"* {epm_col}: tau* = {tau_optimo} pasos ({tau_optimo * paso_horas:.0f}h) | "
              f"T(TPM→EPM)={te_max:.4f} bits | T(EPM→TPM)={max(te_epm_tpm):.4f} bits")
```

**Celda siguiente — surrogate test (199 permutaciones, ambas direcciones; el costo es
bajo porque `transfer_entropy` es un conteo de histograma, no una llamada a pyEDM —
debería tardar minutos, no horas, a diferencia del surrogate test de CCM):**
```python
N_PERMUTACIONES = 199
rng = np.random.default_rng(42)

for tpm_col in tpm_cols:
    for epm_col in epm_cols:
        entrada = te_tpm_epm_dict[tpm_col][epm_col]
        te_max = entrada["te_max"]
        tau_optimo = entrada["tau_optimo"]

        dist_nula_tpm_epm = [
            transfer_entropy(rng.permutation(tpm[tpm_col].values), epm[epm_col].values, tau=tau_optimo)
            for _ in range(N_PERMUTACIONES)
        ]
        umbral = np.percentile(dist_nula_tpm_epm, 95)
        p_valor = np.mean(np.array(dist_nula_tpm_epm) >= te_max)
        entrada["umbral"] = umbral
        entrada["p_valor"] = p_valor
        entrada["distribucion_nula"] = dist_nula_tpm_epm

        entrada_inv = te_epm_tpm_dict[tpm_col][epm_col]
        te_max_inv = entrada_inv["te_max"]
        tau_optimo_inv = entrada_inv["tau_optimo"]
        dist_nula_epm_tpm = [
            transfer_entropy(rng.permutation(epm[epm_col].values), tpm[tpm_col].values, tau=tau_optimo_inv)
            for _ in range(N_PERMUTACIONES)
        ]
        p_valor_inv = np.mean(np.array(dist_nula_epm_tpm) >= te_max_inv)
        entrada_inv["p_valor"] = p_valor_inv
```

**Celda siguiente — el conteo agregado que faltaba en AMBOS notebooks anteriores
(el "55/56" y "45/56" de la presentación no eran reproducibles hasta ahora; esta celda
es la que finalmente los produce de forma verificable):**
```python
n_sig_tpm_epm = sum(
    1 for tpm_col in tpm_cols for epm_col in epm_cols
    if te_tpm_epm_dict[tpm_col][epm_col]["p_valor"] < 0.05
)
n_sig_epm_tpm = sum(
    1 for tpm_col in tpm_cols for epm_col in epm_cols
    if te_epm_tpm_dict[tpm_col][epm_col]["p_valor"] < 0.05
)
n_pares = len(tpm_cols) * len(epm_cols)

print(f"Pares TPM→EPM significativos (p<0.05): {n_sig_tpm_epm}/{n_pares}")
print(f"Pares EPM→TPM significativos (p<0.05): {n_sig_epm_tpm}/{n_pares}")
```

---

## PARTE D — Explícitamente fuera de alcance en este pase (no hacer todavía)

- No optimizar `exclusionRadius` ni `tau` de CCM desde autocorrelación — tarea aparte.
- No implementar el kernel de Nishihara como subclase de `GPy.kern.Kern` — es el Paso 3
  del ablation study, viene después de tener listos los pasos anteriores.
- No modificar `tpm_y_ccm.ipynb` — queda como registro histórico; todo lo reutilizable de
  ahí ya se copió corregido a `libro_1.ipynb` en la Parte C.

---

## Orden de ejecución recomendado

1. Parte A completa (A.1 a A.4) — son correcciones rápidas y no tienen dependencias entre sí.
2. Parte B — depende de que A.1 y A.3 ya estén aplicadas (reutiliza `t_train`, `t_hidden`, etc.).
3. Parte C — independiente de A y B, pero debe ir al final del notebook. Correr la celda
   de `assert paso_horas == 6.0` primero; si falla, detenerse y avisar antes de seguir.
