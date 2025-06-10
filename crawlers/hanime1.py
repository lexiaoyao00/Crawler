import curl_cffi
from parsel import Selector
from pydantic import BaseModel
from typing import List, Iterator, Optional
from loguru import logger
from pathlib import Path
import sys
import time


logger.remove()
logger.add(sys.stderr, level="INFO")
# logger.add('logs/hanime1_debug.log',level='DEBUG')

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

class IHanime(BaseModel):
    def to_json(self,filename:str = 'hanime.json'):

        path = Path('output/' + filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=4),encoding='utf-8')

class HanimePostDownloadInfo(IHanime):
    quality:str
    video_type:str
    url:str

    # def to_json(self,filename:str = 'hanime_post_download_info.json'):
    #     with open(filename,'w',encoding='utf-8') as f:
    #         json.dump(self.model_dump(),f,ensure_ascii=False,indent=4)

class HanimeDownloadList(IHanime):
    dowloads : List[HanimePostDownloadInfo] = []

    # def to_json(self,filename:str = 'hanime_download_list.json'):
    #     with open(filename,'w',encoding='utf-8') as f:
    #         json.dump(self.model_dump(),f,ensure_ascii=False,indent=4)

class HanimePostInfo(IHanime):
    id:int
    title:str
    url:str
    pre_img:str

    # def to_json(self,filename:str = 'hanime_post_info.json'):
    #     with open(filename,'w',encoding='utf-8') as f:
    #         json.dump(self.model_dump(),f,ensure_ascii=False,indent=4)


class HanimePostList(IHanime):
    posts:List[HanimePostInfo] = []

    # def to_json(self,filepath:str = 'hanime_post_list.json'):

    #     path = Path(filepath)
    #     path.parent.mkdir(parents=True, exist_ok=True)
    #     path.write_text(self.model_dump_json(indent=4),encoding='utf-8')

    def merge(self, other_collection: 'HanimePostList'):
        """将另一个集合的所有帖子添加到当前集合中"""
        self.posts.extend(other_collection.posts)
        return self

class HanimePostDetail(IHanime):
    id:int
    title:str
    artist:str
    vidoe_type:str
    brief:str
    watch_url:str
    tags:List[str]
    download_infos:HanimeDownloadList|None=None
    play_list:HanimePostList|None=None

    # def to_json(self,filename:str = 'hanime_post_detail.json'):
    #     with open(filename,'w',encoding='utf-8') as f:
    #         json.dump(self.model_dump(),f,ensure_ascii=False,indent=4)

