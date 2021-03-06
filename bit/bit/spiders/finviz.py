from scrapy import Spider
import json
import os
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def getStartUrls():
    urls = []
    i = 1
    while i <= 7061:
        valuationURI = 'http://finviz.com/screener.ashx?v=121&r=%d' % i
        financialURI = 'http://finviz.com/screener.ashx?v=161&r=%d' % i
        urls.append(valuationURI)
        # urls.append(financialURI)
        i += 20

    return urls

def reset_files(paths):
    for path in paths:
        try:
            f = open(path, 'w')
            f.write('')
            f.close()
        except:
            pass

class FinvizSpider(Spider):
    name = 'finviz'
    allowed_domains = ['finviz.com']
    valuationPath = os.path.join(BASE, 'outputs/valuation.txt')
    financialPath = os.path.join(BASE, 'outputs/financial.txt')
    

    usablePath = valuationPath
    reset_files([usablePath])
    start_urls = getStartUrls()

    def parse(self, response):
        indexes = []
        tickers = {}
        # print "<<<>>>", # Separator
        tables = response.css('table[bgcolor="#d3d3d3"]')
        for table in tables:
            table = tables[0]
            trs = table.xpath('tr')
            for row, tr in enumerate(trs):
                tds = tr.xpath('td')
                ticker = None
                for column, td in enumerate(tds):
                    if column is 1:
                        text = td.xpath('a/text()').extract()
                    else:
                        text = td.xpath('text()').extract()

                    if len(text) is 0:
                        #Try to get text with color
                        text = td.xpath('span/text()').extract()

                    if len(text) is 0:
                        text = ['Ticket']

                    text = text[0]

                    #First tr is labels row
                    if row is 0:
                        indexes.append(text)
                        continue

                    if column is 1:
                        #Guardar nuevo ticker
                        ticker = text
                        tickers[ticker] = {}
                    elif column > 1:
                        #Guardar valor en index de ticker
                        index = indexes[column]
                        tickers[ticker][index] = text
        

        f = open(self.usablePath, 'a')
        f.write('<<<>>>')
        f.write(json.dumps(tickers))
        f.close()
