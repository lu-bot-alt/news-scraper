```markdown
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
| 功能模块         | 技术实现                                                                 |
|------------------|--------------------------------------------------------------------------|
| **词云生成**     | `jieba` 分词 + `WordCloud` 生成可视化词云                                |
| **词频统计**     | `pandas.Series.plot` 绘制高频词条形图                                   |
| **情感分析**     | `snownlp` 实现情感评分，支持按天聚合趋势分析                             |
| **交互式图表**   | `Plotly` 生成可缩放、可下载的动态传播趋势图                              |
| **中文支持**     | 显式指定 `simhei.ttf` 字体，强制解决中文乱码问题                         |
| **拓展功能**     | 调用HuggingFace上的语言模型进行情感分析                        |

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
├── visualizations/   # 输出图表（wordcloud.png, sentiment_trend.png, trend_plot.html 等）
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
| `wordcloud.png`            | 新闻关键词词云                 |
| `word_frequency.png`       | 高频词前30名条形图             |
| `sentiment_trend.png`      | 每日平均情感评分（0-1）        |
| `trend_plot_interactive.html` | 可缩放、可下载的动态传播趋势图 |

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

## 📞 联系方式
如有疑问或需要协作开发，请联系：
- GitHub: https://github.com/lu-bot-alt/news-scraper
- 邮箱: qwe20041102@163.com
``` 
