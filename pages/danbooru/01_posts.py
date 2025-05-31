import streamlit as st
from crawlers.danbooru_crawler import DanbooruCrawler



if 'post_id' not in st.session_state:
    st.session_state.post_id = 5924778
    st.session_state.last_post_id = -1


def show_posts(colums_num :int = 4,user_params:dict|None = None , max_page_count:int = 1):
    cols = st.columns(colums_num)
    post_count = 0
    for id,pre_img in st.session_state.danbooru.get_posts(user_params,max_page_count):
        cont = cols[post_count % colums_num].container(height=400,border=False)
        cont.image(pre_img, caption=id,use_container_width=True)
        if cont.button("detaile",key=id):
            st.session_state.post_id = id
            st.switch_page('pages/danbooru/02_detaile.py')

        post_count += 1


def show_new():
    user_params = {}
    with st.form("new"):
        col1, col2 = st.columns(2)
        with col1:
            page_number = st.number_input("page",min_value=1,max_value=1000,value=1,key='page')
        with col2:
            max_page = st.number_input("max_page",min_value=1,max_value=1000,value=1,key='max_page')

        tags = st.text_input("tags",key='tags')

        submitted = st.form_submit_button("确认")


    if submitted:
        user_params = {'tags':tags,'page':page_number}
    #     show_posts(4,user_params,max_page)
    show_posts(4,user_params,max_page)


def show_hot():
    pass

def show_popular():
    pass

select_options = {
    'new':show_new,
    'hot':show_hot,
    'popular':show_popular
}


st.title("Danbooru")

if 'danbooru' not in st.session_state:
    st.session_state.danbooru = DanbooruCrawler()

opts = select_options.keys()
option  = st.selectbox('show posts',
            key='show_posts',
            options=opts)

select_options[option]()

