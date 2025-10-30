import os
import requests


def main():
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️ SLACK_WEBHOOK_URLが設定されていません。")
        return

    message = {"text": "🐍 PythonからのSlack通知テストです！"}
    response = requests.post(webhook_url, json=message)

    if response.status_code == 200:
        print("✅ Slackに通知を送信しました。")
    else:
        print(f"❌ Slack送信エラー: {response.text}")


if __name__ == "__main__":
    main()
