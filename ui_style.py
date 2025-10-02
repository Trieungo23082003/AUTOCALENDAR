import streamlit as st

def navbar():
    st.markdown(
        """
        <style>
        /* Thanh navbar */
        .navbar {
            background-color: #2e7d32; /* xanh lá */
            overflow: hidden;
            display: flex;
            justify-content: center;
            padding: 12px 0;
        }

        .navbar a {
            float: left;
            color: white;
            text-align: center;
            padding: 12px 20px;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
        }

        .navbar a:hover {
            background-color: #1b5e20;
            color: #fff176;
            border-radius: 6px;
        }

        .active {
            background-color: #1b5e20;
            color: white;
            border-radius: 6px;
        }
        </style>

        <div class="navbar">
          <a href="?menu=home" class="active">Trang Chủ</a>
          <a href="?menu=about">Giới Thiệu</a>
          <a href="?menu=event">Sự Kiện</a>
          <a href="?menu=download">Tải File</a>
          <a href="?menu=contact">Liên Hệ</a>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_page(menu):
    if menu == "home":
        st.markdown("<h1 style='text-align:center; color:#2e7d32;'>THỜI KHÓA BIỂU</h1>", unsafe_allow_html=True)
        st.image("thoikhoabieu.jpg", use_column_width=True)

    elif menu == "about":
        st.header("Giới thiệu")
        st.write("Đây là website thời khóa biểu demo bằng Streamlit.")

    elif menu == "event":
        st.header("Sự kiện")
        st.write("Chế độ prefix sự kiện... (sẽ thêm tính năng sau)")

    elif menu == "download":
        st.header("Tải File")
        with open("thoikhoabieu.jpg", "rb") as file:
            st.download_button(
                label="📥 Tải thời khóa biểu",
                data=file,
                file_name="thoikhoabieu.jpg",
                mime="image/jpeg"
            )

    elif menu == "contact":
        st.header("Liên hệ")
        st.write("📧 Email: contact@demo.com")
        st.write("📞 Hotline: 0123.456.789")
