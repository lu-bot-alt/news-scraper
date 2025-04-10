# 确认网页结构：首先，我们需要确认新闻数据在页面中的位置。可以通过F12观察HTML文档，而本案例中新浪新闻的列表通过JavaScript动态加载。
## 这意味着使用requests和BeautifulSoup直接抓取HTML是无法获取到完整的内容的。
## 既然页面是动态加载的，我们可以考虑使用Selenium来模拟浏览器行为，从而能够获取到完全加载后的HTML内容。

# 选择器修正：待爬取的新闻项可能位于不同的类名下，通过右键检查可以快速锁定这些新闻项。


from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging
import pandas as pd

# 配置日志
logging.basicConfig(
    filename='logs/scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_driver():
    """初始化Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 无头模式运行
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

def get_news_list(url):
    """使用Selenium获取新闻列表页的HTML"""
    driver = get_driver()
    driver.get(url)
    time.sleep(5)  # 等待时间:由于页面加载时间可能变化，请根据实际情况调整time.sleep()的时间参数，以确保页面完全加载后再提取数据。
    html = driver.page_source
    driver.quit()
    return html

def parse_news_list(html):
    """解析新闻列表页的HTML"""
    news_list = []
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='feed-card-item')  # 根据实际HTML调整选择器
    for item in items:
        headline_element = item.find('h2', class_='title')  # 假设标题标签为h2.title
        if headline_element:
            headline = headline_element.text.strip()
            news_url = item.find('a')['href']
            news_list.append({'headline': headline, 'url': news_url})
    logging.info(f"成功提取 {len(news_list)} 条新闻链接")
    return news_list

def main():
    sources = [
        {'name': 'sina', 'url': 'https://news.sina.com.cn/china/'}
    ]
    
    all_news = []
    for source in sources:
        logging.info(f"开始爬取 {source['name']} 的新闻...")
        html = get_news_list(source['url'])
        news_list = parse_news_list(html)
        all_news.extend(news_list)
    
    df = pd.DataFrame(all_news)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"data/news_data_{timestamp}.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logging.info(f"数据已保存到 {output_file}")

if __name__ == "__main__":
    main()