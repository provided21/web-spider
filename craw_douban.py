import json
import requests
from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
import re
from lxml import etree
import time
import random
from user_agent import generate_user_agent
urllib3.disable_warnings()  # 关闭SSL警告
import string


def get_random_headers():
    return {
        'Host': 'movie.douban.com',
        'User-Agent': generate_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': random.choice(['zh-CN,zh;q=0.9', 'en-US,en;q=0.8']),
        'Referer': random.choice([
            'https://www.douban.com',
            'https://movie.douban.com',
            'https://search.douban.com'
        ]),
        'Cookie': "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11)),
        'Connection': 'keep-alive'
    }
# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 读取代理IP列表
iplist = []
with open("ip代理.txt", 'r', encoding='utf-8') as f:
    iplist = [line.strip() for line in f if line.strip()]  # 自动去除空行和换行符


def getip():
    username = "4b5p0z"  # 替换为你的代理用户名
    password = "x27avt9h"  # 替换为你的代理密码
    proxy = random.choice(iplist)  # 更简洁的随机选择
    proxies = {
        "http": f"http://{username}:{password}@{proxy}",
        "https": f"http://{username}:{password}@{proxy}",
    }
    return None

def parse_iso_duration(duration):
    pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?'
    matches = re.match(pattern, duration)
    hours = int(matches.group(1)) if matches.group(1) else 0
    minutes = int(matches.group(2)) if matches.group(2) else 0

    return f"{hours}小时{minutes}分钟" if hours else f"{minutes}分钟"



def get_movie_data(movie_url):
    """获取并解析单部电影的JSON-LD数据"""
    try:
        response = requests.get(
            movie_url,
            headers=get_random_headers(),  # 动态headers
            proxies=getip(),
            verify=False,
            timeout=10
        )
        tree = etree.HTML(response.text)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', type='application/ld+json')


        if not script:
            print(f"未找到JSON-LD数据: {movie_url}")
            return None

        print('这里正常1')
        data = json.loads(script.string)
        print('这里正常2')
        movie_name = data.get('name')
        print(f'正在爬取{movie_name}...')

        # 处理相对URL
        base_url = 'https://movie.douban.com'

        crawl2 = requests.get(
            movie_url,
            headers=get_random_headers(),  # 新headers
            proxies=getip(),
            verify=False,
            timeout=10
        )
        crawl2.encoding = crawl2.apparent_encoding
        crawl2.raise_for_status()  # 检查请求是否成功
        tree1 = etree.HTML(crawl2.text)
        primary = ['类型:', '制片国家/地区:', '语言:', '上映日期:', '片长:', '又名:', 'IMDb:']
        No = tree1.xpath('//span[@class="top250-no"]/text()')
        Five_stars_rating = tree1.xpath('//span[@class="stars5 starstop"]/following-sibling::span/text()')
        Four_stars_rating = tree1.xpath('//span[@class="stars4 starstop"]/following-sibling::span/text()')
        Three_stars_rating = tree1.xpath('//span[@class="stars3 starstop"]/following-sibling::span/text()')
        Two_stars_rating = tree1.xpath('//span[@class="stars2 starstop"]/following-sibling::span/text()')
        One_stars_rating = tree1.xpath('//span[@class="stars1 starstop"]/following-sibling::span/text()')
        country = tree1.xpath('//span[contains(text(), "制片国家/地区")]/following-sibling::text()[1]')
        language = tree1.xpath('//span[contains(text(), "语言")]/following-sibling::text()[1]')
        alternate_name = tree1.xpath('//span[contains(text(), "又名")]/following-sibling::text()[1]')
        IMDb = tree1.xpath('//span[contains(text(), "IMDb")]/following-sibling::text()[1]')
        description = tree1.xpath('//span[@class="all hidden"]/text()')
        conbined = ''.join(description)
        description = re.sub(r'\s+', '', conbined).strip()
        locate = tree1.xpath('//div[@class="rating_betterthan"]/a/text()')
        locate = [item.strip() for item in locate if item.strip()]
        rating_betterthan = ['好于' + i for i in locate]
        all = tree1.xpath('//div[@id="info"]/span[@class="pl"]/text()')
        extra = []
        for i in all:
            if i not in primary:
                value = tree1.xpath(f'//span[contains(text(), "{i}")]/following-sibling::a/text()[1]')
                extra.append({i: value})
        time.sleep(random.uniform(1, 5))


        movie_info = {
            '电影名称': data.get('name'),
            '豆瓣链接': urljoin(base_url, data.get('url')),
            '海报图片': data.get('image'),
            '导演': [{
                '姓名': director['name'],
                '豆瓣链接': urljoin(base_url, director.get('url', ''))
            } for director in data.get('director', [])],
            '编剧': [{
                '姓名': author['name'],
                '豆瓣链接': urljoin(base_url, author.get('url', ''))
            } for author in data.get('author', [])],
            '主演': [{
                '姓名': actor['name'],
                '豆瓣链接': urljoin(base_url, actor.get('url', ''))
            } for actor in data.get('actor', [])],
            '上映日期': data.get('datePublished') or ''.join(
                tree1.xpath('//span[contains(text(), "上映日期")]/following-sibling::text()[1]')).strip(),
            '电影类型': data.get('genre', []) or [x.strip() for x in tree1.xpath(
                '//span[contains(text(), "类型")]/following-sibling::span[@property="v:genre"]/text()')],
            '片长': parse_iso_duration(data.get('duration', '')) or ''.join(
                tree1.xpath('//span[contains(text(), "片长")]/following-sibling::text()[1]')).strip(),
            '剧情简介': description,
            '评分信息': {
                '评分': data.get('aggregateRating', {}).get('ratingValue'),
                '评分人数': data.get('aggregateRating', {}).get('ratingCount'),
                '最高分': data.get('aggregateRating', {}).get('bestRating'),
                '最低分': data.get('aggregateRating', {}).get('worstRating'),
                '五星评分占比': Five_stars_rating[0] if Five_stars_rating else None,
                '四星评分占比': Four_stars_rating[0] if Four_stars_rating else None,
                '三星评分占比': Three_stars_rating[0] if Three_stars_rating else None,
                '二星评分占比': Two_stars_rating[0] if Two_stars_rating else None,
                '一星评分占比': One_stars_rating[0] if One_stars_rating else None,
                '评分对比': rating_betterthan
            },
            '其他信息': {
                'TOP250排名': No[0] if No else None,
                '制片国家/地区': country[0].strip() if country else None,
                '语言': language[0].strip() if language else None,
                '又名': alternate_name[0].strip() if alternate_name else None,
                'IMDb编号': IMDb[0].strip() if IMDb else None,
                '额外信息': extra
            }
        }
        comment_url = str(tree1.xpath('//*[@id="hot-comments"]/a/@href')[0])
        if movie_url not in comment_url:
            comment_url = movie_url + comment_url
        comments_data = get_comment_data(comment_url)
        movie_info['评论'] = comments_data
        return movie_info

    except Exception as e:
        print(f"获取电影数据失败: {movie_url} - {str(e)}")
        return None

