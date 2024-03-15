import asyncio
import aiohttp
import async_timeout
from proxylists import ProxyLists
from rotating_proxies import RotatingProxies
import tkinter as tk

url = "https://example.com/file.zip"

# Tempo de espera entre as solicitações (em segundos)
delay = 10

# Número máximo de tentativas
max_retries = 5

proxy_providers = [
    "luminati.io",
    "oxylabs.io",
    "smartproxy.com",
    "privoxy.org",
    "swiperproxy.github.io",
    "haproxy.org",
    # ...
]


async def download_file(url, proxy):
  
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
    }

    try:
        timeout = async_timeout.timeout(5)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(proxy=proxy)) as session:
            response = await session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Erro ao baixar o arquivo: {e}")
        return None

    return response


async def start_download():
    
    # Obtem um novo proxy da lista rotativa
    current_proxy = rotating_proxies.get_next_proxy()

    # Reinicia a contagem de tentativas
    retry_count = 0

    # Inicia o download em uma thread separada
    asyncio.create_task(download_file(url, current_proxy))


def update_gui():

    global retry_count

    if retry_count < max_retries:
        button["text"] = f"Baixando... (Tentativa {retry_count + 1}/{max_retries})"
    else:
        button["text"] = "Erro: Número máximo de tentativas excedido."

    if response is not None:
        progress_bar["value"] = response.content_length / response.headers["Content-Length"]

async def main():

    global rotating_proxies, response, retry_count

    window = tk.Tk()
    window.title("Ola Mundo")

    progress_bar = tk.ttk.Progressbar(window, orient=tk.HORIZONTAL, length=200)
    progress_bar.pack(padx=10, pady=10)

    button = tk.Button(window, text="Iniciar Download", command=start_download)
    button.pack(padx=10, pady=10)

    proxy_list = ProxyLists()
    proxies = []
    for provider in proxy_providers:
        proxies.extend(proxy_list.get_proxies(provider, country="BR", anonymous=True))
