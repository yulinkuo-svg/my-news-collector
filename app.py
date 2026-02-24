import streamlit as st
import feedparser
from googletrans import Translator
import time
import re
from datetime import datetime

# 1. 網頁頁面標題與佈局設定
st.set_page_config(
    page_title="全球新聞自選站", 
    page_icon="🌍", 
    layout="wide"
)

# 2. 自訂 iPhone 主畫面圖示
st.markdown(
    """
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/512/21/21601.png">
    """,
    unsafe_allow_html=True
)

def clean_text(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def start_scraping(selected_sources, num_news):
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
                    
                    is_chinese_source = any(kw in name for kw in ["自由時報", "新華社"])
                    
                    if is_chinese_source:
                        trans_title = translator.translate(raw_title, dest='zh-tw').text if "新華社" in name else raw_title
                        trans_summary = translator.translate(raw_summary[:300], dest='zh-tw').text if "新華社" in name else raw_summary
                    else:
                        trans_title = translator.translate(raw_title, src='auto', dest='zh-tw').text
                        trans_summary = translator.translate(raw_summary[:200], src='auto', dest='zh-tw').text
                    
                    st.markdown(f"#### {i}. {raw_title}")
                    if "自由時報" not in name:
                        st.caption(f"✨ 繁體對照標題：{trans_title}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**[原文摘要]**")
                        st.write(f"{raw_summary[:350]}...")
                    with col2:
                        if "自由時報" not in name:
                            st.markdown("**[摘要對照]**")
                            st.write(f"{trans_summary}...")
                        else:
                            st.empty()
                    
                    st.write(f"🔗 [閱讀原文連結]({entry.link})")
                    st.divider()
                    if "自由時報" not in name:
                        time.sleep(1.1)
                except Exception as e:
                    st.error(f"該則新聞處理失敗：{e}")
        
        progress_bar.progress((idx + 1) / len(selected_sources))
    st.success("✅ 已完成本日新聞摘要。")

# --- 主畫面與側邊欄 ---
today = datetime.now().strftime('%Y-%m-%d')
st.title(f"🌍 全球重大新聞監測系統 ({today})")

st.sidebar.title("🛠 控制面板")
source_options = [
    "🇯🇵 日本 (NHK World)", "🇨🇳 中國 (新華社-國際)", "🇨🇳 中國 (新華社-即時時政)",
    "🇩🇪 德國 (DW News)", "🇹🇼 台灣 (自由時報-國際)", "🇬🇧 英國 (BBC World)", "🇺🇸 美國 (WSJ)"
]

selected_sources = st.sidebar.multiselect("選擇媒體：", options=source_options, default=source_options)
num_news = st.sidebar.slider("每個媒體抓取則數", 1, 10, 3)
run_button = st.sidebar.button("🔍 更新新聞")

# --- 關鍵改動：自動執行邏輯 ---
# 檢查 session_state 是否有 'first_run'，如果沒有，代表是第一次開啟
if 'first_run' not in st.session_state:
    st.session_state['first_run'] = True  # 標記為已執行過
    start_scraping(selected_sources, num_news)  # 第一次打開時自動執行
elif run_button:
    # 之後只有按下按鈕才會手動執行
    start_scraping(selected_sources, num_news)
else:
    st.info("新聞已就緒。如需獲取最新消息，請點擊「更新新聞」。")
