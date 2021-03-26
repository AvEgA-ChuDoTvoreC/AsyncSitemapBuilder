import time
import datetime

import xml.etree.cElementTree as ET


class ElementTreeCreator:
    def __init__(self, links_list):
        self.links_list = links_list

    def creating_sitemap(self):
        """
        Sitemap cr8 func()
        """
        time.sleep(2)
        # os.system('clear')
        print('Creating Sitemap...')
        urlset = ET.Element("urlset", xlmns="http://www.sitemaps.org/schemas/sitemap/0.9")
        count = 0
        while count < len(self.links_list):
            urls = ET.SubElement(urlset, "url")
            today = datetime.datetime.today().strftime('%Y-%m-%d')
            ET.SubElement(urls, "loc", ).text = str(self.links_list[count])
            ET.SubElement(urls, "lastmod", ).text = str(today)
            ET.SubElement(urls, "priority", ).text = "1.00"
            count = count + 1
        else:
            tree = ET.ElementTree(urlset)

            print("Your Sitemap is Ready!\n Don't close, program is still running...\n Check link below later:")

        return tree

