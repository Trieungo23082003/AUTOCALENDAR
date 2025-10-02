import streamlit as st
import io
import os
import traceback
import secrets

from read_excel import doc_tkb
from read_excel_teacher import doc_tkb_giangvien
from google_calendar import (
    get_auth_url,
    exchange_code_for_token,
    tao_su_kien,
    xoa_su_kien_tkb,
)


# ---------------- Helper ----------------
def get_uploaded_bytes(uploaded_file):
    if uploaded_file is None:
        return None
    if (
        "uploaded_name" not in st.session_state
        or st.session_state["uploaded_name"] != uploaded_file.name
    ):
        st.session_state["uploaded_bytes"] = uploaded_file.read()
        st.session_state["uploaded_name"] = uploaded_file.name
    return st.session_state.get("uploaded_bytes")


def show_exception(e):
    st.error(f"Lỗi: {e}")
    st.exception(traceback.format_exc())


# ---------------- Streamlit App ----------------
def main():
    st.set_page_config(page_title="AutoCalendar", layout="wide")
    
    # 🎨 CSS custom
    st.markdown(
        """
        <style>
        /* Nền xanh dương lợt */
        .stApp {
            background-color: #f0f6ff;
        }

        /* Khung container */
        .block-container {
            background: #ffffff;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            max-width: 900px;
        }

        /* Tiêu đề */
        h1, h2, h3 {
            color: #1e40af;
            text-align: center;
            font-weight: 700;
        }

        /* Radio button */
        div[role="radiogroup"] > label {
            background: #f9fbff;
            border: 2px solid #2563eb;
            border-radius: 8px;
            color: #2563eb;
            padding: 6px 16px;
            margin-right: 8px;
            cursor: pointer;
            transition: 0.3s;
        }
        div[role="radiogroup"] > label:hover {
            background: #eef4ff;
        }
        div[role="radiogroup"] > label[data-baseweb="radio"]:has(input:checked) {
            background: #2563eb;
            color: white !important;
        }

        /* Upload box */
        .stFileUploader {
            border: 2px dashed #60a5fa !important;
            border-radius: 12px;
            background: #f9fbff;
            padding: 1rem;
        }
        .stFileUploader:hover {
            border-color: #2563eb !important;
            background: #eef4ff;
        }

        /* Nút bấm */
        button[kind="primary"] {
            background-color: #2563eb;
            color: white;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
            transition: 0.3s;
        }
        button[kind="primary"]:hover {
            background-color: #1e40af;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title("📅 AutoCalendar - TKB lên Google Calendar")

    # --- Đăng nhập Google ---
    query_params = st.query_params  # Streamlit 1.27+
    if "code" in query_params and "google_service" not in st.session_state:
        code = query_params["code"]
        try:
            service = exchange_code_for_token(code)
            st.session_state["google_service"] = service
            st.success("✅ Đăng nhập Google thành công!")
        except Exception as e:
            show_exception(e)

    if "google_service" not in st.session_state:
        # Sinh state random cho từng session
        login_url, state = get_auth_url()
        st.session_state["oauth_state"] = state
        st.markdown(f"[🔑 Đăng nhập Google]({login_url})")
        st.stop()

    service = st.session_state["google_service"]

    # --- App logic sau khi login ---
    mode = st.radio("Chế độ:", ["Sinh viên", "Giảng viên"])

    ten_gv = ""
    if mode == "Giảng viên":
        ten_gv = st.text_input("Nhập tên giảng viên:")

    prefix = st.text_input("Prefix sự kiện:", "[TKB]")

    file_excel = st.file_uploader("Tải lên file Excel TKB", type=["xls", "xlsx"])
    file_bytes = get_uploaded_bytes(file_excel)

    if file_excel and file_bytes:
        st.write(f"Đã tải file: {file_excel.name} ({len(file_bytes)} bytes)")

        # ---------------- XEM TRƯỚC ----------------
        if st.button("👀 Xem trước"):
            with st.spinner("⏳ Đang xử lý dữ liệu..."):
                try:
                    bio = io.BytesIO(file_bytes)
                    if mode == "Sinh viên":
                        events = doc_tkb(bio)
                    else:
                        if not ten_gv:
                            st.warning("Hãy nhập tên giảng viên.")
                            events = []
                        else:
                            events = doc_tkb_giangvien(bio, ten_gv)

                    for e in events:
                        e["checked"] = True
                    st.session_state["preview_events"] = events
                except Exception as e:
                    show_exception(e)

        # ---------------- HIỂN THỊ PREVIEW ----------------
        if "preview_events" in st.session_state and st.session_state["preview_events"]:
            events = st.session_state["preview_events"]
            st.success(f"✅ Đã đọc được {len(events)} sự kiện")

            selected = []
            for idx, e in enumerate(events):
                checked = st.checkbox(
                    f"{e['mon']} - {e.get('phong','')} - {e.get('gio_bd','')}→{e.get('gio_kt','')}",
                    value=e.get("checked", True),
                    key=f"event_{idx}"
                )
                e["checked"] = checked
                if checked:
                    selected.append(e)

            st.session_state["selected_events"] = selected
        else:
            st.info("Chưa có dữ liệu xem trước. Bấm '👀 Xem trước' để đọc file.")

        # ---------------- TẠO SỰ KIỆN ----------------
        if st.button("📅 Tạo sự kiện trên Google Calendar"):
            try:
                events = st.session_state.get("selected_events", [])
                if not events:
                    st.warning("⚠️ Chưa chọn sự kiện nào.")
                else:
                    with st.spinner("⏳ Đang tạo sự kiện trên Google Calendar..."):
                        created = 0
                        for e in events:
                            try:
                                tao_su_kien(
                                    service=service,
                                    mon=e["mon"],
                                    phong=e.get("phong", ""),
                                    giang_vien=e.get("giang_vien", None),
                                    start_date=e["ngay_bat_dau"],
                                    end_date=e["ngay_ket_thuc"],
                                    weekday=e["thu"],
                                    start_time=e["gio_bd"],
                                    end_time=e["gio_kt"],
                                    reminders=[{"method": "popup", "minutes": 10}],
                                    prefix=prefix,
                                )
                                created += 1
                            except Exception as sub_e:
                                st.warning(f"Lỗi tạo event '{e.get('mon')}' — {sub_e}")
                        st.success(f"✅ Hoàn tất! Đã tạo {created} sự kiện.")
            except Exception as e:
                show_exception(e)

        # ---------------- XOÁ SỰ KIỆN ----------------
        if st.button("🗑️ Xoá toàn bộ sự kiện theo prefix"):
            try:
                with st.spinner(f"⏳ Đang xoá sự kiện prefix '{prefix}'..."):
                    count = xoa_su_kien_tkb(service, prefix=prefix)
                    st.success(f"🗑️ Đã xoá {count} sự kiện có prefix '{prefix}'.")
            except Exception as e:
                show_exception(e)

    else:
        st.info("⬆️ Vui lòng tải lên file Excel để bắt đầu.")


if __name__ == "__main__":
    main()



