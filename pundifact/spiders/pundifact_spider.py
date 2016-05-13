import scrapy

from pundifact.items import PundifactItem

class PundifactSpider(scrapy.Spider):
	name = "pundifact"
	allowed_domains = ["politifact.com"]
	start_urls = [
		"http://www.politifact.com/punditfact/tv/abc/",
		"http://www.politifact.com/punditfact/tv/cbs/",
		"http://www.politifact.com/punditfact/tv/nbc/",
		"http://www.politifact.com/punditfact/tv/cnn",
		"http://www.politifact.com/punditfact/tv/fox/",
	]

	def parse(self, response):
		station = response.url.split("/")[-2] 
		
		# iterate through statements
		for statement in response.xpath('//div[@class="statement"]'):
			item = PundifactItem()
			item['station'] = station
			item['score'] = statement.xpath('div[@class="meter"]/a/img/@alt').extract()[0]
			
			href_statement = statement.xpath('div[@class="statement__body"]/p/a/@href').extract()
			url_statement = response.urljoin(href_statement[0])
			
			request = scrapy.Request(url_statement, callback=self.parse_statement)
			request.meta['item'] = item
			
			yield request
		
		href_next = response.xpath('//a[@class="step-links__next"]/@href').extract()
		if href_next:
			url_next = response.urljoin(href_next[0])
			
			yield scrapy.Request(url_next, callback=self.parse)
					
	
	def parse_statement(self, response):
		item = response.meta['item']
		
		subjects = response.xpath('//div[@class="widget__content"]/p')[3]
		item['subjects'] = subjects.xpath('a/text()').extract()
		
		yield item