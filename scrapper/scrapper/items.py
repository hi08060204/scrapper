import scrapy

class MfahItem(scrapy.Item):
    artistName = scrapy.Field()
    workName = scrapy.Field()
    photoLink = scrapy.Field()
    category = scrapy.Field()
    about = scrapy.Field()
    nationality = scrapy.Field()
    lifeTime = scrapy.Field()
    date = scrapy.Field()
    description = scrapy.Field()
