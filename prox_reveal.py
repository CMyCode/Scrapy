# -*- coding: utf-8 -*-

import scrapy
from scrapeit.items import ProxItem
import nltk
from nltk.tokenize import TreebankWordTokenizer
from collections import defaultdict
from nltk.corpus import stopwords
import string
#nltk.download('all')

from datetime import datetime, timedelta

class ProxRevealSpider(scrapy.Spider):
    name = 'prox-reveal'
    #allowed_domains = ['www.proxemate.com/']
    start_urls = ['http://www.proxemate.com']

    def parse(self, response):
        for i in set(response.css('div.navigation a::attr(href)')):
             #print(i)
             yield response.follow(i,self.parse_ptag)

    def GetWordCount2(self,data):
        #print(data)
        tokenizer = TreebankWordTokenizer()
        stop_words = set(stopwords.words('english'))
        words = []
        POSVals = {}
        wordcount = defaultdict(int)
        words = tokenizer.tokenize(data)
        for j in set(words):
            wordcount[j] = wordcount[j] + words.count(j)
        for (k, v) in list(wordcount.items()):
            if (k.lower() in stop_words or k.lower() in list(string.punctuation)):
                del wordcount[k]
            else:
                # print(PosTags(k))
                POSVals[k] = self.PosTags(k)
        # print(POSVals)
        return {'WORDS': [k for k in sorted(wordcount.keys())],
                'COUNTS': [wordcount[k] for k in sorted(wordcount.keys())],
                'POS': [POSVals[k] for k in sorted(wordcount.keys())]}

    def PosTags(self,word):
        # print(word)
        if word not in list(string.punctuation):
            ValNTag = list(nltk.pos_tag([word]))
            # print(ValNTag)

            if any([ValNTag[0][1] == "NN", ValNTag[0][1] == "NNP", ValNTag[0][1] == "NNS", ValNTag[0][1] == "NNPS"]):
                return 'NOUN'
            elif any([ValNTag[0][1] == "WP", ValNTag[0][1] == "WPS", ValNTag[0][1] == "PRP", ValNTag[0][1] == "PRPS"]):
                return 'PRONOUN'
            elif any([ValNTag[0][1] == "VBN", ValNTag[0][1] == "VB", ValNTag[0][1] == "VBD", ValNTag[0][1] == "VBG",
                      ValNTag[0][1] == "VBGN", ValNTag[0][1] == "VBP", ValNTag[0][1] == "VBZ"]):
                return 'VERB'
            elif any([ValNTag[0][1] == "JJ", ValNTag[0][1] == "JJR", ValNTag[0][1] == "JJS"]):
                return 'ADJECTIVE'
            elif any([ValNTag[0][1] == "RB", ValNTag[0][1] == "RBR", ValNTag[0][1] == "RBS", ValNTag[0][1] == "WRB"]):
                return 'ADVERB'
            elif any([ValNTag[0][1] == "IN"]):
                return 'PREP/CONJ'
            elif any([ValNTag[0][1] == "CD"]):
                return 'NUM/CARDINAL'
            else:
                return 'OTHERS'
        else:
            return 'OTHERS'

    def parse_ptag(self,response):
        item= ProxItem()
        item['Link']=response.url
        item['content']=''

        for text in  response.xpath('/html/body/div[4]/p/text()').extract():

            #pass
            item['content']+=text
        #item['Timeend'] = datetime.now().strftime('%Y%m%d_%H%M%S%f')
            #yield{'Author':'balaji'}
        yield (self.GetWordCount2(str(item['content'])))


