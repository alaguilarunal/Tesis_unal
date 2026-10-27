# Genera ejemplos de sustitutos con las funciones internas de RTransferEntropy 0.2.21
# (las mismas que usa transfer_entropy()). Solo para ilustrar la guia.
library(RTransferEntropy)
ns <- asNamespace("RTransferEntropy")
set.seed(2026)
d <- read.csv("../TE_R/data/series_diferencias_6h.csv", check.names = FALSE)
ok <- !(is.na(d[["Tilt(5)"]]) | is.na(d[["Sensor 4 (10m)"]]))
tpm <- d[["Tilt(5)"]][ok]; epm <- d[["Sensor 4 (10m)"]][ok]
code <- get("code_sample", ns); boot <- get("markov_boot_step", ns)
tpm_s <- code(tpm); epm_s <- code(epm)
out <- data.frame(t = seq_along(tpm), tpm = tpm, tpm_barajado = sample(tpm, length(tpm), replace = TRUE),
                  epm_simbolos = epm_s, epm_markov = boot(epm_s, 1, 50))
write.csv(out, "figuras/sustitutos_ejemplo.csv", row.names = FALSE)
cat("cuantiles 5% y 95% del EPM S4:", quantile(epm, c(.05,.95), type = 8), "\n")
print(table(epm_s)); print(table(out$epm_markov))
