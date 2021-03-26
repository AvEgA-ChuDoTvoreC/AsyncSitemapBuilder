# -*- coding: utf-8 -*-
import asyncio
import time
import json
import os
import sys
import re
from pprint import pprint
from datetime import timedelta
import subprocess
from subprocess import Popen, PIPE
import logging
from logging.handlers import TimedRotatingFileHandler

import requests
import aiohttp
from bs4 import BeautifulSoup

from arg_parser import cmd_line_parser
from errors_exceptions import response_status_codes, UserError, ServerError
from csv_creator import CSVCreator
from visual_grath import VisualSitemapView
from element_tree import ElementTreeCreator


try:
    contid = subprocess.check_output('cut -c9-20 < /proc/1/cpuset', shell=True, universal_newlines=True)[:-1]
except Exception as e:
    print("You are using not docker container build! contid in logs will be set as NotContainer")
    contid = "NotContainer"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s : [' + contid + '] :[%(filename)s.%(lineno)d]: %(levelname)s : %(message)s',
    handlers=[TimedRotatingFileHandler("logs/Crawler_{}.log".format(contid), when="midnight")])


class Configurator:
    """ Gather information from config file """

    def __init__(self, config_file):
        self.config_file = config_file

        self.default_config = dict()

        self.update_date = None
        self.text = None
        self.extra = None

        self.update_config()

    def update_config(self):
        if os.path.exists("webconf/{}".format(self.config_file)):
            with open("webconf/{}".format(self.config_file)) as web_f:
                self.default_config = json.load(web_f)
                # FIXME: self.default_config = json.load(f)
        else:
            with open("baseconfig/{}".format(self.config_file)) as def_f:
                self.default_config = json.load(def_f)

    def nested_get(self, input_dict, nested_key):
        internal_dict_value = input_dict
        for k in nested_key:
            internal_dict_value = internal_dict_value.get(k, "NoMatchOption")
            if internal_dict_value == "NoMatchOption":
                return "NoMatchOption"
        return internal_dict_value

    def config_get_param(self, *params):
        data = self.nested_get(self.default_config, params)
        if data == "NoMatchOption":
            data = None
        return data

    def file_reader(self, filename):
        """
        Simple file reader
        """
        with open(filename, "r") as file_text:
            self.text = file_text.read()
        return self.text

    def set_update_date(self, now=None, hour=None, minute=None):
        """
        Set update Date to the next day.

        :param now: datetime.now()
        :param hour: integer:
        :param minute: integer:
        :return: date:  self.update_date
        """
        # if 1:00 < 3:00 AM
        if now < now.replace(hour=hour, minute=minute):
            # update_date = 3:00 18.01.2020
            self.update_date = now.replace(hour=hour, minute=minute)
        else:
            # update_date = 3:00 19.01.2020
            self.update_date = (now + timedelta(days=1)).replace(hour=hour, minute=minute)
        logging.info("Update date time: {}".format(self.update_date), extra=self.extra)

        return self.update_date


