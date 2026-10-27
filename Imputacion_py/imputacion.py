"""
Imputacion de las series EPM con GP univariado y con MOGP-ICM usando las series TPM
mejores y peores segun TE y CCM.

Mismo modelo que `libro 1.ipynb` (celdas 54 y 80): GPy, kernel RBF, ICM de rango 1
(GPy.util.multioutput.ICM), un solo arranque del optimizador, max_iters=1000.
Este archivo NO modifica el libro; reproduce su configuracion en un script aparte.

Diferencias declaradas respecto al libro (decisiones propias):
- La estandarizacion del EPM usa SOLO los datos de entrenamiento. En el libro usa
  todo el EPM (incluido el post-brecha), lo que filtra la media del post-brecha a la
  media del prior.
- Para que el MOGP con varias TPM quepa en memoria, en la brecha real el TPM se toma
  una vez al dia (uno de cada 4 puntos de 6 h). Se hace igual en todas las
  configuraciones para que la comparacion sea justa.

Seleccion de TPM (regla del usuario, 2026-10-26):
- Mejores: TPM significativas en TE (p<0.05) y en CCM (criterios 1, 2 y 3). Si ninguna
  coincide: la mejor de TE + la mejor de CCM. Si solo un metodo da significativas: la
  mejor de ese metodo. Sensor 4: su CCM no se usa (cuantizacion), solo TE.
- Peores: la misma regla al reves. Ninguna TPM es la peor en ambos, asi que se usa la
  peor de TE (mayor p) + la peor de CCM (menor rho). Sensor 4: solo la peor de TE.

Escenarios (ejercicio A = solo el pasado; ejercicio B = tambien el post-brecha):
- 'real': entrena con el EPM previo a la brecha y predice la brecha real (2023-06-20 a
  2025-05-01) y el post-brecha. El EPM post-brecha (no usado al entrenar) sirve de control.
- 'simulada': dentro del tramo previo a la brecha oculta los puntos 200 a 700 del EPM
  (la misma brecha del libro, celda 8) y los predice; mismo hueco para los 4 sensores.
- 'realB': entrena con el EPM de antes y despues de la brecha (post-brecha promediado
  en ventanas de 6 h) y reconstruye la brecha real por interpolacion.
- 'simuladaB': el mismo hueco simulado, entrenando con el resto del pre-brecha y el post.

Ejecutar desde la carpeta Imputacion_py:  python imputacion.py
"""
import json
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
DATOS = AQUI.parent / 'Data_limpia_completa'
SALIDA = AQUI / 'data'
SALIDA.mkdir(exist_ok=True)

BRECHA_INICIO = pd.Timestamp('2023-06-20')
BRECHA_FIN = pd.Timestamp('2025-05-01')
HUECO_INICIO, HUECO_LARGO = 200, 500      # libro 1.ipynb, celda 8
PASO_TPM_REAL = 4                          # 1 de cada 4 puntos de 6 h = 1 por dia
N_GRILLA = 3000                            # libro 1.ipynb, celdas 54 y 80

SELECCION = {
    'Sensor 1 (5m)':  {'mejores': ['POT(4)', 'POT(7)', 'POT(6)'], 'peores': ['Tilt(7)', 'POT(2)']},
    'Sensor 2 (10m)': {'mejores': ['POT(7)'],                     'peores': ['Tilt(6)', 'Tilt(3)']},
    'Sensor 3 (5m)':  {'mejores': ['Tilt(4)'],                    'peores': ['POT(2)', 'POT(5)']},
    'Sensor 4 (10m)': {'mejores': ['Tilt(5)'],                    'peores': ['POT(4)']},
}


def cargar():
    epm = pd.read_csv(DATOS / 'EPM_completo.csv', parse_dates=['date']).sort_values('date')
    tpm = pd.read_csv(DATOS / 'TPM_completo.csv', parse_dates=['date']).sort_values('date')
    return epm, tpm


