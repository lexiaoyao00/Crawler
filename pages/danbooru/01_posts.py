import streamlit as st
from crawlers.danbooru import DanbooruCrawler



if 'post_id' not in st.session_state:
    st.session_state.post_id = 5924778
    st.session_state.last_post_id = -1

@st.cache_data
def fetch_post_data(user_params:dict|None = None , max_page_count:int = 1, post_type:str = 'normal'):
    posts = list(st.session_state.danbooru.get_posts(user_params,max_page_count,post_type))
    return posts


def show_posts(colums_num :int = 4,user_params:dict|None = None , max_page_count:int = 1,post_type:str = 'normal'):
    cols = st.columns(colums_num)
    post_count = 0
    for id,pre_img in fetch_post_data(user_params,max_page_count,post_type):
        cont = cols[post_count % colums_num].container(height=450,border=False)
        cont.image(pre_img, caption=id,use_container_width=True)
        if cont.button("detaile",key=id):
            st.session_state.post_id = id
            st.switch_page('pages/danbooru/02_detaile.py')

        post_count += 1


def show_new():
    with st.form("new"):
        col1, col2 = st.columns(2)
        with col1:
            page_number = st.number_input("page",min_value=1,max_value=1000,value=1,key='page')
        with col2:
            max_page = st.number_input("max_page",min_value=1,max_value=1000,value=1,key='max_page')

        tags = st.text_input("tags",key='tags')

        submitted = st.form_submit_button("确认")

        st.session_state.user_params = {'tags':tags,'page':page_number}


    if submitted:
        st.cache_data.clear()
    show_posts(4,st.session_state.user_params,max_page)


def show_hot():
    with st.form("hot"):
        col1, col2 = st.columns(2)
        with col1:
            page_number = st.number_input("page",min_value=1,max_value=1000,value=1,key='page')
        with col2:
            max_page = st.number_input("max_page",min_value=1,max_value=1000,value=1,key='max_page')

        tags = st.text_input("tags",key='tags',value='order:rank')

        submitted = st.form_submit_button("确认")


        st.session_state.user_params = {'tags':tags,'page':page_number}

    if submitted:
        st.cache_data.clear()
    show_posts(4,st.session_state.user_params,max_page)

def show_popular():
    with st.form("popular"):
        col1, col2 = st.columns(2)
        with col1:
            page_number = st.number_input("page",min_value=1,max_value=1000,value=1,key='page')
        with col2:
            max_page = st.number_input("max_page",min_value=1,max_value=1000,value=1,key='max_page')

        submitted = st.form_submit_button("确认")

        st.session_state.user_params = {'page':page_number}

    if submitted:
        st.cache_data.clear()
    show_posts(4,st.session_state.user_params,max_page,'popular')

select_options = {
    'new':show_new,
    'hot':show_hot,
    'popular':show_popular
}


st.title("Danbooru")

if 'danbooru' not in st.session_state:
    st.session_state.danbooru = DanbooruCrawler()
if 'user_params' not in st.session_state:
    st.session_state.user_params = {}

opts = select_options.keys()
option  = st.selectbox('show posts',
            key='show_posts',
            options=opts,
            on_change=lambda : st.cache_data.clear())

select_options[option]()

