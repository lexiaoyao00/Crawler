import curl_cffi
from parsel import Selector
from pydantic import BaseModel
from typing import List
import re


class Post(BaseModel):
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

class DanbooruCrawler():
    def __init__(self):
        self.base_url = 'https://danbooru.donmai.us'
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

    def get_post(self, post_id: int):
        # post_info = Post(id=post_id)
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

            return Post(id=post_id, tags=tags, source_url=source_url, artist=artist, copyrights=copyrights, character=character, meta=meta, size=size, type=type, dimensions=dimensions)

        else:
            print('response error:',res.status_code)


if __name__ == '__main__':
    dc = DanbooruCrawler()
    post = dc.get_post(9358913)
    post.save_to_json('post.json')

    # print('post',post.id,'original_url is ',post.source_url)