from scrapy.exceptions import DropItem


class FilterWordsPipeline(object):
	"""A pipeline for filtering out items which contain certain words in their
	description"""

	# put all words in lowercase
	words_to_filter = ['sexual']

	def process_item(self, item, spider):
		return item;