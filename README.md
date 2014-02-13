TripAdvisor Scraper
===================

Only for educational purposes.
Use at own risk, it might violate TripAdvisor policies.

# Dependencies
Install: 
* [Scrapy](http://doc.scrapy.org/en/0.20/intro/install.html)


# Have fun
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
but pay attention [it doesn’t scale well for large amounts of data since incremental (aka. stream-mode)](https://scrapy.readthedocs.org/en/latest/topics/exporters.html#json-with-large-data)


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/magic890/tripadvisor-scraper/trend.png)](https://bitdeli.com/free "Bitdeli Badge")