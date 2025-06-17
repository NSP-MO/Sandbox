# Pastikan package dplyr, caret, class, reshape2, dan ggplot2 terpasang
if (!require(dplyr)) install.packages("dplyr", quiet = TRUE)
if (!require(caret)) install.packages("caret", quiet = TRUE)
if (!require(class)) install.packages("class", quiet = TRUE)
if (!require(reshape2)) install.packages("reshape2", quiet = TRUE)
if (!require(ggplot2)) install.packages("ggplot2", quiet = TRUE)

library(caret)
library(class)
library(dplyr)
library(ggplot2)
library(reshape2)

data_path <- "C:\\Users\\Hp\\Downloads\\alzheimers_disease_data.csv"
alz_data <- read.csv(data_path, stringsAsFactors = FALSE)

# Pra-pemrosesan Data
# Hapus kolom PatientID jika ada
if ("PatientID" %in% names(alz_data)) {
  alz_data$PatientID <- NULL
}

# Konversi Gender
if ("Gender" %in% names(alz_data)) {
  alz_data$Gender <- ifelse(alz_data$Gender == "Male", 1, 0)
}

# Konversi Ethnicity menjadi faktor dan melakukan one-hot encoding
if ("Ethnicity" %in% names(alz_data)) {
  cat("Nilai unik Ethnicity awal:\n")
  print(head(unique(alz_data$Ethnicity)))
  cat("Jumlah NA di Ethnicity sebelum diproses:", sum(is.na(alz_data$Ethnicity)), "\n")
  
  alz_data$Ethnicity <- as.character(alz_data$Ethnicity)
  alz_data$Ethnicity[is.na(alz_data$Ethnicity) | alz_data$Ethnicity == "" | trimws(alz_data$Ethnicity) == ""] <- "Unknown_Ethnicity"
  alz_data$Ethnicity <- factor(alz_data$Ethnicity)
  
  cat("Nilai unik Ethnicity setelah penanganan NA (sebagai factor):\n")
  print(levels(alz_data$Ethnicity))
  
  if (length(levels(alz_data$Ethnicity)) > 0 && nrow(alz_data) > 0) {
    ethnicity_dummies <- NULL
    tryCatch({
      ethnicity_dummies <- model.matrix(~ Ethnicity - 1, data = alz_data)
    }, error = function(e) {
      warning(paste("Terjadi kesalahan pada model.matrix untuk Ethnicity:", e$message))
    })
    
    if (!is.null(ethnicity_dummies) && nrow(ethnicity_dummies) == nrow(alz_data)) {
      alz_data <- cbind(alz_data, ethnicity_dummies)
      alz_data$Ethnicity <- NULL 
      cat("One-hot encoding untuk Ethnicity berhasil.\n")
    } else if (!is.null(ethnicity_dummies)) {
      warning(paste("Jumlah baris tidak cocok untuk Ethnicity. nrow(alz_data):", nrow(alz_data), "nrow(dummies):", nrow(ethnicity_dummies)))
      alz_data$Ethnicity <- NULL
    } else {
      warning("model.matrix untuk Ethnicity menghasilkan NULL.")
      alz_data$Ethnicity <- NULL
    }
  } else {
    warning("Kolom Ethnicity tidak memiliki level atau data kosong. One-hot encoding dilewati.")
    alz_data$Ethnicity <- NULL
  }
} else {
  warning("Kolom Ethnicity tidak ditemukan.")
}

# Konversi EducationLevel
if ("EducationLevel" %in% names(alz_data)) {
  cat("Nilai unik EducationLevel (perlakuan sebagai numeric ordinal):\n")
  print(head(unique(alz_data$EducationLevel)))
  alz_data$EducationLevel <- as.numeric(as.character(alz_data$EducationLevel))
} else {
  warning("Kolom EducationLevel tidak ditemukan.")
}

