import streamlit as st
import feedparser
from googletrans import Translator
import time
import re
from datetime import datetime

# 1. 網頁頁面標題與基礎設定
st.set_page_config(page_title="全球新聞自選站", page_icon="🌍", layout="wide")

def clean_text(text):
    """清理摘要中的 HTML 標籤及多餘換行"""
    if not text: return ""
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    return " ".join(text.split())

def start_scraping(selected_sources, num_news):
    # 媒體清單：包含新華社國際與時政版
    all_sources = {
        "🇺🇸 美國 (WSJ)": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (自由時報-國際)": "https://news.ltn.com.tw/rss/world.xml", 
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (新華社-國際)": "http://www.xinhuanet.com/world/news_world.xml",
        "🇨🇳 中國 (新華社-即時時政)": "http://www.xinhuanet.com/politics/news_politics.xml",
    }

    translator = Translator()
    
    if not selected_sources:
        st.warning("👈 請在左側選單至少勾選一個新聞來源！")
        return

    progress_bar = st.progress(0)
    
    # 開始執行抓取
    for idx, name in enumerate(selected_sources):
        url = all_sources[name]
        st.subheader(f"📍 {name}")
        
        # 偽裝瀏覽器請求
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        feed = feedparser.parse(url, agent=user_agent)
        
        if not feed.entries:
            st.warning(f"目前無法從 {name} 取得內容。")
            continue

        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                # 這裡開始是 try 區塊，負責處理翻譯與排版
                try:
                    raw_title = entry.title
                    raw_summary = clean_text(entry.get('summary', '無提供摘要內容'))
                    
                    # 邏輯分流：判斷是否為中文來源 (自由時報、新華社)
                    is_chinese_source = any(kw in name for kw in ["自由時報", "新華社"])
                    
                    if is_chinese_source:
                        # 自由時報完全不動，新華社執行簡體轉繁體
                        trans_title = translator.translate(raw_title, dest='zh-tw').text if "新華社" in name else raw_title
                        trans_summary = translator.translate(raw_summary[:300], dest='zh-tw').text if "新華社" in name else raw_summary
                    else:
                        # 英文媒體執行英文轉繁體中文
                        trans_title = translator.translate(raw_title, src='auto', dest='zh-tw').text
                        trans_summary = translator.translate(raw_summary[:200], src='auto', dest='zh-tw').text
                    
                    # --- 介面呈現 ---
                    # 標題以原文為主
                    st.markdown(f"#### {i}. {raw_title}")
                    
                    # 如果不是台灣媒體，則在下方加註翻譯標題
                    if "自由時報" not in name:
                        st.caption(f"✨ 繁體對照標題：{trans_title}")
                    
                    # 兩欄式摘要對照
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**[原文摘要]**")
                        st.write(f"{raw_summary[:350]}...")
                    
                    with col2:
                        if "自由時報" not in name:
                            st.markdown("**[翻譯對照]**")
                            st.write(f"{trans_summary}...")
                        else:
                            st.empty() # 台灣來源右欄留白
                    
                    st.write(f"🔗 [閱讀原文連結]({entry.link})")
                    st.divider()
                    
                    # 避免 API 請求過快
                    if "自由時報" not in name:
                        time.sleep(1.2)
                        
                except Exception as e:
                    # 捕捉並顯示翻譯或解析過程中的錯誤
                    st.error(f"該則新聞處理失敗，請稍後再試。詳細錯誤：{e}")
        
        # 更新進度條
        progress_bar.progress((idx + 1) / len(selected_sources))

    st.success("✅ 已完成本日新聞摘要，請閱讀。")
    st.balloons()

# --- 主畫面顯示區域 ---
today = datetime.now().strftime('%Y-%m-%d')
st.title(f"🌍 全球重大新聞監測系統 ({today})")

# --- 側邊欄控制面板 ---
st.sidebar.title("🛠 控制面板")

# 媒體選項
source_options = [
    "🇺🇸 美國 (WSJ)","🇬🇧 英國 (BBC World)","🇩🇪 德國 (DW News)", "🇹🇼 台灣 (自由時報-國際)","🇨🇳 中國 (新華社-國際)","🇨🇳 中國 (新華社-即時時政)",
      "🇯🇵 日本 (NHK World)"
]

# 預設勾選清單內所有來源
selected_sources = st.sidebar.multiselect(
    "選擇媒體：", 
    options=source_options, 
    default=source_options
)

num_news = st.sidebar.slider("每個媒體抓取則數", 1, 10, 3)
run_button = st.sidebar.button("🔍 更新新聞")

if run_button:
    start_scraping(selected_sources, num_news)
else:
    st.info("請確認左側來源並點擊「更新新聞」。")