def a_dias(fechas, t0):
    return ((fechas - t0).dt.total_seconds().values / 86400.0).reshape(-1, 1)


def ajustar(tarea):
    """Una configuracion (sensor, escenario, conjunto). Devuelve metricas y guarda un .npz."""
    import GPy
    epm_col, escenario, conjunto = tarea
    slug = f"{escenario}_{conjunto}_{epm_col}".replace(' ', '_').replace('(', '').replace(')', '')
    archivo = SALIDA / f'{slug}.npz'
    if archivo.exists():
        return json.loads(str(np.load(archivo)['metricas']))

    epm, tpm = cargar()
    t0 = epm['date'].min()
    e = epm[['date', epm_col]].dropna()
    pre = e[e['date'] < BRECHA_INICIO].reset_index(drop=True)

    if escenario == 'real':
        X_tr, Y_tr = a_dias(pre['date'], t0), pre[epm_col].values.reshape(-1, 1)
        post = e[e['date'] >= BRECHA_FIN]
        X_ctrl, Y_ctrl = a_dias(post['date'], t0), post[epm_col].values
        t_fin = a_dias(tpm['date'], t0).max()
        ventana_tpm = (tpm['date'] >= t0)
        paso = PASO_TPM_REAL
    elif escenario == 'simulada':
        oculto = np.zeros(len(pre), dtype=bool)
        oculto[HUECO_INICIO:HUECO_INICIO + HUECO_LARGO] = True
        X_all = a_dias(pre['date'], t0)
        X_tr, Y_tr = X_all[~oculto], pre[epm_col].values[~oculto].reshape(-1, 1)
        X_ctrl, Y_ctrl = X_all[oculto], pre[epm_col].values[oculto]
        t_fin = X_all.max()
        ventana_tpm = (tpm['date'] >= t0) & (tpm['date'] < BRECHA_INICIO)
        paso = 1
    else:
        # Ejercicio B: el EPM post-brecha tambien entra al entrenamiento. Se promedia en
        # ventanas de 6 h (como el pre-brecha, preparar_datos.py) porque se registra mas seguido.
        post = (e[e['date'] >= BRECHA_FIN].set_index('date')[epm_col]
                .resample('6h').mean().dropna().reset_index())
        X_pre, Y_pre = a_dias(pre['date'], t0), pre[epm_col].values
        X_post, Y_post = a_dias(post['date'], t0), post[epm_col].values
        if escenario == 'realB':
            X_tr = np.vstack([X_pre, X_post])
            Y_tr = np.concatenate([Y_pre, Y_post]).reshape(-1, 1)
            X_ctrl, Y_ctrl = X_post, Y_post          # ajuste dentro de la muestra (referencia)
        else:  # 'simuladaB': mismo hueco del pre-brecha, entrenando tambien con el post
            oculto = np.zeros(len(pre), dtype=bool)
            oculto[HUECO_INICIO:HUECO_INICIO + HUECO_LARGO] = True
            X_tr = np.vstack([X_pre[~oculto], X_post])
            Y_tr = np.concatenate([Y_pre[~oculto], Y_post]).reshape(-1, 1)
            X_ctrl, Y_ctrl = X_pre[oculto], Y_pre[oculto]
        t_fin = a_dias(tpm['date'], t0).max()
        ventana_tpm = (tpm['date'] >= t0)
        paso = PASO_TPM_REAL

    mu, sigma = Y_tr.mean(), Y_tr.std()          # solo datos de entrenamiento
    Yn = (Y_tr - mu) / sigma

    series = [] if conjunto == 'univariado' else SELECCION[epm_col][conjunto]
    Xs, Ys = [X_tr], [Yn]
    for s in series:
        ts = tpm.loc[ventana_tpm, ['date', s]].dropna().iloc[::paso]
        y = ts[s].values.reshape(-1, 1)
        Xs.append(a_dias(ts['date'], t0))
        Ys.append((y - y.mean()) / y.std())     # el TPM esta disponible en todo el periodo

    t_ini = time.time()
    if not series:
        modelo = GPy.models.GPRegression(X_tr, Yn, GPy.kern.RBF(input_dim=1))
    else:
        icm = GPy.util.multioutput.ICM(input_dim=1, num_outputs=1 + len(series),
                                       kernel=GPy.kern.RBF(input_dim=1))
        modelo = GPy.models.GPCoregionalizedRegression(Xs, Ys, kernel=icm)
    modelo.optimize(messages=False, max_iters=1000)
    segundos = time.time() - t_ini

    def predecir(X):
        if not series:
            m, v = modelo.predict(X)
        else:
            Xe = np.hstack([X, np.zeros_like(X)])
            m, v = modelo.predict(Xe, Y_metadata={'output_index': Xe[:, 1:].astype(int)})
        return m.flatten() * sigma + mu, np.sqrt(v.flatten()) * sigma

    X_grid = np.linspace(X_tr.min(), t_fin, N_GRILLA).reshape(-1, 1)
    m_grid, s_grid = predecir(X_grid)
    m_ctrl, s_ctrl = predecir(X_ctrl)

    # varianza del prior (lejos de los datos): varianza del kernel del EPM + ruido
    if not series:
        var_k = float(modelo.kern.variance)
        var_n = float(modelo.likelihood.variance)
    else:
        B = modelo.kern.B.B
        var_k = float(modelo.kern.parts[0].variance) * float(B[0, 0])
        var_n = float(modelo.likelihood.likelihoods_list[0].variance)
    std_prior = np.sqrt(var_k + var_n) * sigma

    err = m_ctrl - Y_ctrl
    met = {
        'EPM': epm_col, 'escenario': escenario, 'conjunto': conjunto, 'TPM': ', '.join(series),
        'n_entrenamiento_epm': int(len(X_tr)), 'n_control': int(len(X_ctrl)),
        'RMSE': float(np.sqrt(np.mean(err ** 2))), 'MAE': float(np.mean(np.abs(err))),
        'cobertura_95': float(np.mean(np.abs(err) <= 1.96 * s_ctrl)),
        'std_media_control': float(np.mean(s_ctrl)),
        'media_prior': float(mu), 'std_prior': float(std_prior),
        'log_verosimilitud': float(modelo.log_likelihood()), 'segundos': round(segundos, 1),
    }
    if escenario in ('real', 'realB'):
        en_brecha = (X_grid[:, 0] >= a_dias(pd.Series([BRECHA_INICIO]), t0)[0, 0]) & \
                    (X_grid[:, 0] < a_dias(pd.Series([BRECHA_FIN]), t0)[0, 0])
        met['std_media_brecha'] = float(np.mean(s_grid[en_brecha]))
    np.savez(archivo, t_dias=X_grid.flatten(), media=m_grid, std=s_grid,
             t_ctrl=X_ctrl.flatten(), y_ctrl=Y_ctrl, m_ctrl=m_ctrl, s_ctrl=s_ctrl,
             metricas=json.dumps(met), t0=str(t0))
    print(f"{slug}: {segundos:.0f} s  RMSE={met['RMSE']:.2f}  cobertura={met['cobertura_95']:.2f}", flush=True)
    return met


if __name__ == '__main__':
    import sys
    tareas = [(e, esc, c) for esc in ('simulada', 'real', 'simuladaB', 'realB') for e in SELECCION
              for c in ('univariado', 'mejores', 'peores')]
    if len(sys.argv) > 1 and sys.argv[1] == 'prueba':
        tareas = [('Sensor 3 (5m)', 'simulada', 'mejores')]
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(ajustar, tareas))
    pd.DataFrame(res).to_csv(SALIDA / 'metricas_imputacion.csv', index=False)
    print('Guardado:', SALIDA / 'metricas_imputacion.csv')