# Konversi kolom biner
binary_cols <- c("Smoking", "FamilyHistoryAlzheimers", "CardiovascularDisease", "Diabetes")
for (col in binary_cols) {
  if (col %in% names(alz_data)) {
    cat("Nilai unik di kolom", col, "(asumsi sudah 0/1):\n")
    print(head(unique(alz_data[[col]])))
    alz_data[[col]] <- as.numeric(as.character(alz_data[[col]]))
  } else {
    warning(paste("Kolom", col, "tidak ditemukan untuk konversi biner."))
  }
}

# Perlakuan terhadap beberapa kolom sebagai numeric continu
continuous_cols_to_treat_as_numeric <- c("AlcoholConsumption", "PhysicalActivity", "DietQuality", "SleepQuality")
for(col_name in continuous_cols_to_treat_as_numeric){
  if (col_name %in% names(alz_data)) {
    cat("Nilai unik", col_name, "sebelum konversi (perlakuan numeric):\n")
    print(head(unique(alz_data[[col_name]])))
    alz_data[[col_name]] <- as.numeric(as.character(alz_data[[col_name]]))
  } else {
    warning(paste("Kolom", col_name, "tidak ditemukan."))
  }
}

# Konversi Diagnosis (sebagai target)
if ("Diagnosis" %in% names(alz_data)) {
  cat("--- Nilai Diagnosis sebelum konversi factor (harusnya 0/1) ---\n")
  print(table(alz_data$Diagnosis, useNA = "ifany"))
  
  diagnosis_values <- as.numeric(as.character(alz_data$Diagnosis))
  
  if(any(is.na(diagnosis_values[!is.na(alz_data$Diagnosis)]))) {
    warning("Terdapat NA yang tak terduga saat konversi Diagnosis ke numeric.")
  }
  if(all(is.na(diagnosis_values[!is.na(alz_data$Diagnosis)])) && sum(!is.na(alz_data$Diagnosis)) > 0) {
    warning("Semua nilai Diagnosis non-NA menjadi NA. Mungkin bukan 0/1.")
  }
  
  cat("--- Diagnosis setelah konversi numeric, sebelum factor ---\n")
  print(table(diagnosis_values, useNA="ifany"))
  
  alz_data$Diagnosis <- factor(diagnosis_values, levels = c(0, 1))
  
  cat("--- Diagnosis sebagai factor ---\n")
  print(table(alz_data$Diagnosis, useNA = "ifany"))
  cat("Level Diagnosis:", paste(levels(alz_data$Diagnosis), collapse=", "), "\n")
} else {
  stop("Kolom Diagnosis tidak ditemukan. Proses dihentikan.")
}

# Cek NA dan hilangkan baris NA
cat("Jumlah NA per kolom setelah semua konversi:\n")
print(sapply(alz_data, function(x) sum(is.na(x))))

original_rows <- nrow(alz_data)
if (original_rows > 0) { 
  alz_data <- na.omit(alz_data) 
  cat("Baris sebelum na.omit:", original_rows, "\nBaris setelah na.omit:", nrow(alz_data), "\n")
} else {
  cat("Data kosong sebelum na.omit. Jumlah baris:", original_rows, "\n")
}

data_processed <- alz_data

# Periksa Diagnosis setelah na.omit
if ("Diagnosis" %in% names(data_processed)) {
  cat("--- Diagnosis setelah na.omit ---\n")
  print(table(data_processed$Diagnosis, useNA = "ifany"))
  cat("Level Diagnosis di data_processed:", paste(levels(data_processed$Diagnosis), collapse=", "), "\n")
  cat("Jumlah nilai unik non-NA di Diagnosis:", length(unique(na.omit(data_processed$Diagnosis))), "\n")
}

