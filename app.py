import streamlit as st
import feedparser
from googletrans import Translator
import time
import re

# 1. 網頁頁面標題與設定
st.set_page_config(page_title="全球新聞自選站", page_icon="🌍", layout="wide")

def clean_text(text):
    """清理摘要中的 HTML 標籤及多餘換行"""
    if not text: return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def start_scraping(selected_sources, num_news):
    # 更新後的新聞來源清單 (更換了 Reuters 連結並加入自由時報)
    all_sources = {
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (SCMP)": "https://www.scmp.com/rss/2/feed",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (自由時報)": "https://news.ltn.com.tw/rss/all.xml",
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇺🇸 美國 (Reuters)": "https://www.reuters.com/arc/outboundfeeds/rss/?outputType=xml"
    }

    translator = Translator()
    
    if not selected_sources:
        st.warning("👈 請在左側選單至少勾選一個新聞來源！")
        return

    progress_bar = st.progress(0)
    
    # 開始抓取各個來源
    for idx, name in enumerate(selected_sources):
        url = all_sources[name]
        st.subheader(f"📍 {name}")
        
        # 💡 加入 User-Agent 偽裝瀏覽器，解決 Reuters 等網站的阻擋問題
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        feed = feedparser.parse(url, agent=user_agent)
        
        if not feed.entries:
            st.warning(f"目前無法從 {name} 取得內容，建議稍後再試或更換來源。")
            continue

        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                try:
                    raw_title = entry.title
                    raw_summary = clean_text(entry.get('summary', '無提供摘要內容'))
                    
                    # 判
