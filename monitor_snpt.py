import requests
import json

# 監視するウォレットアドレスとコントラクトアドレス
SENDER_ADDRESS = "0x288e7b339a17075114c28d902e45af78da44543f"
RECIPIENT_ADDRESS = "0xe7ee1d51f58a450552ff45c37630335d534ce9e3"
CONTRACT_ADDRESS = "0x22737f5bbb7c5b5ba407b0c1c9a9cdf66cf25d7d"
POLYGON_RPC_URL = "https://polygon-rpc.com"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1339531632675389452/XiNRFIVRGmbP1Hqheuh_vSY4n7AV1E-G2bx8NWmihHvAJA8pxm_Z4U4Nde-WczS23GgF"  # ここにDiscordのWebhook URLを記入

# 送金履歴を取得する関数
def get_transactions():
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getLogs",
        "params": [{
            "address": CONTRACT_ADDRESS,  # SNPTコントラクトのアドレス
            "fromBlock": "latest",
            "toBlock": "latest",
            "topics": [
                None,  # 任意のトピックフィルタ
                f"0x{SENDER_ADDRESS[2:].lower()}",  # 送信者のアドレス
                f"0x{RECIPIENT_ADDRESS[2:].lower()}",  # 受信者のアドレス
            ]
        }],
        "id": 1
    }

    response = requests.post(POLYGON_RPC_URL, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("result"):
            print(f"Found transaction: {data['result']}")
            send_discord_notification(data['result'])
        else:
            print("No transaction found.")
    else:
        print("Failed to retrieve data", response.status_code)

# Discordに通知を送る関数
def send_discord_notification(transaction_data):
    # 通知メッセージの構築
    message = {
        "content": f"New SNPT transaction detected:\n{json.dumps(transaction_data, indent=2)}"
    }
    # DiscordへPOSTリクエスト
    response = requests.post(DISCORD_WEBHOOK_URL, data=message)
    if response.status_code == 204:
        print("Notification sent to Discord!")
    else:
        print(f"Failed to send notification: {response.status_code}")

# 実行
get_transactions()