# Normalisasi fitur numerik
if (nrow(data_processed) > 0) {
  cols_to_normalize <- names(data_processed)[sapply(data_processed, is.numeric)]
  
  ethnicity_dummy_patterns <- names(data_processed)[grep(paste0("^","Ethnicity"), names(data_processed))]
  actual_ethnicity_dummies_in_data <- intersect(ethnicity_dummy_patterns, names(data_processed)[sapply(data_processed, is.numeric)])
  cols_to_normalize <- setdiff(cols_to_normalize, actual_ethnicity_dummies_in_data)
  
  if(length(cols_to_normalize) > 0 ) {
    cat("Kolom yang akan dinormalisasi:", paste(cols_to_normalize, collapse=", "), "\n")
    col_variances <- sapply(data_processed[, cols_to_normalize, drop = FALSE], var, na.rm = TRUE)
    cols_with_variation <- names(col_variances[!is.na(col_variances) & col_variances > 0])
    
    if(length(cols_with_variation) > 0) {
      cat("Kolom yang benar-benar dinormalisasi (punya variasi):", paste(cols_with_variation, collapse=", "), "\n")
      preProcValues <- preProcess(data_processed[, cols_with_variation, drop = FALSE], method = c("range"))
      data_processed_normalized_part <- predict(preProcValues, data_processed[, cols_with_variation, drop = FALSE])
      
      data_processed_other_part <- data_processed[, !(names(data_processed) %in% cols_with_variation), drop = FALSE]
      data_processed <- cbind(data_processed_normalized_part, data_processed_other_part)
      cat("Normalisasi selesai.\n")
    } else {
      cat("Tidak ada kolom dengan variasi untuk dinormalisasi.\n")
    }
  } else {
    cat("Tidak ada kolom yang perlu dinormalisasi.\n")
  }
  
  if("Diagnosis" %in% names(data_processed) && is.factor(data_processed$Diagnosis)) { 
    diagnosis_col <- data_processed$Diagnosis
    cols_without_diagnosis <- setdiff(names(data_processed), "Diagnosis")
    data_processed <- data_processed[, c(cols_without_diagnosis, "Diagnosis"), drop = FALSE]
  }
} else {
  cat("data_processed kosong sebelum normalisasi. Proses selanjutnya dilewati.\n")
}

# Pembagian data latih dan uji
if (nrow(data_processed) == 0) {
  stop("data_processed kosong setelah pra-pemrosesan. Tidak dapat melanjutkan.")
}
if (!("Diagnosis" %in% names(data_processed))) {
  stop("Kolom Diagnosis hilang di data_processed.")
}
if ((is.factor(data_processed$Diagnosis) && length(levels(data_processed$Diagnosis)) < 2) ||
    (!is.factor(data_processed$Diagnosis) && length(unique(na.omit(as.character(data_processed$Diagnosis)))) < 2)) {
  stop("Kolom Diagnosis harus punya minimal dua kelas unik.")
}

set.seed(123)
trainIndex <- createDataPartition(data_processed$Diagnosis, p = .8, list = FALSE, times = 1)
train_data <- data_processed[trainIndex, ]
test_data <- data_processed[-trainIndex, ]

train_features <- train_data[, -which(names(train_data) == "Diagnosis"), drop = FALSE]
train_target <- train_data$Diagnosis
test_features <- test_data[, -which(names(test_data) == "Diagnosis"), drop = FALSE]
test_target <- test_data$Diagnosis

# Penerapan PCA pada data latih
train_pca <- NULL
test_pca <- NULL

