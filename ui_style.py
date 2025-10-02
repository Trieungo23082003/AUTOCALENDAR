import streamlit as st

def apply_style():
    """Chèn CSS vào giao diện Streamlit"""
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