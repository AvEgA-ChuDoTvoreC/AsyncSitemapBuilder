import time

import pandas as pd


class CSVCreator:
    """
    Categorize a list of URLs by file path.

    The file containing the URLs should exist in the working directory and be
    named sitemap_urls.dat. It should contain one URL per line.
    """

    # Set global variables
    def __init__(self, filename, layers_level):
        self.sitemap_layers = pd.DataFrame()  # Store results in a dataframe
        self.layer = layers_level
        self.file = filename

    # Main script functions, слоев 5
    def peel_layers(self, urls, layers=5):
        """
        Builds a dataframe containing all unique page identifiers up
        to a specified depth and counts the number of sub-pages for each.
        Prints results to a CSV file.

        :param urls : list
            List of page URLs.

        :param layers : int
            Depth of automated URL search. Large values for this parameter
            may cause long runtimes depending on the number of URLs.

        :return: sitemap_layers = pd.Series(in urls) == DataFrame
        """

        # Get base levels
        bases = pd.Series([url.split('//')[-1].split('/')[0] for url in urls])
        self.sitemap_layers[0] = bases

        # Get specified number of layers
        for layer in range(1, layers + 1):

            page_layer = []
            for url, base in zip(urls, bases):
                try:
                    page_layer.append(url.split(base)[-1].split('/')[layer])
                except:
                    # There is nothing that deep!
                    page_layer.append('')

            self.sitemap_layers[layer] = page_layer

        # Count and drop duplicate rows + sort
        sitemap_layers = self.sitemap_layers.groupby(list(range(0, layers + 1)))[0].count() \
            .rename('counts').reset_index() \
            .sort_values('counts', ascending=False) \
            .sort_values(list(range(0, layers)), ascending=True) \
            .reset_index(drop=True)

        # Convert column names to string types and export
        sitemap_layers.columns = [str(col) for col in sitemap_layers.columns]
        sitemap_layers.to_csv(f'tmp_sitemap/sitemap_layers.csv', index=False)

        # Return the dataframe
        return sitemap_layers

    def make_csv(self):

        with open(f'{self.file}', 'r') as f:
            sitemap_urls = f.read().splitlines()
            print(f'Loaded {len(sitemap_urls)} URLs')

        print(f'Depth level is {self.layer}')
        sitemap_layers = self.peel_layers(urls=sitemap_urls,
                                          layers=self.layer)
        print(f'Printed {len(sitemap_layers)} rows of data to tmp_sitemap/sitemap_layers.csv')
        time.sleep(2)