if(nrow(train_features) > 0 && ncol(train_features) > 0){
  train_features_numeric <- train_features %>% select_if(is.numeric)
  
  if(ncol(train_features_numeric) > 0) {
    nzv <- nearZeroVar(train_features_numeric, saveMetrics = TRUE, freqCut = 95/5, uniqueCut = 10)
    train_features_numeric_nzv <- train_features_numeric[, !nzv$nzv, drop = FALSE]
    
    if(ncol(train_features_numeric_nzv) > 0) {
      vars_check <- sapply(train_features_numeric_nzv, var, na.rm = TRUE)
      cols_to_keep_for_pca <- names(vars_check[!is.na(vars_check) & vars_check > .Machine$double.eps])
      
      if(length(cols_to_keep_for_pca) > 0) {
        train_features_for_pca <- train_features_numeric_nzv[, cols_to_keep_for_pca, drop=FALSE]
        pca_model <- prcomp(train_features_for_pca, center = TRUE, scale. = TRUE)
        
        explained_variance <- cumsum(pca_model$sdev^2 / sum(pca_model$sdev^2))
        num_components <- which(explained_variance >= 0.95)[1]
        if (is.na(num_components) || num_components == 0) { 
          num_components <- min(1, ncol(train_features_for_pca))
          if (ncol(train_features_for_pca) == 0) num_components = 0
        }
        if (num_components == 0 && ncol(train_features_for_pca) > 0) num_components = 1
        if (num_components > ncol(train_features_for_pca)) num_components = ncol(train_features_for_pca)
        
        cat("Jumlah komponen utama terpilih:", num_components, "\n")
        
        if(num_components > 0) {
          train_pca <- as.data.frame(predict(pca_model, newdata = train_features_for_pca)[, 1:num_components, drop = FALSE])
          test_features_numeric <- test_features %>% select_if(is.numeric)
          if(ncol(test_features_numeric) > 0 && all(cols_to_keep_for_pca %in% names(test_features_numeric))){
            test_features_for_pca_transform <- test_features_numeric[, cols_to_keep_for_pca, drop = FALSE]
            test_pca <- as.data.frame(predict(pca_model, newdata = test_features_for_pca_transform)[, 1:num_components, drop = FALSE])
          } else {
            warning("Fitur numerik pada data uji tidak sesuai atau kosong. Test PCA kemungkinan salah.")
            test_pca <- data.frame(matrix(NA, nrow = nrow(test_features), ncol = num_components))
            if(num_components > 0) colnames(test_pca) <- paste0("PC", 1:num_components)
          }
        } else {
          cat("Tidak ada komponen utama terpilih. Proses PCA dilewati.\n")
          train_pca <- train_features_for_pca
          test_features_numeric <- test_features %>% select_if(is.numeric)
          if(all(cols_to_keep_for_pca %in% names(test_features_numeric))){
            test_pca <- test_features_numeric[, cols_to_keep_for_pca, drop = FALSE]
          } else {
            test_pca <- data.frame(matrix(NA, nrow = nrow(test_features_numeric), ncol = ncol(train_pca)))
            if(ncol(train_pca) > 0) colnames(test_pca) <- colnames(train_pca)
          }
        }
      } else {
        cat("Tidak ada fitur numerik yang variansinya > 0 setelah NZV. Tetap gunakan numeric pasca-NZV untuk KNN.\n")
        train_pca <- train_features_numeric_nzv
        test_features_numeric <- test_features %>% select_if(is.numeric)
        if(all(colnames(train_features_numeric_nzv) %in% names(test_features_numeric))){
          test_pca <- test_features_numeric[, colnames(train_features_numeric_nzv), drop = FALSE]
        } else {
          test_pca <- data.frame(matrix(NA, nrow = nrow(test_features_numeric), ncol = ncol(train_pca)))
          if(ncol(train_pca) > 0) colnames(test_pca) <- colnames(train_pca)
        }
      }
    } else {
      cat("Tidak ada fitur numerik tersisa setelah NZV. Gunakan semua numeric tanpa PCA.\n")
      train_pca <- train_features_numeric
      test_features_numeric <- test_features %>% select_if(is.numeric)
      common_numeric_cols_pca_fallback <- intersect(names(train_pca), names(test_features_numeric))
      train_pca <- train_pca[, common_numeric_cols_pca_fallback, drop = FALSE]
      test_pca <- test_features_numeric[, common_numeric_cols_pca_fallback, drop = FALSE]
    }
  } else {
    cat("Tidak ada fitur numerik untuk PCA. KNN mungkin memakai set fitur kosong.\n")
    train_pca <- data.frame()[1:max(1,nrow(train_features)), , drop = FALSE]
    test_pca <- data.frame()[1:max(1,nrow(test_features)), , drop = FALSE]
  }
} else {
  cat("train_features kosong. Lewati PCA.\n")
  train_pca <- data.frame()[1:max(1,nrow(train_data)), , drop = FALSE]
  test_pca <- data.frame()[1:max(1,nrow(test_data)), , drop = FALSE]
}

