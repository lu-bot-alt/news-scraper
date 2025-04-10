import os
import pandas as pd
import time
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams

from wordcloud import WordCloud
import jieba
import jieba.analyse
from collections import Counter

# 设置全局中文字体（必须）
font_path = 'simhei.ttf'  # 确保该字体文件存在
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
else:
    font_prop = fm.FontProperties(family='Microsoft YaHei')  # 使用系统字体

# 配置matplotlib全局参数
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

# 配置日志
logging.basicConfig(
    filename='logs/scrape.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DATA_DIR = "data"
MERGED_DATA_FILE = "merged_news_data.csv"
CUTOFF_DATE = "2025-03-01"  # 设置截止日期（格式：YYYY-MM-DD）

# 数据挖掘
STOPWORDS_PATH = "stopwords.txt"  # 停用词表路径
WORDCLOUD_IMG = "visualizations/wordcloud.png"
TREND_PLOT = "visualizations/trend_plot.png"
def get_driver():
    """初始化Selenium WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )

def parse_relative_time(relative_time_str, now=None):
    """增强版时间解析（支持更多格式）"""
    if now is None:
        now = datetime.now()
    
    try:
        if '分钟前' in relative_time_str:
            minutes = int(relative_time_str.split('分钟前')[0])
            return (now - timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
        elif '小时前' in relative_time_str:
            hours = int(relative_time_str.split('小时前')[0])
            return (now - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 处理 "今天00:02" 或 "4月9日 19:32" 等格式
            match = re.match(r'^(今天|昨天)?(\d+月\d+日)?\s*(\d{1,2}:\d{2})?$', relative_time_str.strip())
            if match:
                today_yesterday = match.group(1)
                date_part_str = match.group(2)
                time_part_str = match.group(3)
                
                # 处理日期部分
                if today_yesterday:
                    if today_yesterday == '今天':
                        date_str = now.strftime("%Y-%m-%d")
                    elif today_yesterday == '昨天':
                        yesterday = now - timedelta(days=1)
                        date_str = yesterday.strftime("%Y-%m-%d")
                elif date_part_str:
                    # 处理 "4月9日" 格式
                    month_str = date_part_str.split('月')[0].zfill(2)
                    day_str = date_part_str.split('月')[1].replace('日', '').zfill(2)
                    date_str = f"{now.year}-{month_str}-{day_str}"
                else:
                    # 假设是标准日期格式（如 "2025-04-09"）
                    date_str = relative_time_str.strip().split(' ')[0]
                
                # 处理时间部分
                if time_part_str:
                    time_str = time_part_str
                else:
                    time_str = "00:00"  # 默认时间
                
                full_time_str = f"{date_str} {time_str}"
                parsed_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
                return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 其他情况，尝试简单分割
                parts = relative_time_str.strip().split(' ')
                date_part = parts[0]
                time_part = parts[1] if len(parts) > 1 else '00:00'
                
                # 处理中文日期格式（如 "4月9日"）
                if '月' in date_part and '日' in date_part:
                    month_str = date_part.split('月')[0].zfill(2)
                    day_str = date_part.split('月')[1].replace('日', '').zfill(2)
                    date_str = f"{now.year}-{month_str}-{day_str}"
                elif '今天' in date_part:
                    date_str = now.strftime("%Y-%m-%d")
                elif '昨天' in date_part:
                    yesterday = now - timedelta(days=1)
                    date_str = yesterday.strftime("%Y-%m-%d")
                else:
                    # 假设是标准日期格式（如 "2025-04-09"）
                    date_str = date_part
                
                full_time_str = f"{date_str} {time_part}"
                parsed_time = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
                return parsed_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.warning(f"时间解析失败: {relative_time_str} -> {str(e)}")
        return ''

def parse_news_list(html):
    """解析新闻列表页（匹配实际结构）"""
    news_list = []
    if not html:
        return news_list
    
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('div.feed-card-content div.feed-card-item')
    if not items:
        logging.error("未找到新闻项，请检查选择器是否正确！")
        return news_list
    
    for item in items:
        try:
            # 提取标题和链接
            headline_tag = item.select_one('h2 a')
            headline = headline_tag.text.strip() if headline_tag else ''
            news_url = headline_tag['href'] if headline_tag else ''
            
            # 提取时间
            time_element = item.select_one('div.feed-card-time')
            relative_time = time_element.text.strip() if time_element else ''
            absolute_time = parse_relative_time(relative_time)
            
            # 提取摘要
            summary_tag = item.select_one('a.feed-card-txt-summary')
            summary = summary_tag.text.strip() if summary_tag else ''
            
            # 提取标签
            tags = item.select('div.feed-card-tags a')
            tags_list = [tag.text for tag in tags] if tags else []
            
            # 过滤非新浪新闻链接
            if "sina.com.cn" in news_url:
                news_list.append({
                    'headline': headline,
                    'url': news_url,
                    'time': absolute_time,
                    'summary': summary,
                    'tags': ','.join(tags_list) if tags_list else ''
                })
        except Exception as e:
            logging.warning(f"解析新闻项失败: {str(e)}")
    
    logging.info(f"成功提取 {len(news_list)} 条新闻数据")
    return news_list

def get_news_list(url, cutoff_date_str):
    """获取新闻列表页数据（添加截止日期限制）"""
    try:
        driver = get_driver()
        driver.get(url)
        # 等待新闻内容加载
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.feed-card-content div.feed-card-item'))
        )
        
        cutoff_date = datetime.strptime(cutoff_date_str, "%Y-%m-%d")
        all_news = []
        page_count = 0
        
        # 清空调试文件
        with open("debug.html", "w", encoding="utf-8") as f:
            pass
        
        while True:
            try:
                current_html = driver.page_source
                # 保存前两页调试文件
                if page_count < 2:
                    with open("debug.html", "a", encoding="utf-8") as f:
                        f.write(current_html)
                    page_count += 1
                
                current_news = parse_news_list(current_html)
                all_news.extend(current_news)
                
                # 检查是否到达截止日期
                if current_news:
                    last_article_time_str = current_news[-1]['time']
                    if not last_article_time_str:
                        last_article_time_str = "1970-01-01 00:00:00"
                    last_article_time = datetime.strptime(last_article_time_str, "%Y-%m-%d %H:%M:%S")
                    
                    if last_article_time < cutoff_date:
                        logging.info(f"已到达截止日期 {cutoff_date_str}，停止翻页")
                        break
                
                # 尝试点击下一页按钮
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'div.feed-card-page .pagebox_next a')
                    )
                )
                next_button.click()
                
                # 等待新页面加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, 'div.feed-card-content div.feed-card-item')
                    )
                )
                
                # 检查是否翻页成功（避免重复内容）
                new_html = driver.page_source
                if new_html == current_html:
                    logging.warning("翻页后内容未更新，结束翻页")
                    break
            except Exception as e:
                logging.warning(f"翻页失败: {str(e)}，结束翻页")
                break
        
        driver.quit()
        return all_news
    
    except Exception as e:
        logging.error(f"获取新闻列表失败: {str(e)}")
        return []

def save_to_csv(data, filename):
    """保存数据到CSV（添加空数据检查）"""
    if not data:
        logging.warning("数据为空，跳过保存")
        return
    df = pd.DataFrame(data)
    df.to_csv(f"{DATA_DIR}/{filename}.csv", index=False, encoding='utf-8-sig')
    logging.info(f"数据已保存到 {DATA_DIR}/{filename}.csv")

def clean_data(df):
    """数据清洗：过滤无效数据并标准化"""
    df = df.copy()  # 解决SettingWithCopyWarning
    # 移除时间无效的条目
    df = df[df['time'].notna()]
    df['time'] = pd.to_datetime(df['time'])
    
    # 移除标题或摘要为空的条目
    df = df[(df['headline'].str.strip() != '') & (df['summary'].str.strip() != '')]
    
    # 处理标签字段（转换为列表）
    df['tags'] = df['tags'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    
    return df

def generate_wordcloud(df):
    """生成热点话题词云图"""
    # 创建目录
    os.makedirs("visualizations", exist_ok=True)

    # 填充缺失值并转换为字符串
    df['headline'] = df['headline'].fillna('').astype(str)
    df['summary'] = df['summary'].fillna('').astype(str)
    # 合并文本内容（标题+摘要）
    text = " ".join(df['headline'] + " " + df['summary'])
    
    # 加载停用词
    with open(STOPWORDS_PATH, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().splitlines())
    # 中文分词（使用jieba）
    words = jieba.cut(text, cut_all=False)
    words_filtered = [word for word in words if len(word) > 1 and word not in stopwords and not word.isdigit()]
    # 过滤单字、停用词和数字
    
    # 统计词频：不使用 Counter 而是 pandas Series 方便绘图
    word_counts = pd.Series(Counter(words_filtered)).sort_values(ascending=False).head(30)
    
    # 生成词云
    wc = WordCloud(
        font_path='SentyEtherealWander.ttf',  # 中文字体路径
        width=800,
        height=400,
        background_color='white'
    ).generate_from_frequencies(word_counts)
    
    # 保存词云图
    wc.to_file(WORDCLOUD_IMG)
    logging.info(f"词云图已保存至 {WORDCLOUD_IMG}")

    # 保存词频数据用于后续绘图
    return word_counts

def generate_word_frequency(word_counts):
    """生成词频统计图（使用 pandas Series 的 plot 方法）"""
    plt.figure(figsize=(12, 6))
    word_counts.plot(kind='bar', color='skyblue', fontsize=10)
    # 设置标题和坐标轴字体
    plt.title('高频词汇词频统计', fontproperties=font_prop)
    plt.xlabel('词汇', fontproperties=font_prop)
    plt.ylabel('出现次数', fontproperties=font_prop)
    
    # 旋转x轴标签并指定字体
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.tight_layout()
    
    # 保存为PNG和PDF（PDF确保字体嵌入）
    plt.savefig("visualizations/word_frequency.png", dpi=300, bbox_inches='tight')
    plt.savefig("visualizations/word_frequency.pdf", dpi=300, bbox_inches='tight')
    plt.close()
    logging.info("词频统计图已保存（PNG和PDF格式）")

def analyze_trend(df):
    """分析热点传播趋势"""
    # 按天统计新闻数量
    df['date'] = df['time'].dt.date
    daily_count = df.groupby('date').size().reset_index(name='count')
    
    # 绘制趋势图
    plt.figure(figsize=(12, 6))
    plt.plot(daily_count['date'], daily_count['count'], marker='o', linestyle='-')
    # 设置标题和坐标轴字体
    plt.title('热点新闻传播趋势（按天）', fontproperties=font_prop)
    plt.xlabel('日期', fontproperties=font_prop)
    plt.ylabel('新闻数量', fontproperties=font_prop)
    plt.grid(True)
    # 旋转x轴标签并指定字体
    plt.xticks(rotation=45, fontproperties=font_prop)
    plt.tight_layout()
    
    # 保存趋势图
    plt.savefig(TREND_PLOT)
    logging.info(f"传播趋势图已保存至 {TREND_PLOT}")

def main():
    # 确保目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    sources = [
        {'name': 'sina', 'url': 'https://news.sina.com.cn/china/'}
    ]
    all_news = []
    for source in sources:
        logging.info(f"开始爬取 {source['name']} 的新闻...")
        news_list = get_news_list(source['url'], CUTOFF_DATE)
        if not news_list:
            continue
        all_news.extend(news_list)
        time.sleep(2)
    
    if not all_news:
        logging.error("未获取到新闻数据，终止程序")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_csv(all_news, f"news_data_{timestamp}")
    
    dfs = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv") and "news_data" in file:
            try:
                df = pd.read_csv(os.path.join(DATA_DIR, file))
                dfs.append(df)
            except Exception as e:
                logging.warning(f"读取文件 {file} 失败: {str(e)}")
    
    if dfs:
        merged_df = pd.concat(dfs, ignore_index=True).drop_duplicates(subset=['url'])
        
        # 数据清洗
        cleaned_df = clean_data(merged_df)
        
        # 生成词云、词频和趋势图
        word_counts = generate_wordcloud(cleaned_df)
        generate_word_frequency(word_counts)
        analyze_trend(cleaned_df)
        
        # 保存清洗后的数据
        cleaned_df.to_csv(os.path.join(DATA_DIR, MERGED_DATA_FILE), index=False)
        logging.info(f"清洗后的合并数据已保存（共 {len(cleaned_df)} 条）")
    else:
        logging.error("无有效数据文件，分析终止")

if __name__ == "__main__":
    main()