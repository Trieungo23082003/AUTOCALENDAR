import os
import json
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


# -------------------- GHI FILE CREDENTIALS/TOKEN TỪ ENV --------------------
def ensure_credentials_files():
    creds_env = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_env:
        with open("credentials.json", "w", encoding="utf-8") as f:
            f.write(creds_env)

    token_env = os.environ.get("GOOGLE_TOKEN")
    if token_env:
        try:
            token_data = json.loads(token_env)
        except json.JSONDecodeError:
            token_data = json.loads(base64.b64decode(token_env).decode("utf-8"))
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump(token_data, f)


# -------------------- ĐĂNG NHẬP GOOGLE --------------------
def dang_nhap_google():
    creds = None

    # Nếu đã có token.json thì dùng lại
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Nếu chưa có hoặc hết hạn
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            ensure_credentials_files()
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("❌ Không tìm thấy credentials.json")

            # ⚠️ Quan trọng: ép redirect_uri = domain Railway
            redirect_uri = os.environ.get(
                "GOOGLE_REDIRECT_URI", "https://autocalendar-production.up.railway.app"
            )

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES, redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(prompt="consent")
            raise RuntimeError(
                f"⚠️ Chưa có token. Mở link này để đăng nhập:\n{auth_url}"
            )

        # Lưu token ra file
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        # Lưu vào env (Railway)
        os.environ["GOOGLE_TOKEN"] = creds.to_json()

    return build("calendar", "v3", credentials=creds)


# -------------------- TẠO SỰ KIỆN --------------------
def tao_su_kien(
    service,
    mon,
    phong,
    giang_vien,
    start_date,
    end_date,
    weekday,
    start_time,
    end_time,
    reminders,
    prefix,
):
    if service is None:
        raise ValueError("Service Google Calendar chưa được khởi tạo.")

    summary = f"{prefix} {mon}"
    if giang_vien:
        summary += f" - {giang_vien}"

    event = {
        "summary": summary,
        "location": phong,
        "description": "Tự động tạo bởi AutoCalendar",
        "start": {
            "dateTime": f"{start_date}T{start_time}:00",
            "timeZone": "Asia/Ho_Chi_Minh",
        },
        "end": {
            "dateTime": f"{start_date}T{end_time}:00",
            "timeZone": "Asia/Ho_Chi_Minh",
        },
        "recurrence": [
            f"RRULE:FREQ=WEEKLY;BYDAY={weekday};UNTIL={end_date.replace('-','')}T235959Z"
        ],
        "reminders": {"useDefault": False, "overrides": reminders},
    }

    service.events().insert(calendarId="primary", body=event).execute()


# -------------------- XOÁ SỰ KIỆN --------------------
def xoa_su_kien_tkb(service, prefix="[TKB]"):
    if service is None:
        raise ValueError("Service Google Calendar chưa được khởi tạo.")

    events_result = service.events().list(calendarId="primary").execute()
    events = events_result.get("items", [])

    count = 0
    for event in events:
        if event.get("summary", "").startswith(prefix):
            service.events().delete(
                calendarId="primary", eventId=event["id"]
            ).execute()
            count += 1
    return count
