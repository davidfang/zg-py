#! /usr/bin/env python3
# /Users/david/anaconda3/bin python3
# -*- coding: utf-8 -*-

'''index recommend huasheng'''

import requests
import json
import time
import urllib3
import threading

# 不显示错误
urllib3.disable_warnings()
from create_cache import create_cache


def get_product_detail(goodsId, tag):
    small_images_url = 'https://api.drgou.com/goods/undertakeGoods'
    detail_images_url = 'https://api.drgou.com/goods/goodsUrlList'
    small_images_result = requests.post(small_images_url, data={'goodsId': goodsId}, verify=False)
    detail_images_result = requests.post(detail_images_url, data={'goodsId': goodsId}, verify=False)
    if (small_images_result.status_code == 200 and detail_images_result.status_code == 200):
        small_images = small_images_result.json()
        detail_images = detail_images_result.json()
        if (small_images['status'] == 200 and detail_images['status'] == 200):
            small = small_images['data']['banner']
            guess_like = small_images['data']['guessLike']
            detail = detail_images['data']['imgList']
            create_cache('small_images_' + str(goodsId), small)
            create_cache('guess_like_' + str(goodsId), guess_like)
            create_cache('detail_images_' + str(goodsId), detail)
            print('%s 轮播图：%d 推荐关联： %d  详细图： %d' % (tag, len(small), len(detail), len(guess_like)))
        else:
            if (not (small_images['status'] == 200)):
                print('xxxxxxx轮播图推荐失败xxxxxx')
            if (not (detail_images['status'] == 200)):
                print('xxxxxxx详细说明图失败xxxxxx')


# 抓取首页推荐列表
def get_index_recommend_list():
    indexRecommendUrl = 'https://api.drgou.com/homgPage/guessLikeList'
    pageNo = 1

    while True:
        postData = {u'pageno': pageNo, u'pagesize': 20}
        if (pageNo == 50):
            break
        response = requests.post(indexRecommendUrl, data=postData, verify=False)
        if (response.status_code == 200):
            results = response.json()
            print('---------------%d---------------' % (pageNo))
            i = 0
            threads = []
            if(results['status'] == 200):
                for product in results['data']['guessLike']:
                    i = i + 1
                    print('%d: %s: %d' % (i, product['title'], product['goodsId']))
                    tag = '%d-%d ' % (pageNo, i)
                    # get_product_detail(product['goodsId'])
                    t = threading.Thread(target=get_product_detail, args=(product['goodsId'], tag))
                    threads.append(t)
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()

                # 生成缓存
                create_cache('indexRecommend_' + str(pageNo), results['data']['guessLike'])
            else:
                print('下载失败')
                break
            if (i < 20):  # 没有时候退出
                break

            pageNo = pageNo + 1


if __name__ == '__main__':
    get_index_recommend_list()
