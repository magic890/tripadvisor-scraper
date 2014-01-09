import re

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from tripadvisorbot.items import *


class TripAdvisorRestaurantBaseSpider(BaseSpider):
	name = "tripadvisor-restaurant-base"

	allowed_domains = ["tripadvisor.com"]
	base_uri = "http://www.tripadvisor.com"
	start_urls = [
		base_uri + "/RestaurantSearch?geo=187849&q=Milan%2C+Italy&cat=&pid="
	]


	# Entry point for BaseSpider.
	def parse(self, response):
		tripadvisor_items = []

		print "FUNC 1"

		sel = Selector(response)
		snode_restaurants = sel.xpath('//div[@id="EATERY_SEARCH_RESULTS"]/div[starts-with(@class, "listing")]')
		
		# Build item index.
		for snode_restaurant in snode_restaurants:
			tripadvisor_item = TripAdvisorItem()
			tripadvisor_item['url'] = snode_restaurant.xpath('div[@class="quality easyClear"]/a[@class="property_title"]/@href').extract()[0].strip()
			tripadvisor_item['name'] = snode_restaurant.xpath('div[@class="quality easyClear"]/a[@class="property_title"]/text()').extract()[0].strip()
			tripadvisor_item['avg_stars'] = snode_restaurant.xpath('div[@class="wrap"]/div[@class="entry wrap"]/div[@class="wrap"]/div[@class="rs rating"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]/@content').extract()
			
			tripadvisor_items.append(tripadvisor_item)

			# Popolate reviews and address for current item.
			yield Request(url=self.base_uri + tripadvisor_item['url'], meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)
		

	# Popolate reviews and address in item index for a single item.
	def parse_search_page(self, response):
		tripadvisor_review_items = []
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		print "FUNC 2"

		# TripAdvisor address for item.
		snode_address = sel.xpath('//div[@class="wrap infoBox"]')
		tripadvisor_address_item = TripAdvisorAddressItem()

		tripadvisor_address_item['street'] = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="street-address"]/text()').extract()[0]
		
		snode_address_postal_code = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:postal-code"]/text()').extract()
		if snode_address_postal_code:
			tripadvisor_address_item['postal_code'] = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:postal-code"]/text()').extract().pop(0).strip()

		snode_address_locality = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:locality"]/text()').extract()
		if snode_address_locality:
			tripadvisor_address_item['locality'] = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:locality"]/text()').extract().pop(0).strip()

		tripadvisor_address_item['country'] = snode_address.xpath('address/span/span[@class="format_address"]/span[@class="country-name"]/text()').extract()[0].strip()
		
		tripadvisor_item['address'] = tripadvisor_address_item
		
		# TripAdvisor reviews for item.
		snode_reviews = sel.xpath('//div[@id="REVIEWS"]/div[@class="reviewSelector "]/div[starts-with(@class, "review")]/div[@class="col2of2"]')

		#print "ALL SEARCH RESULT"
		#print snode_reviews

		for snode_review in snode_reviews:
			tripadvisor_review_item = TripAdvisorReviewItem()

			#print "SINGLE SEARCH RESULT"
			#print snode_review

			tripadvisor_review_item['title'] = snode_review.xpath('div[@class="quote"]/a/span[@class="noQuotes"]/text()').extract()
			tripadvisor_review_item['description'] = snode_review.xpath('div[@class="entry"]/p/text()').extract()
			tripadvisor_review_item['stars'] = snode_review.xpath('div[@class="rating reviewItemInline"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]/@content').extract()
			
			snode_review_item_date = snode_review.xpath('div[@class="rating reviewItemInline"]/span[@class="ratingDate"]/text()').extract()[0].strip()
			tripadvisor_review_item['date'] = re.sub(r'Reviewed ', '', snode_review_item_date, flags=re.IGNORECASE)

			#print "RATES SINGLE ITEM"
			#print snode_review.xpath('div[@class="rating reviewItemInline"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]')
			#print tripadvisor_review_item

			tripadvisor_review_items.append(tripadvisor_review_item)

		tripadvisor_item['reviews'] = tripadvisor_review_items
		return tripadvisor_item
