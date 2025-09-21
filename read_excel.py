import pandas as pd
import re
from tiet_gio import quy_doi_tiet


def parse_thoigian_hoc(text):
    if not isinstance(text, str) or text.strip() == "":
        return []

    # Ngày bắt đầu - kết thúc
    m = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}/\d{2}/\d{4})", text)
    if not m:
        return []
    ngay_bat_dau, ngay_ket_thuc = m.groups()

    # Cắt thành nhiều đoạn theo "Thứ"
    parts = re.split(r"(?=Thứ\s*\d+)", text, flags=re.IGNORECASE)

    results = []
    for part in parts:
        part = part.strip()
        if not part.lower().startswith("thứ"):
            continue

        # Thứ
        m = re.search(r"Thứ\s*(\d+)", part, re.IGNORECASE)
        thu = int(m.group(1)) if m else None

        # Tiết
        m = re.search(r"Tiết\s*(\d+)\s*-\s*(\d+)", part, re.IGNORECASE)
        tiet_bd, tiet_kt = (int(m.group(1)), int(m.group(2))) if m else (None, None)
        gio_bd, gio_kt = quy_doi_tiet(tiet_bd, tiet_kt) if tiet_bd and tiet_kt else ("", "")

        # ----------------- PHÒNG HỌC + GIẢNG VIÊN -----------------
        phong, giang_vien = "", ""
        if ',' in part:
            left, giang_vien = part.rsplit(',', 1)
            giang_vien = giang_vien.strip()
            left = left.strip()

            if ')' in left:
                phong = left.split(')')[-1].strip()
            elif ',' in left:
                phong = left.split(',')[-1].strip()
            else:
                phong = left.strip()

            phong = phong.lstrip('),(').strip()

        results.append({
            "ngay_bat_dau": ngay_bat_dau,
            "ngay_ket_thuc": ngay_ket_thuc,
            "thu": thu,
            "tiet_bd": tiet_bd,
            "tiet_kt": tiet_kt,
            "gio_bd": gio_bd,
            "gio_kt": gio_kt,
            "phong": phong,
            "giang_vien": giang_vien
        })

    return results


def doc_tkb(file_path):
    print(f"Đang đọc file: {file_path}")
    df = pd.read_excel(file_path, header=None)

    events = []
    for _, row in df.iterrows():
        mon = str(row[2]).strip() if len(row) > 2 else ""   # cột C
        thoigian = str(row[6]).strip() if len(row) > 6 else ""  # cột G

        if mon in ["", "nan"] or thoigian in ["", "nan"]:
            continue

        tgs = parse_thoigian_hoc(thoigian)
        if not tgs:
            continue

        for tg in tgs:
            events.append({
                "mon": mon,
                **tg
            })

    return events
