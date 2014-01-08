from scrapy.item import Item, Field

# Default item
class Website(Item):

	name = Field()
	description = Field()
	url = Field()


# TripAdvisor items
class TripAdvisorItem(Item):

	url = Field()
	name = Field()
	address = Field()
	avg_stars = Field()
	reviews = Field()

class TripAdvisorAddressItem(Item):

	street = Field()
	postal_code = Field()
	locality = Field()
	country = Field()
	
class TripAdvisorReviewItem(Item):

	date = Field()
	title = Field()
	description = Field()
	stars = Field()
	helpful_votes = Field()

	user = Field()

class TripAdvisorUserItem(Item):

	url = Field()
	name = Field()
	address = Field()