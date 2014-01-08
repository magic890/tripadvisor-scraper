# Scrapy settings for dirbot project

SPIDER_MODULES = ['tripadvisorbot.spiders']
NEWSPIDER_MODULE = 'tripadvisorbot.spiders'

ITEM_PIPELINES = ['tripadvisorbot.pipelines.FilterWordsPipeline']
