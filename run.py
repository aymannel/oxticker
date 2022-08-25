import sys
import logging

from core import FacebookScraper
from core import Parser

sys_options = [op for op in sys.argv[1:] if op != '']
logging.basicConfig(level=logging.INFO, format='(%(levelname)-s) %(asctime)s %(message)s', datefmt='%H:%M:%S')


def scrape():
    scraper = FacebookScraper()
    scraper.login()
    scraper.get_page('https://www.facebook.com/groups/oxtickets')

    keys = input('press <Enter> to commit page source / press any other key to quit')
    
    while keys == '':
        scraper.get_html()
        logging.info('Page source commited to file')
        keys = input()

    scraper.teardown()
    
def parse():
    logging.info('Creating instance of Parser object')
    parser = Parser()
    logging.info('Parser object initialised')

    parser.get_post_titles()
    parser.get_post_content()
    parser.get_post_names()
    parser.get_post_prices_locations()
    parser.get_comment_number()
    parser.compile_data()
    parser.print_data()
    logging.info('Parsing process complete')


if len(sys_options) == 0:
    logging.info('No options set')
if 'scrape' in sys_options:
    scrape()
if 'parse' in sys_options:
    parse()
else:
    unkn_options = ', '.join(["'" + op + "'" for op in sys_options])
    logging.error(f'Unknown option(s) {unkn_options}')

