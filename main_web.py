import streamlit as st
import io
import os
import traceback

from read_excel import doc_tkb
from read_excel_teacher import doc_tkb_giangvien
from google_calendar import dang_nhap_google, tao_su_kien


# ---------------- Helper ----------------
def get_uploaded_bytes(uploaded_file):
    """Lưu bytes của file upload vào session_state để reuse sau rerun"""
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
    st.title("📅 AutoCalendar - TKB lên Google Calendar")

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

                    st.session_state["preview_events"] = events
                except Exception as e:
                    show_exception(e)

        if "preview_events" in st.session_state and st.session_state["preview_events"]:
            events = st.session_state["preview_events"]
            st.success(f"✅ Đã đọc được {len(events)} sự kiện")
            st.dataframe(events)
        else:
            st.info("Chưa có dữ liệu xem trước. Bấm '👀 Xem trước' để đọc file.")

        # ---------------- KIỂM TRA CREDENTIALS ----------------
        has_credentials = os.path.exists("credentials.json") or bool(
            os.environ.get("GOOGLE_CREDENTIALS")
        )
        has_token = os.path.exists("token.json") or bool(os.environ.get("GOOGLE_TOKEN"))

        if not has_credentials:
            st.info(
                "⚠️ Chưa có credentials.json. Trên Railway hãy đặt biến môi trường "
                "`GOOGLE_CREDENTIALS` (nội dung file credentials.json)."
            )
        if not has_token:
            st.info(
                "⚠️ Chưa có token.json. Hãy chạy local để sinh token.json, "
                "sau đó copy nội dung vào biến môi trường `GOOGLE_TOKEN` trên Railway."
            )

        # Debug (không in bí mật, chỉ trạng thái)
        with st.expander("🔧 Debug môi trường (chỉ hiển thị trạng thái)"):
            creds_env = os.environ.get("GOOGLE_CREDENTIALS")
            token_env = os.environ.get("GOOGLE_TOKEN")
            st.write("GOOGLE_CREDENTIALS present:", bool(creds_env))
            st.write("GOOGLE_CREDENTIALS length (chars):", len(creds_env) if creds_env else 0)
            st.write("GOOGLE_TOKEN present:", bool(token_env))
            st.write("GOOGLE_TOKEN length (chars):", len(token_env) if token_env else 0)
            if st.button("Ghi env -> file (dùng để kiểm tra)"):
                try:
                    from google_calendar import ensure_credentials_files
                    ensure_credentials_files()
                    st.success("Đã ghi credentials.json/token.json từ biến môi trường (nếu có).")
                except Exception as e:
                    st.error(f"Lỗi khi ghi file từ env: {e}")

        # ---------------- TẠO SỰ KIỆN ----------------
        if st.button("📅 Tạo sự kiện trên Google Calendar"):
            try:
                events = st.session_state.get("preview_events")
                if not events:
                    st.warning("⚠️ Chưa có dữ liệu sự kiện. Hãy bấm '👀 Xem trước' trước.")
                else:
                    if not (has_credentials and has_token):
                        st.error("❌ Thiếu credentials/token. Không thể đăng nhập Google.")
                    else:
                        with st.spinner("⏳ Đang tạo sự kiện trên Google Calendar..."):
                            service = dang_nhap_google()
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
                                        reminders=[
                                            {"method": "popup", "minutes": 10}
                                        ],
                                        prefix=prefix,
                                    )
                                    created += 1
                                except Exception as sub_e:
                                    st.warning(
                                        f"Lỗi tạo event '{e.get('mon')}' — {sub_e}"
                                    )
                            st.success(f"✅ Hoàn tất! Đã tạo {created} sự kiện.")
            except Exception as e:
                show_exception(e)

    else:
        st.info("⬆️ Vui lòng tải lên file Excel để bắt đầu.")


if __name__ == "__main__":
    main()
