# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PundifactItem(scrapy.Item):
	# define the fields for your item here like:
	# name = scrapy.Field()
	station = scrapy.Field()
	subjects = scrapy.Field()
	score = scrapy.Field()
