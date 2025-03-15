import pandas as pd

def load_data(file_path, commodity_name):
    """Membaca data komoditas dari file CSV"""
    try:
        df = pd.read_csv(file_path)
        
        # Membersihkan dan mengkonversi kolom numerik
        numeric_columns = ['Price', 'Open', 'High', 'Low']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace(',', '').astype(float)
        
        df['Date'] = pd.to_datetime(df['Date'])
        df.sort_values('Date', ascending=False, inplace=True)
        
        # Konversi volume
        if 'Vol.' in df.columns:
            df['Vol.'] = df['Vol.'].str.replace('K', '').astype(float) * 1000
            
        return df, None
    except Exception as e:
        return None, f"Error loading {commodity_name} data: {str(e)}"
def display_latest_price(df, commodity_name):
    """Menampilkan harga terbaru dan informasi terkait"""
    latest = df.iloc[0]
    print(f"\nHarga Terbaru {commodity_name}:")
    print(f"Tanggal: {latest['Date'].strftime('%Y-%m-%d')}")
    print(f"Harga Penutupan: ${latest['Price']:.2f}")
    print(f"Perubahan: {latest['Change %']}")
    print(f"Volume: {latest['Vol.']:,.0f} kontrak")

def main():
    # Update: Menambahkan dataset baru
    commodities = {
        'Crude Oil WTI': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\Crude Oil WTI Futures Historical Data.csv',
        'Natural Gas': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\Natural Gas Futures Historical Data.csv',
        'US Sugar 11': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\US Sugar 11 Futures Historical Data.csv',
        'US Wheat': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\US Wheat Futures Historical Data.csv',
        'Newcastle Coal': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\Newcastle Coal Futures Historical Data.csv',
        'Palm Oil': r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\Palm Oil Futures Historical Data.csv'
    }

    # Memuat data
    data = {}
    for name, file in commodities.items():
        df, error = load_data(file, name)
        if error:
            print(error)
            return
        data[name] = df

    # Antarmuka pengguna
    while True:
        print("\n=== Analisis Harga Komoditas Global ===")
        print("Pilih komoditas:")
        for i, name in enumerate(data.keys(), 1):
            print(f"{i}. {name}")
        print("0. Keluar")
        
        max_choice = len(data)
        choice = input(f"Masukkan pilihan (0-{max_choice}): ")
        
        if choice == '0':
            print("Program selesai.")
            break
            
        # Update: Validasi pilihan dinamis
        elif choice.isdigit() and 1 <= int(choice) <= max_choice:
            commodity = list(data.keys())[int(choice)-1]
            df = data[commodity]
            
            # Menampilkan informasi dasar
            display_latest_price(df, commodity)
            
            # Analisis tambahan
            print("\nStatistik 7 Hari Terakhir:")
            last_week = df.head(7)
            print(f"Rata-rata Harga: ${last_week['Price'].mean():.2f}")
            print(f"Perubahan Maksimum: {last_week['Change %'].max()}")
            print(f"Volume Total: {last_week['Vol.'].sum():,.0f} kontrak")
            
        else:
            print("Pilihan tidak valid!")

if __name__ == "__main__":
    main()