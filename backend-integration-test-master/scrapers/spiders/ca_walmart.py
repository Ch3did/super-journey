import scrapy
import json

from scrapers.items import ProductItem


class CaWalmartSpider(scrapy.Spider):
    name = "ca_walmart"
    allowed_domains = ["walmart.ca"]
    start_urls = ["https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852"]
    header = {
		'Host': 'www.walmart.ca',
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate, br',
		'Content-Type': 'application/json',
		'Connection': 'keep-alive'
	}
    

    def parse(self, response):
        #Get the URL of every product
        url_prod = response.xpath(
            ".//a[@class='product-link']/@href").getall()
        for url_prod in url_prod:    
            yield scrapy.Request(
                response.urljoin(url_prod),
                callback=self.parse_product
                )
        #Call the next page URL
        next_page = response.css('#loadmore::attr(href)').get()
        
        #Verify if exist 
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)
            
    def parse_product(self, response):
        script = response.xpath('/html/body/script[1]/text()').get()
        product = script.replace('window.__PRELOADED_STATE__=', '')[:-1]
        json_product = json.dumps(product)
        
        #Call models Product and append info in every Column
        item = ProductItem()
        item['store'] = response.xpath('/html/head/meta[10]/@content').get()
        item['barcodes'] = ' '.join(json_product['entities']['skus'][sku]['upc'])
        item['image_url'] = json_product['entities']['skus'][sku]['images'][0]['large']['url']
        item['sku'] = jason_product['sku']
        item['brand'] = json_product['entities']['skus'][sku]['brand']['name']
        item['name'] = json_product['entities']['skus'][sku]['name']
        item['description'] = json_product['entities']['skus'][sku]['longDescription']
        item['package'] = json_product['product']['item']['description']
        item['url'] = url
        item['category'] = json_product['entities']['skus'][sku]['categories'][0]['displayName']

        #Call 
        product_upc = json_product['entities']['skus'][sku]['upc'][0]
        branch_url = '/api/product-page/find-in-store?latitude=48.4120872&longitude=-89.2413988&lang=en&upc='
        url_api_product = self.walmart_url + branch_url + product_upc
        yield scrapy.Request(url_api_product, callback=self.branch)

    def branch(self, response, item):
        json_branch = json.loads(response.text)
        item['branch'] = json_branch['info'][0]['id']
        item['stock'] = json_branch['info'][0]['availableToSellQty']
        item['price'] = json_branch['info'][0]['sellPrice']

        yield item