#!/usr/bin/env python3
"""
block_alert_once.py
监听最新区块 → 最大≥阈值交易 → 推送 Telegram（一次性）
依赖：requests
"""
import os, requests, time
from decimal import Decimal

os.environ["https_proxy"] = "http://192.168.225.1:7890"
os.environ["http_proxy"]  = "http://192.168.225.1:7890"

ALCHEMY_URL = os.getenv("ALCHEMY_URL") or "https://eth-mainnet.g.alchemy.com/v2/你的KEY"
BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("请先 export TG_BOT_TOKEN")
CHAT_ID     = os.getenv("TG_CHAT_ID")
if not CHAT_ID:
    raise RuntimeError("请先 export TG_CHAT_ID")
THRESHOLD   = 10          # ETH

# ---------- 工具 ----------
def eth_call(method, params):
    r = requests.post(ALCHEMY_URL, json={"jsonrpc":"2.0","id":1,"method":method,"params":params}, timeout=10)
    return r.json().get("result")

# ---------- 主逻辑 ----------
def main():
    # 1. 最新块号
    block_num = eth_call("eth_blockNumber", [])
    if not block_num:
        print("获取最新块号失败")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": "获取最新块号失败"})
        return
    print("监听区块:", int(block_num, 16))

    # 2. 获取区块内交易
    block = eth_call("eth_getBlockByNumber", [block_num, True])
    if not block or not block.get("transactions"):
        print("区块无交易")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": "没有超过阈值的"})
        return

    # 3. 找最大≥阈值的交易
    max_tx = None
    max_val = 0
    for tx in block["transactions"]:
        val_wei = int(tx.get("value", "0x0"), 16)
        val_eth = float(Decimal(val_wei) / Decimal(10**18))
        if val_eth >= THRESHOLD and val_eth > max_val:
            max_val = val_eth
            max_tx = tx

    # 4. 输出 & 推送
    if max_tx:
        msg = f"🐋 新区块大额交易！\n区块：{int(block_num, 16)}\n交易额：{max_val:.4f} ETH\n哈希：{max_tx['hash']}"
        print("有超过阈值的，交易额为：", max_val)
    else:
        msg = "没有超过阈值的"
    r = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                  data={"chat_id": CHAT_ID, "text": msg},timeout=10)
    print("【DEBUG】Telegram status:", r.status_code, r.text)
    print(msg)
    
if __name__ == "__main__":
    main()
