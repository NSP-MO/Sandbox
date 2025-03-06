import pandas as pd
import numpy as np

def calculate_futures_price(data_path, r, s, c, t):
    # Membaca data dari CSV
    df = pd.read_csv(data_path)
    
    # Membersihkan dan memproses data
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    
    # Menghitung Change % jika tidak ada
    if 'Change %' not in df.columns:
        df['Change %'] = df['Close'].pct_change() * 100
    
    # Menghitung harga futures menggunakan rumus cost of carry
    df['Futures Price'] = df['Close'] * np.exp((r + s - c) * t)
    
    return df[['Date', 'Close', 'Futures Price', 'Change %', 'Volume']]

# Parameter input (contoh nilai default)
parameters = {
    'risk_free_rate': 0.0025,    # r (contoh: 0.25%)
    'storage_cost': 0.015,       # s (1.5% per tahun)
    'convenience_yield': 0.005,  # c (0.5% per tahun)
    'time_to_maturity': 0.5      # t (6 bulan/0.5 tahun)
}

# Contoh penggunaan untuk satu komoditas
commodity_data = calculate_futures_price(
    r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Mata Uang\MYRUSD=X.csv',
    parameters['risk_free_rate'],
    parameters['storage_cost'],
    parameters['convenience_yield'],
    parameters['time_to_maturity']
)

# Menampilkan hasil
print("Harga Komoditas dan Perhitungan Futures:")
print(commodity_data.tail())

# Visualisasi data
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(commodity_data['Date'], commodity_data['Close'], label='Spot Price')
plt.plot(commodity_data['Date'], commodity_data['Futures Price'], label='Futures Price')
plt.title('Perbandingan Harga Spot dan Futures')
plt.xlabel('Tanggal')
plt.ylabel('Harga')
plt.legend()
plt.show()