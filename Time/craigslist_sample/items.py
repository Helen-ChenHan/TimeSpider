from scrapy.item import Item, Field

class TimeItem(Item):
    title = Field()
    link = Field()
    article = Field()
    date = Field()
