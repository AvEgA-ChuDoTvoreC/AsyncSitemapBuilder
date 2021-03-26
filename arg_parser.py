# -*- coding: utf-8 -*-
import argparse
import textwrap


def cmd_line_parser():
    arg_parser = argparse.ArgumentParser(
            prog='sitemapBuilder',
            usage='%(prog)s [domain] -l [level] -d [depth]      type -h, --help for more info\n'
                  '\n'
                  '>>> sitemapBuilder.py examplesite.com\n'
                  '\n'
                  'check that sitemapBuilder.py is in your Home directory\n'
                  '-----',
            formatter_class=argparse.RawDescriptionHelpFormatter,  # pretty print format
            description=textwrap.dedent('''
                Please Note, that all sitemaps will be at your home directory: 
                for example -  /Users/agent007/Sitemaps/github.com  
                --------------------------------------------
                     _____________________________________
                    < Oh wow, you're on the sitemap prog! >
                     -------------------------------------
                            \   ^__^
                             \  (oo)\_______
                                (__)\       )\/\'
                                    ||----w |
                                    ||     ||
                            Check --help info below
                '''),
            epilog=textwrap.dedent('''
                --------------------------------------------
                The End
    
                ''')
        )

    arg_parser.add_argument(
        'domain',
        type=str,
        help="Site link : vistexample.ru"
    )
    arg_parser.add_argument(
        '-l', '--level',
        dest="level",  # returns the name of the argument through args = parse_args() -> if args.get('level'):
        default=5,  # default value for depth
        type=int,
        metavar='',  # argument name in usage message
        help="search depth level (fo CSVCreator), глубина рекурсии поиска ссылок (для CSVCreator)",
        action="store"
    )
    arg_parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s v1.1'
    )
    arg_parser.add_argument(
        '-w', '--workers',
        dest="workers",
        default=5,
        type=int,
        metavar='',
        help="this workers = threads, the number will auto set depending on number of 1st level links, "
             "запускаем потоки исходя из количества папок первого уровня",
        action="store"
    )
    arg_parser.add_argument(
        '-fd', '--folder-depth',
        dest="fdepth",
        default=2,
        type=int,
        metavar='',
        help="THE MOST USEFUL ARGUMENT, default set -fd 2, if you try to make sitemap and graph map for yandex.ru "
             "or google.com it will stops on /news/ folder and all will be good. Else if you set -fd 4 for yandex.ru "
             "it wil find links over 50 000+ in /news/ folder and probably you get request exception or any bug "
             "that I do not explore yet, глубина поиска папок на сайте ",
        action="store"
    )

    # there are some problems with display dependencies: main -> args.xxx -> make_sitemap_graph
    # depth = 5  # Number of layers deep to plot categorization
    # limit = 50  # Maximum number of nodes for a branch
    # title = ''  # Graph title
    # style = 'light'  # Graph style, can be "light" or "dark"
    # size = '8,5'  # Size of rendered graph
    # output_format = 'pdf'  # Format of rendered image - pdf,png,tiff
    # skip = ''  # List of branches to restrict from expanding
    arg_parser.add_argument('-d', '--depth', dest="depth", type=int, default=5, metavar='',
                            help='number of layers deep to plot categorization (for VisualSitemapView), '
                                 'количество слоев (для VisualSitemapView)')
    arg_parser.add_argument('--limit', dest="limit", type=int, default=50,
                            help='maximum number of nodes for a branch', metavar='')
    arg_parser.add_argument('--title', dest="title", type=str, default='',
                            help='graph title', metavar='')
    arg_parser.add_argument('--style', dest="style", type=str, default='light',
                            help='graph style, can be "light" or "dark"', metavar='')
    arg_parser.add_argument('--size', dest="size", type=str, default='8,5',
                            help='size of rendered graph', metavar='')
    arg_parser.add_argument('--output-format', dest="output_format", type=str, default='pdf',
                            help='format of the graph you want to save. Allowed -- JPG, PDF, PNG, TIF', metavar='')
    arg_parser.add_argument('--skip', dest="skip", type=str, default='', metavar='',
                            help="list of branches that you do not want to expand. "
                                 "Comma separated: e.g. --skip 'news,events,datasets'")

    args = arg_parser.parse_args()

    return args


# parser()

