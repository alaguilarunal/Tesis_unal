"""
Edita in-place dos celdas de libro 1.ipynb (por 'id', no por indice):

- celda id=cbb50dcc ("EPM_COL_B = ...") -- recorta X_tpm_b a la ventana donde el EPM
  tiene datos (>= t0_b), en vez de usar los ~8 anios completos de TPM. Esto es lo que
  bajaba N de 10,640 a un numero manejable (causa de fondo del MemoryError).

- celda id=3ecd1830 (def ajustar_mogp_y_predecir + llamadas) -- cachea el resultado
  liviano (t_dias, media, std, log_likelihood) en models/resultado_<kernel>.npz, y deja
  de retener el objeto GPy completo ('modelo') en el dict de retorno (eso fue lo que
  hizo fallar por memoria la segunda llamada la primera vez que se corrio esto).
"""
import json
from pathlib import Path

NB_PATH = Path("libro 1.ipynb")

with open(NB_PATH, encoding="utf-8") as f:
    nb = json.load(f)

CELDA_VENTANA_ID = "cbb50dcc"
CELDA_CACHE_ID = "3ecd1830"

nueva_fuente_ventana = '''EPM_COL_B = 'Sensor 1 (5m)'
TPM_COL_B = 'POT(1)'
BRECHA_INICIO = pd.Timestamp("2023-06-20")
BRECHA_FIN = pd.Timestamp("2025-05-01")

t0_b = epm_ext['date'].min()

def a_dias(fechas):
    return (fechas - t0_b).dt.total_seconds().values / 86400.0

epm_b = epm_ext[['date', EPM_COL_B]].dropna().sort_values('date').reset_index(drop=True)

# El TPM crudo cubre 2017-2025 (~8 anios), pero solo la ventana donde el EPM tiene datos
# (pre-brecha + brecha + post-brecha) aporta informacion util para este ajuste. Sin este
# recorte, X_tpm_b tenia ~10,379 puntos y el MOGP necesitaba una matriz de covarianza de
# 10,640 x 10,640 (~864 MiB solo para una de las matrices intermedias) -- causo el
# MemoryError de la primera corrida.
tpm_b = tpm_ext[['date', TPM_COL_B]].dropna()
tpm_b = tpm_b[tpm_b['date'] >= t0_b].sort_values('date').reset_index(drop=True)

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
print(f"TPM recortado a >= {t0_b.date()} (pre+durante+post brecha): {len(X_tpm_b)} puntos "
      f"(antes del recorte: {tpm_ext[TPM_COL_B].notna().sum()} puntos en todo el historico desde "
      f"{tpm_ext['date'].min().date()})")
'''

nueva_fuente_cache = '''from pathlib import Path

MODELOS_DIR = Path("models")
MODELOS_DIR.mkdir(exist_ok=True)


def ajustar_mogp_y_predecir(kernel_base, nombre_kernel):
    """
    Ajusta un MOGP coregionalizado (ICM, GPy) de 2 salidas (EPM Sensor 1, TPM POT(1))
    usando SOLO el tramo pre-brecha de EPM + todo el TPM recortado a la ventana relevante,
    y predice la salida EPM en toda la linea de tiempo (incluida la brecha real).

    Cachea el resultado liviano (t_dias, media, std, log_likelihood) en
    models/resultado_<kernel>.npz -- el ajuste (modelo.optimize) es la parte costosa
    (minutos); si el cache ya existe, se carga directo y no se vuelve a entrenar.
    El objeto GPy completo ('modelo') NO se guarda ni se retiene en memoria despues de
    predecir -- mantenerlo vivo fue lo que hizo fallar por memoria la segunda llamada
    (RBF seguido de Matern) la primera vez que se corrio esto.
    """
    nombre_archivo = nombre_kernel.replace(' ', '_').replace('/', '-')
    cache_path = MODELOS_DIR / f"resultado_{nombre_archivo}.npz"

    if cache_path.exists():
        datos = np.load(cache_path)
        print(f"--- {nombre_kernel} (cargado desde cache: {cache_path}) ---")
        return {
            'nombre': nombre_kernel,
            't_dias': datos['t_dias'], 'media': datos['media'], 'std': datos['std'],
            'log_likelihood': float(datos['log_likelihood']),
        }

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
    log_likelihood = float(modelo.log_likelihood())

    np.savez(cache_path, t_dias=X_pred.flatten(), media=mean, std=std,
             log_likelihood=log_likelihood)
    print(f"Resultado guardado en {cache_path}")

    del modelo  # ver docstring -- no se retiene el objeto GPy completo

    return {
        'nombre': nombre_kernel,
        't_dias': X_pred.flatten(), 'media': mean, 'std': std,
        'log_likelihood': log_likelihood,
    }


resultado_rbf = ajustar_mogp_y_predecir(GPy.kern.RBF(input_dim=1), "RBF")
resultado_matern = ajustar_mogp_y_predecir(GPy.kern.Matern32(input_dim=1), "Matern 3/2")

print()
print(f"Log-verosimilitud marginal RBF:        {resultado_rbf['log_likelihood']:.2f}")
print(f"Log-verosimilitud marginal Matern 3/2: {resultado_matern['log_likelihood']:.2f}")
'''

encontrados = {"ventana": False, "cache": False}
for cell in nb['cells']:
    if cell.get('id') == CELDA_VENTANA_ID:
        cell['source'] = nueva_fuente_ventana.splitlines(keepends=True)
        cell['outputs'] = []
        cell['execution_count'] = None
        encontrados['ventana'] = True
    elif cell.get('id') == CELDA_CACHE_ID:
        cell['source'] = nueva_fuente_cache.splitlines(keepends=True)
        cell['outputs'] = []
        cell['execution_count'] = None
        encontrados['cache'] = True

assert all(encontrados.values()), f"No se encontraron todas las celdas: {encontrados}"

with open(NB_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("Celdas actualizadas:", encontrados)
