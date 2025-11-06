#!/usr/bin/env python3
"""
whale_alert.py
扫描地址 → 大额转账 → Telegram 推送
依赖：requests python-telegram-bot
"""
import os, time, requests
from telegram import Bot

ALCHEMY_URL = os.getenv("ALCHEMY_URL") or "https://eth-mainnet.g.alchemy.com/v2/你的KEY"
BOT_TOKEN   = "8473342497:AAHq32ZpBRAvzdAR-IPdETPnOaiCTNFt0b8"  # 替换
CHAT_ID     = 5669443848                                # 替换
THRESHOLD   = 0.1  # ETH

bot = Bot(token=BOT_TOKEN)

def eth_call(method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    r = requests.post(ALCHEMY_URL, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
    return r.json().get("result")

def scan_address(address):
    # 获取最新一笔转账
    result = eth_call("alchemy_getAssetTransfers", [{
         "fromBlock": hex(max(0, int(eth_call("eth_blockNumber", []), 16) - 100)),  # 最近 100 块
        "toBlock": "latest",
        "address": address,
        "category": ["external","internal","erc20"],
        "maxCount": "0x5"
    }])
  # print("DEBUG result:", result)   # 看每次返回什么
    if not result or not result.get("transfers"):
        print("无新的交易")
        return
    tx = result["transfers"][0]
    value_eth = int(tx["value"]) / 1e18
    print("value_eth = ",value_eth)
    if value_eth >= THRESHOLD:
        msg = f"🐋 大额异动！\n地址：{address}\n金额：{value_eth:.2f} ETH\n哈希：{tx['hash']}"
        print("【准备推送】金额=", value_eth, "阈值=", THRESHOLD)
        bot.send_message(chat_id=CHAT_ID, text=msg)
        print("已推送：", msg)

if __name__ == "__main__":
    target = "0x28C6c06298d514Db089934071355E5743bf21d60"  # 可改
    while True:
        scan_address(target)
        time.sleep(60)  # 每分钟扫一次
