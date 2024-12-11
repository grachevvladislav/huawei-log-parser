"""Main."""

import streamlit as st
from PIL import Image

from constants import NAME, exception_message
from settings import DEBUG
from visualization import hide_loader, make_page, zip_file_parsing


def main() -> None:
    """
    Launch the project.

    :return: None
    """
    im = Image.open("static/favicon.png")
    st.set_page_config(
        page_title=NAME,
        page_icon=im,
        layout="wide",
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
    except Exception:
        if DEBUG:
            raise Exception
        st.write(exception_message, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
