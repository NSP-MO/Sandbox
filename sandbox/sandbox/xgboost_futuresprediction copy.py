import pandas as pd
import numpy as np
from datetime import timedelta
from xgboost import XGBRegressor

# Load data
df = pd.read_csv(r'C:\Users\Hp\Downloads\comodity-price-prediction-penyisihan-arkavidia-9\Global Commodity Price\Crude Oil WTI Futures Historical Data.csv', parse_dates=['Date'], thousands=',')
df = df.sort_values('Date').reset_index(drop=True)

# Feature Engineering
def create_features(df):
    df = df.copy()
    for lag in [1, 7, 14, 30]:
        df[f'lag_{lag}'] = df['Price'].shift(lag)
    df['day_of_week'] = df['Date'].dt.dayofweek
    df['month'] = df['Date'].dt.month
    return df

df = create_features(df)
df = df.dropna()

# Split data
X = df.drop(columns=['Price', 'Date', 'Open', 'High', 'Low', 'Vol.', 'Change %'])
y = df['Price']
model = XGBRegressor(n_estimators=1000)
model.fit(X, y)

# Generate future dates
last_date = df['Date'].max()
future_dates = [last_date + timedelta(days=i) for i in range(1, 93)]

# Recursive prediction
current_data = df.copy().iloc[-30:].reset_index(drop=True)
predictions = []

for date in future_dates:
    features = current_data.iloc[-1][['lag_1', 'lag_7', 'lag_14', 'lag_30', 'day_of_week', 'month']].copy()
    pred = model.predict(pd.DataFrame([features]))[0]
    
    predictions.append({
        'date': date,
        'price': pred
    })
    
    # Update features for next prediction
    new_row = {
        'Date': date,
        'Price': pred,
        'lag_1': current_data.iloc[-1]['Price'],
        'lag_7': current_data.iloc[-7]['Price'] if len(current_data) >=7 else np.nan,
        'lag_14': current_data.iloc[-14]['Price'] if len(current_data) >=14 else np.nan,
        'lag_30': current_data.iloc[-30]['Price'] if len(current_data) >=30 else np.nan,
        'day_of_week': date.dayofweek,
        'month': date.month
    }
    
    current_data = pd.concat([current_data, pd.DataFrame([new_row])], ignore_index=True)

# Create output
output = pd.DataFrame({
    'id': [f"Crude Oil WTI/Global/{d.strftime('%Y-%m-%d')}" for d in future_dates],
    'price': [p['price'] for p in predictions]
})

output.to_csv('oil_price_predictions.csv', index=False)