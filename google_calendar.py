import os
import datetime as dt
import streamlit as st

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Phạm vi quyền cho Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Lấy URL domain của app từ ENV (nếu không có thì mặc định local)
REDIRECT_URI = os.environ.get(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8501"
)


def dang_nhap_google():
    """
    Hàm xử lý OAuth login.
    Nếu chưa đăng nhập → hiển thị nút login.
    Nếu đăng nhập rồi → trả về service Google Calendar.
    """

    # Đọc credentials.json từ biến môi trường GOOGLE_CREDENTIALS
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        st.error("❌ Thiếu GOOGLE_CREDENTIALS trong biến môi trường Railway.")
        return None

    # Kiểm tra session đã có token chưa
    if "google_token" not in st.session_state:
        flow = Flow.from_client_config(
            eval(creds_json),  # chuyển string JSON → dict
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI,
        )

        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )

        st.markdown(f"[👉 Đăng nhập với Google]({auth_url})")
        return None

    # Nếu đã có token → tạo credentials
    creds = Credentials.from_authorized_user_info(
        st.session_state["google_token"], SCOPES
    )

    # Refresh token nếu hết hạn
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    # Tạo service
    service = build("calendar", "v3", credentials=creds)
    return service


def luu_token(token_dict):
    """Lưu token Google vào session"""
    st.session_state["google_token"] = token_dict


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
    return created_event.get('id')


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

    return count
