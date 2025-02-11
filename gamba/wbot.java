import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.math.BigDecimal;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.*;
import java.util.concurrent.*;

public class wbot {
    private static final String API_KEY = "4c1029f9-6317-4c87-903f-3923f56de4d1";
    private static final String API_SECRET = "B565C60ED402A2EA0DD41167F60E8CD6";
    private static final String PASS_PHRASE = "Step463656!";
    private static final String API_URL = "https://www.okx.com/api/v5/market/candles";
    private static final HttpClient CLIENT = HttpClient.newHttpClient();
    private static final ObjectMapper objectMapper = new ObjectMapper(); // Jackson ObjectMapper

    public static void main(String[] args) {
        List<String> symbols = Arrays.asList("SOL-USDT-SWAP", "BTC-USDT-SWAP", "ETH-USDT-SWAP", "DOGE-USDT-SWAP", "ACE-USDT-SWAP");
        int maPeriod = 90;
        int srWindow = 20;
        double tradeAmount = 0.5;
        int leverage = 15;

        // Use a thread pool to handle multiple symbols concurrently
        ExecutorService executor = Executors.newFixedThreadPool(symbols.size());

        for (String symbol : symbols) {
            executor.submit(() -> runBot(symbol, maPeriod, srWindow, tradeAmount, leverage));
        }
    }

    private static void runBot(String symbol, int maPeriod, int srWindow, double tradeAmount, int leverage) {
        while (true) {
            try {
                // Fetch candles for the symbol
                List<Candle> candles = fetchCandles(symbol, "5m", 300);
                if (candles.size() < Math.max(maPeriod, srWindow)) {
                    System.out.println("Insufficient data for " + symbol + ", waiting...");
                    Thread.sleep(10000);  // Sleep for 10 seconds before retry
                    continue;
                }

                // Calculate strategy indicators
                List<Candle> updatedCandles = calculateStrategy(candles, maPeriod, srWindow);

                // Get the most recent candle and its corresponding signal
                Candle latestCandle = updatedCandles.get(updatedCandles.size() - 1);
                int signal = latestCandle.signal;

                // Print results for debugging
                System.out.println("Timestamp: " + latestCandle.timestamp);
                System.out.println("Latest signal for " + symbol + ": " + signal);
                System.out.println("Support: " + latestCandle.support + ", Resistance: " + latestCandle.resistance);
                System.out.println("MA Slope: " + latestCandle.sma125Slope);

                // Place an order based on the signal
                if (signal == 1) {
                    placeOrder(symbol, "buy", tradeAmount, leverage);
                } else if (signal == -1) {
                    placeOrder(symbol, "sell", tradeAmount, leverage);
                }

                Thread.sleep(10000);  // Sleep for 10 seconds before fetching the next candle
            } catch (Exception e) {
                System.err.println("Error in trading loop for " + symbol + ": " + e.getMessage());
            }
        }
    }

    private static List<Candle> fetchCandles(String symbol, String interval, int limit) throws Exception {
        String url = API_URL + "?instId=" + symbol + "&bar=" + interval + "&limit=" + limit;
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Authorization", "Bearer " + API_KEY)
                .build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
        String responseBody = response.body();

        // Parse the response body (using Jackson)
        return parseCandles(responseBody);
    }

    private static List<Candle> parseCandles(String responseBody) {
        List<Candle> candles = new ArrayList<>();
        try {
            // Use Jackson to parse the JSON response
            JsonNode jsonResponse = objectMapper.readTree(responseBody);
            if (jsonResponse.has("data")) {
                JsonNode dataArray = jsonResponse.get("data");

                for (JsonNode candleData : dataArray) {
                    Candle candle = new Candle();
                    candle.timestamp = candleData.get(0).asText();
                    candle.open = new BigDecimal(candleData.get(1).asText());
                    candle.high = new BigDecimal(candleData.get(2).asText());
                    candle.low = new BigDecimal(candleData.get(3).asText());
                    candle.close = new BigDecimal(candleData.get(4).asText());
                    candle.volume = new BigDecimal(candleData.get(5).asText());

                    candles.add(candle);
                }
            }
        } catch (Exception e) {
            System.err.println("Error parsing candle data: " + e.getMessage());
        }
        return candles;
    }

    private static List<Candle> calculateStrategy(List<Candle> candles, int maPeriod, int srWindow) {
        // Calculate moving averages, support, resistance, and signal based on MA slope
        for (int i = maPeriod; i < candles.size(); i++) {
            Candle candle = candles.get(i);
            candle.sma125 = calculateSMA(candles, i, maPeriod);
            candle.sma125Slope = candle.sma125.subtract(candles.get(i - 1).sma125);
            candle.support = calculateSupport(candles, i, srWindow);
            candle.resistance = calculateResistance(candles, i, srWindow);

            // Set signal based on conditions
            if (candle.close.compareTo(candle.support) <= 0 && candle.sma125Slope.compareTo(BigDecimal.ZERO) > 0) {
                candle.signal = 1;  // Buy signal
            } else if (candle.close.compareTo(candle.resistance) >= 0 && candle.sma125Slope.compareTo(BigDecimal.ZERO) < 0) {
                candle.signal = -1;  // Sell signal
            } else {
                candle.signal = 0;  // No signal
            }
        }
        return candles;
    }

    private static BigDecimal calculateSMA(List<Candle> candles, int index, int period) {
        BigDecimal sum = BigDecimal.ZERO;
        for (int i = index - period + 1; i <= index; i++) {
            sum = sum.add(candles.get(i).close);
        }
        return sum.divide(BigDecimal.valueOf(period), 2, BigDecimal.ROUND_HALF_UP);
    }

    private static BigDecimal calculateSupport(List<Candle> candles, int index, int window) {
        BigDecimal min = candles.get(index).low;
        for (int i = index - window + 1; i <= index; i++) {
            min = min.min(candles.get(i).low);
        }
        return min;
    }

    private static BigDecimal calculateResistance(List<Candle> candles, int index, int window) {
        BigDecimal max = candles.get(index).high;
        for (int i = index - window + 1; i <= index; i++) {
            max = max.max(candles.get(i).high);
        }
        return max;
    }

    private static void placeOrder(String symbol, String side, double amount, int leverage) {
        // Logic to place an order through the exchange API (not shown)
        System.out.println("Placing order: " + side + " " + amount + " of " + symbol + " with leverage " + leverage);
    }
}

class Candle {
    String timestamp;
    BigDecimal open;
    BigDecimal high;
    BigDecimal low;
    BigDecimal close;
    BigDecimal volume;
    BigDecimal sma125;
    BigDecimal sma125Slope;
    BigDecimal support;
    BigDecimal resistance;
    int signal;

    // Constructor and other methods (e.g., toString) can be added as needed
}
