import streamlit as st

def apply_style():
    st.markdown(
        """
        <style>
        /* Nền tổng thể */
        .stApp {
            background: linear-gradient(rgba(255,255,255,0.7), rgba(255,255,255,0.7)), 
                        url("https://i.ibb.co/6Jxn0Cx/timetable-bg.jpg");
            background-size: cover;
            background-position: center;
            color: #2c3e50;
        }

        /* Tiêu đề */
        h1 {
            text-align: center;
            color: #2e7d32;  /* xanh lá đậm */
            font-weight: 800;
            text-shadow: 1px 1px 2px #c8e6c9;
        }

        /* Radio button + Input */
        .stRadio label, .stTextInput label {
            color: #1b5e20;
            font-weight: bold;
        }

        /* Các khung upload / card */
        .stFileUploader, .stButton button {
            border-radius: 12px;
        }

        /* Nút bấm */
        .stButton>button {
            background-color: #43a047;
            color: white;
            border: none;
            padding: 10px 20px;
            bord
