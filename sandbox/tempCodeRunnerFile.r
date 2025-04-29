
# PRAKTIKUM 9 - ANALISIS BIPLOT DENGAN PCA
# Nama : ____________________
# NIM  : ____________________

# 1. Instalasi dan Load Paket
# (jika belum terinstal sekali saja)
install.packages(c("FactoMineR", "factoextra"))

# Load library
library(FactoMineR)
library(factoextra)

# 2. Baca Dataset
data_path <- "C:/Users/Hp/Downloads/ocean_plastic_pollution_data.csv"
data <- read.csv(data_path, header = TRUE, sep = ",")



# 6. Melakukan PCA
hasil_pca <- prcomp(data_num, scale. = TRUE)
# Tampilkan ringkasan hasil PCA
print(hasil_pca)
summary(hasil_pca)
