import os
import datetime as dt
import json
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import streamlit as st

# Phạm vi quyền cho Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

def _normalize_env_value(s: str) -> str:
    if s is None:
        return None
    s = str(s).strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1]
    s = s.replace('\\n', '\n')
    return s

# ---------------- Đảm bảo có file credentials ----------------
def ensure_credentials_files():
    creds_str = os.environ.get("GOOGLE_CREDENTIALS")
    creds_str = _normalize_env_value(creds_str)
    if creds_str:
        try:
            with open("credentials.json", "w", encoding="utf-8") as f:
                f.write(creds_str)
            print(f"✅ Đã tạo credentials.json từ biến môi trường (chiều dài: {len(creds_str)} chars)")
        except Exception as e:
            print(f"❌ Lỗi khi ghi credentials.json: {e}")
    else:
        print("❌ Không tìm thấy GOOGLE_CREDENTIALS")

# ---------------- Đăng nhập Google ----------------
def dang_nhap_google():
    ensure_credentials_files()

    # Load config từ credentials.json
    with open("credentials.json", "r", encoding="utf-8") as f:
        creds_config = json.load(f)

    flow = Flow.from_client_config(
    creds_config,
    scopes=SCOPES,
    redirect_uri="https://autocalendar-production.up.railway.app"
) 
    # 🚨 Khi deploy Railway: đổi redirect_uri thành URL Railway

    if "code" not in st.query_params:
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.markdown(f"[👉 Đăng nhập Google để cấp quyền]({auth_url})")
        return None
    else:
        code = st.query_params["code"]
        flow.fetch_token(code=code)
        creds = flow.credentials
        service = build("calendar", "v3", credentials=creds)
        return service

# ---------------- Tạo sự kiện ----------------
def tao_su_kien(service, mon, phong, giang_vien,
                start_date, end_date, weekday, start_time, end_time,
                reminders=None, prefix="[TKB]"):

    start_date = dt.datetime.strptime(start_date.strip(), "%d/%m/%Y").date()
    end_date = dt.datetime.strptime(end_date.strip(), "%d/%m/%Y").date()

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

