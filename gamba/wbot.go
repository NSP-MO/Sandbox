package main

import (
	"encoding/json"
	"fmt"
	"math"
	"time"

	"github.com/go-resty/resty/v2"
	"github.com/shopspring/decimal"
)

// Define a struct for the response structure
type Candle struct {
	Timestamp    string          `json:"ts"`
	Open         decimal.Decimal `json:"open"`
	High         decimal.Decimal `json:"high"`
	Low          decimal.Decimal `json:"low"`
	Close        decimal.Decimal `json:"close"`
	Volume       decimal.Decimal `json:"vol"`
	Currency     string          `json:"currency"`
	TimestampEnd string          `json:"timestamp_end"`
	MarketType   string          `json:"market_type"`
}

// Fetch Candles from OKX API
func fetchCandles(symbol string, interval string, limit int) ([]Candle, error) {
	client := resty.New()
	url := "https://www.okx.com/api/v5/market/candles"

	params := map[string]string{
		"instId": symbol,
		"bar":    interval,
		"limit":  fmt.Sprintf("%d", limit),
	}

	resp, err := client.R().SetQueryParams(params).Get(url)
	if err != nil {
		return nil, fmt.Errorf("error fetching candles: %w", err)
	}

	// Log the raw response to debug
	fmt.Println("Raw response:", string(resp.Body()))

	var data struct {
		Data []Candle `json:"data"`
	}

	err = json.Unmarshal(resp.Body(), &data)
	if err != nil {
		return nil, fmt.Errorf("error parsing JSON: %w", err)
	}

	if len(data.Data) == 0 {
		return nil, fmt.Errorf("no candle data retrieved")
	}

	fmt.Println("Fetched candles:", len(data.Data))
	return data.Data, nil
}


// Calculate Moving Averages
func calculateMovingAverages(candles []Candle, maPeriod int) ([]Candle, error) {
	for i := maPeriod - 1; i < len(candles); i++ {
		sum := decimal.NewFromInt(0)
		for j := i - maPeriod + 1; j <= i; j++ {
			sum = sum.Add(candles[j].Close)
		}
		candles[i].Open = sum.Div(decimal.NewFromInt(int64(maPeriod)))
	}
	return candles, nil
}

// Calculate Support and Resistance
func calculateSupportResistance(candles []Candle, window int) ([]Candle, error) {
	for i := window - 1; i < len(candles); i++ {
		minLow := candles[i].Low
		maxHigh := candles[i].High
		for j := i - window + 1; j <= i; j++ {
			if candles[j].Low.Cmp(minLow) < 0 {
				minLow = candles[j].Low
			}
			if candles[j].High.Cmp(maxHigh) > 0 {
				maxHigh = candles[j].High
			}
		}
		// Save the support and resistance
		candles[i].Open = minLow
		candles[i].High = maxHigh
	}
	return candles, nil
}

// Determine Slope of the 125-period MA
func calculateMASlope(candles []Candle, maPeriod int) ([]Candle, error) {
	for i := maPeriod; i < len(candles); i++ {
		// Calculate the slope as the difference between current MA and MA 125 periods ago
		slope := candles[i].Open.Sub(candles[i-maPeriod].Open)
		// Store the slope for later use
		candles[i].Open = slope
	}
	return candles, nil
}

// Calculate Buy/Sell Signals
func calculateCombinedStrategy(candles []Candle, maPeriod int, srWindow int) ([]Candle, error) {
	// Calculate the MA, Support, Resistance, and Slope
	candles, err := calculateMovingAverages(candles, maPeriod)
	if err != nil {
		return nil, err
	}
	candles, err = calculateSupportResistance(candles, srWindow)
	if err != nil {
		return nil, err
	}
	candles, err = calculateMASlope(candles, maPeriod)
	if err != nil {
		return nil, err
	}

	// Generate signals
	for i := 0; i < len(candles); i++ {
		if candles[i].Close.LessThanOrEqual(candles[i].Open) && candles[i].Open.GreaterThan(decimal.NewFromInt(0)) {
			// Buy Signal
			fmt.Println("Buy signal detected")
		} else if candles[i].Close.GreaterThanOrEqual(candles[i].Open) && candles[i].Open.LessThan(decimal.NewFromInt(0)) {
			// Sell Signal
			fmt.Println("Sell signal detected")
		}
	}

	return candles, nil
}

// Place an Order (mocking the place order function)
func placeOrder(symbol string, side string, amount float64) {
	// Mock order placement
	fmt.Printf("Placing %s order: %f %s\n", side, amount, symbol)
}

// Set Leverage (mocking the leverage set function)
func setLeverage(symbol string, leverage int) {
	// Mock leverage setting
	fmt.Printf("Leverage set to %d for %s\n", leverage, symbol)
}

// Trading Bot Logic
func tradingBot(symbols []string, interval string, maPeriod int, srWindow int, tradeAmount float64, leverage int) {
	for _, symbol := range symbols {
		setLeverage(symbol, leverage)
	}

	for {
		for _, symbol := range symbols {
			candles, err := fetchCandles(symbol, interval, 100)
			if err != nil || len(candles) < int(math.Max(float64(maPeriod), float64(srWindow))) {
				fmt.Printf("Insufficient data for %s\n", symbol)
				continue
			}

			candles, err = calculateCombinedStrategy(candles, maPeriod, srWindow)
			if err != nil {
				fmt.Printf("Error calculating strategy for %s: %s\n", symbol, err)
				continue
			}

			latestSignal := candles[len(candles)-1].Open
			if latestSignal.Cmp(decimal.NewFromInt(1)) == 0 {
				// Buy Signal
				placeOrder(symbol, "buy", tradeAmount)
			} else if latestSignal.Cmp(decimal.NewFromInt(-1)) == 0 {
				// Sell Signal
				placeOrder(symbol, "sell", tradeAmount)
			}
		}

		// Sleep for 10 seconds before the next loop
		time.Sleep(10 * time.Second)
	}
}

func main() {
	// List of symbols to trade
	symbols := []string{"SOL-USDT-SWAP", "BTC-USDT-SWAP", "ETH-USDT-SWAP", "DOGE-USDT-SWAP", "ACE-USDT-SWAP"}

	// Run the trading bot
	tradingBot(symbols, "5m",90, 20, 0.5, 15)
}


