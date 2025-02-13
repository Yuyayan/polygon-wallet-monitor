import requests
import json
import time

# Polygon RPC URL (Mainnet)
POLYGON_RPC_URL = "https://polygon-rpc.com"

# 監視対象のウォレットアドレス（送信元）
WATCH_WALLET = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3"

# 監視対象のSNPTコントラクトアドレス
SNPT_CONTRACT_ADDRESS = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d"

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/your-webhook-url"

# 最後に取得したブロック番号（最初は0）
last_block = 0

def send_to_discord(message):
    """Discordにメッセージを送信"""
    payload = {"content": message}
    headers = {"Content-Type": "application/json"}
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(payload), headers=headers)

    if response.status_code != 204:
        print(f"Error sending message to Discord: {response.status_code}")
    else:
        print("Message sent to Discord")

def get_transactions_from_block(block_number):
    """指定したブロック番号からトランザクションを取得"""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [{
            "fromBlock": hex(block_number),
            "toBlock": hex(block_number),
            "address": SNPT_CONTRACT_ADDRESS
        }],
        "id": 1
    }

    response = requests.post(POLYGON_RPC_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("result", [])
    else:
        print(f"Failed to retrieve transactions: {response.status_code}")
        return []

def monitor():
    global last_block
    while True:
        # 最新のブロック番号を取得
        payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 1
        }

        response = requests.post(POLYGON_RPC_URL, json=payload)
        if response.status_code == 200:
            latest_block = int(response.json()['result'], 16)

            # 新しいブロックが来た場合にチェック
            if latest_block > last_block:
                print(f"New block detected: {latest_block}")
                for block in range(last_block + 1, latest_block + 1):
                    print(f"Checking transactions for block {block}")
                    transactions = get_transactions_from_block(block)
                    for tx in transactions:
                        # 送信元アドレスが監視対象ウォレットか確認
                        if tx.get('from').lower() == WATCH_WALLET.lower():
                            message = f"New SNPT transfer detected from {WATCH_WALLET}:\n" \
                                      f"Tx Hash: {tx['transactionHash']}\n" \
                                      f"Block: {block}\n"
                            send_to_discord(message)
                
                # 最新のブロックを記録
                last_block = latest_block
            else:
                print("No new blocks detected.")
        else:
            print(f"Failed to retrieve latest block: {response.status_code}")

        # 10秒待機して次回チェック
        time.sleep(10)

if __name__ == "__main__":
    monitor()
