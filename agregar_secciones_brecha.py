"""
Agrega dos secciones nuevas al final de libro 1.ipynb:

  A) Validacion post-brecha: Pearson, dCor, TE y CCM sobre la ventana 2025-05-01 -> fin,
     comparando contra los resultados pre-brecha ya calculados en celdas anteriores.
  B) Reconstruccion preliminar (kernel generico RBF/Matern, "a priori") de la brecha real
     de 680 dias usando un MOGP (GPy, ICM) con EPM Sensor 1 + TPM POT(1) como par D=2,
     usando Data_limpia_completa/{EPM,TPM}_completo.csv.

No se ejecuta aqui (no hay pandas/GPy/pyEDM en los entornos locales disponibles) --
solo se valida que el notebook resultante sea JSON/nbformat valido.
"""
import json
import uuid
from pathlib import Path

NB_PATH = Path("libro 1.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)


def new_id():
    return uuid.uuid4().hex[:8]


def md(text):
    return {
        "cell_type": "markdown",
        "id": new_id(),
        "metadata": {},
        "source": text.splitlines(keepends=True),
    }


def code(text):
    return {
        "cell_type": "code",
        "execution_count": None,
        "id": new_id(),
        "metadata": {},
        "outputs": [],
        "source": text.splitlines(keepends=True),
    }


nuevas_celdas = []

# =============================================================================
# SECCION A -- Validacion post-brecha
# =============================================================================

nuevas_celdas.append(md(
"""# Validacion post-brecha: Pearson, dCor, TE y CCM (2025-05 a 2025-09)

Hasta aqui todo el analisis de correlacion/causalidad (CCM, TE) se corrio sobre los 7
meses **pre-brecha** (2022-11 a 2023-06), que es la unica ventana donde EPM y TPM se
superponen en `data/EPMDATA_INTERPOLATED_v2.csv` / `data/TPMDATA_CLEANED.csv`. Esos
archivos nunca llegaron a cubrir la brecha real.

`Data_limpia_completa/EPM_completo.csv` y `Data_limpia_completa/TPM_completo.csv`
(generados en `limpiar_datos_crudos.py` a partir de `Data_cruda/`) si cubren el periodo
en que el EPM vuelve a medirse (2025-05-01 en adelante), y el TPM nunca dejo de
observarse. Esto permite repetir **exactamente el mismo analisis** en una segunda
ventana temporal, separada por casi dos anios de la primera.

**Por que importa:** si Pearson, dCor, TE y CCM dan resultados consistentes en dos
ventanas separadas por ~2 anios, eso es mucho mas dificil de explicar como una
correlacion espuria inducida por una tendencia compartida de corto plazo (una de las
objeciones metodologicas mas fuertes que se le puede hacer a un analisis de una sola
ventana continua) -- es evidencia de que la relacion TPM-EPM es estructural, no un
artefacto de ese tramo especifico.

**Decision metodologica:** se remuestrea todo a la rejilla de 6 horas (igual paso que
`EPMDATA_INTERPOLATED_v2.csv`/`TPMDATA_CLEANED.csv`), en vez de usar la resolucion nativa
post-brecha (30 min / 1h). Esto se hace por dos razones: (1) comparar manzanas con
manzanas -- misma resolucion temporal en ambas ventanas, para que una diferencia en los
resultados no pueda explicarse por un cambio de muestreo; (2) mantener el costo
computacional de dCor (O(n^2) en memoria) y de CCM (pyEDM) manejable."""
))

nuevas_celdas.append(code(
"""epm_ext = pd.read_csv("Data_limpia_completa/EPM_completo.csv", parse_dates=['date'])
tpm_ext = pd.read_csv("Data_limpia_completa/TPM_completo.csv", parse_dates=['date'])

print(f"EPM extendido: {len(epm_ext)} filas, {epm_ext['date'].min()} -> {epm_ext['date'].max()}")
print(f"TPM extendido: {len(tpm_ext)} filas, {tpm_ext['date'].min()} -> {tpm_ext['date'].max()}")
"""
))

nuevas_celdas.append(code(
"""# Ventana post-brecha: desde que el EPM vuelve a medirse hasta el final del registro.
# Se remuestrea a una rejilla regular de 6h (igual paso que el periodo pre-brecha) y se
# alinean EPM/TPM sobre ella con merge_asof (misma tolerancia que ya se usaba en la
# celda de CCM pre-brecha: 3h).
POST_BRECHA_INICIO = pd.Timestamp("2025-05-01")

rejilla_post = pd.DataFrame({
    'date': pd.date_range(POST_BRECHA_INICIO, epm_ext['date'].max(), freq='6h')
})

epm_post = pd.merge_asof(
    rejilla_post, epm_ext.sort_values('date'),
    on='date', direction='nearest', tolerance=pd.Timedelta('3h')
).dropna().reset_index(drop=True)

tpm_post = pd.merge_asof(
    rejilla_post, tpm_ext.drop(columns=['freq']).sort_values('date'),
    on='date', direction='nearest', tolerance=pd.Timedelta('3h')
).dropna().reset_index(drop=True)

# df_ccm_post: mismo formato posicional que df_ccm (pre-brecha, celda de mas arriba) --
# intersecta ambos en 'date' y descarta la columna de fecha para pyEDM/transfer_entropy.
df_ccm_post = pd.merge(epm_post, tpm_post, on='date', how='inner')
print(f"Filas EPM post-brecha (6h): {len(epm_post)}, TPM: {len(tpm_post)}, "
      f"alineadas: {len(df_ccm_post)}")

paso_horas_post = (df_ccm_post['date'].iloc[1] - df_ccm_post['date'].iloc[0]).total_seconds() / 3600
print(f"Paso temporal detectado (post-brecha): {paso_horas_post} horas")
assert paso_horas_post == 6.0, "El remuestreo no quedo en 6h -- revisar antes de continuar"

df_ccm_post_sin_fecha = df_ccm_post.drop(columns=['date'])
"""
))

nuevas_celdas.append(md(
"""## Pearson y Distance Correlation (Szekely, Rizzo & Bakirov, 2007)

Estas dos metricas nunca se habian calculado dentro de este cuaderno (los heatmaps de
Pearson/dCor que ya estan en la presentacion vienen de un script externo que no esta en
este proyecto). Aqui se implementan ambas desde cero y se calculan en las **dos**
ventanas (pre y post brecha), usando `df_ccm` (ya construido mas arriba, pre-brecha) y
`df_ccm_post_sin_fecha` (post-brecha), para que la comparacion sea reproducible de punta
a punta dentro de este mismo cuaderno."""
))

nuevas_celdas.append(code(
"""def distance_correlation(x, y):
    \"\"\"
    Distance correlation de Szekely, Rizzo & Bakirov (2007), via doble centrado.
    O(n^2) en memoria -- aceptable para n del orden de cientos/miles (ventanas de
    6h de unos pocos meses), no para series completas de alta frecuencia.
    \"\"\"
    x = np.asarray(x, dtype=float).reshape(-1, 1)
    y = np.asarray(y, dtype=float).reshape(-1, 1)

    a = np.abs(x - x.T)
    b = np.abs(y - y.T)

    A = a - a.mean(axis=0, keepdims=True) - a.mean(axis=1, keepdims=True) + a.mean()
    B = b - b.mean(axis=0, keepdims=True) - b.mean(axis=1, keepdims=True) + b.mean()

    dcov2 = (A * B).mean()
    dvarx2 = (A * A).mean()
    dvary2 = (B * B).mean()
    denom = np.sqrt(dvarx2 * dvary2)
    return float(np.sqrt(dcov2 / denom)) if denom > 0 else 0.0


def matriz_pearson_dcor(df, series_tpm, series_epm):
    filas = []
    for tpm_col in series_tpm:
        for epm_col in series_epm:
            x = df[tpm_col].values
            y = df[epm_col].values
            r = float(np.corrcoef(x, y)[0, 1])
            dc = distance_correlation(x, y)
            filas.append({'TPM': tpm_col, 'EPM': epm_col, 'pearson_r': r, 'dcor': dc})
    return pd.DataFrame(filas)


pre_dcor_df = matriz_pearson_dcor(df_ccm, series_tpm, series_epm)
post_dcor_df = matriz_pearson_dcor(df_ccm_post_sin_fecha, series_tpm, series_epm)

print("=== Pearson/dCor pre-brecha (2022-11 a 2023-06) ===")
print(pre_dcor_df.round(3).sort_values('pearson_r', key=abs, ascending=False).head(10))
print()
print("=== Pearson/dCor post-brecha (2025-05 a 2025-09) ===")
print(post_dcor_df.round(3).sort_values('pearson_r', key=abs, ascending=False).head(10))
"""
))

nuevas_celdas.append(code(
"""# Comparacion directa par a par: ¿se sostiene la relacion en las dos ventanas?
comparacion_corr = pre_dcor_df.merge(
    post_dcor_df, on=['TPM', 'EPM'], suffixes=('_pre', '_post')
)
comparacion_corr['dif_pearson'] = (comparacion_corr['pearson_r_post']
                                    - comparacion_corr['pearson_r_pre'])
comparacion_corr['dif_dcor'] = comparacion_corr['dcor_post'] - comparacion_corr['dcor_pre']

pd.set_option('display.width', 200)
pd.set_option('display.max_columns', None)
print(comparacion_corr.round(3).sort_values('pearson_r_pre', key=abs, ascending=False))

print()
print(f"Pearson |r] medio pre-brecha:  {comparacion_corr['pearson_r_pre'].abs().mean():.3f}")
print(f"Pearson |r| medio post-brecha: {comparacion_corr['pearson_r_post'].abs().mean():.3f}")
print(f"dCor medio pre-brecha:  {comparacion_corr['dcor_pre'].mean():.3f}")
print(f"dCor medio post-brecha: {comparacion_corr['dcor_post'].mean():.3f}")
"""
))

nuevas_celdas.append(md(
"""## Transfer Entropy post-brecha

Se reutiliza `transfer_entropy()` (definida arriba, sin cambios) sobre `df_ccm_post`, y
se compara contra `te_tpm_epm_dict`/`te_epm_tpm_dict` (ya calculados pre-brecha mas
arriba)."""
))

nuevas_celdas.append(code(
"""epm_post_arr = {c: df_ccm_post_sin_fecha[c].values for c in series_epm}
tpm_post_arr = {c: df_ccm_post_sin_fecha[c].values for c in series_tpm}

te_tpm_epm_post = {}
te_epm_tpm_post = {}

for tpm_col in series_tpm:
    for epm_col in series_epm:
        lags = np.arange(1, 29)  # mismo rango que el calculo pre-brecha (hasta 7 dias)
        te_fwd = [transfer_entropy(tpm_post_arr[tpm_col], epm_post_arr[epm_col], tau=int(l)) for l in lags]
        te_bwd = [transfer_entropy(epm_post_arr[epm_col], tpm_post_arr[tpm_col], tau=int(l)) for l in lags]

        te_tpm_epm_post.setdefault(tpm_col, {})[epm_col] = {
            'tau_optimo': int(lags[np.argmax(te_fwd)]), 'te_max': max(te_fwd),
        }
        te_epm_tpm_post.setdefault(tpm_col, {})[epm_col] = {
            'tau_optimo': int(lags[np.argmax(te_bwd)]), 'te_max': max(te_bwd),
        }

N_PERMUTACIONES_POST = 199
rng_post = np.random.default_rng(42)

for tpm_col in series_tpm:
    for epm_col in series_epm:
        entrada = te_tpm_epm_post[tpm_col][epm_col]
        dist_nula = [
            transfer_entropy(rng_post.permutation(tpm_post_arr[tpm_col]), epm_post_arr[epm_col],
                              tau=entrada['tau_optimo'])
            for _ in range(N_PERMUTACIONES_POST)
        ]
        entrada['p_valor'] = float(np.mean(np.array(dist_nula) >= entrada['te_max']))

n_sig_post = sum(
    1 for tpm_col in series_tpm for epm_col in series_epm
    if te_tpm_epm_post[tpm_col][epm_col]['p_valor'] < 0.05
)
print(f"TE: pares TPM->EPM significativos post-brecha (p<0.05): {n_sig_post}/{len(series_tpm)*len(series_epm)}")
print(f"TE: pares TPM->EPM significativos pre-brecha (ya calculado arriba): "
      f"{n_sig_tpm_epm}/{n_pares}")
"""
))

nuevas_celdas.append(md(
"""## CCM post-brecha

Mismo pipeline de `pyEDM.EmbedDimension` + `pyEDM.CCM` que se uso pre-brecha, mismos
parametros (`maxE=40`, `sample=100`, `exclusionRadius=10`), sobre `df_ccm_post_sin_fecha`.
**Advertencia de costo:** igual que el bloque pre-brecha, el test de surrogates completo
(`N=99`) para los 56 pares puede tardar del orden de horas; se deja como celda aparte,
opcional, al final."""
))

nuevas_celdas.append(code(
"""n_post = len(df_ccm_post_sin_fecha)
lib_end_post = int(n_post * 0.68)
lib_range_post = f"1 {lib_end_post}"
pred_range_post = f"{lib_end_post + 1} {n_post}"
maxE = 40  # mismo valor que el bloque pre-brecha

tabla_E_post = []
for col in columnas_tpm_epm:
    resultado = pyEDM.EmbedDimension(
        dataFrame=df_ccm_post_sin_fecha, lib=lib_range_post, pred=pred_range_post,
        maxE=maxE, columns=[col], target=[col], showPlot=False,
    )
    tabla_E_post.append({
        'serie': col,
        'E_optimo': resultado.loc[resultado['rho'].idxmax(), 'E'],
        'rho_max': resultado['rho'].max(),
    })
tabla_E_post = pd.DataFrame(tabla_E_post)
print(tabla_E_post)
"""
))

nuevas_celdas.append(code(
"""E_optimo_post = tabla_E_post.set_index('serie')['E_optimo'].to_dict()
sample_post = 100
exclusionRadius_post = 10

resultados_ccm_post = {}
for i, (tpm_col, epm_col) in enumerate(pares):
    print(f"[{i+1}/{len(pares)}] (post-brecha) {tpm_col} vs {epm_col}...", flush=True)
    E_par_post = max(E_optimo_post[tpm_col], E_optimo_post[epm_col])
    inicio_post = E_par_post + 10
    libSizes_par_post = f"{inicio_post} {n_post} 40"

    res = pyEDM.CCM(
        dataFrame=df_ccm_post_sin_fecha, E=E_par_post, columns=[tpm_col], target=[epm_col],
        libSizes=libSizes_par_post, sample=sample_post, exclusionRadius=exclusionRadius_post,
        showPlot=False, parallel=False,
    )
    resultados_ccm_post[(tpm_col, epm_col)] = res

resumen_post = []
for (tpm_col, epm_col), res in resultados_ccm_post.items():
    res_sorted = res.sort_values('LibSize')
    fila_final = res_sorted.iloc[-1]
    col_tpm_a_epm = res.columns[1]
    col_epm_a_tpm = res.columns[2]
    resumen_post.append({
        'TPM': tpm_col, 'EPM': epm_col,
        'skill_TPMmanifold_predice_EPM': fila_final[col_tpm_a_epm],
        'skill_EPMmanifold_predice_TPM': fila_final[col_epm_a_tpm],
    })
resumen_df_post = pd.DataFrame(resumen_post)

comparacion_ccm = resumen_df[['TPM', 'EPM', 'skill_TPMmanifold_predice_EPM']].merge(
    resumen_df_post[['TPM', 'EPM', 'skill_TPMmanifold_predice_EPM']],
    on=['TPM', 'EPM'], suffixes=('_pre', '_post'),
)
print(comparacion_ccm.round(3).sort_values('skill_TPMmanifold_predice_EPM_pre', ascending=False))
"""
))

nuevas_celdas.append(code(
"""# OPCIONAL -- costoso (horas). Test de surrogates para CCM post-brecha, mismo metodo
# que la celda pre-brecha (permutacion + percentil 95, N=99, sample reducido a 30).
N_PERMUTACIONES_CCM_POST = 99
SAMPLE_SURROGATE_POST = 30
libSize_max_str_post = f"{n_post} {n_post} 1"
rng_ccm_post = np.random.default_rng(42)

surrogate_post = []
for i, (tpm_col, epm_col) in enumerate(pares):
    print(f"[{i+1}/{len(pares)}] surrogates post-brecha {tpm_col} vs {epm_col}...", flush=True)
    E_par_post = max(E_optimo_post[tpm_col], E_optimo_post[epm_col])

    skill_obs = resumen_df_post.loc[
        (resumen_df_post['TPM'] == tpm_col) & (resumen_df_post['EPM'] == epm_col),
        'skill_TPMmanifold_predice_EPM'
    ].iloc[0]

    df_perm = df_ccm_post_sin_fecha.copy()
    null_dist = []
    for _ in range(N_PERMUTACIONES_CCM_POST):
        df_perm[tpm_col] = rng_ccm_post.permutation(df_ccm_post_sin_fecha[tpm_col].values)
        res_null = pyEDM.CCM(
            dataFrame=df_perm, E=E_par_post, columns=[tpm_col], target=[epm_col],
            libSizes=libSize_max_str_post, sample=SAMPLE_SURROGATE_POST,
            exclusionRadius=exclusionRadius_post, showPlot=False, parallel=False,
        )
        null_dist.append(res_null.iloc[0][f'{tpm_col}:{epm_col}'])

    surrogate_post.append({
        'TPM': tpm_col, 'EPM': epm_col,
        'p_valor_post': float(np.mean(np.array(null_dist) >= skill_obs)),
    })

surrogate_post_df = pd.DataFrame(surrogate_post)
n_sig_ccm_post = (surrogate_post_df['p_valor_post'] < 0.05).sum()
print(f"CCM: pares TPM->EPM significativos post-brecha (p<0.05): {n_sig_ccm_post}/{len(pares)}")
"""
))

# =============================================================================
# SECCION B -- Reconstruccion preliminar con kernel generico (RBF/Matern)
# =============================================================================

nuevas_celdas.append(md(
"""# Reconstruccion preliminar de la brecha real (kernel generico, resultado "a priori")

Todo lo anterior (ablation study, CCM, TE, Pearson, dCor) corrio sobre la ventana
pre-brecha, o sobre brechas **sinteticas** dentro de ella -- nunca sobre la brecha real
de 680 dias, porque `data/EPMDATA_INTERPOLATED_v2.csv` no la cubre.

Esta seccion usa `Data_limpia_completa/` (que si cubre la brecha real) para dar un
primer resultado de reconstruccion con un **kernel generico** (RBF o Matern, sin
informacion fisica de Nishihara todavia -- de ahi "a priori": es el resultado de
referencia contra el que se debe comparar el kernel $K_{TE}$ informado por el modelo
constitutivo una vez que su derivacion quede cerrada).

**Diseno del experimento (para que sirva tambien como validacion, no solo como demo):**
- Par $D=2$: EPM Sensor 1 (5m) + TPM POT(1) -- el mismo par identificado como el de
  mayor CCM skill (ver `funciones_vector_valuadas.md`, seccion 6).
- El MOGP se entrena **solo** con el tramo pre-brecha de EPM Sensor 1, mas **todo** el
  TPM disponible (pre, durante y despues de la brecha -- el TPM nunca deja de
  observarse, por eso puede "ver" la brecha aunque el EPM no).
- El tramo **post-brecha de EPM se deja fuera del entrenamiento a proposito** y se usa
  solo al final, como punto de comparacion cualitativo: si la media posterior +
  intervalo de credibilidad al reanudarse la medicion es consistente con el valor real
  observado, eso es evidencia (no prueba) de que el mecanismo de transferencia de
  informacion TPM->EPM generaliza mas alla del tramo de ajuste."""
))

nuevas_celdas.append(code(
"""EPM_COL_B = 'Sensor 1 (5m)'
TPM_COL_B = 'POT(1)'
BRECHA_INICIO = pd.Timestamp("2023-06-20")
BRECHA_FIN = pd.Timestamp("2025-05-01")

t0_b = epm_ext['date'].min()

def a_dias(fechas):
    return (fechas - t0_b).dt.total_seconds().values / 86400.0

epm_b = epm_ext[['date', EPM_COL_B]].dropna().sort_values('date').reset_index(drop=True)
tpm_b = tpm_ext[['date', TPM_COL_B]].dropna().sort_values('date').reset_index(drop=True)

X_epm_b = a_dias(epm_b['date']).reshape(-1, 1)
Y_epm_b = epm_b[EPM_COL_B].values.reshape(-1, 1)
X_tpm_b = a_dias(tpm_b['date']).reshape(-1, 1)
Y_tpm_b = tpm_b[TPM_COL_B].values.reshape(-1, 1)

# Estandarizacion por salida -- EPM esta en ~3000 (Digits del extensometro), TPM en ~8
# (ver tambien la discusion pendiente sobre unidades mm vs Digits en la presentacion).
epm_mu, epm_sigma = Y_epm_b.mean(), Y_epm_b.std()
tpm_mu, tpm_sigma = Y_tpm_b.mean(), Y_tpm_b.std()
Y_epm_b_std = (Y_epm_b - epm_mu) / epm_sigma
Y_tpm_b_std = (Y_tpm_b - tpm_mu) / tpm_sigma

# Solo el tramo PRE-brecha de EPM entra al entrenamiento; el post-brecha se reserva
# para comparar al final (no se usa para ajustar hiperparametros).
mask_epm_train = X_epm_b[:, 0] < (BRECHA_INICIO - t0_b).total_seconds() / 86400.0
X_epm_train_b = X_epm_b[mask_epm_train]
Y_epm_train_b = Y_epm_b_std[mask_epm_train]
X_epm_heldout_b = X_epm_b[~mask_epm_train]
Y_epm_heldout_b = Y_epm_b_std[~mask_epm_train]

print(f"EPM entrenamiento (pre-brecha): {len(X_epm_train_b)} puntos")
print(f"EPM reservado para comparar (post-brecha, NO se entrena con esto): {len(X_epm_heldout_b)} puntos")
print(f"TPM total disponible (pre+durante+post brecha): {len(X_tpm_b)} puntos")
"""
))

nuevas_celdas.append(code(
"""def ajustar_mogp_y_predecir(kernel_base, nombre_kernel):
    \"\"\"
    Ajusta un MOGP coregionalizado (ICM, GPy) de 2 salidas (EPM Sensor 1, TPM POT(1))
    usando SOLO el tramo pre-brecha de EPM + todo el TPM, y predice la salida EPM en
    toda la linea de tiempo (incluida la brecha real).
    \"\"\"
    icm = GPy.util.multioutput.ICM(input_dim=1, num_outputs=2, kernel=kernel_base.copy())
    modelo = GPy.models.GPCoregionalizedRegression(
        [X_epm_train_b, X_tpm_b], [Y_epm_train_b, Y_tpm_b_std], kernel=icm
    )
    modelo.optimize(messages=False, max_iters=1000)
    print(f"--- {nombre_kernel} ---")
    print(modelo)

    t_min = X_epm_b.min()
    t_max = X_tpm_b.max()
    X_pred = np.linspace(t_min, t_max, 3000).reshape(-1, 1)
    X_pred_epm = np.hstack([X_pred, np.zeros_like(X_pred)])
    noise_dict = {'output_index': X_pred_epm[:, 1:].astype(int)}

    mean_std, var_std = modelo.predict(X_pred_epm, Y_metadata=noise_dict)
    mean = mean_std.flatten() * epm_sigma + epm_mu
    std = np.sqrt(var_std.flatten()) * epm_sigma

    return {
        'nombre': nombre_kernel, 'modelo': modelo,
        't_dias': X_pred.flatten(), 'media': mean, 'std': std,
        'log_likelihood': float(modelo.log_likelihood()),
    }


resultado_rbf = ajustar_mogp_y_predecir(GPy.kern.RBF(input_dim=1), "RBF")
resultado_matern = ajustar_mogp_y_predecir(GPy.kern.Matern32(input_dim=1), "Matern 3/2")

print()
print(f"Log-verosimilitud marginal RBF:        {resultado_rbf['log_likelihood']:.2f}")
print(f"Log-verosimilitud marginal Matern 3/2: {resultado_matern['log_likelihood']:.2f}")
"""
))

nuevas_celdas.append(code(
"""def graficar_reconstruccion(resultado):
    fig, ax = plt.subplots(figsize=(13, 5.5))

    ax.plot((epm_b.loc[mask_epm_train, 'date']), Y_epm_train_b.flatten() * epm_sigma + epm_mu,
            '.', color='steelblue', markersize=3, label='EPM observado (entrenamiento, pre-brecha)')
    ax.plot((epm_b.loc[~mask_epm_train, 'date']), Y_epm_heldout_b.flatten() * epm_sigma + epm_mu,
            '.', color='black', markersize=3,
            label='EPM observado (post-brecha, NO usado para entrenar)')

    fechas_pred = t0_b + pd.to_timedelta(resultado['t_dias'], unit='D')
    ax.plot(fechas_pred, resultado['media'], '-', color='crimson', linewidth=1.5,
            label=f"Media posterior MOGP ({resultado['nombre']})")
    ax.fill_between(fechas_pred, resultado['media'] - 2 * resultado['std'],
                     resultado['media'] + 2 * resultado['std'],
                     color='crimson', alpha=0.2, label='Intervalo ±2σ')

    ax.axvspan(BRECHA_INICIO, BRECHA_FIN, color='gray', alpha=0.15, label='Brecha real (sin datos EPM)')
    ax.set_xlabel('Fecha')
    ax.set_ylabel(f'{EPM_COL_B} [Digits]')
    ax.set_title(f"Reconstruccion preliminar de la brecha -- kernel {resultado['nombre']} "
                 "(generico, sin informacion de Nishihara)")
    ax.legend(loc='upper left', fontsize=8)
    plt.tight_layout()
    plt.show()


graficar_reconstruccion(resultado_rbf)
graficar_reconstruccion(resultado_matern)
"""
))

nuevas_celdas.append(code(
"""# Chequeo cualitativo de consistencia en el borde: ¿la media posterior + IC al final de
# la brecha predicha es compatible con el primer tramo real observado post-brecha?
def chequeo_borde(resultado, dias_borde=15):
    idx_borde = (resultado['t_dias'] >= (BRECHA_FIN - t0_b).total_seconds() / 86400.0) & \\
                (resultado['t_dias'] <= (BRECHA_FIN - t0_b).total_seconds() / 86400.0 + dias_borde)
    media_borde = resultado['media'][idx_borde].mean()
    std_borde = resultado['std'][idx_borde].mean()

    real_borde = Y_epm_heldout_b.flatten()[:50] * epm_sigma + epm_mu  # primeros ~50 puntos post-brecha
    real_media = real_borde.mean()

    dentro_ic = abs(real_media - media_borde) <= 2 * std_borde
    print(f"[{resultado['nombre']}] media predicha en el borde: {media_borde:.2f} ± {2*std_borde:.2f} (2σ) | "
          f"media real observada (primeros ~{len(real_borde)} puntos post-brecha): {real_media:.2f} | "
          f"¿dentro del IC 95%? {'SI' if dentro_ic else 'NO'}")


chequeo_borde(resultado_rbf)
chequeo_borde(resultado_matern)
"""
))

nb['cells'].extend(nuevas_celdas)

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Agregadas {len(nuevas_celdas)} celdas nuevas. Total celdas en el notebook: {len(nb['cells'])}")
