# ========================================== #
# ANALISIS BIPLOT - DATA SAMPAH PLASTIK LAUT #
# ========================================== #

install.packages(c("FactoMineR", "factoextra", "readr"))

library(FactoMineR)
library(factoextra)
library(readr)

data <- read.csv("C:/Users/Hp/Downloads/ocean_plastic_pollution_data.csv")

cat("\n[Data Pertama]\n")
print(head(data))

set.seed(123)
sample_data <- data[sample(nrow(data), 50), ]
numeric_columns <- sapply(sample_data, is.numeric)
datacolumns <- sample_data[, numeric_columns]

cat("\n[Kolom Numerik yang Digunakan]\n")
print(colnames(datacolumns))

hasil_pca <- prcomp(datacolumns, scale = TRUE)

cat("\n[Analisis PCA]\n")
print(summary(hasil_pca))

cat("\n[Visualisasi Eigenvalues]\n")
fviz_eig(hasil_pca, addlabels = TRUE, linecolor = "red", barfill = "steelblue", main = "Scree Plot - Pemilihan Komponen Utama")

cat("\n[Visualisasi Biplot]\n")
biplot <- fviz_pca_biplot(hasil_pca,
                          repel = TRUE,
                          col.var = "#2E9FDF",
                          col.ind = "#696969",
                          gradient.cols = c("#00AFBB", "#E7B800", "#FC4E07"),
                          title = "Biplot - Analisis Sampah Plastik Laut")

print(biplot)