class Parsers:
    def __init__(self):
        self.soup = None
        self.bs4_parser = None
        self.bs4_default_parser = 'lxml'
        self.html_page = None

        self.protocol = None
        self.domain = None
        self.url = None
        self.domain_validator_regex = None

        self.count_links = False
        self.parse_main_page = False

        self.href_links = list()
        self.data_href_links = list()
        self.src_links = list()

        self.html_page_routes = list()
        self.html_page_links = list()
        self.new_routes = list()

    def routes_parser(self, routes_list, count_links, domain_url):
        new_list_of_urls = list()

        count = 0
        if count_links:
            # FIXME: add count links
            pass
        else:
            while count < len(routes_list):
                pass


        return new_list_of_urls

    def BS4_parser(self, html_page, bs4_parser=None, count_links=False, domain_url=None, parse_main_page=False) -> list:
        """
        Find all HREF, DATA_HREF, SRC -> and put it in list:  HTML_PAGE_LINKS

            :param parse_main_page: False
            :param domain_url:
            :param count_links: True
            :param html_page:
            :param bs4_parser: "html.parser", "lxml", "lxml-xml", "xml", "html5lib"
                            check https://en.wikipedia.org/wiki/Beautiful_Soup_(HTML_parser)
            :return: html_page_links
        """
        # -- Configure bs4 --
        if bs4_parser:
            self.bs4_parser = bs4_parser
        else:
            self.bs4_parser = self.bs4_default_parser

        self.html_page = html_page
        self.soup = BeautifulSoup(self.html_page, self.bs4_parser)

        self.count_links = count_links
        self.domain = domain_url
        self.parse_main_page = parse_main_page

        # == Gather links ==
        self.href_links = [h['href'] for h in self.soup.findAll('a', href=True) if h is not None]
        # print("self.href_links: \n", self.href_links)
        self.data_href_links = [d.get('data-href') for d in self.soup.findAll() if d.get('data-href') is not None]
        # print("self.data_href_links: \n", self.data_href_links)
        self.src_links = [s.get('src') for s in self.soup.findAll() if s.get('src') is not None]
        # print("self.src_links: \n", self.src_links)

        # == Add links/routes to list ==
        self.html_page_routes = self.add_routes(self.href_links, self.data_href_links, self.src_links)
        # self.html_page_links = self.add_links(self.href_links, self.data_href_links, self.src_links)

        # if parse_main_page is False:
        #     self.new_routes = self.routes_parser(routes_list=self.html_page_routes,
        #                                          count_links=self.count_links,
        #                                          domain_url=self.domain)
        #     return self.new_routes

        return self.html_page_routes  # , self.html_page_links

    def add_links(self):
        """ Gather links """
        pass

    def add_routes(self, *args):
        """ Gather routes """
        # == Check for extension ==
        extension = re.compile(r'(\.([\w-]{1,10}))$')
        true_word = re.compile(r'/(\w{1,62})/?$')

        # == Clean up routes ==
        routes_list = list()
        for arg in args:
            for _ in arg:
                if _ and _ != '/' and 'http' not in _ and 'mailto:' not in _ and 'tel' not in _ and \
                        not extension.search(_) and '.' not in _.split('/')[-1] and not _.startswith('#'):
                    # FIXME: and true_word.search(_) and '.' not in _.split('/')[-1]  -???
                    if self.count_links:
                        routes_list.append(_)
                    else:
                        if _ not in routes_list:
                            routes_list.append(_)

        # == Add slash to the end of route ==
        c = 0
        while c < len(routes_list):
            for tmp_link in routes_list:
                if not tmp_link.endswith('/'):  # and not tmp_link.startswith('http') and '.' not in tmp_link:
                    routes_list[c] += '/'
                if self.domain:
                    if not tmp_link.startswith(self.domain):
                        routes_list[c] = self.domain + routes_list[c]
                c += 1

        return routes_list

    def domain_parser(self, domain) -> []:
        self.domain_validator_regex = re.compile(r'^((?!-))(xn--)?[a-z0-9][a-z0-9-_]{0,61}[a-z0-9]{0,1}\.'
                                                 r'(xn--)?([a-z0-9\-]{1,61}|[a-z0-9-]{1,30}\.[a-z]{2,})$')

        if domain.startswith('http://'):
            protocol = 'http://'
            domain = domain.replace(protocol, '')
        elif domain.startswith('https://'):
            protocol = 'https://'
            domain = domain.replace(protocol, '')
        else:
            protocol = 'https://'

        if 'www.' in domain:
            domain = domain.replace('www.', '')
        elif 'ww.' in domain:
            return None

        valid = self.domain_validator_regex.fullmatch(domain)
        if valid:
            print(f'Domain:      "{domain}"  VALID!')
        else:
            print(f'Domain:      "{domain}"  NOT VALID!')

        self.url = protocol + domain

        print(f'Protocol:    "{protocol}"')
        print(f'Domain:      "{domain}"')
        print(f'Url:         "{self.url}"')

        return self.url, domain


