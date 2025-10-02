import streamlit as st
import base64

def apply_style(logo_path="utc2.jpg"):
    """Chèn CSS + logo vào giao diện Streamlit"""
    # Đọc file ảnh logo và encode sang base64
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        logo_html = f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}">
        </div>
        """
    except:
        logo_html = ""  # nếu không tìm thấy logo thì bỏ qua

    st.markdown(
        f"""
        <style>
        /* Nền tổng thể */
        .stApp {{
            background-color: #e6f0ff; /* nền xanh dương lợt */
            font-family: 'Inter', sans-serif;
        }}

        /* Khung nội dung chính */
        .block-container {{
            background: #ffffff;
            padding: 2rem 2.5rem;
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
            max-width: 900px;
        }}

        /* Tiêu đề */
        h1 {{
            color: #1e3a8a;
            text-align: center;
            font-size: 2rem !important;
            font-weight: 700;
        }}

        /* Logo cố định bên phải */
        .logo-container {{
            position: fixed;
            top: 100px;
            right: 20px;
            width: 70px;
            z-index: 1000;
        }}
        .logo-container img {{
            width: 70px;
            border-radius: 12px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        }}
        </style>
        {logo_html}
        """,
        unsafe_allow_html=True
    )


