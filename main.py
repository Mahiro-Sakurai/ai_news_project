import os
import requests
from datetime import datetime


def send_slack(message: str):
    """Slack通知を送る関数"""
    webhook_url = os.environ.get("SLACK_WEBHOOK")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})
    else:
        print("⚠️ Slack Webhook URLが設定されていません")


def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    send_slack(f"📰 AIニュース自動生成処理開始 ({now})")

    # --- ここにメイン処理を記述する ---
    # 例：ClaudeやGeminiにリクエストして要約・記事生成
    print("AIニュース処理を実行中...")
    # -------------------------------

    send_slack(f"✅ AIニュース生成完了 ({now})")


if __name__ == "__main__":
    main()
