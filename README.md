# 新浪新闻热点分析爬虫项目 README

---

## 📌 项目简介
本项目是一个基于Python的新浪新闻数据采集与分析系统，可以提取特定时间点到今日的新浪新闻首页的所有新闻，支持以下核心功能：
- 新闻数据采集（可扩展）
- 词云与词频统计可视化
- 情感趋势分析
- 交互式传播趋势图（Plotly）
- 中文显示完整支持（无乱码）
- 调用HuggingFace大语言模型进行情感分析（尚未完善好）

---

## 🚀 功能亮点

### 🐛 新浪微博网页数据爬取

#### 技术栈
1. **Python**：用于编写爬虫脚本。
2. **requests**：用于发送HTTP请求获取网页内容。
3. **BeautifulSoup（bs4）**：解析HTML文档，提取所需信息。
4. **selenium**（可选）：当需要处理动态加载的内容或登录验证时使用。
5. **time**：控制请求频率，避免触发反爬机制。
6. **pandas**：用于数据清洗和预处理。

#### 方法介绍
##### 1. 确定目标与合法性检查
- 在开始之前，请确保遵守新浪微博的服务条款和robots协议（网页后缀改为robots.txt）。
- 对于公开数据，通常可以直接抓取；但对于用户隐私数据，则需特别注意并遵循相关法律法规。

##### 2. 登录与身份验证
由于新浪微博的部分内容可能需要登录后才能访问，因此你可能需要模拟登录过程。这里有两种主要方式：
- 使用`requests.Session()`结合POST请求模拟登录。
- 使用`selenium`驱动浏览器完成登录流程。

###### 示例：使用`selenium`模拟登录
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def weibo_login(username, password):
    driver = webdriver.Chrome()  # 需要安装对应版本的ChromeDriver
    driver.get('https://weibo.com/login.php')
    
    # 输入用户名和密码，并点击登录按钮
    driver.find_element(By.NAME, 'username').send_keys(username)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.find_element(By.XPATH, '//a[@action-type="btn_submit"]').click()
    
    # 等待页面加载完成
    time.sleep(5)
    
    return driver
```

##### 3. 数据抓取
一旦成功登录或确认不需要登录即可访问所需内容，接下来就是根据页面结构定位并抓取数据。

###### 示例：使用`BeautifulSoup`抓取微博内容
```python
import requests
from bs4 import BeautifulSoup

def scrape_weibo_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 假设每条微博都在<li class="weibo-item">标签内
    posts = []
    for post in soup.find_all('li', {'class': 'weibo-item'}):
        content = post.find('div', {'class': 'content'}).text.strip()
        posts.append(content)
    
    return posts
```

##### 4. 数据存储与分析
- 将抓取的数据保存为CSV文件或其他格式以便后续分析。
- 利用`pandas`进行数据分析，如统计词频、生成词云等。

###### 示例：保存为CSV
```python
import pandas as pd

def save_to_csv(posts, filename='weibo_posts.csv'):
    df = pd.DataFrame(posts, columns=['Content'])
    df.to_csv(filename, index=False, encoding='utf-8-sig')
