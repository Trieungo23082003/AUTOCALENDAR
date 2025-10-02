import streamlit as st
import base64

def apply_style(image_path="tkb.png", opacity=0.3):
    """
    Tạo style cho app với nền ảnh + chữ xanh bo tròn viền đẹp
    - image_path: ảnh nền (cùng thư mục với main.py)
    - opacity: độ mờ nền (0 -> trong suốt, 1 -> rõ nét)
    """

    # Đọc ảnh và encode sang base64
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        /* Toàn bộ nền */
        .stApp {{
            background: 
                linear-gradient(rgba(255,255,255,{opacity}), rgba(255,255,255,{opacity})), 
                url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            color: #2c3e50;
            font-family: "Segoe UI", sans-serif;
        }}

        /* Tiêu đề */
        h1 {{
            text-align: center;
            color: #2e7d32;
            font-weight: 900;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            border: 3px solid #2e7d32;
            border-radius: 12px;
            display: inline-block;
            padding: 8px 20px;
            background-color: rgba(255, 255, 255, 0.7);
        }}

        /* Các nhãn input */
        .stRadio label, .stTextInput label {{
            color: #1b5e20;
            font-weight: bold;
        }}

        /* Nút bấm */
        .stButton>button {{
            background-color: #43a047;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        }}
        .stButton>button:hover {{
            background-color: #2e7d32;
            transform: scale(1.08);
        }}

        /* Thông báo */
        .stAlert {{
            border-radius: 12px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
