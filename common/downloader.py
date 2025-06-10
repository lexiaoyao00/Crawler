import requests
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, Callable

class MediaDownloader:
    def __init__(
        self,
        timeout: int = 10,
        headers: Optional[dict] = None,
        chunk_size: int = 8192
    ):
        """
        初始化下载器
        :param timeout: 请求超时时间（秒）
        :param headers: 自定义请求头
        :param chunk_size: 下载分片大小（字节）
        """
        self.timeout = timeout
        self.chunk_size = chunk_size
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self._is_cancelled = False  # 下载取消标志

    def download(
        self,
        url: str,
        target_path: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """
        下载媒体文件
        :param url: 文件URL地址
        :param target_path: 目标路径
        :param progress_callback: 进度回调函数 (已下载字节数, 总字节数)
        :return: 下载文件的最终保存路径
        """
        self._is_cancelled = False
        try:
            response = requests.get(
                url,
                stream=True,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"下载请求失败: {str(e)}") from e

        # 处理目标路径
        if target_path.is_dir():
            file_name = self._get_filename_from_url(url)
            save_path = target_path / file_name
        else:
            save_path = target_path

        # 创建父目录
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # 获取文件大小
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded_size = 0

        try:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=self.chunk_size):
                    if self._is_cancelled:
                        break

                    if chunk:  # 过滤keep-alive数据块
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # 触发进度回调
                        if progress_callback:
                            progress_callback(downloaded_size, total_size)

        except IOError as e:
            raise RuntimeError(f"文件写入失败: {str(e)}") from e
        finally:
            response.close()
            if self._is_cancelled:
                save_path.unlink(missing_ok=True)  # 删除未完成文件
                raise RuntimeError("下载已被取消")

        return save_path

    def cancel_download(self):
        """取消当前下载"""
        self._is_cancelled = True

    @staticmethod
    def _get_filename_from_url(url: str) -> str:
        """从URL中提取文件名"""
        path = urlparse(url).path
        filename = Path(path).name
        return filename if filename else "unknown_file"
