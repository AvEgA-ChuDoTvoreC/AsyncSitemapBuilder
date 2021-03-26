import time
import subprocess
from subprocess import Popen, PIPE

import graphviz
import pandas as pd


# there are some problems with display dependencies: main -> args.xxx -> make_sitemap_graph
# depth = 5  # Number of layers deep to plot categorization
# limit = 50  # Maximum number of nodes for a branch
# title = ''  # Graph title
# style = 'light'  # Graph style, can be "light" or "dark"
# size = '8,5'  # Size of rendered graph
# output_format = 'pdf'  # Format of rendered image - pdf,png,tiff
# skip = ''  # List of branches to restrict from expanding


class VisualSitemapView:
    """
    Visualize a list of URLs by site path.

    This script reads in the sitemap_layers.csv file created by the
    categorize_urls.py script and builds a graph visualization using Graphviz.
    """

    # Set global variables
    def __init__(self):

        # Update variables with arguments if included
        self.graph_depth = 5  # same == layer
        self.limit = 50
        self.title = "title"
        self.style = "light"
        self.size = "8,5"
        self.output_format = "pdf"
        self.skip = ""
        self.filename = ""

        self.layers_checked = 0  # checked layers == REAL DEPTH

    # Main script functions
    def make_sitemap_graph(self, sitemap_layers, layers, limit, size,
                           output_format, skip):
        """
        Make a sitemap graph up to a specified layer depth.

        sitemap_layers : DataFrame
            The dataframe created by the peel_layers function
            containing sitemap information.

        layers : int
            Maximum depth to plot.

        limit : int
            The maximum number node edge connections. Good to set this
            low for visualizing deep into site maps.

        output_format : string
            The type of file you want to save in PDF, PNG, TIFF, JPG

        skip : list
            List of branches that you do not want to expand.

        Check --help arg in terminal for more info
        """

        # Check to make sure we are not trying to create too many layers
        if layers > len(sitemap_layers) - 1:
            layers = len(sitemap_layers) - 1
            print(f'There are only {layers} layers available to create, setting layers = {layers}')
        self.layers = layers

        # Initialize graph
        f = graphviz.Digraph('sitemap', filename=f'tmp_sitemap/sitemap_graph_{layers}_layer',
                             format=f'{output_format}')
        f.body.extend(['rankdir=LR', f'size="{size}"'])

        def add_branch(f, names, vals, limit, connect_to=''):
            """ Adds a set of nodes and edges to nodes on the previous layer. """

            # Get the currently existing node names
            node_names = [item.split('"')[1] for item in f.body if 'label' in item]

            # Only add a new branch it it will connect to a previously created node
            if connect_to:
                if connect_to in node_names:
                    for name, val in list(zip(names, vals))[:limit]:
                        f.node(name=f'{connect_to}-{name}', label=name)
                        f.edge(connect_to, f'{connect_to}-{name}', label='{:,}'.format(val))

        f.attr('node', shape='component', fillcolor='gold', fontsize='20')  # Plot nodes as rectangles / components ..
        # http://www.graphviz.org/doc/info/shapes.html#polygon

        # Add the first layer of nodes
        for name, counts in sitemap_layers.groupby(['0'])['counts'].sum().reset_index().sort_values(['counts'],
                                                                                                    ascending=False).values:
            f.node(name=name, label='{} ({:,})'.format(name, counts))

        if layers == 0:
            return f

        f.attr('node', shape='oval', fillcolor='#dbdddd')  # Plot nodes as ovals / folders ..
        f.graph_attr.update()

        # Loop over each layer adding nodes and edges to prior nodes
        for i in range(1, layers + 1):
            cols = [str(i_) for i_ in range(i)]
            nodes = sitemap_layers[cols].drop_duplicates().values
            for j, k in enumerate(nodes):

                # Compute the mask to select correct data
                mask = True
                for j_, ki in enumerate(k):
                    mask &= sitemap_layers[str(j_)] == ki

                # Select the data then count branch size, sort, and truncate
                data = sitemap_layers[mask].groupby([str(i)])['counts'].sum().reset_index().sort_values(['counts'],
                                                                                                        ascending=False)

                # Add to the graph unless specified that we do not want to expand k-1
                if (not skip) or (k[-1] not in skip):
                    add_branch(f,
                               names=data[str(i)].values,
                               vals=data['counts'].values,
                               limit=limit,
                               connect_to='-'.join(['%s'] * i) % tuple(k))

                print(f'Built graph up to node {j} / {len(nodes)} in layer {i}'.ljust(50), end='\r')

        return f

    def apply_style(self, f, style, title=''):
        """
        Apply the style and add a title if desired. More styling options are
        documented here: http://www.graphviz.org/doc/info/attrs.html#d:style

        f : graphviz.dot.Digraph
            The graph object as created by graphviz.

        style : str
            Available styles: 'light', 'dark'

        title : str
            Optional title placed at the bottom of the graph.
        """

        dark_style = {
            'graph': {
                'label': self.title,
                'bgcolor': '#3a3a3a',
                'fontname': 'Helvetica',
                'fontsize': '18',
                'fontcolor': 'white',
            },
            'nodes': {
                'style': 'filled',
                'color': 'white',
                'fillcolor': 'black',
                'fontname': 'Helvetica',
                'fontsize': '14',
                'fontcolor': 'white',
            },
            'edges': {
                'color': 'white',
                'arrowhead': 'open',
                'fontname': 'Helvetica',
                'fontsize': '12',
                'fontcolor': 'white',
            }
        }

        light_style = {
            'graph': {
                'label': self.title,
                'fontname': 'Helvetica',
                'fontsize': '18',
                'fontcolor': 'black',
            },
            'nodes': {
                'style': 'filled',
                'color': 'black',
                'fillcolor': '#dbdddd',
                'fontname': 'Helvetica',
                'fontsize': '14',
                'fontcolor': 'black',
            },
            'edges': {
                'color': 'black',
                'arrowhead': 'open',
                'fontname': 'Helvetica',
                'fontsize': '12',
                'fontcolor': 'black',
            }
        }

        if style == 'light':
            apply_style = light_style

        elif style == 'dark':
            apply_style = dark_style

        f.graph_attr = apply_style['graph']
        f.node_attr = apply_style['nodes']
        f.edge_attr = apply_style['edges']

        return f

    def make_pdf_jpg(self):
        # Read in categorized data
        sitemap_layers = pd.read_csv(f'tmp_sitemap/sitemap_layers.csv', dtype=str)

        # Convert numerical column to integer
        sitemap_layers.counts = sitemap_layers.counts.apply(int)
        print(f'Loaded {len(sitemap_layers)} rows of categorized data from tmp_sitemap/sitemap_layers.csv')

        print('Building {} layer deep sitemap graph'.format(self.graph_depth))
        f = self.make_sitemap_graph(sitemap_layers, layers=self.graph_depth,
                                    limit=self.limit, size=self.size, output_format=self.output_format, skip=self.skip)
        f = self.apply_style(f, style=self.style, title=self.title)

        f.render(cleanup=True)
        print('Exported graph to tmp_sitemap/sitemap_graph_{}_layer.{}'.
              format(self.layers, self.output_format))
        time.sleep(5)
        self.run_command(f'open tmp_sitemap/sitemap_graph_{self.layers}_layer.{self.output_format}')
        time.sleep(2)
        self.run_command(f'open tmp_sitemap/sitemap.xml')

    def run_command(self, cmd, echo=True, exit_on_error=False):
        """Communication to bash frow terminal using subprocess"""
        p = Popen(cmd, stdout=subprocess.PIPE, stderr=PIPE, shell=True, universal_newlines=True)
        o, e = p.communicate()
        return p.returncode, o, e

