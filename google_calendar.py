import os
import json
import pickle
import base64
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# -------------------- CONSTANTS --------------------
SCOPES = ["https://www.googleapis.com/auth/calendar"]


# -------------------- HELPER: LƯU/ĐỌC TỪ ENV --------------------
def ensure_credentials_files():
    """
    Nếu trên Railway có biến môi trường GOOGLE_CREDENTIALS / GOOGLE_TOKEN
    thì ghi chúng ra file credentials.json / token.json để Google SDK dùng.
    """
    creds_env = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_env:
        with open("credentials.json", "w", encoding="utf-8") as f:
            f.write(creds_env)

    token_env = os.environ.get("GOOGLE_TOKEN")
    if token_env:
        try:
            token_data = json.loads(token_env)
        except json.JSONDecodeError:
            # Nếu lưu dưới dạng base64
            token_data = json.loads(base64.b64decode(token_env).decode("utf-8"))
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump(token_data, f)


# -------------------- LOGIN GOOGLE --------------------
def dang_nhap_google():
    """
    Đăng nhập Google Calendar API.
    Nếu chưa có token thì tạo flow OAuth và lưu lại token vào env/file.
    """
    creds = None

    # Load token từ file nếu có
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Nếu chưa có hoặc hết hạn
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            ensure_credentials_files()

            # Lấy credentials.json
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("Không tìm thấy credentials.json")

            redirect_uri = os.environ.get(
                "GOOGLE_REDIRECT_URI", "http://localhost:8501"
            )

            flow = Flow.from_client_secrets_file(
                "credentials.json", scopes=SCOPES, redirect_uri=redirect_uri
            )

            auth_url, _ = flow.authorization_url(prompt="consent")
            raise RuntimeError(
                f"⚠️ Chưa có token. Hãy mở link này để đăng nhập:\n{auth_url}"
            )

        # Lưu lại token ra file
        with open("token.json", "w") as token:
            token.write(creds.to_json())

        # Cập nhật vào biến môi trường (để dùng trên Railway)
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
    """
    Tạo sự kiện trên Google Calendar.
    """
    if service is None:
        raise ValueError("Service Google Calendar chưa được khởi tạo.")

    summary = f"{prefix} {mon}"
    if giang_vien:
        summary += f" - {giang_vien}"
    location = phong

    event = {
        "summary": summary,
        "location": location,
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
    """
    Xoá tất cả sự kiện có prefix trên Google Calendar.
    """
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