class Hanime1Crawler():
    def __init__(self):
        self.base_url = 'https://hanime1.me/'
        self.search_url = 'https://hanime1.me/search'
        self.watch_url = 'https://hanime1.me/watch'
        self.download_url = 'https://hanime1.me/download'
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

    def getPostInfo(self,page_content:str) -> HanimePostList|None:
        sel = Selector(text=page_content)
        items = sel.css('div.home-rows-videos-wrapper a:not([target])')
        posts : List[HanimePostInfo] = []
        for item in items:
            img = item.css('img::attr(src)').get()
            url = item.css('::attr(href)').get()
            title = item.css('div.home-rows-videos-title::text').get()
            if url:
                id = url.split('=')[-1]
                # logger.debug(f'get post success, id: {id}, title: {title}, url: {url}, img: {img}')
                posts.append(HanimePostInfo(id=id, title=title, url=url, pre_img=img))

        if posts:
            return HanimePostList(posts=posts)
        else:
            return None

    def getAllPagePosts(self,param : HanimeSearchParams) -> Iterator[Optional[HanimePostList]]:
        page_info = self.getPageInfo(param)
        if not page_info:
            logger.error(f'get page info failed, param: {param.model_dump()}')
            return None

        for page in range(1,page_info.max_page+1):
            param.page = page
            page_info = self.getPageInfo(param)
            if page_info:
                post_list : HanimePostList|None = self.getPostInfo(page_info.content)
                yield post_list

                time.sleep(1)


    def _getPostDownLoadInfo(self,sel:Selector) -> HanimeDownloadList|None:
        download_page_url = sel.css('a#downloadBtn::attr(href)').get()
        result :List[HanimePostDownloadInfo] = []
        if download_page_url:
            response = self.session.get(download_page_url, headers=self.headers, params=None, impersonate="chrome")
            download_sel = Selector(text=response.text)
            if response.status_code != 200:
                logger.warning(f'get post download info failed, status code: {response.status_code},  url: {response.url}')
                return None

            table = download_sel.css('table.download-table')
            if table:
                trs = table.css('tr')
                for tr in trs:
                    if not tr.css('td > a.exoclick-popunder.juicyads-popunder').get():
                        continue
                    quality = tr.css('td:nth-child(2)::text').get().strip()
                    video_type = tr.css('td:nth-child(3)::text').get()
                    download_url = tr.css('td:nth-child(5) > a.exoclick-popunder.juicyads-popunder::attr(data-url)').get()
                    logger.debug(f'get post download info success, quality: {quality}, video_type: {video_type}, url: {download_url}')
                    result.append(HanimePostDownloadInfo(quality=quality, video_type=video_type, url=download_url))

            return HanimeDownloadList(dowloads=result)
        else:
            logger.warning(f'get post download info failed, no download url')
            return None

    def _getPostPlayeList(self,sel:Selector):
        playlist_items = sel.css('div.hidden-xs.hidden-sm div#playlist-scroll > div')
        resutl = []
        if playlist_items:
            for item in playlist_items:
                url = item.css('a.overlay::attr(href)').get()
                id = url.split('=')[-1]
                panel = item.xpath('./div[@class="card-mobile-panel inner"]//img[2]')
                title = panel.css('::attr(alt)').get()
                pre_img = panel.css('::attr(src)').get()

                logger.debug(f'get PlayeList success, id: {id}, title: {title}, url: {url}, img: {pre_img}')
                resutl.append(HanimePostInfo(id=id, title=title, url=url,pre_img=pre_img))

            return HanimePostList(posts=resutl)
        else:
            logger.warning(f'get PlayeList failed, no playlist items')
            return None

    def getPostDetail(self,post_id:str|int) -> HanimePostDetail|None:
        params = [('v', post_id)]
        response = self.session.get(self.watch_url, headers=self.headers,params=params, impersonate="chrome")

        if response.status_code == 200:
            logger.debug(f'get post details success, url: {response.url}')
            sel = Selector(text=response.text)
            artist = sel.css('div.video-details-wrapper a#video-artist-name::text').get().strip()
            video_type = sel.css('div.video-details-wrapper div.hidden-xs a::text').get().strip()
            title = sel.css('div.video-description-panel div:not([class])::text').get()
            brief = sel.css('div.video-description-panel div.video-caption-text::text').get().strip().replace('\r','').replace('\n','')
            tags = sel.css('div.video-details-wrapper.video-tags-wrapper div.single-video-tag a::text').getall()
            tags = [tag.replace('\xa0', '') for tag in tags]
            play_list = self._getPostPlayeList(sel)
            download_list = self._getPostDownLoadInfo(sel)
            logger.debug(f'get post details success, id: {post_id}, title: {title}, brief: {brief}, tags: {tags}, artist: {artist}, video_type: {video_type} ')
            detail = HanimePostDetail(id=post_id, title=title, brief=brief, tags=tags, artist=artist,watch_url=response.url,
                                    vidoe_type=video_type, play_list=play_list, download_infos=download_list)

            return detail
        else:
            logger.error(f'get {response.url} post details failed, status code: {response.status_code}')
            return None

    def getPostDownloadInfo(self,post_id:str|int):
        params = [('v', post_id)]
        response = self.session.get(self.download_url, headers=self.headers,params=params, impersonate="chrome")
        if response.status_code != 200:
            logger.warning(f'get post download info failed, status code: {response.status_code},  url: {response.url}')
            return None

        result :List[HanimePostDownloadInfo] = []
        sel = Selector(text=response.text)
        table = sel.css('table.download-table')
        if table:
            trs = table.css('tr')
            for tr in trs:
                if not tr.css('td > a.exoclick-popunder.juicyads-popunder').get():
                    continue
                quality = tr.css('td:nth-child(2)::text').get().strip()
                video_type = tr.css('td:nth-child(3)::text').get()
                download_url = tr.css('td:nth-child(5) > a.exoclick-popunder.juicyads-popunder::attr(data-url)').get()
                logger.debug(f'get post download info success, quality: {quality}, video_type: {video_type}, url: {download_url}')
                result.append(HanimePostDownloadInfo(quality=quality, video_type=video_type, url=download_url))

        return HanimeDownloadList(result)

if __name__ == '__main__':
    crawler = Hanime1Crawler()
    types = crawler.getAnimeTypes()
    param = HanimeSearchParams(genre= '裏番')

    # page_info : HanimePageInfo = crawler.getPageInfo(HanimeSearchParams(param)

    # if page_info:
    #     posts_info :HanimePostList  = crawler.getPostInfo(page_info.content)
    #     if posts_info:
    #         posts_info.to_json('posts_info.json')

    #     # for post in posts_info.posts:
    #     #     post_detail:HanimePostDetail = crawler.getPostDetail(post.id)
    #     #     if post_detail:
    #     #         post_detail.to_json(f'post_detail_{post.id}.json')
    #     #     else:
    #     #         logger.error(f'get post detail failed, id: {post.id}')

    posts_list = HanimePostList()

    for  posts in crawler.getAllPagePosts(param):
        posts_list.merge(posts)

    posts_list.to_json('all_posts_list.json')