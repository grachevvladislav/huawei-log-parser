import streamlit as st

from constants import NAME, exception_message
from settings import DEBUG
from visualization import hide_loader, make_page, sas_graph, zip_file_parsing


def main():
    st.set_page_config(
        page_title=NAME,
        page_icon="⚡",  #'static/apple-touch-icon.png',
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_loader()
    st.title(NAME)
    file = st.file_uploader(
        "Загрузить файл",
        type="bz2",
        help="Архив с основного контроллера log_controller_*_MAIN.tar.bz2",
    )
    try:
        if file:
            data = zip_file_parsing(file)
            if data:
                make_page(data)
        elif DEBUG:
            # make_page({})
            sas_graph({})
    except Exception:
        if DEBUG:
            raise Exception
        st.write(exception_message, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
