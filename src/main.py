import streamlit as st

from constants import NAME
from visualization import show_blocks, file_parsing, hide_loader, make_graph


def main():
    st.set_page_config(
        page_title=NAME,
        page_icon='⚡', #'static/apple-touch-icon.png',
        layout="wide",
        initial_sidebar_state="expanded"
    )
    hide_loader()
    with st.sidebar:
        st.title(NAME)
        file = st.file_uploader(
            'Загрузить файл', type='bz2',
            help='Архив с основного контроллера log_controller_*_MAIN.tar.bz2',
        )
    if file:
        data = file_parsing(file)
        if data:
            show_blocks(data)
    # for debug
    make_graph({})


if __name__ == "__main__":
    main()
