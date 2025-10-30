import os, json, requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta, timezone

# ===============================================
# 🔧 設定
# ===============================================
CLAUDE_MODEL = "claude-opus-4-20250514"  # ← モデル名を変更可能（Sonnet / Opusなど）


# ===============================================
# 🚀 Slack通知関数
# ===============================================
def send_slack(msg):
    webhook = os.environ.get("SLACK_WEBHOOK_URL")
    if webhook:
        requests.post(webhook, json={"text": msg})


# ===============================================
# 🤖 Anthropic Claude API呼び出し
# ===============================================
def call_claude(prompt: str):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Anthropic APIキーが設定されていません。")

    headers = {
        "x-api-key": api_key,
        "content-type": "application/json",
        "anthropic-version": "2023-06-01",
    }

    data = {
        "model": CLAUDE_MODEL,
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": prompt}],
    }

    res = requests.post(
        "https://api.anthropic.com/v1/messages", headers=headers, json=data
    )
    res.raise_for_status()
    result = res.json()["content"][0]["text"]
    return result.strip()


# ===============================================
# 📄 Google Sheets操作
# ===============================================
def main():
    # 認証
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
    # 2️⃣ Claudeでニュース調査・執筆
    # ==============================
    try:
        investigate_result = call_claude(prompt_investigate)
        write_prompt = f"{prompt_write}\n\n【参考情報】\n{investigate_result}"
        article_result = call_claude(write_prompt)
    except Exception as e:
        send_slack(f"❌ Claude APIエラー: {e}")
        raise

    char_count = len(article_result)

    # ==============================
    # 3️⃣ スプシ書き込み（日本時間）
    # ==============================
    existing = len(sheet.get_all_values())
    next_row = existing + 1 if existing >= 4 else 4

    JST = timezone(timedelta(hours=9))
    now_jst = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")

    sheet.update(
        f"A{next_row}:E{next_row}",
        [["", now_jst, investigate_result, article_result, char_count]],
    )

    # ==============================
    # 4️⃣ Slack通知
    # ==============================
    send_slack(
        f"✅ Claude記事生成完了！\n"
        f"📄 行番号: {next_row}\n"
        f"🕒 JST: {now_jst}\n"
        f"📝 文字数: {char_count}"
    )

    print("✅ スプレッドシート更新完了。")


if __name__ == "__main__":
    main()
