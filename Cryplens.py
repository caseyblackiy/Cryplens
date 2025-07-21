import requests
import datetime
import time
from collections import defaultdict
import statistics

ETHERSCAN_API_KEY = "YourEtherscanAPIKeyHere"  # <-- Добавь свой ключ

def fetch_transactions(address, startblock=0, endblock=99999999):
    url = f"https://api.etherscan.io/api"
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": startblock,
        "endblock": endblock,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get("result", [])

def analyze_behavior(transactions):
    if not transactions:
        return {"error": "Нет транзакций"}

    time_deltas = []
    values_eth = []
    unknown_tokens = set()

    last_timestamp = None
    for tx in transactions:
        ts = int(tx["timeStamp"])
        val_eth = int(tx["value"]) / 1e18

        values_eth.append(val_eth)

        if last_timestamp:
            delta = ts - last_timestamp
            time_deltas.append(delta)
        last_timestamp = ts

        if tx.get("tokenName") in [None, "", "Unknown"]:
            unknown_tokens.add(tx.get("contractAddress"))

    outliers = detect_outliers(values_eth)
    average_delta = sum(time_deltas) / len(time_deltas) if time_deltas else None

    return {
        "total_tx": len(transactions),
        "avg_tx_gap_sec": average_delta,
        "large_tx_values": outliers,
        "unknown_tokens": list(unknown_tokens)
    }

def detect_outliers(data):
    if len(data) < 3:
        return []
    mean = statistics.mean(data)
    stdev = statistics.stdev(data)
    return [x for x in data if abs(x - mean) > 2 * stdev and x > 1.0]

def run_analysis(address):
    print(f"[+] Анализируем адрес: {address}")
    txs = fetch_transactions(address)
    result = analyze_behavior(txs)
    print("\n[✓] Результаты анализа:")
    for key, value in result.items():
        print(f" - {key}: {value}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Использование: python cryplens.py <Ethereum_адрес>")
        sys.exit(1)
    run_analysis(sys.argv[1])

