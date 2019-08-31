from requests   import get
from lxml.html  import fromstring
from uuid       import uuid4
from tqdm       import tqdm

from json       import dump, load
from os.path    import exists

datadict = dict()
datadict['movie'] = list()

weblink = 'https://yts.lt'

class ScrapePage:

    def __init__(self, year):
        self.year = year

    
    @staticmethod
    def check_empty(x):
        return x[0] if len(x)!=0 else None

    def scrape_get_page(self,link):
        page = get(link)
        if page.status_code==200:
            tree = fromstring(page.content)
            return tree
        # return None

    def parse_movie_page(self, tree):
        if tree is not None:
            movie_data = dict()
            movie_data['id'] = str(uuid4())
            movie_data['movie_name'] = self.check_empty(tree.xpath('//div[@id="movie-info"]/div[@class="hidden-xs"]/h1[1]/text()'))
            movie_data['movie_year'] = self.check_empty(tree.xpath('//div[@id="movie-info"]/div[@class="hidden-xs"]/h2[1]/text()'))
            movie_data['movie_genre'] = self.check_empty(tree.xpath('//div[@id="movie-info"]/div[@class="hidden-xs"]/h2[2]/text()'))
            movie_data['imdb_link'] = self.check_empty(tree.xpath('//div[@class="bottom-info"]/div/a[@title="IMDb Rating"]/@href'))
            movie_data['imdb_rating'] = self.check_empty(tree.xpath('//div[@class="bottom-info"]/div/a[@title="IMDb Rating"]/following-sibling::span/text()'))
            movie_data['down720_link'] = self.check_empty(tree.xpath(
                            '//div[@class="bottom-info"]/p[@class="hidden-md hidden-lg"]/a[contains(.,"720p.BluRay")]/@href'))
            movie_data['down1080_link'] = self.check_empty(tree.xpath(
                            '//div[@class="bottom-info"]/p[@class="hidden-md hidden-lg"]/a[contains(.,"1080p.BluRay")]/@href'))
            movie_data['directors'] = self.check_empty(tree.xpath('//div[@class="directors"]/div/div[2]/a/span/span/text()'))
            movie_data['actors'] = self.check_empty(tree.xpath('//div[@class="actors"]/div/div[2]/a/span/span/text()'))
            movie_data['synopsis'] = self.check_empty(tree.xpath('//div[@id="synopsis"]/p[@class="hidden-xs"]/text()'))
            movie_data['movie_image'] = self.check_empty(tree.xpath('//div[@id="movie-poster"]/img/@src'))
            movie_data['downloads'] = self.check_empty(tree.xpath('//*[@id="synopsis"]/p[4]/em[2]/text()')).split('Downloaded ')[1].split(' times')[0]
            
            return movie_data


    def parse_first_page(self, tree):
        datalist = list()
        if tree is not None:
            movie_element = tree.xpath('*//div[@class="browse-movie-wrap col-xs-10 col-sm-4 col-md-5 col-lg-4"]/div')
            for i in tqdm(movie_element):
                movie_year = self.check_empty(i.xpath('./div/text()'))
                if self.year:
                    if int(movie_year) > self.year:
                        movie_name = self.check_empty(i.xpath('./a[1]/text()'))
                        movie_link = self.check_empty(i.xpath('./a[1]/@href'))
                        movie_data = self.parse_movie_page(self.scrape_get_page(movie_link))
                        if movie_data:
                            datalist.append(movie_data)
            
            if exists('moviedata.json'):
                with open('moviedata.json') as json_file:
                    data = load(json_file)
                    data['movie'] = data['movie'] + datalist
                    with open('moviedata.json', 'w', encoding='utf-8') as f:
                        dump(data, f, ensure_ascii=False, indent=4)
            else:
                datadict['movie'] = datalist
                with open('moviedata.json', 'w', encoding='utf-8') as f:
                    dump(datadict, f, ensure_ascii=False, indent=4)

            next_page = tree.xpath(
                   '//li[@class="pagination-bordered"]/following-sibling::li/a/@href'
                )

            if next_page:
                self.parse_first_page(self.scrape_get_page('{}{}'.format(weblink,next_page[0])))


# with open('moviedata.json') as json_file:
#     cdata = load(json_file)
#     last = cdata['movie'][-1]

s = ScrapePage(2010)
s.parse_first_page(s.scrape_get_page('{}/browse-movies'.format(weblink)))


    
    