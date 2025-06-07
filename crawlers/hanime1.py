import curl_cffi
from parsel import Selector
from pydantic import BaseModel
from typing import List,Literal,Dict
from loguru import logger
from urllib.parse import urlencode, urlparse, urlunparse
import json


class HanimeSearchParams(BaseModel):
    genre:str
    query:str = ''
    page:int=1
    sort:str=''
    year:str=''
    month:str=''
    tags:List[str]|None=None

    def toParam(self):
        result = [
            ('genre',self.genre),
            ('query',self.query),
            ('page',self.page),
            ('sort',self.sort),
            ('year',self.year),
            ('month',self.month)
        ]

        if self.tags:
            for tag in self.tags:
                result.append(('tags[]',tag))

        return result

class HanimePageInfo(BaseModel):
    url:str
    content:str
    max_page:int

class HanimePostInfo(BaseModel):
    id:int
    title:str
    url:str
    pre_img:str

class HanimePostDetail(BaseModel):
    id:int
    title:str
    breif:str
    watch_url:str
    download_urls:Dict[str,str]
    tags:List[str]

class HanimePostList(BaseModel):
    posts:List[HanimePostInfo]
    total_page:int

def build_url(base_url, params):
    url_parts = list(urlparse(base_url))
    url_parts[4] = urlencode(params)
    return urlunparse(url_parts)

