import scrapy
from scrapy.utils.response import open_in_browser
from scrapy.http import FormRequest


class JobsSpider(scrapy.Spider):
    name = "jobs"

    favorite_tags = ['Python', 'Data Science', 'Big Data']  # In this list, specify the tags you want
    persian_to_english = {'۰': 0, '۱':1, '۲':2, '۳':3, '۴':4, '۵':5, '۶':6, '۷':7, '۸':8, '۹':9}
    start_urls = 'https://quera.org/accounts/login'
    base_url = 'https://quera.org/magnet/jobs?page='
    next_page = 2
    email = ''
    password = ''

    def start_requests(self):
        return [scrapy.Request(url=self.start_urls, callback=self.login_page)]

    def login_page(self, response):
        return FormRequest.from_response(response, formdata={
            'login': f'{self.email}',
            'password': f'{self.password}'
        }, callback=self.dashboard)

    def dashboard(self, response):
        magnet_btn_url = response.css('a:nth-child(5)::attr(href)').get()
        jobs_page_url = response.urljoin(magnet_btn_url)
        return scrapy.Request(url=jobs_page_url, callback=self.first_jobs_page)

    def first_jobs_page(self, response):
        persin_last_page_num = response.css('.css-1bm4feb div~ div .css-15wculr::text').get()
        self.last_page_num = ''
        for digit in persin_last_page_num:
            self.last_page_num += str(self.persian_to_english[digit])
        for job_position in response.css('.css-1qgzdoz'):
            tags = job_position.css('.e1pk5grm2 span span::text').getall()
            if any(tag in self.favorite_tags for tag in tags):
                job_position_url = job_position.css('.css-1r4k7cq::attr(href)').get()
                job_url = response.urljoin(job_position_url)
                yield {'url': job_url}
        if self.next_page < int(self.last_page_num)+1:
            next_page_url = self.base_url + str(self.next_page)
            self.next_page += 1
            yield scrapy.Request(url=next_page_url, callback=self.jobs_page_two_and_more)

    def jobs_page_two_and_more(self, response):
        for job_position in response.css('.css-1qgzdoz'):
            tags = job_position.css('.e1pk5grm2 span span::text').getall()
            if any(tag in self.favorite_tags for tag in tags):
                job_position_url = job_position.css('.css-1r4k7cq::attr(href)').get()
                job_url = response.urljoin(job_position_url)
                yield {'url': job_url}
        if self.next_page < int(self.last_page_num)+1:
            next_page_url = self.base_url + str(self.next_page)
            self.next_page += 1
            yield scrapy.Request(url=next_page_url, callback=self.jobs_page_two_and_more)

