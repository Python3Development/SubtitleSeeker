import urllib.request
import urllib.error
import urllib.parse
from bs4 import BeautifulSoup
from subtitleseeker import constant


def search_request(engine_url, search):
    if engine_url and search:
        response = http_request(engine_url + urllib.parse.quote(search))
        if response:
            html = response.decode()
            soup = BeautifulSoup(html, 'html.parser')
            tags = soup.find_all('a')
            for tag in tags:
                href = tag.get('href')
                if href and constant.OPENSUBTITLES in href:
                    return href


def scrape_request(url):
    if url and constant.OPENSUBTITLES in url:
        response = http_request(url)
        if response:
            html = response.decode()
            soup = BeautifulSoup(html, 'html.parser')
            form = soup.find('form', attrs=dict(name='moviehash', id='moviehash'))
            a = form.find('a') if form else soup.find('a', attrs=dict(name='bt-dwl', id='bt-dwl-bt'))
            if a:
                download_url = a.get('href')
                if download_url:
                    return build_request(download_url, dict(Referer=url))


def download_srt(url, file):
    if url and file:
        data = http_request(url)
        if data:
            with open(file, "wb") as srt_file:
                srt_file.write(data)
            return True


# region Helper
def http_request(request):
    try:
        return urllib.request.urlopen(request).read()
    except urllib.error.URLError as e:
        print(e)


def build_request(url, headers=None):
    return urllib.request.Request(url=url, headers=headers)
# endregion
