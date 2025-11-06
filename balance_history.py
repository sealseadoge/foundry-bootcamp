#!/usr/bin/env python3
import os, sys, requests, pandas as pd

ALCHEMY_URL = os.getenv("ALCHEMY_URL") or "https://eth-mainnet.g.alchemy.com/v2/你的KEY"
HEADERS = {"Content-Type": "application/json"}

def eth_call(method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    r = requests.post(ALCHEMY_URL, headers=HEADERS, json=payload, timeout=10)
    resp = r.json()
    if resp.get("error"):
        print("Alchemy 错误:", resp["error"])
        return None
    return resp.get("result")

def main(address):
    balance_wei = int(eth_call("eth_getBalance", [address, "latest"]) or 0, 16)
    balance_eth = balance_wei / 1e18
    print(f"地址 {address} 余额：{balance_eth:.4f} ETH")

    # 改用 fromBlock=0x0 toBlock=latest 且分页 Key 为空
    result = eth_call("alchemy_getAssetTransfers", [{
        "fromBlock": "0x0",
        "toBlock": "latest",
        "address": address,
        "category": ["external", "internal", "erc20"],
        "maxCount": "0x64"  # 100 条
    }])
    if not result or not result.get("transfers"):
        print("该地址无转账记录或达到限额。")
        return

    df = pd.DataFrame(result["transfers"])[["hash", "from", "to", "value", "asset", "blockNum"]]
    df["value"] = pd.to_numeric(df["value"], errors="coerce") / 1e18
    print(df.head())
    csv_file = f"{address}_tx100.csv"
    df.to_csv(csv_file, index=False)
    print(f"已保存 {csv_file}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python3 balance_history.py 0x地址")
        sys.exit(1)
    main(sys.argv[1])
