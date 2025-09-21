import streamlit as st
from read_excel import doc_tkb
from read_excel_teacher import doc_tkb_giangvien
from google_calendar import dang_nhap_google, tao_su_kien, xoa_su_kien_tkb

# ------------------------------------------------------
# Hàm tạo sự kiện cho sinh viên
# ------------------------------------------------------
def len_lich(file_excel, remind_minutes, remind_method, prefix, events):
    try:
        st.write(f"📊 Lên lịch {len(events)} sự kiện sinh viên")

        if not events:
            st.warning("Không tìm thấy dữ liệu TKB sinh viên trong file.")
            return

        service = dang_nhap_google()
        reminders = [{"method": remind_method, "minutes": remind_minutes}]
        created_count = 0

        for e in events:
            if not e["gio_bd"] or not e["gio_kt"] or not e["thu"]:
                st.write(f"⏩ Bỏ qua: {e['mon']} - thiếu dữ liệu")
                continue

            tao_su_kien(
                service=service,
                mon=e["mon"],
                phong=e["phong"],
                giang_vien=e["giang_vien"],
                start_date=e["ngay_bat_dau"],
                end_date=e["ngay_ket_thuc"],
                weekday=e["thu"],
                start_time=e["gio_bd"],
                end_time=e["gio_kt"],
                reminders=reminders,
                prefix=prefix
            )
            st.success(f"✅ SV: {e['mon']} - {e['gio_bd']} → {e['gio_kt']} Thứ {e['thu']}")
            created_count += 1

        if created_count > 0:
            st.info(f"Đã lên lịch {created_count} sự kiện cho sinh viên!")
        else:
            st.warning("Không có sự kiện hợp lệ nào được tạo.")

    except Exception as ex:
        st.error(f"Lỗi: {ex}")


# ------------------------------------------------------
# Hàm tạo sự kiện cho giảng viên
# ------------------------------------------------------
def len_lich_gv(file_excel, ten_giangvien, remind_minutes, remind_method, prefix, events):
    try:
        st.write(f"📊 Lên lịch {len(events)} sự kiện cho giảng viên {ten_giangvien}")

        if not events:
            st.warning(f"Không tìm thấy TKB giảng viên '{ten_giangvien}' trong file.")
            return

        service = dang_nhap_google()
        reminders = [{"method": remind_method, "minutes": remind_minutes}]
        created_count = 0

        for e in events:
            if not e["gio_bd"] or not e["gio_kt"] or not e["thu"]:
                st.write(f"⏩ Bỏ qua: {e['mon']} ({e['giang_vien']}) - thiếu dữ liệu")
                continue

            tao_su_kien(
                service=service,
                mon=e["mon"],
                phong=e["phong"],
                giang_vien=None,
                start_date=e["ngay_bat_dau"],
                end_date=e["ngay_ket_thuc"],
                weekday=e["thu"],
                start_time=e["gio_bd"],
                end_time=e["gio_kt"],
                reminders=reminders,
                prefix=prefix
            )
            st.success(f"✅ GV: {e['mon']} ({e['giang_vien']}) - {e['gio_bd']} → {e['gio_kt']} Thứ {e['thu']}")
            created_count += 1

        if created_count > 0:
            st.info(f"Đã lên lịch {created_count} sự kiện cho giảng viên {ten_giangvien}!")
        else:
            st.warning("Không có sự kiện hợp lệ nào được tạo.")

    except Exception as ex:
        st.error(f"Lỗi: {ex}")


# ------------------------------------------------------
# Hàm xóa sự kiện TKB
# ------------------------------------------------------
def xoa_lich(prefix):
    try:
        service = dang_nhap_google()
        deleted_count = xoa_su_kien_tkb(service, prefix=prefix)
        st.success(f"🗑️ Đã xóa {deleted_count} sự kiện có prefix '{prefix}'.")
    except Exception as ex:
        st.error(f"Lỗi: {ex}")


# ------------------------------------------------------
# Giao diện chính (Streamlit)
# ------------------------------------------------------
def main():
    st.title("📅 Lên lịch thời khóa biểu tự động (Web)")

    # File Excel
    file_excel = st.file_uploader("Chọn file Excel TKB", type=["xls", "xlsx"])

    # Chế độ
    mode = st.radio("Chế độ", ["Sinh viên", "Giảng viên"])
    ten_gv = ""
    if mode == "Giảng viên":
        ten_gv = st.text_input("Tên giảng viên")

    # Nhắc nhở
    remind_value = st.number_input("Nhắc trước (số)", min_value=1, value=10)
    unit = st.selectbox("Đơn vị", ["phút", "giờ", "ngày"])
    if unit == "giờ":
        remind_value *= 60
    elif unit == "ngày":
        remind_value *= 1440

    remind_method = st.selectbox("Hình thức nhắc", ["popup", "email"])

    # Prefix
    prefix = st.text_input("Tiền tố sự kiện", "[TKB]")

    # Xem trước
    if file_excel and st.button("👀 Xem trước"):
        if mode == "Sinh viên":
            events = doc_tkb(file_excel)
        else:
            if not ten_gv:
                st.warning("Hãy nhập tên giảng viên.")
                return
            events = doc_tkb_giangvien(file_excel, ten_gv)

        if not events:
            st.warning("Không tìm thấy dữ liệu TKB.")
            return

        st.dataframe(events)

        # Lên lịch
        if st.button("📌 Lên sự kiện đã chọn"):
            if mode == "Sinh viên":
                len_lich(file_excel, remind_value, remind_method, prefix, events)
            else:
                len_lich_gv(file_excel, ten_gv, remind_value, remind_method, prefix, events)

    # Xóa sự kiện
    if st.button("🗑 Xóa sự kiện theo prefix"):
        xoa_lich(prefix)


if __name__ == "__main__":
    main()
