# Transfer entropy entre las 14 series TPM y los 4 sensores EPM (56 pares)
#
# Metodo: Behrendt, Dimpfl, Peter y Zimmermann (2019). RTransferEntropy --
# Quantifying information flow between different time series using effective
# transfer entropy. SoftwareX 10, 100265. Paquete RTransferEntropy, con todos
# sus valores por defecto:
#   - TE de Shannon (sec. 2.1, ec. 3; Schreiber 2000).
#   - Historia lx = ly = 1 (sec. 3: elegirla "is a non-trivial task" y el
#     paquete no impone un algoritmo -> limitacion declarada).
#   - Discretizacion por cuantiles 5 % y 95 % -> 3 bins (sec. 2.2, ec. 6).
#   - TE efectiva: TE menos el promedio de 100 TE con la fuente barajada
#     (sec. 2.2, ec. 5; Marschinski y Kantz 2002).
#   - Significancia: 300 replicas de bootstrap de bloques de Markov, que
#     conservan la dinamica de cada serie y destruyen la relacion entre ellas;
#     p = 1 - q (sec. 2.2; Dimpfl y Peter 2013).
#   - Filas con NA en cualquiera de las dos series se eliminan (codigo del paquete).
#
# El paquete calcula las dos direcciones:
#   X -> Y = TPM -> EPM (direccion de interes)
#   Y -> X = EPM -> TPM (direccion contraria)
#
# Entrada : data/series_diferencias_6h.csv  (generado por preparar_datos.py)
# Salida  : data/te_resultados_56_pares.csv
# Ejecutar desde la carpeta TE_R:  Rscript te_56_pares.R

library(RTransferEntropy)

SEMILLA <- 2026   # solo para reproducibilidad del barajado y del bootstrap

series_tpm <- c("POT(1)", "POT(2)", "POT(3)", "POT(4)", "POT(5)", "POT(6)", "POT(7)",
                "Tilt(1)", "Tilt(2)", "Tilt(3)", "Tilt(4)", "Tilt(5)", "Tilt(6)", "Tilt(7)")
series_epm <- c("Sensor 1 (5m)", "Sensor 2 (10m)", "Sensor 3 (5m)", "Sensor 4 (10m)")

d <- read.csv("data/series_diferencias_6h.csv", check.names = FALSE)

filas <- list()
inicio <- Sys.time()
for (epm in series_epm) {
  for (tpm in series_tpm) {
    r <- transfer_entropy(x = d[[tpm]], y = d[[epm]], seed = SEMILLA, quiet = TRUE)
    filas[[length(filas) + 1]] <- data.frame(
      TPM = tpm, EPM = epm, n_obs = r$nobs,
      te_tpm_a_epm  = r$coef["X->Y", "te"],
      ete_tpm_a_epm = r$coef["X->Y", "ete"],
      se_tpm_a_epm  = r$coef["X->Y", "se"],
      p_tpm_a_epm   = r$coef["X->Y", "p-value"],
      te_epm_a_tpm  = r$coef["Y->X", "te"],
      ete_epm_a_tpm = r$coef["Y->X", "ete"],
      se_epm_a_tpm  = r$coef["Y->X", "se"],
      p_epm_a_tpm   = r$coef["Y->X", "p-value"],
      check.names = FALSE
    )
    cat(sprintf("%-8s -> %-15s  p(TPM->EPM) = %.3f   p(EPM->TPM) = %.3f\n",
                tpm, epm, r$coef["X->Y", "p-value"], r$coef["Y->X", "p-value"]))
  }
}
resultados <- do.call(rbind, filas)
write.csv(resultados, "data/te_resultados_56_pares.csv", row.names = FALSE)

cat("\nTiempo total:", format(Sys.time() - inicio), "\n")
cat("Pares con p < 0.05, TPM -> EPM:", sum(resultados$p_tpm_a_epm < 0.05), "de 56\n")
cat("Pares con p < 0.05, EPM -> TPM:", sum(resultados$p_epm_a_tpm < 0.05), "de 56\n")
cat("Esperado por azar en cada direccion: 56 x 0.05 =", 56 * 0.05, "\n")
cat("Guardado: data/te_resultados_56_pares.csv\n")
