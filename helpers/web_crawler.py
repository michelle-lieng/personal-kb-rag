import scrapy
import scrapy.crawler as crawler
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue
from twisted.internet import reactor
import logging

class WebsiteSpider(scrapy.Spider):
    name = 'website_spider'
    custom_settings = {
        'FEEDS': {
            'scraped_data.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 4,
            },
        }
    }

    def __init__(self, urls, *args, **kwargs):
        super(WebsiteSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls

    def parse(self, response):
        content = ' '.join([p.get() for p in response.css('p::text')])
        yield {
            'url': response.url,
            'content': content
        }

def run_spider_process(urls, q):
    try:
        settings = {
            'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7'
        }
        runner = crawler.CrawlerRunner(settings)
        deferred = runner.crawl(WebsiteSpider, urls=urls)
        deferred.addBoth(lambda _: reactor.stop())
        reactor.run()
        q.put(None)
    except Exception as e:
        q.put(e)

def run_spider(urls):
    q = Queue()
    p = Process(target=run_spider_process, args=(urls, q))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

# Main script execution

# Configure logging once at the beginning
# configure_logging() -> THIS DIDN'T REMOVE ALL WARNINGS
configure_logging(install_root_handler=False)
logging.basicConfig(
    format='%(levelname)s: %(message)s',
    level=logging.WARNING
)
"""
# Example usage

# First run
urls_list1 = ['https://www.agriculture.gov.au/abares/products/insights/climate-change-impacts-and-adaptation', 'https://www.climatechange.environment.nsw.gov.au/impacts-climate-change/agriculture', 'https://qaafi.uq.edu.au/blog/2021/09/australian-agriculture-and-climate-change-two-way-street', 'https://www.epa.gov/climateimpacts/climate-change-impacts-agriculture-and-food-supply', 'https://www.science.org.au/curious/policy-features/australian-agriculture-and-climate-change-two-way-street', 'https://en.wikipedia.org/wiki/Effects_of_climate_change_on_agriculture', 'https://www.climatechangeauthority.gov.au/sites/default/files/2021-03/2021Factsheet%20-%20Agriculture.pdf', 'https://www.nature.com/articles/s41558-021-01017-6', 'https://www.nature.com/articles/s43016-021-00400-y']
print('first run:')
run_spider(urls_list1)

# You can perform other operations here if needed

# Second run
urls_list2 = ['https://www.agriculture.gov.au/abares/products/insights/climate-change-impacts-and-adaptation', 'https://www.climatechange.environment.nsw.gov.au/impacts-climate-change/agriculture', 'https://qaafi.uq.edu.au/blog/2021/09/australian-agriculture-and-climate-change-two-way-street', 'https://www.epa.gov/climateimpacts/climate-change-impacts-agriculture-and-food-supply', 'https://www.science.org.au/curious/policy-features/australian-agriculture-and-climate-change-two-way-street', 'https://en.wikipedia.org/wiki/Effects_of_climate_change_on_agriculture']
print('\nsecond run:')
run_spider(urls_list2)
"""