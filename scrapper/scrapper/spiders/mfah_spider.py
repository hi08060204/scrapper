# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import re
import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.selector import Selector
from tutorial.items import MfahItem

class MfahSpider(CrawlSpider):
    name = "mfah"
    allowed_domains = ["mfah.org"]
    start_urls = [
        "http://www.mfah.org/art/collections/"
    ]

    rules = [
        Rule(LxmlLinkExtractor(allow=("/art/detail/[^/]+/?$")), callback='parseItem'),
        Rule(LxmlLinkExtractor(allow=("/art/100-highlights/[^/]+/?$")), callback='parseItem'),
        Rule(LxmlLinkExtractor(allow=("/art/collections/arts-of-europe/$", )), follow=True),
        Rule(LxmlLinkExtractor(allow=("/art/collections/arts-of-europe/[^/]page=[\d]+[^/]+/?$",)), follow=True),
        Rule(LxmlLinkExtractor(allow=("/art/collections/arts-of-north-america-placeholder/$",)), follow=True),
        Rule(LxmlLinkExtractor(allow=("/art/collections/arts-of-north-america-placeholder/[^/]page=[\d]+[^/]+/?$",)), follow=True),
    ]

    def parseItem(self, response):
        sel = Selector(response)
        item = MfahItem()
        meta = sel.xpath('//div[@class="artMeta"]').extract()
        metaText = sel.xpath('//div[@class="artMeta"]/text()').extract()
        item['photoLink'] = 'http://www.mfah.org' + sel.xpath('//div[@id="photo_item_wrapper"]').css('img').xpath('@src').extract()[0]
        item['workName'] = sel.xpath('//div[@class="artMeta"]/i/text()').extract()[0]
        item['category'] = re.sub("\n[ ]+"," ",sel.xpath('//div[@class="artMeta"]/a/text()').extract()[0])
        artistName = sel.xpath('//span[@class="artistname"]/text()').extract()
        
        # determine if there is known author information
        nationality = ""
        if len(artistName) != 0:
            item['artistName'] = re.sub("\n[ ]+", " ", artistName[0])
            biographic = re.sub("\n[ ]+","", metaText[2])
            if biographic.find(',') != -1:
                item['nationality'] = re.search('([\w|\s|\(|\)]+),',biographic).group(1)
                item['lifeTime'] = re.sub(item['nationality'] +',','',biographic)
            else :
                item['nationality'] = biographic
            nationality = item['nationality']
        

        # process the about part of artwork
        item['about'] = ""
        about = sel.xpath('//div[@id="artAbout"]').extract()        
        for text in about: 
            stripedText = text.replace('<div id="artAbout">\n      <div id="artAboutLabel">ABOUT</div>\n      ','').replace('</div>','')
            stripedText = stripedText.replace('\r\t\n','').replace('<em>','').replace('</em>','').replace('<p>','').replace('</p>','').replace('<br>','')
            item['about'] = item['about'] + stripedText.strip()
            
        # process the date and description part of artwork, apply string processing on whole artMeta part    
        dateFlag = False 
        descText = ""
        for i in range(1, len(metaText)):
            text = metaText[i].strip()

            if len(text) != 0 and text.find(nationality) != 0:
                if text.find("The Museum of Fine Arts, Houston") != -1:
                    break
                if not dateFlag:
                    item['date'] = text
                    dateFlag = True
                else:
                    descText = descText + text

        item['description'] = descText
            
        #intDate = int(re.search('[\d]+',item['date']).group(0))  
        #if intDate >= 1700 or intDate <= 21:        
        yield item
    
