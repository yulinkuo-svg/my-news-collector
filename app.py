import streamlit as st
import feedparser
from googletrans import Translator
import time
import re
from datetime import datetime

# 1. 網頁頁面標題與設定
st.set_page_config(page_title="全球新聞自選站", page_icon="🌍", layout="wide")

def clean_text(text):
    """清理摘要中的 HTML 標籤及多餘換行"""
    if not text: return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def start_scraping(selected_sources, num_news):
    # 媒體清單：已將財新網替換為新華社國際版
    all_sources = {
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (新華社-國際)": "http://www.xinhuanet.com/world/news_world.xml",
        "🇨🇳 中國 (新華社-即時時政)": "http://www.xinhuanet.com/politics/news_politics.xml",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (自由時報-國際)": "https://news.ltn.com.tw/rss/world.xml", 
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇺🇸 美國 (WSJ)": "https://feeds.a.dj.com/rss/RSSWorldNews.xml"
    }

    translator = Translator()
    
    if not selected_sources:
        st.warning("👈 請在左側選單至少勾選一個新聞來源！")
        return

    progress_bar = st.progress(0)
    
    for idx, name in enumerate(selected_sources):
        url = all_sources[name]
        st.subheader(f"📍 {name}")
        
        # 偽裝瀏覽器
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        feed = feedparser.parse(url, agent=user_agent)
        
        if not feed.entries:
            st.warning(f"目前無法從 {name} 取得內容。")
            continue

        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                try:
                    raw_title = entry.title
                    raw_summary = clean_text(entry.get('summary', '無提供摘要內容'))
                    
                    # 判斷是否需要翻譯 (只要是新華社或自由時報都跳過英文轉中文，改為簡轉繁或直接顯示)
                    is_chinese_source = any(kw in name for kw in ["自由時報", "新華社"])
                    
                    if is_chinese_source:
                        # 自由時報不動，新華社執行簡轉繁
                        trans_title = translator.translate(raw_title, dest='zh-tw').text if "新華社" in name else raw_title
                        trans_summary = translator.translate(raw_summary[:300], dest='zh-tw').text if "新華社" in name else raw_summary
                    else:
                        # 英文媒體執行英文轉繁中
                        trans_title = translator.translate(raw_title, src='auto', dest='zh-tw').text
                        trans_summary = translator.translate(raw_summary[:200], src='auto', dest='zh-tw').text
