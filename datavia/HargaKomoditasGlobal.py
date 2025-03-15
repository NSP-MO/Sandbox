import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Dropdown

def calculate_futures_price(data_path, r, s, c, t):
    df = pd.read_csv(data_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    
    if 'Change %' not in df.columns:
        df['Change %'] = df['Close'].pct_change() * 100
    
    df['Futures Price'] = df['Close'] * np.exp((r + s - c) * t)
    return df[['Date', 'Close', 'Futures Price', 'Change %', 'Volume']]

# Konfigurasi parameter
parameters = {
    'risk_free_rate': 0.0025,
    'storage_cost': 0.015,
    'convenience_yield': 0.005,
    'time_to_maturity': 0.5
}

currencies = ['MYRUSD=X', 'USDIDR=X', 'THBUSD=X', 'SGDUSD=X']
base_path = r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Mata Uang\\'

# Memuat semua data terlebih dahulu
data_dict = {}
for currency in currencies:
    file_path = f'{base_path}{currency}.csv'
    data_dict[currency] = calculate_futures_price(
        file_path,
        parameters['risk_free_rate'],
        parameters['storage_cost'],
        parameters['convenience_yield'],
        parameters['time_to_maturity']
    )

# Membuat figure dan axes
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(left=0.1, bottom=0.25)

# Plot awal
current_currency = currencies[0]
line1, = ax.plot(data_dict[current_currency]['Date'], data_dict[current_currency]['Close'], label='Spot Price')
line2, = ax.plot(data_dict[current_currency]['Date'], data_dict[current_currency]['Futures Price'], label='Futures Price')
ax.set_title(f'Perbandingan Harga Spot dan Futures ({current_currency})')
ax.set_xlabel('Tanggal')
ax.set_ylabel('Harga')
ax.legend()

# Membuat dropdown menu
ax_dropdown = plt.axes([0.1, 0.05, 0.8, 0.1])
dropdown = Dropdown(
    ax_dropdown,
    label='Pilih Mata Uang:',
    options=currencies,
    initialindex=0
)

# Fungsi update plot
def update_plot(currency_name):
    df = data_dict[currency_name]
    
    # Update data plot
    line1.set_xdata(df['Date'])
    line1.set_ydata(df['Close'])
    line2.set_xdata(df['Date'])
    line2.set_ydata(df['Futures Price'])
    
    # Update axis limits
    ax.relim()
    ax.autoscale_view()
    
    # Update judul
    ax.set_title(f'Perbandingan Harga Spot dan Futures ({currency_name})')
    
    plt.draw()

# Menghubungkan dropdown dengan fungsi update
dropdown.on_clicked(update_plot)

plt.show()