import asyncio
import aiohttp
import async_timeout
from rotating_proxies import RotatingProxies
import tkinter as tk
import os
import logging
import schedule
import time

url = "https://example.com/large_file.zip"
chunk_size = 1024 * 1024  # 1 MB
download_dir = "downloads"
log_file = "download_log.txt"


delay = 10


max_retries = 5

proxy_providers = [
    "luminati.io",
    "oxylabs.io",
    "smartproxy.com",
    "privoxy.org",
    "swiperproxy.github.io",
    "haproxy.org",
]

async def download_chunk(session, url, start_byte, end_byte, proxy):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
        "Range": f"bytes={start_byte}-{end_byte}"
    }

    try:
        timeout = async_timeout.timeout(5)
        async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as response:
            if is_captcha_detected(await response.text()):
                print("CAPTCHA detected. Switching to a new proxy.")
                return None
            response.raise_for_status()
            return await response.read()
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error downloading chunk: {e}")
        return None

def is_captcha_detected(content):
    return "captcha" in content.lower()

async def download_file(url, file_name):
    current_proxy = rotating_proxies.get_next_proxy()

    retry_count = 0

    os.makedirs(download_dir, exist_ok=True)

    file_path = os.path.join(download_dir, file_name)

    async with aiohttp.ClientSession() as session:
        try:
            timeout = async_timeout.timeout(5)
            async with session.head(url, proxy=current_proxy, timeout=timeout) as response:
                file_size = int(response.headers["Content-Length"])
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error getting file size: {e}")
            return

        if os.path.exists(file_path):
            start_byte = os.path.getsize(file_path)
        else:
            start_byte = 0

        num_chunks = (file_size + chunk_size - 1) // chunk_size
        chunks = [(i * chunk_size, min((i + 1) * chunk_size - 1, file_size - 1)) for i in range(num_chunks)]

        with open(file_path, "ab") as f:
            while retry_count < max_retries:
                tasks = [download_chunk(session, url, start, end, current_proxy) for start, end in chunks]
                results = await asyncio.gather(*tasks)

                if all(result is not None for result in results):
                    for chunk in results:
                        f.write(chunk)
                    print(f"Download completed: {file_name}")
                    break

                if any(result is None for result in results):
                    print("CAPTCHA detected. Switching to a new proxy.")
                    current_proxy = rotating_proxies.get_next_proxy()

                retry_count += 1
            else:
                print(f"Error: Maximum number of retries exceeded for {file_name}")

async def download_manager():
    while True:
        url, file_name = await download_queue.get()
        await download_file(url, file_name)
        download_queue.task_done()

async def main():
    global rotating_proxies

    window = tk.Tk()
    window.title("Hello World")

    progress_bar = tk.ttk.Progressbar(window, orient=tk.HORIZONTAL, length=200)
    progress_bar.pack(padx=10, pady=10)

    button = tk.Button(window, text="Start Download", command=lambda: asyncio.create_task(download_file(url, "large_file.zip")))
    button.pack(padx=10, pady=10)

    proxy_list = ProxyLists()
    proxies = []
    for provider in proxy_providers:
        proxies.extend(proxy_list.get_proxies(provider, country="BR", anonymous=True))

    rotating_proxies = RotatingProxies(proxies)

    for _ in range(5):
        asyncio.create_task(download_manager())

    download_queue.put_nowait((url, "large_file.zip"))
    download_queue.put_nowait(("https://example.com/another_file.zip", "another_file.zip"))

    schedule.every(1).hour.do(lambda: asyncio.create_task(download_file(url, "large_file.zip")))
    schedule.every(2).hour.do(lambda: asyncio.create_task(download_file("https://example.com/another_file.zip", "another_file.zip")))

    while True:
        schedule.run_pending()
        time.sleep(1)

    await download_queue.join()

    window.mainloop()

logging.basicConfig(filename=log_file, level=logging.INFO)

asyncio.run(main())