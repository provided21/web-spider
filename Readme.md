# 豆瓣电影Top250爬虫系统 - README

## 项目简介

本项目是一个基于Python的豆瓣电影Top250数据爬取系统，能够自动抓取豆瓣电影Top250榜单中的电影详细信息，包括电影基本信息、演职人员、评分数据和用户评论等，并将结果保存为结构化的JSON文件。

## 注
由于ip是从网上的神龙ip获取的
现已无效
若想简单查看运行效果，可将getip()函数的返回值改为None

## 功能特性

- ✅ 完整抓取豆瓣Top250电影数据
- ✅ 支持电影详情信息获取（导演、演员、评分等）
- ✅ 获取电影热门评论数据
- ✅ 自动处理反爬机制（代理IP、随机UA等）
- ✅ 数据保存为结构化JSON文件

## 环境要求

- Python 3.7+
- 以下Python库：
  - requests >= 2.25.1
  - beautifulsoup4 >= 4.9.3
  - lxml >= 4.6.3
  - pymysql >= 1.0.2
  - urllib3 >= 1.26.5

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备代理IP文件

在项目根目录下创建`ip代理.txt`文件，每行一个代理IP，格式如下：

```
123.123.123.123:8888
111.111.111.111:9999
```


### 3. 配置数据库（可选）

数据库在我的项目应用较少
仅仅用于存储每个电影详情页的url（并且只存储了豆瓣Top250的前25部电影）
  这一部分操作很简单没有展示在代码里
如果需要从数据库获取URL列表，请修改代码中的数据库配置：

```python
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'db': 'douban_movie_top250',
    'charset': 'utf8mb4'
}
```

### 4. 运行爬虫

```bash
python main.py
```

## 文件结构

```
douban-movie-spider/
├── main.py                  # 主程序入口
├── ip代理.txt               # 代理IP列表文件
├── movie_data/              # 电影数据存储目录
├── requirements.txt         # 依赖库列表
└── README.md                # 说明文档
```

## 配置选项

可在代码中修改以下配置：

1. **请求延迟**：调整`time.sleep(random.uniform(1, 5))`中的参数控制请求间隔
2. **代理认证**：修改`getip()`函数中的用户名和密码
3. **数据存储路径**：修改`save_to_json()`函数中的路径

## 注意事项

1. 请合理设置爬取间隔，避免对豆瓣服务器造成过大压力
2. 代理IP需要定期更新以保证可用性
3. 大量频繁请求可能导致IP被封禁，请谨慎使用
4. 常常一次只能爬取一部或两部电影，这时需要及时更新ip

## 常见问题

**Q: 爬取时遇到403错误怎么办？**
A: 请尝试：
- 更换代理IP
- 更新User-Agent列表
- 增加请求间隔时间

**Q: 如何扩大爬取范围？**
A: 修改`get_top10_movie_urls()`函数中的SQL查询语句或URL列表

**Q: 数据保存格式能改吗？**
A: 可以修改`save_to_json()`函数来改变输出格式

## 贡献指南

欢迎提交Issue或Pull Request，请确保：
1. 代码符合PEP8规范
2. 提交前通过基本测试
3. 更新相关文档

## 许可证

MIT License