```

#### 注意事项
- **反爬机制**：为了避免被封IP或账号，建议合理设置请求间隔（如使用`time.sleep(random.uniform(1, 3))`），并且可以考虑使用代理IP。
- **动态内容**：如果目标网站大量采用JavaScript动态加载内容，那么仅靠`requests`+`BeautifulSoup`可能无法满足需求，此时可以转向`selenium`或者尝试分析Ajax请求直接获取数据源。

### 🖥️ 数据可视化

| 数据分析模块         | 技术实现                                                                 |
|------------------|--------------------------------------------------------------------------|
| **词云生成**     | `jieba` 分词 + `WordCloud` 生成可视化词云                                |
| **词频统计**     | `pandas.Series.plot` 绘制高频词条形图                                   |
| **情感分析（尚未实现）**     | `snownlp` 实现情感评分，支持按天聚合趋势分析                             |
| **交互式图表（尚未实现）**   | `Plotly` 生成可缩放、可下载的动态传播趋势图                              |
| **中文支持**     | 显式指定 `simhei.ttf` 字体，强制解决中文乱码问题                         |
| **拓展功能（见LLM_Sent_Analysis库）**     | 调用HuggingFace上的语言模型进行情感分析                        |

---

## 🧰 环境依赖
```bash
# 通过 requirements.txt 安装
pip install -r requirements.txt
conda list --explicit>requirements.txt
# 通过 environment_frozen.yml 安装
conda env create -n ENVNAME --file environment_frozen.yml # 官方
```

> ⚠️ 需额外准备(已有通用版)：
- `simhei.ttf` 中文字体文件（放在项目根目录，目前已有SentyEtherealWander.ttf和simhei.ttf）
- `stopwords.txt` 停用词文件（每行一个词，目前集合了中文停用词、百度停用词、哈工大停用词以及四川大学机器智能实验室停用词以及针对项目新增的一些停用词）

---

## 🛠 使用方法
### 1. 数据采集
```python
# 示例：采集多源新闻（需根据实际需求实现）
dfs = [
    scrape_news(source1),
    scrape_news(source2)
]
```

### 2. 数据清洗
```python
cleaned_df = clean_data(pd.concat(dfs))
```

### 3. 生成分析结果
```python
if __name__ == "__main__":
    # 生成词云 + 词频图
    word_counts = generate_wordcloud(cleaned_df)
    generate_word_frequency(word_counts)
    
    # 生成情感趋势图
    analyze_sentiment(cleaned_df)
    
    # 生成交互式传播趋势图
    analyze_trend(cleaned_df)
```

---

## 📁 目录结构
```
XLWBscraper/
├── data/             # 原始采集数据
├── visualizations/   # 输出图表（词云图 wordcloud.png, 高频词汇词频图 word_frquency.png, 热点新闻传播趋势图 trend_plot.png）
├── stopwords.txt     # 自定义停用词文件
├── simhei.ttf、SentyEtherealWander.ttf、MSYH.TTC  # 中文字体文件
├── logs/             # 输出日志文件
├── debug.html        # html占位符检查文件
├── main.py           # 爬虫主程序入口
└── environment_frozen.yml、requirements.txt  # 依赖包清单

```
---

## ⚠️ 注意事项
### 1. 中文显示问题解决
- 确保 `simhei.ttf` 文件存在且路径正确
- 若仍显示乱码，尝试以下方案：
  ```python
  import matplotlib.pyplot as plt
  plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体
  plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
  ```

### 2. 词频图异常处理
- 错误示例：
  ```python
  Counter(words).plot()  # ❌ Counter 无 plot 方法
  ```
- 正确示例：
  ```python
  pd.Series(Counter(words)).plot(kind='bar')  # ✅ 转换为 Series
  ```
### 3. 时间节点调整
- 修改配置项下`CUTOFF_DATE`的时间，目前默认为2025-03-01
---

## 📈 核心输出示例
| 输出文件                     | 说明                           |
|----------------------------|--------------------------------|
| `data/merged_news_data`         | 去重聚合的新闻合集             |
| `visualizations/wordcloud.png`            | 新闻关键词词云                 |
| `visualizations/word_frequency.png`       | 高频词前30名条形图             |
| `visualizations/trend_plot.png` | 热点新闻传播趋势图 |


---

## 🔧 扩展建议

1. **交互式仪表盘**：
   ```bash
   pip install dash
   ```
   使用 `Dash` 构建集成所有图表的Web界面

2. **自动化优化**：
   ```python
   def update_stopwords(top_words):
       """根据词频自动优化停用词"""
       with open('stopwords.txt', 'a') as f:
           f.write('\n'.join(top_words))
   ```

---

## 📚 参考资料
- [jieba 中文分词文档](https://github.com/fxsjy/jieba)
- [snownlp 情感分析](https://github.com/isnowfy/snownlp)
- [Plotly Python 文档](https://plotly.com/python/)
- [Matplotlib 中文显示指南](https://matplotlib.org/stable/tutorials/text/usetex.html)

---
## 🤖 测试
该项目截至2025年5月23日，测试未出现问题，提取自2025年3月1日至今日的新闻共3473条

---

## 📞 联系方式
如有疑问或需要协作开发，请联系：
- GitHub: https://github.com/lu-bot-alt/news-scraper
- 邮箱: qwe20041102@163.com
