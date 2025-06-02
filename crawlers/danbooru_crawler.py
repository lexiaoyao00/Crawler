import curl_cffi
from parsel import Selector
from pydantic import BaseModel
from typing import List,Literal
import re

class PostInfo(BaseModel):
    id: int
    tags: List[str]
    source_url: str|None = None
    artist: List[str]|None = None
    copyrights: List[str]|None = None
    character: List[str]|None = None
    meta: List[str]|None = None
    size: str|None = None
    type: str|None = None
    dimensions :str|None = None

    def save_to_json(self,filename:str):
        with open(filename,'w',encoding='utf-8') as f:
            f.write(self.model_dump_json(indent=2))
    def get_url(self):
        return f'https://danbooru.donmai.us/posts/{self.id}'

class DanbooruCrawler():
    def __init__(self):
        self.base_url = 'https://danbooru.donmai.us'
        self.polular_url = 'https://danbooru.donmai.us/explore/posts/popular'
        self.session = curl_cffi.Session()
        self.headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        }
        self.cookies = {
            '_danbooru2_session': 'mLCHs0Mzz6ueB0JRe2mSw0vIwbVSgzEcsCNAVItjUCwGtES9IriSs0BjN3fdkkA10FPWJ21S%2Fj%2BTsKQI5a0IoP3q01UnxSscdBTMtLvfMq%2BIuCDqMDHkvVg%2BjdAxtXaO5Z0%2BKCeniPdeG2%2FJJLOCBMqEoLRBRpZKu2iqv2ferkEOC2XVkTaVIpsKBV3QS%2FofbQ3jriTa2jFbtehPus08v2AaLLO4Dv89ZkVTc9K1o4Ytac4TwZRpJOTnu6FvK0NybDp4izPs3WrrCBD%2B1%2BOeC0AYhvmryZjjWjAYvmX%2BA3KutDsKZjekDyiaj2Ny0RYpZxaiCS14tmd5EGFSKSN5Fl0gNsc8S5OndJLYr6eqWUSP2L2%2Bttw5LCsTR1mSK%2FSzcGP5639LVmx8b1q3RjOQippoX%2FcwhIL3--ERLrY0K%2Bj1SQH1ge--%2BV5xffiATmAgvDXkqGGW%2Fg%3D%3D',
        }

    def get_posts(self, user_params:dict|None = None , max_page_count:int = 1, url_type : Literal['normal','popular'] = 'normal' ):
        page_count = 1
        if user_params is None:
            user_params = {}
        params = user_params
        while page_count <= max_page_count:
            if 'page' not in params.keys():
                params.update({'page':page_count})
            else:
                page_num = params['page']
                params.update({'page':page_num + page_count - 1})


            url = self.polular_url if url_type == 'popular' else self.base_url
            print(f'url {url} params {params}')
            res = self.session.get(url=url, headers=self.headers, cookies=self.cookies,params=params)
            if res.status_code != 200:
                print(f'page {page_count} response error:{res.status_code}')
                return None
            page_count += 1

            sel = Selector(text=res.text)
            post_preview_container = sel.css('div.posts-container div.post-preview-container')

            for post in post_preview_container:
                post_id = int(post.css('a.post-preview-link::attr(href)').get().split('/')[-1].split('?')[0])
                post_pre_img = post.css('img.post-preview-image::attr(src)').get()

                # print(post_id,post_pre_img)
                yield post_id,post_pre_img

                # return post_id
            # post_id = post_preview_container.css('a.post-preview-link::attr(href)').getall()
            # post_pre_img = post_preview_container.css('img.post-preview-image::attr(src)').getall()

            # return post_id



    def get_post_detail(self, post_id: int):
        url = f'{self.base_url}/posts/{post_id}'
        res = self.session.get(url=url, headers=self.headers, cookies=self.cookies)
        if res.status_code == 200:
            sel = Selector(text=res.text)
            artist = sel.css('ul.artist-tag-list li.flex::attr(data-tag-name)').getall()
            copyrights = sel.css('ul.copyright-tag-list li.flex::attr(data-tag-name)').getall()
            character = sel.css('ul.character-tag-list li.flex::attr(data-tag-name)').getall()
            tags = sel.css('ul.general-tag-list li.flex::attr(data-tag-name)').getall()
            meta = sel.css('ul.meta-tag-list li.flex::attr(data-tag-name)').getall()

            file_info_text = sel.css('#post-info-size a:nth-child(1)::text').get()
            match = re.match(r'(\d+(?:\.\d+)?\s*[KMG]B)\s*(\.[\w]+)', file_info_text)

            if match:
                size = match.group(1)
                type = match.group(2)
            else:
                size = None
                type = None

            dimensions = sel.css('li#post-info-size::text').getall()[1].strip()

            source_url = sel.css('#post-info-size a:nth-child(1)::attr(href)').get()
            # print(tags)

            return PostInfo(id=post_id, tags=tags, source_url=source_url, artist=artist, copyrights=copyrights, character=character, meta=meta, size=size, type=type, dimensions=dimensions)

        else:
            print(f'post id {post_id} response error:{res.status_code}')
            return None

    def download_file(self, url: str, filename: str):
        res = self.session.get(url=url, headers=self.headers, cookies=self.cookies)
        if res.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(res.content)
        else:
            print('response error:', res.status_code)


if __name__ == '__main__':
    dc = DanbooruCrawler()
    for id,pre in dc.get_posts():
        print(id,pre)
