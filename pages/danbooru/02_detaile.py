import streamlit as st
from pathlib import Path
import time

from crawlers.danbooru_crawler import DanbooruCrawler


def danbooru_download_file():

    post = st.session_state.post
    download_path = Path(f'Downloads/{post.id}'+post.type)
    download_path.parent.mkdir(exist_ok=True,parents=True)
    st.session_state.danbooru.download_file(post.source_url, str(download_path))



def danbooru_show_detaile(id:int):
    if id != st.session_state.last_post_id:
        st.session_state.post = st.session_state.danbooru.get_post_detail(id)
    post = st.session_state.post
    if not post:
        st.error(f"post {id} not found")
        return

    if post.type.lower() == '.mp4':
        st.video(post.source_url)
    elif post.type.lower() == '.zip':
        st.markdown(post.source_url)
    else:
        st.image(post.source_url)


    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Download", key=f"dl_btn_{id}"):
            danbooru_download_file()
    with col2:
        st.link_button("Source", post.get_url())

    st.text_area('Tags:', ','.join(post.tags),key=f"tags_{id}",height=300)


st.title("post detail")

if 'danbooru' not in st.session_state:
    st.session_state.danbooru = DanbooruCrawler()
if 'post_id' not in st.session_state:
    st.session_state.post_id = 5924778
    st.session_state.last_post_id = -1
if 'post' not in st.session_state:
    st.session_state.post = None




st.number_input("Post ID",
                min_value=0,
                step=1,
                value=st.session_state.post_id,
                key="post_id_input")

st.success(f"Current Post ID = {st.session_state.post_id}")


danbooru_show_detaile(st.session_state.post_id)
st.session_state.last_post_id = st.session_state.post_id  # 更新标记


# st.success(f"post id = {st.session_state.post_id},number = {new_id}")
# danbooru_show_detaile(st.session_state.post_id)
# st.session_state.prev_post_id = new_id

# print(f"before refresh post id = {st.session_state.post_id},number = {new_id}")
# print(f"after refresh post id = {st.session_state.post_id},number = {new_id}")

# danbooru_show_detaile(new_id)