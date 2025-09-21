import pandas as pd
import os
import re
import unicodedata
from tiet_gio import quy_doi_tiet


def _normalize_text(s: str) -> str:
    """Chuẩn hoá văn bản: lower-case, bỏ dấu, đổi đ->d."""
    if s is None:
        return ""
    s = str(s)
    s = s.replace("đ", "d").replace("Đ", "D")
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower().strip()


def find_column_by_keywords(df: pd.DataFrame, keywords):
    """Tìm cột sao cho tất cả từ khóa xuất hiện trong tên cột (sau chuẩn hoá)."""
    norm_keywords = [_normalize_text(k) for k in keywords if k]
    for col in df.columns:
        norm_col = _normalize_text(col)
        if all(k in norm_col for k in norm_keywords):
            return col
    raise KeyError(f"Không tìm thấy cột chứa từ khóa: {keywords}")


def doc_tkb_giangvien(file_path, ten_giangvien):
    """
    Đọc thời khóa biểu giảng viên từ file Excel (hàng tiêu đề dòng 9 → header=8).
    Lọc theo tên giảng viên (không phân biệt hoa/thường, dấu).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    print(f"Đang đọc TKB giảng viên từ: {file_path}")

    # chọn engine theo đuôi file
    ext = os.path.splitext(file_path)[-1].lower()
    if ext == ".xlsx":
        engine = "openpyxl"
    elif ext == ".xls":
        engine = "xlrd"
    else:
        raise ValueError("File không phải Excel (.xls hoặc .xlsx)")

    # đọc từ dòng 9
    df = pd.read_excel(file_path, sheet_name=0, engine=engine, header=7)

    print("Cột tìm thấy trong file:", df.columns.tolist())

    # xác định cột
    col_mon = find_column_by_keywords(df, ["lop", "hoc", "phan"])
    col_thu   = df.columns[9]   # cột J = "Thứ"
    col_tiet = find_column_by_keywords(df, ["tiet"])
    col_phong = find_column_by_keywords(df, ["phong"])
    col_ngaybd = find_column_by_keywords(df, ["ngay", "bd"])
    col_ngaykt = find_column_by_keywords(df, ["ngay", "kt"])
    col_gv = find_column_by_keywords(df, ["giao", "vien"])

    # lọc theo tên giảng viên (bỏ dấu + thường hóa)
    norm_target = _normalize_text(ten_giangvien)
    df[col_gv] = df[col_gv].astype(str)
    df_gv = df[df[col_gv].apply(lambda x: norm_target in _normalize_text(x))].copy()

    events = []
    for _, row in df_gv.iterrows():
        mon = str(row[col_mon]).strip()

        # Thứ
        thu = None
        if pd.notna(row[col_thu]):
            m = re.search(r"\d+", str(row[col_thu]))
            if m:
                thu = int(m.group())

        # Tiết
        tiet_raw = str(row[col_tiet]).strip()
        tiet_bd = tiet_kt = gio_bd = gio_kt = None
        if "-" in tiet_raw:
            nums = re.findall(r"\d+", tiet_raw)
            if len(nums) >= 2:
                tiet_bd, tiet_kt = map(int, nums[:2])
                gio_bd, gio_kt = quy_doi_tiet(tiet_bd, tiet_kt)
        elif tiet_raw.isdigit():
            tiet_bd = tiet_kt = int(tiet_raw)
            gio_bd, gio_kt = quy_doi_tiet(tiet_bd, tiet_kt)

        # Phòng
        phong = str(row[col_phong]).strip()

        # Ngày bắt đầu / kết thúc
        ngay_bd = (
            pd.to_datetime(row[col_ngaybd]).strftime("%d/%m/%Y")
            if pd.notna(row[col_ngaybd])
            else ""
        )
        ngay_kt = (
            pd.to_datetime(row[col_ngaykt]).strftime("%d/%m/%Y")
            if pd.notna(row[col_ngaykt])
            else ""
        )

        # Giảng viên
        giang_vien = str(row[col_gv]).strip()

        events.append(
            {
                "mon": mon,
                "ngay_bat_dau": ngay_bd,
                "ngay_ket_thuc": ngay_kt,
                "thu": thu,
                "tiet_bd": tiet_bd,
                "tiet_kt": tiet_kt,
                "gio_bd": gio_bd,
                "gio_kt": gio_kt,
                "phong": phong,
                "giang_vien": giang_vien,
            }
        )

    return events


if __name__ == "__main__":
    file_excel = "TKB HK1 25-26 180925 ( chính thức ).xls"
    ds = doc_tkb_giangvien(file_excel, "NGUYỄN CÔNG hậu")  # viết hoa/thường/dấu đều được
    print("===== DANH SÁCH MÔN HỌC CỦA GIẢNG VIÊN =====")
    for e in ds:
        print(e)
