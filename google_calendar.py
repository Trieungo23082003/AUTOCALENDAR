import os
import datetime as dt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

import streamlit as st
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']

# ---------------- Đọc credentials từ biến môi trường ----------------
def _load_client_config():
    creds_str = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_str:
        raise RuntimeError("❌ Thiếu GOOGLE_CREDENTIALS env")
    creds_str = creds_str.strip().replace('\\n', '\n')
    return json.loads(creds_str)

# ---------------- Lấy URL đăng nhập Google ----------------
def get_auth_url():
    client_config = _load_client_config()
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")
    if not redirect_uri:
        raise RuntimeError("❌ Thiếu GOOGLE_REDIRECT_URI env")

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url

# ---------------- Đổi code thành token ----------------
def exchange_code_for_token(code: str):
    client_config = _load_client_config()
    redirect_uri = os.environ.get("GOOGLE_REDIRECT_URI")

    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    flow.fetch_token(code=code)
    creds = flow.credentials
    return build("calendar", "v3", credentials=creds)

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
    return created_event.get('id')

# ---------------- Xoá sự kiện ----------------
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
