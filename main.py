import os
import json
import requests
import gspread
from google.oauth2.service_account import Credentials


def send_slack(message: str):
    """Slack通知を送信"""
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})
    else:
        print("⚠️ Slack Webhook URLが設定されていません。")


def main():
    # ===============================
    # 🔐 Google認証設定
    # ===============================
    creds_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    if not creds_json:
        send_slack("❌ GCP認証情報が設定されていません。")
        return

    # GitHub Secrets に保存したJSON文字列を辞書に変換
    creds_dict = json.loads(creds_json)

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)

    # ===============================
    # 📄 スプレッドシート操作
    # ===============================
    SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
    if not SPREADSHEET_ID:
        send_slack("❌ SPREADSHEET_IDが設定されていません。")
        return

    sheet = client.open_by_key(SPREADSHEET_ID).sheet1

    # ✅ A1に書き込み
    sheet.update("A1", [["接続成功！"]])
    print("✅ A1セルに『接続成功！』と書き込みました。")

    # ✅ B1を読み取り
    value_b1 = sheet.acell("B1").value
    print(f"📗 B1セルの値: {value_b1 if value_b1 else '(空欄)'}")

    # Slackにも結果通知
    send_slack(
        f"✅ Google Sheets接続完了！\nA1: 接続成功！\nB1: {value_b1 or '(空欄)'}"
    )


if __name__ == "__main__":
    main()
