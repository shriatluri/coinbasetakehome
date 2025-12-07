import requests
import json
import datetime

BASE_URL = "https://api.exchange.coinbase.com"

def fetch_data(product_id: str, start: str, end: str, granularity: int = 3600) -> list:
    '''
    Args:
        product_id: The ID of the product to fetch data for.
        start: The start time of the data to fetch.
        end: The end time of the data to fetch.
        granularity: The granularity of the data to fetch.

    Returns:
        A list of data points, specifically a list of tuples, each containing: [timestamp, low, high, open, close, volume]
    '''
    url = f"{BASE_URL}/products/{product_id}/candles"
    params = {
        "start": start,
        "end": end,
        "granularity": granularity,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def format_candles(candles:list, product_id: str) -> list:
    # Convert the raw data into readable dicttionaty format
    formatted_candles = []
    for candle in candles:
        timestamp, low, high, open_price, close_price, volume = candle
        formatted_candles.append({
            "product" : product_id,
            "timestamp" : timestamp,
            "datetime" : datetime.datetime.utcfromtimestamp(timestamp).isoformat(),
            "open" : open_price,
            "close" : close_price,
            "high" : high,
            "low" : low,
            "volume" : volume,
        })
    # sort by timestamp
    formatted_candles.sort(key=lambda x: x["timestamp"])
    return formatted_candles

# main function to call
def main():
    product_id = "BTC-USD"
    start = "2025-11-17T00:00:00Z"
    end = "2025-11-24T23:59:59Z"

    coins = ['BTC-USD', 'ETH-USD']
    granularity = 3600

    all_data = {}

    for coin in coins:
        print(f"Fetching data for {coin}...")
        raw_candles = fetch_data(coin, start, end, granularity)
        formatted_candles = format_candles(raw_candles, coin)
        all_data[coin] = formatted_candles
        print(f"Successfully retrieved {len(formatted_candles)} candles")
    
    # Save to a JSON
    output_file = "coinbase_data.json"
    with open(output_file, "w") as f:
        json.dump(all_data, f, indent=4)
    print(f"Data saved to {output_file}")

    # Print the full summary of the data
    for coin, candles in all_data.items():
        if candles:
            print(f"\n{coin} Summary:")
            print(f"  Period: {candles[0]['datetime']} to {candles[-1]['datetime']}")
            print(f"  Candles: {len(candles)}")
            prices = [c['close'] for c in candles]
            volumes = [c['volume'] for c in candles]
            print(f"  Price range: ${min(prices):,.2f} - ${max(prices):,.2f}")
            print(f"  Total volume: {sum(volumes):,.2f}")
                                                    
if __name__ == "__main__":
    main()