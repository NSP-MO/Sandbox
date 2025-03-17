import os
import pandas as pd
import numpy as np
from datetime import timedelta
from xgboost import XGBRegressor
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial

def create_features(df, target_col, date_col='Date'):
    """Membuat fitur lag dan fitur temporal secara vektor"""
    df = df.copy()
    
    # Membuat fitur lag menggunakan numpy untuk operasi vektor
    lags = [1, 7, 14, 30]
    for lag in lags:
        df[f'lag_{lag}'] = df[target_col].values.copy()
        df[f'lag_{lag}'] = df[f'lag_{lag}'].shift(lag)
    
    # Membuat fitur waktu
    dates = df[date_col].dt
    df['day_of_week'] = dates.dayofweek
    df['month'] = dates.month
    
    return df.dropna()

def predict_future(model, last_date, initial_data, target_col, days=92):
    """Membuat prediksi rekursif dengan optimasi numpy"""
    current_data = initial_data.copy()
    predictions = []
    
    # Konversi ke numpy array untuk akses lebih cepat
    lag_1 = current_data[target_col].values
    lag_7 = current_data[target_col].values if len(current_data) >=7 else np.full(len(current_data), np.nan)
    lag_14 = current_data[target_col].values if len(current_data) >=14 else np.full(len(current_data), np.nan)
    lag_30 = current_data[target_col].values if len(current_data) >=30 else np.full(len(current_data), np.nan)
    
    for day in range(days):
        # Menggunakan indeks untuk akses cepat
        idx = len(current_data) - 1
        features = [
            current_data['lag_1'].iloc[idx],
            current_data['lag_7'].iloc[idx-6] if idx >=6 else np.nan,
            current_data['lag_14'].iloc[idx-13] if idx >=13 else np.nan,
            current_data['lag_30'].iloc[idx-29] if idx >=29 else np.nan,
            (last_date + timedelta(days=day+1)).weekday(),
            (last_date + timedelta(days=day+1)).month
        ]
        
        # Prediksi dengan numpy array
        pred = model.predict(np.array([features]).reshape(1, -1))[0]
        pred_date = last_date + timedelta(days=day+1)
        
        # Update lags menggunakan numpy roll
        new_lag_1 = np.roll(lag_1, -1)
        new_lag_1[-1] = pred
        
        predictions.append((pred_date, pred))
        
        # Update untuk iterasi berikutnya
        lag_1 = new_lag_1
        if day % 7 == 6 and len(lag_7) >=7:
            lag_7 = np.roll(lag_7, -1)
            lag_7[-1] = pred
        if day % 14 == 13 and len(lag_14) >=14:
            lag_14 = np.roll(lag_14, -1)
            lag_14[-1] = pred
        if day % 30 == 29 and len(lag_30) >=30:
            lag_30 = np.roll(lag_30, -1)
            lag_30[-1] = pred
    
    return predictions

def process_file(file_path, commodity):
    """Memproses satu file dan mengembalikan hasil prediksi"""
    try:
        # Perbaikan pada bagian pembacaan CSV
        df = pd.read_csv(
            file_path, 
            parse_dates=['Date'],
            thousands=',',
            dtype={commodity: 'float32'}
        )
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Validasi kolom target
        if commodity not in df.columns or len(df) <30:
            return None
        
        processed_df = create_features(df, commodity)
        if len(processed_df) <30:
            return None
        
        X = processed_df[['lag_1', 'lag_7', 'lag_14', 'lag_30', 'day_of_week', 'month']]
        y = processed_df[commodity]
        
        # Model dengan parameter yang dioptimasi
        model = XGBRegressor(
            n_estimators=500,
            tree_method='hist',
            n_jobs=-1,
            random_state=42
        )
        model.fit(X, y)
        
        last_date = processed_df['Date'].iloc[-1]
        initial_data = processed_df.iloc[-30:]
        predictions = predict_future(model, last_date, initial_data, commodity)
        
        # Format nama komoditas dan provinsi
        formatted_commodity = commodity.replace('-', ' ').title()
        province = os.path.basename(file_path).replace('.csv', '')
        formatted_province = province.replace('-', ' ').title()
        
        return [(f"{formatted_commodity}/{formatted_province}/{date.strftime('%Y-%m-%d')}", round(price, 2))
                for date, price in predictions]
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

def main():
    parent_path = r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Google Trend'
    all_predictions = []
    
    with ProcessPoolExecutor() as executor:
        futures = []
        # Kumpulkan semua tugas
        for dir_name in os.listdir(parent_path):
            commodity_path = os.path.join(parent_path, dir_name)
            if not os.path.isdir(commodity_path):
                continue
            
            original_commodity = dir_name  # Nama direktori asli untuk kolom CSV
            for file_name in os.listdir(commodity_path):
                if file_name.endswith('.csv'):
                    file_path = os.path.join(commodity_path, file_name)
                    futures.append(executor.submit(
                        partial(process_file, commodity=original_commodity),
                        file_path
                    ))
        
        total_files = len(futures)
        processed = 0
        print(f"Total files to process: {total_files}")
        
        # Proses hasil dan tampilkan progres
        for future in as_completed(futures):
            processed += 1
            progress = (processed / total_files) * 100
            print(f"\rProgress: {progress:.2f}% ({processed}/{total_files} files processed)", end='', flush=True)
            result = future.result()
            if result:
                df = pd.DataFrame(result, columns=['id', 'price'])
                all_predictions.append(df)
        print("\nProcessing complete.")  # Pindah baris setelah selesai
    
    if all_predictions:
        final_output = pd.concat(all_predictions, ignore_index=True)
        final_output.to_csv('prediction1.csv', index=False)
        print("Prediksi berhasil disimpan di prediction1.csv")
    else:
        print("Tidak ada data yang berhasil diproses")

if __name__ == "__main__":
    main()