class Hanime1Crawler():
    def __init__(self):
        self.base_url = 'https://hanime1.me/'
        self.search_url = 'https://hanime1.me/search'
        self.watch_url = 'https://hanime1.me/watch'
        self.session = curl_cffi.Session()
        # self.cookies = {
        #     'remember_web_59ba36addc2b2f9401580f014c7f58ea4e30989d': 'eyJpdiI6IlFkajlPZDEyQlFHYmdaWmtkMks4MVE9PSIsInZhbHVlIjoiNHhcLzZJQlVBRUtyMFFCaGhzNHk2REJQOW5rU2tRdGdrYzU1YVJwV2o0YmlxeisyS2RcL0RQOHZjanRoWlhIQUIwOGw4dFNONW9sK0xrRm1mUmp1RmFicWhLalhmUFpPbFFuKzFrMG00Zm1vUkwyMWtBUnBXT2djV0l4NlZMaWt2YWsyV005eEM3c21EaVwvVWl3SFErXC9PSnZ0TXZGRDBBQVo0WXFsMU4rcjI5aHlTbG5ZNFJ5R0tOT2tKTkNsdFVHXC8iLCJtYWMiOiIxNmYzODhmZDM0OGJiYzIzNzg5MDU4ZGRjZjQzNjJjYmYzMzk2MTkyODQwZjcxNzg0YWJjYjBiMzFjYWExYWNiIn0%3D',
        #     '__atuvc': '0%7C34%2C52%7C35%2C0%7C36%2C0%7C37%2C79%7C38',
        #     '_gid': 'GA1.2.363816166.1749136720',
        #     'cf_clearance': 'FBx2wdX_ALt0qzgaeg5buEJ4Cr_NFbPc.4sObmwLYKw-1749137804-1.2.1.1-8pVoErYLRJKUhvk.GpUTS9I_GYq0IKF.CDvvRMwGI_M.sdzYV.PZRog5QeoaBqk5d41yUaCdstt1h.qnBDjdT8C42LRgrpQHwjNL3pS3_BrdBGNu.tFwbyOCPrN9trcxV_A.gBAqoRRepBoKfDvd6qr_gRGciLSfWmVDXpALHRW8u9VZ0lU6_VYWrlvDFeG1vBb2.AuI0fV.l1_ziVdyyI4FNDLl3RcYYTaCQEvqxJbXo8r1BHLlKIjYqVRGF22ZspIItCQodHvWmaqZYgU4HF.GEEbc.0wX8g3eFyclylGDnDeB3sru1CAF0iB7eWz4PWkhh7qS4jEQVumQopMKg6Cq.v7EQ2btCSe.Mnm_z0U',
        #     'XSRF-TOKEN': 'eyJpdiI6ImRWTWpjejZDSFwvcmFiSWVPZkFTWXdRPT0iLCJ2YWx1ZSI6IkZiTDNidTNVSTVqR1Z5WGw3dWZsTTNuVmVRbWpVUWpNR0R1XC95R1UxbVRMM0RuNFd0SkpENGRYSWpRbFVYdGcxIiwibWFjIjoiMzQ4ZDFiODI5N2MyMmNhZGQxOGQxYTJmZTAyZjQ0YzZjYjI5NzE4MjE4ZTQ1ZGNjNzA4NWM5YzVkZjYyYjQ3MSJ9',
        #     'hanime1_session': 'eyJpdiI6IjM1d0FoVGd4d0phNXRxRFdZRnE5TWc9PSIsInZhbHVlIjoicytIc2x6K1l6ejVIQnBwbiswS1BweE8ySWRMMHp5cHFuWGZcL01nbFZqZXBMaDhhUERtSlltY29jMUxTcmFwYVQiLCJtYWMiOiI3NzZjNWMxZjc0NjJiNDMyNzdhMjY2YmJjYmI0YTkzN2UyNzY5ODBlZWVjNWU4NWY1ZjFmMWRlMjM0YTM1MjIxIn0%3D',
        #     '_gat_gtag_UA_125786247_2': '1',
        #     '_ga_2JNTSFQYRQ': 'GS2.1.s1749136719$o21$g1$t1749138390$j59$l0$h0',
        #     '_ga': 'GA1.1.1934604255.1705925664',
        # }

        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'cache-control': 'max-age=0',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        }


    def getAnimeTypes(self):
        response = self.session.get(self.search_url, headers=self.headers, impersonate="chrome")
        if response.status_code == 200:
            logger.debug(f'get anime types success, url: {response.url}')
            sel = Selector(text=response.text)
            types = sel.css('div.simple-dropdown-item.genre-option::attr(data-value)').getall()
            logger.debug(f'get post success, types: {types}')
            return types
        else:
            logger.error(f'get anime types failed, status code: {response.status_code}')
            return None

    def obtainAnimeTags(self,page_content:str):
        sel = Selector(text=page_content)
        tags = sel.css('label.hentai-tags-wrapper input::attr(value)').getall()
        logger.debug(f'get post success, tags: {tags}')
        return tags


    def getPageInfo(self,param : HanimeSearchParams):
        params = param.toParam()
        response = self.session.get(self.search_url, headers=self.headers, params=params, impersonate="chrome")
        if response.status_code == 200:
            url = response.url
            content = response.text
            sel = Selector(text=content)
            max_page = sel.css('ul.pagination li')[-2].css('::text').get()
            logger.debug(f'get post success, url: {url}, max_page: {max_page}, current_page: {param.page}')
            page_info = HanimePageInfo(url=url, content=content, max_page=max_page)
            return page_info
        else:
            logger.error(f'get post failed, status code: {response.status_code},url: {response.url}')
            return None

    def getPostInfo(self,page_content:str):
        sel = Selector(text=page_content)
        items = sel.css('div.home-rows-videos-wrapper a:not([target])')
        for item in items:
            img = item.css('img::attr(src)').get()
            url = item.css('::attr(href)').get()
            title = item.css('div.home-rows-videos-title::text').get()
            if url:
                id = url.split('=')[-1]
                # logger.debug(f'get post success, id: {id}, title: {title}, url: {url}, img: {img}')
                info = HanimePostInfo(id=id, title=title, url=url, pre_img=img)
                yield info

    def getAllPagePosts(self,param : HanimeSearchParams):
        page_info = self.getPageInfo(param)
        if not page_info:
            logger.error(f'get page info failed, param: {param.model_dump()}')
            return None

        for page in range(1,page_info.max_page+1):
            param.page = page
            page_info = self.getPageInfo(param)
            if page_info:
                post_list = list(self.getPostInfo(page_info.content))
                yield post_list



    def getPostDetailes(self,post_id:str):
        pass

if __name__ == '__main__':
    crawler = Hanime1Crawler()
    types = crawler.getAnimeTypes()
    param = HanimeSearchParams(genre=types[1])
    page_info  = crawler.getPageInfo(param)
    # if page_info:
    #     # crawler.obtainAnimeTags(content)
    #     post_info= list(crawler.getPostInfo(page_info.content))
    #     post_list = HanimePostList(posts=post_info,total_page=page_info.max_page)
    #     # print(len(page_info))
    #     # print(post_list.model_dump())
    #     with open('hanime1.json','w',encoding='utf-8') as f:
    #         json.dump(post_list.model_dump(),f,ensure_ascii=False,indent=4)

    all_post_list = []
    max_page = 0
    if page_info:
        max_page = page_info.max_page

        for post_list in crawler.getAllPagePosts(param):
            # print(post_list)
            all_post_list.extend(post_list)

    posts = HanimePostList(posts=all_post_list,total_page=max_page)

    with open('hanime1.json','w',encoding='utf-8') as f:
        json.dump(posts.model_dump(),f,ensure_ascii=False,indent=4)