# Pelatihan model KNN
if(is.null(train_pca) || nrow(train_pca) == 0 || ncol(train_pca) == 0 || length(train_target) == 0 || nrow(train_pca) != length(train_target)) {
  stop("Data latih untuk KNN (train_pca) tidak mencukupi. Periksa PCA dan pemisahan data.")
}

ctrl <- trainControl(method = "cv", number = min(10, nrow(train_pca)))
max_k_try <- min(19, nrow(train_pca)-1)
if (max_k_try < 1) max_k_try = 1

knn_model <- train(
  x = train_pca,
  y = train_target,
  method = "knn",
  trControl = ctrl,
  preProcess = NULL,
  tuneGrid = expand.grid(k = seq(1, max_k_try, by = 2))
)

k_optimal <- knn_model$bestTune$k
cat("Nilai K optimal:", k_optimal, "\n")

# Visualisasi optimasi K
plot(knn_model, main = "Optimasi Nilai K untuk KNN")

# Prediksi pada data uji
if(is.null(test_pca) || (!is.null(train_pca) && ncol(test_pca) != ncol(train_pca))) {
  stop(paste("Jumlah kolom berbeda atau test_pca NULL. train_pca cols:", ncol(train_pca), "test_pca cols:", if(!is.null(test_pca)) ncol(test_pca) else "NULL"))
}

if(nrow(test_data) > 0 && nrow(test_pca) == nrow(test_data) && ncol(test_pca) > 0) {
  knn_pred <- predict(knn_model, newdata = test_pca)
  
  if (!is.factor(test_target)) test_target <- factor(test_target, levels = levels(knn_pred))
  if (length(knn_pred) != length(test_target)){
    stop("Panjang hasil prediksi tidak cocok dengan target data uji.")
  }
  
  confusion_matrix <- confusionMatrix(knn_pred, test_target)
  print(confusion_matrix)
  
  accuracy <- confusion_matrix$overall['Accuracy']
  precision <- if("Pos Pred Value" %in% names(confusion_matrix$byClass)) confusion_matrix$byClass['Pos Pred Value'] else NA
  recall <- if("Sensitivity" %in% names(confusion_matrix$byClass)) confusion_matrix$byClass['Sensitivity'] else NA
  f1_score <- if("F1" %in% names(confusion_matrix$byClass)) confusion_matrix$byClass['F1'] else NA
  specificity <- if("Specificity" %in% names(confusion_matrix$byClass)) confusion_matrix$byClass['Specificity'] else NA
  
  cat("Akurasi:", accuracy, "\n")
  cat("Presisi (Kelas Alzheimer's):", precision, "\n")
  cat("Recall (Kelas Alzheimer's):", recall, "\n")
  cat("F1-Score (Kelas Alzheimer's):", f1_score, "\n")
  cat("Spesifisitas (Kelas No Alzheimer's):", specificity, "\n")
  
  if (inherits(confusion_matrix, "confusionMatrix")) {
    cm_table <- as.data.frame(confusion_matrix$table)
    if(nrow(cm_table) > 0) {
      print(
        ggplot(data = cm_table, aes(x = Prediction, y = Reference, fill = Freq)) +
          geom_tile() +
          geom_text(aes(label = Freq), vjust = 1, color = "white", size = 6) +
          scale_fill_gradient(low = "lightblue", high = "darkblue") +
          labs(title = paste("Confusion Matrix KNN (K=", k_optimal, ")", sep=""),
               x = "Kelas Prediksi", y = "Kelas Aktual") +
          theme_minimal() +
          theme(axis.text.x = element_text(angle = 45, hjust = 1))
      )
    } else {
      cat("Tabel confusion matrix kosong, plot dilewati.\n")
    }
  }
} else {
  cat("test_pca memiliki 0 baris/kolom atau tidak sesuai dengan test_data. Proses prediksi dilewati.\n")
}