def add_evaluation(evaluation):
    mapping = {
        '力荐': '力荐 五星',
        '推荐': '推荐 四星',
        '还行': '还行 三星',
        '较差': '较差 二星',
        '很差': '很差 一星'
    }
    return mapping.get(evaluation, '未知评级')

def get_comment_data(comment_url1):
    comment_elements = []
    def for_each_page(url):
        comment_page = requests.get(
            url,
            headers=get_random_headers(),  # 动态headers
            proxies=getip(),
            verify=False,
            timeout=10
        )
        comment_page.encoding = comment_page.apparent_encoding
        comment_page.raise_for_status()  # 检查请求是否成功
        tree1 = etree.HTML(comment_page.text)
        comment1 = tree1.xpath('//*[@class="comment-item"]')
        for i in comment1:
            comment_elements.append(i)

        print('正在获取评论页面...')
    comment_url2 = comment_url1.replace("status=P", "start=20&limit=20&status=P&sort=new_score")
    comment_url3 = comment_url1.replace("status=P", "start=40&limit=20&status=P&sort=new_score")
    for_each_page(comment_url1)
    time.sleep(random.uniform(1, 5))
    for_each_page(comment_url2)
    time.sleep(random.uniform(1, 5))
    for_each_page(comment_url3)
    def get_data_from_element(comment_elements):
        comments = []
        print('正在爬取评论详情...')
        for element in comment_elements:
            classification = element.xpath('//h1/text()')[0]
            author = element.xpath('.//div[@class="avatar"]/a/@title')[0]
            vote = element.xpath('.//span[@class="votes vote-count"]/text()')[0]
            content = element.xpath('.//p[@class="comment-content"]/span[@class="short"]/text()')[0]
            evaluation = element.xpath('.//span[contains(text(),"看过")]/following-sibling::span/@title')[0]
            evaluation = add_evaluation(evaluation)
            time = element.xpath('.//span[@class="comment-time"]/text()')[0].strip()
            comments.append({
                '分类': classification,
                '评论者': author,
                '时间': time,
                '评价': evaluation,
                '点赞': vote,
                '内容': content
            })
        return comments

    return get_data_from_element(comment_elements)


import pymysql
from pymysql.cursors import DictCursor


def get_top10_movie_urls():
    # 数据库连接配置 - 请根据你的实际配置修改
    db_config = {
        'host': 'localhost',  # 数据库服务器地址
        'port': 3306,  # 端口，默认3306
        'user': 'root',  # 数据库用户名
        'password': 'hhr2318118',  # 数据库密码
        'db': 'douban_movie_top250',  # 数据库名
        'charset': 'utf8mb4',  # 字符集
        'cursorclass': DictCursor  # 返回字典格式的结果
    }

    try:
        # 建立数据库连接
        connection = pymysql.connect(**db_config)

        with connection.cursor() as cursor:
            # 执行SQL查询，获取前10条URL
            sql = "SELECT url FROM movies_url LIMIT 25"
            cursor.execute(sql)

            # 获取查询结果
            results = cursor.fetchall()

            # 提取URL列表
            urls = [row['url'] for row in results]

            return urls[3:]

    except pymysql.Error as e:
        print(f"数据库操作出错: {e}")
        return None

    finally:
        # 确保连接被关闭
        if connection:
            connection.close()


def save_to_json(name,movie_data):
    print(f'正在保存{name}文件...')
    # with open(f'movie_data/{name}.json', 'w', encoding='utf-8') as f:
    #     json.dump(movie_data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存为 movie_data/{name}.json")

if __name__ == '__main__':
    douban_urls = get_top10_movie_urls()
    for douban_url in douban_urls:
        time.sleep(random.uniform(1, 5))
        movie_data = get_movie_data(douban_url)
        if movie_data is None:
            print(f"获取电影数据失败，跳过: {douban_url}")
            continue  # 跳过当前URL，继续下一个

        name = movie_data['电影名称']
        save_to_json(name, movie_data)
        save_to_json(name,movie_data)


