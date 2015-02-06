TripAdvisor Scraper
===================

Only for educational purposes.
Use at own risk, it might violate TripAdvisor policies.

# Dependencies
Install: 
* [Scrapy](http://doc.scrapy.org/en/0.24/intro/install.html)

# Tested configuration
* Python 2.7.6 + Scrapy 0.24.4
* Python 2.7.6 + Scrapy 0.20.2

# Usage - Have fun!
```shell
cd tripadvisor-scraper/
```

Scrape and save data in JSON lines format:
```shell
scrapy crawl tripadvisor-restaurant -o output/result.json
```

For JSON format use:
```shell
scrapy crawl tripadvisor-restaurant -o output/result.json -t json
```
but pay attention [it doesn’t scale well for large amounts of data since incremental (aka. stream-mode)](https://scrapy.readthedocs.org/en/0.24/topics/exporters.html#json-with-large-data)