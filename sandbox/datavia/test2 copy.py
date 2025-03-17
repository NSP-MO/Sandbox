import pandas as pd
import numpy as np

def calculate_futures_price(data_path, r, s, c, t):
    # Read data from CSV
    df = pd.read_csv(data_path)
    
    # Clean and process data
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    
    # Calculate Change % if not present
    if 'Change %' not in df.columns:
        df['Change %'] = df['Close'].pct_change() * 100
    
    # Calculate futures price using cost of carry formula
    df['Futures Price'] = df['Close'] * np.exp((r + s - c) * t)
    
    return df[['Date', 'Close', 'Futures Price', 'Change %', 'Volume']]

# Input parameters (example default values)
parameters = {
    'risk_free_rate': 0.0025,    # r (example: 0.25%)
    'storage_cost': 0.015,       # s (1.5% per year)
    'convenience_yield': 0.005,  # c (0.5% per year)
    'time_to_maturity': 0.5      # t (6 months/0.5 year)
}

# Example usage for THBUSD
commodity_data = calculate_futures_price(
    r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Mata Uang\THBUSD=X.csv',  # Updated file path
    parameters['risk_free_rate'],
    parameters['storage_cost'],
    parameters['convenience_yield'],
    parameters['time_to_maturity']
)

# Display results
print("Harga Komoditas dan Perhitungan Futures:")
print(commodity_data.tail())

# Visualize data
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 6))
plt.plot(commodity_data['Date'], commodity_data['Close'], label='Spot Price')
plt.plot(commodity_data['Date'], commodity_data['Futures Price'], label='Futures Price')
plt.title('Perbandingan Harga Spot dan Futures (THBUSD)')
plt.xlabel('Tanggal')
plt.ylabel('Harga')
plt.legend()
plt.show()