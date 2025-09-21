import os
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import streamlit as st

# Phạm vi quyền cho Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']


# ---------------- Đảm bảo có file credentials/token ----------------
def ensure_credentials_files():
    creds_str = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_str:
        with open("credentials.json", "w", encoding="utf-8") as f:
            f.write(creds_str)
        print("✅ Đã tạo credentials.json từ biến môi trường")
    else:
        print("❌ Không tìm thấy GOOGLE_CREDENTIALS")

    token_str = os.environ.get("GOOGLE_TOKEN")
    if token_str:
        with open("token.json", "w", encoding="utf-8") as f:
            f.write(token_str)
        print("✅ Đã tạo token.json từ biến môi trường")
    else:
        print("⚠️ Không tìm thấy GOOGLE_TOKEN")


# ---------------- Đăng nhập Google ----------------
def dang_nhap_google():
    # Luôn tạo lại credentials.json và token.json từ biến môi trường
    ensure_credentials_files()

    creds = None
    # Đọc token nếu có
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            print("🔑 Đọc token.json thành công")
        except Exception as e:
            st.error(f"Lỗi khi đọc token.json: {e}")
            print(f"❌ Lỗi khi đọc token.json: {e}")

    # Refresh nếu token hết hạn
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            print("🔄 Refresh token thành công")
        except Exception as e:
            st.error(f"Lỗi refresh token: {e}")
            print(f"❌ Lỗi refresh token: {e}")
            creds = None

    # Nếu không có token hợp lệ thì login (chỉ local mới dùng được)
    if not creds or not creds.valid:
        if not os.path.exists("credentials.json"):
            raise FileNotFoundError("❌ Không tìm thấy credentials.json")
        try:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)  # Railway không mở browser được
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            print("✅ Đăng nhập Google thành công (local)")
        except Exception as e:
            st.error(f"Lỗi đăng nhập Google: {e}")
            print(f"❌ Lỗi đăng nhập Google: {e}")

    # Trả về service để gọi API Calendar
    service = build('calendar', 'v3', credentials=creds)
    return service


# ---------------- Tạo sự kiện ----------------
def tao_su_kien(service, mon, phong, giang_vien,
                start_date, end_date, weekday, start_time, end_time,
                reminders=None, prefix="[TKB]"):

    # Parse ngày
    start_date = dt.datetime.strptime(start_date.strip(), "%d/%m/%Y").date()
    end_date = dt.datetime.strptime(end_date.strip(), "%d/%m/%Y").date()

    # Google weekday: 0=Mon, 6=Sun
    google_weekday = weekday - 2
    if google_weekday < 0:
        google_weekday = 6

    current = start_date
    while current.weekday() != google_weekday:
        current += dt.timedelta(days=1)

    start_dt = dt.datetime.strptime(
        f"{current.strftime('%d/%m/%Y')} {start_time}", "%d/%m/%Y %H:%M"
    )
    end_dt = dt.datetime.strptime(
        f"{current.strftime('%d/%m/%Y')} {end_time}", "%d/%m/%Y %H:%M"
    )

    # Mô tả sự kiện
    description = f"Phòng: {phong}"
    if giang_vien and str(giang_vien).strip().lower() not in ["none", "nan", ""]:
        description += f"\nGiảng viên: {giang_vien}"

    event = {
        'summary': f"{prefix} {mon}",
        'location': phong,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Asia/Ho_Chi_Minh'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Asia/Ho_Chi_Minh'},
        'recurrence': [f"RRULE:FREQ=WEEKLY;UNTIL={end_date.strftime('%Y%m%d')}T235959Z"],
        'reminders': {'useDefault': False, 'overrides': reminders if reminders else []}
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"📅 Đã tạo sự kiện: {created_event.get('summary')}")
    return created_event.get('id')


# ---------------- Xoá sự kiện theo prefix ----------------
def xoa_su_kien_tkb(service, prefix="[TKB]"):
    events_result = service.events().list(
        calendarId='primary', singleEvents=True, orderBy='startTime', maxResults=2500
    ).execute()
    events = events_result.get('items', [])

    count = 0
    for event in events:
        if 'summary' in event and event['summary'].startswith(prefix):
            service.events().delete(calendarId='primary', eventId=event['id']).execute()
            count += 1

    print(f"🗑️ Đã xoá {count} sự kiện có prefix '{prefix}'")
    return count
