import os, json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta, timezone
import requests


def send_slack(msg):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        requests.post(webhook, json={"text": msg})


def main():
    # 🔐 Google認証
    creds_json = os.environ.get("GCP_SERVICE_ACCOUNT_JSON")
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ],
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ["SPREADSHEET_ID"]).sheet1

    # ==============================
    # 1️⃣ プロンプト読み込み
    # ==============================
    prompt_row = sheet.row_values(2)
    prompt_investigate = prompt_row[2] if len(prompt_row) > 0 else ""
    prompt_write = prompt_row[3] if len(prompt_row) > 1 else ""

    print(f"調査プロンプト: {prompt_investigate}")
    print(f"執筆プロンプト: {prompt_write}")

    # ==============================
    # 2️⃣ ダミーAI結果（後でClaude/Geminiに置き換え）
    # ==============================
    dummy_investigation = "（仮）今日のAIニュース: OpenAIが新モデルを発表。"
    dummy_article = "（仮）この記事では新モデルの特徴と影響を解説します。"
    char_count = len(dummy_article)

    # ==============================
    # 3️⃣ 書き込み（JST時刻付き）
    # ==============================
    existing = len(sheet.get_all_values())
    next_row = existing + 1 if existing >= 4 else 4

    # 🇯🇵 日本時間に変換（UTC+9）
    JST = timezone(timedelta(hours=9))
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

    values = [["", now_jst, dummy_investigation, dummy_article, char_count]]

    sheet.update(f"A{next_row}:E{next_row}", values)

    print(f"✅ {next_row} 行目に書き込み完了（JST: {now_jst}）")
    send_slack(
        f"✅ スプシ更新完了！\n{next_row} 行目（JST: {now_jst}）に書き込みました！"
    )


if __name__ == "__main__":
    main()
