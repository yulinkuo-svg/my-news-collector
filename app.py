import streamlit as st
import feedparser
from googletrans import Translator
import time
import re

# 頁面設定
st.set_page_config(page_title="全球新聞自選站", page_icon="🌍", layout="wide")

def clean_text(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return " ".join(re.sub(clean, '', text).split())

def start_scraping(selected_sources, num_news):
    # 定義所有可選的新聞來源
    all_sources = {
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (SCMP)": "https://www.scmp.com/rss/2/feed",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (Focus Taiwan)": "https://focustaiwan.tw/rss/focus-taiwan.xml",
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇺🇸 美國 (Reuters)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best"
    }

    translator = Translator()
    
    if not selected_sources:
        st.warning("👈 請在左側選單至少勾選一個新聞來源！")
        return

    progress_bar = st.progress(0)
    
    for idx, name in enumerate(selected_sources):
        url = all_sources[name]
        st.header(f"📍 {name}")
        
        feed = feedparser.parse(url)
        
        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                try:
                    # 翻譯標題與摘要 (src='auto' 增加相容性)
                    trans_title = translator.translate(entry.title, src='auto', dest='zh-tw').text
                    raw_summary = clean_text(entry.get('summary', '無提供摘要'))
                    trans_summary = translator.translate(raw_summary[:150], src='auto', dest='zh-tw').text
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**[{i}] Original Title**")
                        st.write(entry.title)
                    with col2:
                        st.markdown(f"**[{i}] 中文翻譯**")
                        st.write(trans_title)
                    
                    with st.expander("查看摘要對照"):
                        st.write(f"**EN:** {raw_summary[:200]}...")
                        st.write(f"**中:** {trans_summary}...")
                    
                    st.write(f"🔗 [點擊閱讀原文]({entry.link})")
                    st.divider()
                    time.sleep(1.2)
                except Exception as e:
                    st.error(f"該則新聞載入失敗，可能翻譯伺服器繁忙。")
        
        progress_bar.progress((idx + 1) / len(selected_sources))

# --- 側邊欄介面 ---
st.sidebar.title("🛠 控制面板")

# 定義可選的來源清單
source_options = [
    "🇯🇵 日本 (NHK World)", 
    "🇨🇳 中國 (SCMP)", 
    "🇩🇪 德國 (DW News)", 
    "🇹🇼 台灣 (Focus Taiwan)", 
    "🇬🇧 英國 (BBC World)", 
    "🇺🇸 美國 (Reuters)"
]

# 讓使用者勾選來源
selected_sources = st.sidebar.multiselect(
    "選擇想要追蹤的媒體：",
    options=source_options,
    default=["🇯🇵 日本 (NHK World)", "🇹🇼 台灣 (Focus Taiwan)"] # 預設勾選這兩個
)

num_news = st.sidebar.slider("每個媒體抓取則數", 1, 5, 2)

run_button = st.sidebar.button("🔍 立即更新新聞")

# --- 主畫面顯示 ---
st.title("🌍 全球重大新聞監測系統")

if run_button:
    start_scraping(selected_sources, num_news)
else:
    st.info("請在左側選擇來源並點擊「立即更新新聞」。")
