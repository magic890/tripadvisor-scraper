import re
import time

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from tripadvisorbot.items import *
from tripadvisorbot.spiders.crawlerhelper import *


class TripAdvisorRestaurantBaseSpider(BaseSpider):
	name = "tripadvisor-restaurant"

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
			tripadvisor_item['url'] = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="quality easyClear"]/a[@class="property_title"]/@href'))
			tripadvisor_item['name'] = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="quality easyClear"]/a[@class="property_title"]/text()'))
			tripadvisor_item['avg_stars'] = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="wrap"]/div[@class="entry wrap"]/div[@class="wrap"]/div[@class="rs rating"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]/@content'))
			
			tripadvisor_items.append(tripadvisor_item)

			# Popolate reviews and address for current item.
			yield Request(url=self.base_uri + tripadvisor_item['url'], meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)
		

	# Popolate reviews and address in item index for a single item.
	def parse_search_page(self, response):
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		print "FUNC 2"

		# The default page contains the reviews but the reviews are shrunk and need to click 'More' to view the complete content.
		# An alternate way is to click one of the reviews in the page to open the expanded reviews display page.
		# We're using this last solution to avoid AJAX here.
		expanded_review_url = clean_parsed_string(get_parsed_string(sel, '//div[contains(@class, "basic_review")]//a/@href'))
		if expanded_review_url:
			yield Request(url=self.base_uri + expanded_review_url, meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)
			

		# If the page is not a basic review page, we can proceed with parsing the expanded reviews.
		else:


			# TripAdvisor address for item.
			snode_address = sel.xpath('//div[@class="wrap infoBox"]')
			tripadvisor_address_item = TripAdvisorAddressItem()

			tripadvisor_address_item['street'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="street-address"]/text()'))

			snode_address_postal_code = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:postal-code"]/text()'))
			# Prevent default null field in JSON.
			if snode_address_postal_code:
				tripadvisor_address_item['postal_code'] = snode_address_postal_code

			snode_address_locality = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:locality"]/text()'))
			# Prevent default null field in JSON.
			if snode_address_locality:
				tripadvisor_address_item['locality'] = snode_address_locality

			tripadvisor_address_item['country'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="country-name"]/text()'))
			
			tripadvisor_item['address'] = tripadvisor_address_item


			# TripAdvisor reviews for item.
			tripadvisor_review_items = []
			snode_reviews = sel.xpath('//div[@id="REVIEWS"]/div[starts-with(@class, "reviewSelector")]/div[contains(@class, "review")]/div[@class="col2of2"]')

			#print "ALL SEARCH RESULT"
			#print snode_reviews.extract()

			for snode_review in snode_reviews:
				tripadvisor_review_item = TripAdvisorReviewItem()

				#print "SINGLE SEARCH RESULT"
				#print snode_review
				
				tripadvisor_review_item['title'] = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="quote"]/text()'))

				# Review item description is a list of strings.
				# Strings in list are generated parsing user intentional newline. DOM: <br>
				tripadvisor_review_item['description'] = get_parsed_string_multiple(snode_review, 'div[@class="entry"]/p/text()')
				tripadvisor_review_item['stars'] = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]/@content'))
				
				snode_review_item_date = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[@class="ratingDate"]/text()'))
				snode_review_item_date = re.sub(r'Reviewed ', '', snode_review_item_date, flags=re.IGNORECASE)
				snode_review_item_date = time.strptime(snode_review_item_date, '%B %d, %Y') if snode_review_item_date else None
				tripadvisor_review_item['date'] = time.strftime('%Y-%m-%d', snode_review_item_date) if snode_review_item_date else None

				#print "RATES SINGLE ITEM"
				#print snode_review.xpath('div[@class="rating reviewItemInline"]/span[starts-with(@class, "rate rate_s")]/img[@class="sprite-ratings"]')
				#print tripadvisor_review_item

				tripadvisor_review_items.append(tripadvisor_review_item)

			tripadvisor_item['reviews'] = tripadvisor_review_items


			# TripAdvisor photos for item.
			tripadvisor_photos_item = []
			
			tripadvisor_photo_item = TripAdvisorPhotoItem()
			print 'PHOTO DOM'
			print sel.xpath('//img[@id="HERO_PHOTO"]').extract()
			#TODO: IMG SRC empty because we've to eval the JS in order to populate the src.
			print 'PHOTO DOM SRC'
			print sel.xpath('//img[@id="HERO_PHOTO"]/@src').extract()
			tripadvisor_photo_item['url'] = clean_parsed_string(get_parsed_string(sel, '//img[@id="HERO_PHOTO"]/@src'))

			tripadvisor_item['photos'] = tripadvisor_photos_item


			yield tripadvisor_item
