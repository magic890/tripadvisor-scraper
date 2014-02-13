from scrapy.exceptions import DropItem


class FilterWordsPipeline(object):
	"""A pipeline for filtering out items which contain certain words in their
	description"""

	def process_item(self, item, spider):
		return item;