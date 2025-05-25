import os
import sys

import streamlit as st
import streamlit.web.cli as stcli

from danbooru_crawler import DanbooruCrawler

def run_streamlit():
    # 设置命令行参数
    sys.argv = ["streamlit", "run", __file__, "--server.port=8501"]

    # 调用 Streamlit CLI
    sys.exit(stcli.main())

class App:
    def danbooru_download_file(self):

        post = st.session_state.post
        if not os.path.exists('Downloads'):
            os.makedirs('Downloads')
        st.session_state.danbooru.download_file(post.source_url, f'Downloads/{post.id}'+post.type)

    def danbooru_crawl(self,id:int):
        if 'danbooru' not in st.session_state:
            st.session_state.danbooru = DanbooruCrawler()
            st.session_state.post = st.session_state.danbooru.get_post_detail(id)
        post = st.session_state.post

        if post.type.lower() == '.mp4':
            st.video(post.source_url)
        else:
            st.image(post.source_url)
        st.button("Download",on_click=self.danbooru_download_file)
        # st.download_button(label="Download image",data=post.source_url,file_name='test'+post.type)
        # for tag in post.tags:
        #     st.badge(tag,color="primary")
        st.text_area('Tags:',','.join(post.tags))

    def show_danbooru(self,id:int):
        st.title("Danbooru")

        if 'btn_state' not in st.session_state:
            st.session_state.btn_state = ''

        if st.sidebar.button("danbooru"):
            st.session_state.btn_state = "danbooru"

        if st.session_state.btn_state == "danbooru":
            self.danbooru_crawl(id)





if __name__ == "__main__":
    app = App()
    app.show_danbooru(9358835)