class AsyncContentDownoader:
    """
    To use Asynchronous class we need to reassign methods:
            __aenter__, __aexit__ which represents bock 'with'
            so we get coroutine class
    Also we need Context Manager construction 'async with Class() as name:'
    To get attributes from Context Manager (__aenter__, __aexit__)
    """

    def __init__(self):
        self.filename = str()
        self.headers = headers
        self.links = None

    async def __aenter__(self):
        self._aio_session = aiohttp.ClientSession(headers=self.headers)
        self._session = await self._aio_session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            return await self._session.__aexit__(exc_type, exc, tb)

    async def download_content(self, url):
        # print(f'Started downloading {url}')
        try:
            resp = await self._session.get(url)
            content = await resp.read()
        except Exception as err:
            print(err)
            content = None
        finally:
            pass
            # print(f'Finished downloading {url}')
        return content

    async def parse_content(self, n, content, url, _domain_url=None, parse_main_page=False):
        self.filename = f'async_{n}.html'
        # print(self.filename)
        if content:
            link_list = parsers.BS4_parser(content,
                                           count_links=False,
                                           domain_url=_domain_url,
                                           parse_main_page=parse_main_page)
        else:
            print("link_list ----> 0")
            link_list = list()

        if _domain_url:
            print(f"{len(link_list)} Result Links for {url}")
            # pprint(link_list)

            with open('tmp_sitemap/tmp.dat', 'a+') as ff:
                xx = ff.readlines()

            with open('tmp_sitemap/tmp.dat', 'a') as ff:
                for li in link_list:
                    if li+'\n' not in xx:
                        ff.write(li + '\n')

        return link_list

    async def scrape_task(self, n, url, _domain_url=None, parse_main_page=False):
        content = await self.download_content(url)
        parsed_links = await self.parse_content(n, content, url, _domain_url, parse_main_page)
        for i in parsed_links:
            if i not in crawler_links:
                crawler_links.append(i)

    async def main(self, _links, _domain_url=None, parse_main_page=False):
        tasks = list()
        self.links = _links

        for n, url in enumerate(self.links, 1):
            tasks.append(asyncio.create_task(self.scrape_task(n, url, _domain_url, parse_main_page)))
        await asyncio.gather(*tasks)


class AsyncCrawlerStarter:
    def __init__(self, crawler_links_list, domain_url=None, parse_main_page=False):
        self.acd = AsyncContentDownoader()
        self.loop = asyncio.get_event_loop()
        self.links = crawler_links_list
        self.domain_url = domain_url
        self.parse_main_page = parse_main_page

    def get_ticks(self):
        return self.loop.run_until_complete(self.__async__get_ticks())

    async def __async__get_ticks(self):
        async with self.acd as acd:
            return await acd.main(_links=self.links, _domain_url=self.domain_url, parse_main_page=self.parse_main_page)


def find_all_paths(graph, start, end, path=[]):
    path = path + [start]

    if start == end:
        return [path]
    if not graph.__contains__(start):
        return []

    paths = []
    for node in graph[start]:
        if node not in path:
            newpaths = find_all_paths(graph, node, end, path)
            for newpath in newpaths:
                paths.append(newpath)

    return paths


if __name__ == '__main__':
    print("Go")
    t = time.perf_counter()

    config_file_name = 'config.json'

    cf = Configurator(config_file_name)
    headers = cf.config_get_param("User_Agent_Headers")
    resp_status_code = response_status_codes()
    parsers = Parsers()
    cmd_args = cmd_line_parser()

    run_links = list()
    crawler_links = list()

    # link = 'vistgroup.ru'
    link = cmd_args.domain
    fdepth = cmd_args.fdepth

    parsed_domain_url, parsed_domain = parsers.domain_parser(domain=link.strip())
    run_links.append(parsed_domain_url)

    crawler = AsyncCrawlerStarter(crawler_links_list=run_links,
                                  domain_url=parsed_domain_url,
                                  parse_main_page=True)
    crawler.get_ticks()

    # count = 0
    # while len(checked_links) > 0:
    tmp_list = crawler_links.copy()
    checked_links = crawler_links.copy()

    count = 0
    while len(tmp_list) != 0:
        tmp_list = crawler_links.copy()

        print("TMP LIST BEFORE: ", len(tmp_list))
        count += 1
        if count >= 2:
            try:
                for _ in checked_links:
                    if _ in tmp_list:
                        tmp_list.remove(_)
            except ValueError as err:
                print(err)

        print("TMP LIST AFTER: ", len(tmp_list))
        if len(tmp_list) > 0:

            crawler = AsyncCrawlerStarter(crawler_links_list=tmp_list,
                                          domain_url=parsed_domain_url)
            crawler.get_ticks()
        else:
            print("BREAK")
            break

        checked_links = checked_links + tmp_list.copy()

    sitemap = ElementTreeCreator(links_list=crawler_links)
    sitemap_file = sitemap.creating_sitemap().write('tmp_sitemap/sitemap.xml')

    creator = CSVCreator(filename='tmp_sitemap/tmp.dat', layers_level=5)
    creator.make_csv()

    creator2 = VisualSitemapView()
    creator2.make_pdf_jpg()

    t2 = time.perf_counter() - t
    print(f'Total time taken: {t2:0.2f} seconds')
