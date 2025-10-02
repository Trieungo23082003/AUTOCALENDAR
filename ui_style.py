import streamlit as st
import base64

def apply_style(logo_path="utc2.jpg"):
    try:
        with open(logo_path, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode()
        logo_html = f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_base64}">
        </div>
        """
    except:
        logo_html = ""

    st.markdown(
        f"""
        <style>
        /* Nền tổng thể */
        .stApp {{
            background-color: #e6f0ff; 
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

        /* Tiêu đề chính */
        h1 {{
            color: #1e3a8a;
            text-align: center;
            font-size: 2rem !important;
            font-weight: 700;
            border: 3px solid #1e3a8a;
            padding: 12px;
            border-radius: 20px;
            display: inline-block;
            margin: auto;
            text-shadow: 2px 2px 6px rgba(0,0,0,0.2);
            transform: rotate(-1deg); /* chữ hơi uốn lượn */
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

        /* Box xanh đậm bao quanh label + input */
        .highlight-box {{
            background-color: #1e3a8a;
            color: white;
            padding: 12px 16px;
            border-radius: 12px;
            margin: 16px 0;
        }}

        .highlight-box label, 
        .highlight-box div, 
        .highlight-box input {{
            color: white !important;
            font-weight: 600;
        }}

        /* Style riêng cho input trong box */
        .highlight-box input {{
            background-color: #2d4ea0 !important;
            border: none !important;
            border-radius: 6px;
            padding: 6px;
            color: #fff !important;
        }}
        </style>
        {logo_html}
        """,
        unsafe_allow_html=True
    )
