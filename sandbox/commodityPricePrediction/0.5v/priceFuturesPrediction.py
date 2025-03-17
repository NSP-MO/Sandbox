import os
import pandas as pd
import numpy as np
from datetime import timedelta
from xgboost import XGBRegressor

def create_features(df, target_col='bawang', date_col='Date'):
    """Membuat fitur lag dan fitur temporal"""
    df = df.copy()
    
    # Membuat fitur lag
    lags = [1, 7, 14, 30]
    for lag in lags:
        df[f'lag_{lag}'] = df[target_col].shift(lag)
    
    # Membuat fitur waktu
    df['day_of_week'] = df[date_col].dt.dayofweek
    df['month'] = df[date_col].dt.month
    
    return df.dropna()

def predict_future(model, last_date, initial_data, days=92):
    """Membuat prediksi rekursif untuk hari-hari mendatang"""
    current_data = initial_data.copy()
    predictions = []
    
    for day in range(days):
        # Membuat fitur untuk prediksi
        features = current_data.iloc[-1][['lag_1', 'lag_7', 'lag_14', 'lag_30', 'day_of_week', 'month']]
        
        # Membuat prediksi
        pred = model.predict(pd.DataFrame([features]))[0]
        pred_date = last_date + timedelta(days=day+1)
        
        # Update data untuk prediksi berikutnya
        new_row = {
            'Date': pred_date,
            'bawang': pred,
            'lag_1': current_data.iloc[-1]['bawang'],
            'lag_7': current_data.iloc[-7]['bawang'] if len(current_data) >=7 else np.nan,
            'lag_14': current_data.iloc[-14]['bawang'] if len(current_data) >=14 else np.nan,
            'lag_30': current_data.iloc[-30]['bawang'] if len(current_data) >=30 else np.nan,
            'day_of_week': pred_date.weekday(),
            'month': pred_date.month
        }
        
        current_data = pd.concat([current_data, pd.DataFrame([new_row])], ignore_index=True)
        predictions.append((pred_date, pred))
    
    return predictions

def process_file(file_path):
    """Memproses satu file dan mengembalikan hasil prediksi"""
    try:
        # Load data
        df = pd.read_csv(file_path, parse_dates=['Date'], thousands=',')
        df = df.sort_values('Date').reset_index(drop=True)
        
        # Validasi data
        if len(df) < 30:
            print(f"Data historis kurang dari 30 hari untuk {file_path}")
            return None
        
        # Feature engineering
        processed_df = create_features(df)
        
        # Persiapan training
        X = processed_df[['lag_1', 'lag_7', 'lag_14', 'lag_30', 'day_of_week', 'month']]
        y = processed_df['bawang']
        
        # Training model
        model = XGBRegressor(n_estimators=1000, random_state=42)
        model.fit(X, y)
        
        # Membuat prediksi
        last_date = processed_df['Date'].iloc[-1]
        initial_data = processed_df.iloc[-30:]
        predictions = predict_future(model, last_date, initial_data, days=92)
        
        # Format output
        province = os.path.basename(file_path).replace('.csv', '')  # Hilangkan .lower()
        return pd.DataFrame([{
            'id': f"Bawang Merah/{province}/{date.strftime('%Y-%m-%d')}",  # Perbaikan format
            'price': round(price, 2)
        } for date, price in predictions])
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None

def main():
    # Daftar file CSV
    base_path = r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Google Trend\bawang'  # Update path sesuai kebutuhan
    provinces = [
        'Aceh', 'Bali', 'Banten', 'Bengkulu', 'DI Yogyakarta', 'DKI Jakarta',
        'Gorontalo', 'Jambi', 'Jawa Barat', 'Jawa Tengah',
        'Jawa Timur', 'Kalimantan Barat', 'Kalimantan Selatan',
        'Kalimantan Tengah', 'Kalimantan Timur', 'Kalimantan Utara',
        'Kepulauan Bangka Belitung', 'Kepulauan Riau', 'Lampung',
        'Maluku', 'Maluku Utara', 'Nusa Tenggara Barat',
        'Nusa Tenggara Timur', 'Papua', 'Papua Barat', 'Riau',
        'Sulawesi Barat', 'Sulawesi Selatan', 'Sulawesi Tengah',
        'Sulawesi Tenggara', 'Sulawesi Utara', 'Sumatera Barat',
        'Sumatera Selatan', 'Sumatera Utara'
    ]
    
    # Proses semua file
    all_predictions = []
    
    for province in provinces:
        file_path = os.path.join(base_path, f"{province}.csv")
        if not os.path.exists(file_path):
            print(f"File tidak ditemukan: {file_path}")
            continue
        
        print(f"Memproses {province}...")
        result = process_file(file_path)
        
        if result is not None:
            all_predictions.append(result)
    
    # Gabungkan semua hasil
    if all_predictions:
        final_output = pd.concat(all_predictions, ignore_index=True)
        final_output.to_csv('sample_submission.csv', index=False)  # Nama file sesuai sample
        print("Prediksi berhasil disimpan di sample_submission.csv")
    else:
        print("Tidak ada data yang berhasil diproses")

if __name__ == "__main__":
    main()