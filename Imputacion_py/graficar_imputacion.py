"""
Figuras de las imputaciones (lee los .npz de imputacion.py; no ajusta ningun modelo).

Salida en figuras/:
- prior_<sensor>.png       GP univariado en la brecha real con la media y la banda del prior
- real_<sensor>.png        brecha real: univariado, mejores y peores
- simulada_<sensor>.png    brecha simulada: univariado, mejores y peores

Ejecutar desde la carpeta Imputacion_py:  python graficar_imputacion.py
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from imputacion import (BRECHA_FIN, BRECHA_INICIO, DATOS, HUECO_INICIO, HUECO_LARGO,
                        SELECCION)

AQUI = Path(__file__).resolve().parent
DATA = AQUI / 'data'
FIG = AQUI / 'figuras'
FIG.mkdir(exist_ok=True)
COLOR = {'univariado': 'tab:gray', 'mejores': 'tab:blue', 'peores': 'tab:red'}
TITULO = {'univariado': 'GP univariado (solo el EPM, sin TPM)',
          'mejores': 'MOGP con las TPM mejores', 'peores': 'MOGP con las TPM peores'}

epm = pd.read_csv(DATOS / 'EPM_completo.csv', parse_dates=['date']).sort_values('date')


def cargar(escenario, conjunto, sensor):
    slug = f"{escenario}_{conjunto}_{sensor}".replace(' ', '_').replace('(', '').replace(')', '')
    d = np.load(DATA / f'{slug}.npz')
    t0 = pd.Timestamp(str(d['t0']))
    r = {k: d[k] for k in ('t_dias', 'media', 'std', 't_ctrl', 'y_ctrl', 'm_ctrl', 's_ctrl')}
    r['fechas'] = t0 + pd.to_timedelta(r['t_dias'], unit='D')
    r['fechas_ctrl'] = t0 + pd.to_timedelta(r['t_ctrl'], unit='D')
    r['met'] = json.loads(str(d['metricas']))
    return r


def nombre_archivo(sensor):
    return sensor.replace(' ', '_').replace('(', '').replace(')', '')


for sensor in SELECCION:
    e = epm[['date', sensor]].dropna()
    pre = e[e['date'] < BRECHA_INICIO]
    post = e[e['date'] >= BRECHA_FIN]

    # --- 1. Convergencia al prior (GP univariado, brecha real) ---
    r = cargar('real', 'univariado', sensor)
    mu, sp = r['met']['media_prior'], r['met']['std_prior']
    fig, ax = plt.subplots(figsize=(10, 4.2), constrained_layout=True)
    ax.axvspan(BRECHA_INICIO, BRECHA_FIN, color='0.9', label='Brecha real')
    ax.plot(pre['date'], pre[sensor], '.', ms=2, color='steelblue', label='EPM observado (entrenamiento)')
    ax.plot(post['date'], post[sensor], '.', ms=1, color='k', label='EPM post-brecha (no usado)')
    ax.plot(r['fechas'], r['media'], color='crimson', lw=1.4, label='Media posterior')
    ax.fill_between(r['fechas'], r['media'] - 2 * r['std'], r['media'] + 2 * r['std'],
                    color='crimson', alpha=0.2, label='Media ± 2σ posterior')
    ax.axhline(mu, color='darkgreen', ls='--', lw=1.2, label=f'Media del prior = {mu:.1f}')
    for s in (-2, 2):
        ax.axhline(mu + s * sp, color='darkgreen', ls=':', lw=1.2,
                   label=f'Media del prior ± 2σ prior (σ = {sp:.1f})' if s == 2 else None)
    ax.set_ylabel(f'{sensor} [Digits]')
    ax.set_title(f'{sensor}: GP univariado (RBF) en la brecha real', fontsize=11)
    ax.legend(fontsize=7, loc='best', ncol=2)
    fig.savefig(FIG / f'prior_{nombre_archivo(sensor)}.png', dpi=180)
    plt.close(fig)

    # --- 2. Brecha real: tres modelos ---
    res = {c: cargar('real', c, sensor) for c in ('univariado', 'mejores', 'peores')}
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, sharey=True, constrained_layout=True)
    for ax, (c, r) in zip(axs, res.items()):
        m = r['met']
        ax.axvspan(BRECHA_INICIO, BRECHA_FIN, color='0.9')
        ax.plot(pre['date'], pre[sensor], '.', ms=1.5, color='steelblue')
        ax.plot(post['date'], post[sensor], '.', ms=1, color='k')
        ax.plot(r['fechas'], r['media'], color=COLOR[c], lw=1.3)
        ax.fill_between(r['fechas'], r['media'] - 2 * r['std'], r['media'] + 2 * r['std'],
                        color=COLOR[c], alpha=0.25)
        tpm = f" ({m['TPM']})" if m['TPM'] else ''
        ax.set_title(f"{TITULO[c]}{tpm}.  σ media en la brecha = {m['std_media_brecha']:.1f}.  "
                     f"Post-brecha: RMSE = {m['RMSE']:.1f}, cobertura 95 % = {100 * m['cobertura_95']:.0f} %",
                     fontsize=9, loc='left')
        ax.set_ylabel('[Digits]')
    fig.suptitle(f'{sensor}: brecha real (gris). Azul: entrenamiento; negro: post-brecha no usado', fontsize=10)
    fig.savefig(FIG / f'real_{nombre_archivo(sensor)}.png', dpi=180)
    plt.close(fig)

    # --- 3. Brecha simulada: tres modelos ---
    res = {c: cargar('simulada', c, sensor) for c in ('univariado', 'mejores', 'peores')}
    pre = pre.reset_index(drop=True)
    ini, fin = pre['date'].iloc[HUECO_INICIO], pre['date'].iloc[HUECO_INICIO + HUECO_LARGO - 1]
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, sharey=True, constrained_layout=True)
    for ax, (c, r) in zip(axs, res.items()):
        m = r['met']
        ax.axvspan(ini, fin, color='0.9')
        oculto = pre.index.isin(range(HUECO_INICIO, HUECO_INICIO + HUECO_LARGO))
        ax.plot(pre.loc[~oculto, 'date'], pre.loc[~oculto, sensor], '.', ms=2, color='steelblue')
        ax.plot(pre.loc[oculto, 'date'], pre.loc[oculto, sensor], '.', ms=2, color='k')
        ax.plot(r['fechas'], r['media'], color=COLOR[c], lw=1.3)
        ax.fill_between(r['fechas'], r['media'] - 2 * r['std'], r['media'] + 2 * r['std'],
                        color=COLOR[c], alpha=0.25)
        tpm = f" ({m['TPM']})" if m['TPM'] else ''
        ax.set_title(f"{TITULO[c]}{tpm}.  En el hueco: RMSE = {m['RMSE']:.2f}, "
                     f"cobertura 95 % = {100 * m['cobertura_95']:.0f} %, σ media = {m['std_media_control']:.2f}",
                     fontsize=9, loc='left')
        ax.set_ylabel('[Digits]')
    fig.suptitle(f'{sensor}: brecha simulada (gris, 500 pasos de 6 h). Negro: valores ocultos', fontsize=10)
    fig.savefig(FIG / f'simulada_{nombre_archivo(sensor)}.png', dpi=180)
    plt.close(fig)

    # --- 4. Ejercicio B, brecha real: entrenando con pre y post ---
    post6 = post.set_index('date')[sensor].resample('6h').mean().dropna()
    res = {c: cargar('realB', c, sensor) for c in ('univariado', 'mejores', 'peores')}
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, sharey=True, constrained_layout=True)
    for ax, (c, r) in zip(axs, res.items()):
        m = r['met']
        ax.axvspan(BRECHA_INICIO, BRECHA_FIN, color='0.9')
        ax.plot(pre['date'], pre[sensor], '.', ms=1.5, color='steelblue')
        ax.plot(post6.index, post6.values, '.', ms=1.5, color='steelblue')
        ax.plot(r['fechas'], r['media'], color=COLOR[c], lw=1.3)
        ax.fill_between(r['fechas'], r['media'] - 2 * r['std'], r['media'] + 2 * r['std'],
                        color=COLOR[c], alpha=0.25)
        tpm = f" ({m['TPM']})" if m['TPM'] else ''
        ax.set_title(f"{TITULO[c]}{tpm}.  σ media en la brecha = {m['std_media_brecha']:.2f} Digits",
                     fontsize=9, loc='left')
        ax.set_ylabel('[Digits]')
    fig.suptitle(f'{sensor}: reconstrucción de la brecha real (gris) entrenando con el EPM de antes y después (azul)',
                 fontsize=10)
    fig.savefig(FIG / f'realB_{nombre_archivo(sensor)}.png', dpi=180)
    plt.close(fig)

    # --- 5. Ejercicio B, brecha simulada (vista del tramo previo a la brecha) ---
    res = {c: cargar('simuladaB', c, sensor) for c in ('univariado', 'mejores', 'peores')}
    fig, axs = plt.subplots(3, 1, figsize=(10, 7.2), sharex=True, sharey=True, constrained_layout=True)
    for ax, (c, r) in zip(axs, res.items()):
        m = r['met']
        ax.axvspan(ini, fin, color='0.9')
        oculto = pre.index.isin(range(HUECO_INICIO, HUECO_INICIO + HUECO_LARGO))
        ax.plot(pre.loc[~oculto, 'date'], pre.loc[~oculto, sensor], '.', ms=2, color='steelblue')
        ax.plot(pre.loc[oculto, 'date'], pre.loc[oculto, sensor], '.', ms=2, color='k')
        ver = r['fechas'] < BRECHA_INICIO
        ax.plot(r['fechas'][ver], r['media'][ver], color=COLOR[c], lw=1.3)
        ax.fill_between(r['fechas'][ver], (r['media'] - 2 * r['std'])[ver], (r['media'] + 2 * r['std'])[ver],
                        color=COLOR[c], alpha=0.25)
        tpm = f" ({m['TPM']})" if m['TPM'] else ''
        ax.set_title(f"{TITULO[c]}{tpm}.  En el hueco: RMSE = {m['RMSE']:.2f}, "
                     f"cobertura 95 % = {100 * m['cobertura_95']:.0f} %, σ media = {m['std_media_control']:.2f}",
                     fontsize=9, loc='left')
        ax.set_ylabel('[Digits]')
    fig.suptitle(f'{sensor}: brecha simulada, entrenando también con el post-brecha (no se muestra). Negro: ocultos',
                 fontsize=10)
    fig.savefig(FIG / f'simuladaB_{nombre_archivo(sensor)}.png', dpi=180)
    plt.close(fig)

print('Figuras en', FIG)
