import re
import time

from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request

from tripadvisorbot.items import *
from tripadvisorbot.spiders.crawlerhelper import *


# Constants.
# Max reviews pages to crawl.
# Reviews collected are around: 5 * MAX_REVIEWS_PAGES
MAX_REVIEWS_PAGES = 500


class TripAdvisorRestaurantBaseSpider(BaseSpider):
	name = "tripadvisor-restaurant"

	allowed_domains = ["tripadvisor.com"]
	base_uri = "http://www.tripadvisor.com"
	start_urls = [
		base_uri + "/RestaurantSearch?geo=60763&q=New+York+City%2C+New+York&cat=&pid="
	]


	# Entry point for BaseSpider.
	# Page type: /RestaurantSearch
	def parse(self, response):
		tripadvisor_items = []

		sel = Selector(response)
		snode_restaurants = sel.xpath('//div[@id="EATERY_SEARCH_RESULTS"]/div[starts-with(@class, "listing")]')
		
		# Build item index.
		for snode_restaurant in snode_restaurants:

			tripadvisor_item = TripAdvisorItem()

			tripadvisor_item['url'] = self.base_uri + clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="quality easyClear"]/span/a[@class="property_title "]/@href'))
			tripadvisor_item['name'] = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="quality easyClear"]/span/a[@class="property_title "]/text()'))
			
			# Cleaning string and taking only the first part before whitespace.
			snode_restaurant_item_avg_stars = clean_parsed_string(get_parsed_string(snode_restaurant, 'div[@class="wrap"]/div[@class="entry wrap"]/div[@class="description"]/div[@class="wrap"]/div[@class="rs rating"]/span[starts-with(@class, "rate")]/img[@class="sprite-ratings"]/@alt'))
			tripadvisor_item['avg_stars'] = re.match(r'(\S+)', snode_restaurant_item_avg_stars).group()

			# Popolate reviews and address for current item.
			yield Request(url=tripadvisor_item['url'], meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_search_page)

			tripadvisor_items.append(tripadvisor_item)
		

	# Popolate reviews and address in item index for a single item.
	# Page type: /Restaurant_Review
	def parse_search_page(self, response):
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)


		# TripAdvisor address for item.
		snode_address = sel.xpath('//div[@class="wrap infoBox"]')
		tripadvisor_address_item = TripAdvisorAddressItem()

		tripadvisor_address_item['street'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="street-address"]/text()'))

		snode_address_postal_code = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:postal-code"]/text()'))
		if snode_address_postal_code:
			tripadvisor_address_item['postal_code'] = snode_address_postal_code

		snode_address_locality = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:locality"]/text()'))
		if snode_address_locality:
			tripadvisor_address_item['locality'] = snode_address_locality

		tripadvisor_address_item['country'] = clean_parsed_string(get_parsed_string(snode_address, 'address/span/span[@class="format_address"]/span[@class="locality"]/span[@property="v:region"]/text()'))
		
		tripadvisor_item['address'] = tripadvisor_address_item


		# TripAdvisor photos for item.
		tripadvisor_item['photos'] = []
		snode_main_photo = sel.xpath('//div[@class="photoGrid photoBx"]')

		snode_main_photo_url = clean_parsed_string(get_parsed_string(snode_main_photo, 'div[starts-with(@class, "photo ")]/a/@href'))
		if snode_main_photo_url:
			yield Request(url=self.base_uri + snode_main_photo_url, meta={'tripadvisor_item': tripadvisor_item}, callback=self.parse_fetch_photo)


		tripadvisor_item['reviews'] = []

		# The default page contains the reviews but the reviews are shrink and need to click 'More' to view the complete content.
		# An alternate way is to click one of the reviews in the page to open the expanded reviews display page.
		# We're using this last solution to avoid AJAX here.
		expanded_review_url = clean_parsed_string(get_parsed_string(sel, '//div[contains(@class, "basic_review")]//a/@href'))
		if expanded_review_url:
			yield Request(url=self.base_uri + expanded_review_url, meta={'tripadvisor_item': tripadvisor_item, 'counter_page_review' : 0}, callback=self.parse_fetch_review)


	# If the page is not a basic review page, we can proceed with parsing the expanded reviews.
	# Page type: /ShowUserReviews
	def parse_fetch_review(self, response):
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		counter_page_review = response.meta['counter_page_review']

		# Limit max reviews pages to crawl.
		if counter_page_review < MAX_REVIEWS_PAGES:
			counter_page_review = counter_page_review + 1

			# TripAdvisor reviews for item.
			snode_reviews = sel.xpath('//div[@id="REVIEWS"]/div/div[contains(@class, "review")]/div[@class="col2of2"]/div[@class="innerBubble"]')

			# Reviews for item.
			for snode_review in snode_reviews:
				tripadvisor_review_item = TripAdvisorReviewItem()
				
				tripadvisor_review_item['title'] = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="quote"]/text()'))

				# Review item description is a list of strings.
				# Strings in list are generated parsing user intentional newline. DOM: <br>
				tripadvisor_review_item['description'] = get_parsed_string_multiple(snode_review, 'div[@class="entry"]/p/text()')
				# Cleaning string and taking only the first part before whitespace.
				snode_review_item_stars = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[starts-with(@class, "rate")]/img/@alt'))
				tripadvisor_review_item['stars'] = re.match(r'(\S+)', snode_review_item_stars).group()
				
				snode_review_item_date = clean_parsed_string(get_parsed_string(snode_review, 'div[@class="rating reviewItemInline"]/span[@class="ratingDate"]/text()'))
				snode_review_item_date = re.sub(r'Reviewed ', '', snode_review_item_date, flags=re.IGNORECASE)
				snode_review_item_date = time.strptime(snode_review_item_date, '%B %d, %Y') if snode_review_item_date else None
				tripadvisor_review_item['date'] = time.strftime('%Y-%m-%d', snode_review_item_date) if snode_review_item_date else None

				tripadvisor_item['reviews'].append(tripadvisor_review_item)


			# Find the next page link if available and go on.
			next_page_url = clean_parsed_string(get_parsed_string(sel, '//a[starts-with(@class, "guiArw sprite-pageNext ")]/@href'))
			if next_page_url and len(next_page_url) > 0:
				yield Request(url=self.base_uri + next_page_url, meta={'tripadvisor_item': tripadvisor_item, 'counter_page_review' : counter_page_review}, callback=self.parse_fetch_review)
			else:
				yield tripadvisor_item

		# Limitatore numero di pagine di review da passare. Totale review circa 5*N.
		else:
			yield tripadvisor_item


	# Popolate photos for a single item.
	# Page type: /LocationPhotoDirectLink
	def parse_fetch_photo(self, response):
		tripadvisor_item = response.meta['tripadvisor_item']
		sel = Selector(response)

		# TripAdvisor photos for item.
		snode_photos = sel.xpath('//img[@class="taLnk big_photo"]')

		# Photos for item.
		for snode_photo in snode_photos:
			tripadvisor_photo_item = TripAdvisorPhotoItem()

			snode_photo_url = clean_parsed_string(get_parsed_string(snode_photo, '@src'))
			if snode_photo_url:
				tripadvisor_photo_item['url'] = snode_photo_url
				tripadvisor_item['photos'].append(tripadvisor_photo_item)
