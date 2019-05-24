# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from w3lib.html import remove_tags

from ArticalSpider.models.es_model import ArticleType

from elasticsearch_dsl.connections import connections

es = connections.create_connection(hosts=["192.168.62.140"])


class ArticalspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def gen_suggests(index, info_tuple):
    # 搜索建议数组生成
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es _analyze接口进行分析
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter": ["lowercase"]}, body=text)
            analyzed_words = set([item["token"] for item in words["tokens"] if len(item["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()
        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests


class JobboleArticlrItem(scrapy.Item):
    title = scrapy.Field()
    create_time = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field()
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field()
    fav_nums = scrapy.Field()
    comment_nums = scrapy.Field()
    content = scrapy.Field()
    tags = scrapy.Field()

    def save_es(self):
        article_type = ArticleType()
        article_type.title = self['title']
        article_type.create_time = self['create_time']
        # article_type.url = self.['url']
        article_type.url_object_id = self['url_object_id']
        article_type.front_image_url = self['front_image_url']
        # article_type.front_image_path = self['front_image_path']
        article_type.praise_nums = self['praise_nums']
        article_type.fav_nums = self['fav_nums']
        article_type.comment_nums = self['comment_nums']
        article_type.content = remove_tags(self['content'])
        article_type.tags = self['tags']

        article_type.suggest = gen_suggests(ArticleType._doc_type.index,
                                            ((article_type.title, 10), (article_type.tags, 7)))

        article_type.save()
        return
