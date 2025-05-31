import sys
from pathlib import Path

import streamlit as st
import streamlit.web.cli as stcli


def run_streamlit():
    # 设置命令行参数
    sys.argv = ["streamlit", "run", __file__, "--server.port=8501"]

    # 调用 Streamlit CLI
    sys.exit(stcli.main())


if __name__ == "__main__":

    page_path = Path('pages')

    page_dict : dict[str,list[st.Page]] = {}
    for dir in page_path.iterdir():
        if not dir.is_dir():
            continue

        if dir.name not in page_dict:
            page_dict[dir.name] = []
        for file in dir.glob('*.py'):
            if file.name != '__init__.py':
                page_dict[dir.name].append(st.Page(str(file)))

    # print(page_dict)

    pg = st.navigation(page_dict)
    pg.run()
