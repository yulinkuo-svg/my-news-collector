import streamlit as st
import feedparser
from googletrans import Translator
import time
import re

# 1. 網頁頁面標題設定
st.set_page_config(page_title="全球新聞中英對照站", page_icon="🌍", layout="wide")

def clean_text(text):
    """清理摘要中的 HTML 標籤"""
    if not text: return ""
    clean = re.compile('<.*?>')
    return " ".join(re.sub(clean, '', text).split())

def start_scraping(num_news):
    """抓取新聞的主程式"""
    news_sources = {
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (SCMP)": "https://www.scmp.com/rss/2/feed",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (Focus Taiwan)": "https://focustaiwan.tw/rss/focus-taiwan.xml",
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇺🇸 美國 (Reuters)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best"
    }

    translator = Translator()
    
    # 建立網頁進度條
    progress_bar = st.progress(0)
    total_sources = len(news_sources)

    for idx, (name, url) in enumerate(news_sources.items()):
        st.header(f"{name}")
        feed = feedparser.parse(url)
        
        # 顯示該來源的前幾則新聞
        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                try:
                    # 翻譯標題與摘要
                    trans_title = translator.translate(entry.title, src='auto', dest='zh-tw').text
                    raw_summary = clean_text(entry.get('summary', '無提供摘要'))
                    trans_summary = translator.translate(raw_summary[:200], src='auto', dest='zh-tw').text
                    
                    # 網頁排版：左邊英文、右邊中文
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**EN Title:** {entry.title}")
                        st.caption(f"Summary: {raw_summary[:250]}...")
                    with col2:
                        st.markdown(f"**中文標題：** {trans_title}")
                        st.write(f"摘要翻譯：{trans_summary}...")
                    
                    st.write(f"🔗 [閱讀原文]({entry.link})")
                    st.divider()
                    time.sleep(1) # 避免翻譯過快
                except Exception as e:
                    st.warning(f"這則新聞翻譯稍微卡住了，請稍候。")
        
        # 更新進度條
        progress_bar.progress((idx + 1) / total_sources)

# --- 網頁介面設計 ---
st.title("🌍 全球重大新聞監測系統")
st.markdown("透過 RSS 抓取各國英文媒體，並自動翻譯為繁體中文。")

# 側邊欄控制
st.sidebar.title("設定")
num_news = st.sidebar.slider("每個媒體抓取則數", 1, 5, 3)
if st.sidebar.button("開始抓取最新新聞"):
    start_scraping(num_news)
else:
    st.info("👈 請點擊左側按鈕開始更新新聞。")