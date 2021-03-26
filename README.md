# AsyncSitemapBuilder

Recreation of SitemapBuilder using Asynchronous requests via modules: 'aiohttp' and 'asyncio'


## Installation:

Clone the repo:
```bash
$ git clone https://github.com/AvEgA-ChuDoTvoreC/AsyncSitemapBuilder.git
$ cd AsyncSitemapBuilder
```
Set up virtual environment:
```bash
$ pyenv virtualenv 3.9.2 web
$ source web/bin/activate
$ pip install -r requirements.txt
```
Run the crawler:
```bash
$ python crawler.py crawler-test.com
```
Check ```tmp_sitemap``` folder or wait til ```run_command()``` function open with ```subprocess.Popen()``` them (see ```visual_grath.py```).

FIXME: 
 - [ ] arg_parser.py is not set up
 - [ ] not optimized start with '__main'
 - [ ] no data base saves
 - [ ] no allow redirects function

## Visual Examples


![graphviz ex](https://github.com/AvEgA-ChuDoTvoreC/AsyncSitemapBuilder/blob/main/pic/graphviz_ex.png)

![element_tree_ex](https://github.com/AvEgA-ChuDoTvoreC/AsyncSitemapBuilder/blob/main/pic/element_tree_ex.png)