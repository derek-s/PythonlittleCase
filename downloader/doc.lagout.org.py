#!/usr/bin/python3
# -*- coding:utf-8 -*-

import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
import datetime
from multiprocessing import Pool, current_process
import time
import logging
from requests.adapters import HTTPAdapter

class spider():
    def __init__(self):
        self.header = {
            "Referer": "https://www.baidu.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
            "Connection": "close"
        }
        self.url = "https://doc.lagout.org/"
        self.proxy = {
            "http": "http://127.0.0.1:1090",
            "https": "http://127.0.0.1:1090"
        }
    
    def request(self, url):
        fails = 1
        while fails < 31:
            try:
                r = requests.get(url, headers=self.header, timeout=10, proxies=self.proxy)
                return r.text
            except Exception as e:
                print(e)
                print('error retry')
                fails += 1

    def page_source(self, pgstr, url):
        soup = BeautifulSoup(pgstr, "html.parser")
        for a_link in soup.select('body[bgcolor="white"] > pre > a[href]'):
            link = a_link["href"]
            if link == "../":
                pass
            elif link.split('//')[-1].split('.')[-1].split('/')[-1] == "":
                link = url + link
                print(link)
                self.mkdir(link)
                self.download(link)
                self.page_source(self.request(link), link)
            else:
                link = url + link
                print(link)
                self.mkdir(link)
                self.download(link)

    def mkdir(self, url):
        if url == "":
            path = self.url.split('//')[-1]
            if not os.path.exists(path):
                os.makedirs(path)
                print(path + "create")
            else:
                print(path + "exists")
        else:
            path = str(url).split('//')[-1]
            if str(path).split('//')[-1].split('.')[-1].split('/')[-1] == "":
                if not os.path.exists(path):
                    os.makedirs(path)
                    print(path + " is create")
                else:
                    print(path + " is exists")
            else:
                print(path + " is file")
        
    def download(self, url):
        path = str(url).split('//')[-1]
        filename = str(url).split('/')[-1]
        if filename.split('.')[-1] == '':
            filename = path + "index.html"
            self.indexdown(url, filename)
        else:
            filename = path
            filexists, length = self.isExists(url, filename)
            if filexists:
                self.filedown(url, filename, length)
            else:
                pass
                
    def indexdown(self, url, filename):
        try:
            print("downloading", url)
            if not os.path.exists(filename):
                with open(filename, "wb") as down_write:
                    down_write.write(self.request(url).encode('utf-8'))
                print("done")
            else:
                print(filename + " is exists")
        except Exception as e:
            print(e)

    def isExists(self, url, filename):
        s = requests.Session()
        s.keep_alive = False
        s.mount("http://", HTTPAdapter(max_retries=30))
        s.mount("https://", HTTPAdapter(max_retries=30))
        r = s.head(url, headers=self.header, proxies=self.proxy)
        # r = requests.head(url)
        total_length = int(r.headers["Content-Length"])
        if os.path.exists(filename):
            print('%s is exists' % filename)
            if os.path.getsize(filename) != total_length:
                return True, total_length
            else:
                return False, total_length
        else:
            return True, total_length

    def downproc(self, url, filename, start, end):
        """
        try:  # for Python 3
            from http.client import HTTPConnection
        except ImportError:
            from httplib import HTTPConnection
        HTTPConnection.debuglevel = 1

        logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
            "Range": "bytes=%d-%d" % (start, end),
            "Connection": "close"
            }
        s = requests.Session()
        s.keep_alive = False
        s.mount("http://", HTTPAdapter(max_retries=30))
        s.mount("https://", HTTPAdapter(max_retries=30))
        r = s.get(url, headers=headers, stream=True, proxies=self.proxy)
        # r = requests.get(url, headers=headers, stream=True)
        length = end - start
        text = current_process().name
        postion = str(text).split('-')[-1]
        progress = tqdm(
            ncols=80,
            total=length,
            unit_scale=True,
            position=int(postion),
            unit='B',
            miniters=1
            )
        with open(filename, "r+b") as fp:
            fp.seek(start)
            var = fp.tell()
            for chunk in r.iter_content(chunk_size=256):
                fp.write(chunk)
                fp.flush()
                progress.update(len(chunk))
            progress.close()

    def filedown(self, url, filename, total_length):
        nthreads = 1
        filename_temp = filename + ".temp"
        f = open(filename_temp, "wb")
        f.truncate(total_length)
        f.close()
        print("Total_Length", total_length)
        part = total_length // nthreads
        startime = datetime.datetime.now().replace(microsecond=0)
        l = []
        pool = Pool(nthreads)
        for i in range(nthreads):
            start = part * i
            if i == nthreads - 1:
                end = total_length
            else:
                end = start + part
            l.append((url, filename_temp, start, end))
        pool.starmap(self.downproc, l)

        pool.close()
        pool.join()
        time.sleep(5)
        print("\n" * 4)
        print("download complete")
        os.rename(filename_temp, filename)
        endtime = datetime.datetime.now().replace(microsecond=0)
        print(endtime-startime)


if __name__ == "__main__":
    testurl = "https://doc.lagout.org/"
    spiders = spider()
    spiders.page_source(spiders.request(testurl), testurl)
    #spiders.download("http://tfr.org/cisco/")