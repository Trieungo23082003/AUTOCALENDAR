import streamlit as st
import base64

def apply_style(logo_path="utc2.jpg", position="left"):
    with open(logo_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    if position == "right":
        align = "right:20px; top:20px;"
    else:
        align = "left:20px; top:20px;"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: white;
            color: #2c3e50;
            font-family: "Segoe UI", sans-serif;
        }}

        .logo-container {{
            position: fixed;
            {align}
            width: 80px;
            z-index: 1000;
        }}
        .logo-container img {{
            width: 80px;
            border-radius: 12px;
            box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
        }}

        h1 {{
            text-align: center;
            color: #2e7d32;
            font-weight: 900;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            border: 3px solid #2e7d32;
            border-radius: 12px;
            display: inline-block;
            padding: 8px 20px;
            background-color: rgba(255, 255, 255, 0.8);
        }}

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

        /* 🔵 Box chữ xanh bo tròn */
        .highlight-box {{
            display: inline-block;
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
            padding: 8px 18px;
            border-radius: 25px;
            margin: 10px 0;
            box-shadow: 1px 1px 4px rgba(0,0,0,0.2);
        }}
        </style>

        <div class="logo-container">
            <img src="data:image/png;base64,{encoded}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True,
    )

