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
    # 新聞來源清單
    all_sources = {
        "🇯🇵 日本 (NHK World)": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "🇨🇳 中國 (SCMP)": "https://www.scmp.com/rss/2/feed",
        "🇩🇪 德國 (DW News)": "https://rss.dw.com/rdf/rss-en-all",
        "🇹🇼 台灣 (自由時報)": "https://news.ltn.com.tw/rss/all.xml",
        "🇬🇧 英國 (BBC World)": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "🇺🇸 美國 (Reuters)": "https://www.reutersagency.com/feed/?best-topics=political-general&post_type=best"
    }

    translator = Translator()
    
    if not selected_sources:
        st.warning("👈 請在左側選單至少勾選一個新聞來源！")
        return

    progress_bar = st.progress(0)
    
    # 開始抓取各個來源
    # 在你的 loop 裡面修改這一段
for idx, name in enumerate(selected_sources):
    url = all_sources[name]
    st.subheader(f"📍 {name}")
    
    # 💡 修改點：加入 User-Agent 偽裝成瀏覽器
    feed = feedparser.parse(url, agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    if not feed.entries:
        st.warning(f"目前無法從 {name} 取得內容，可能是該網站暫時阻擋連線。")
        continue
        
        for i, entry in enumerate(feed.entries[:num_news], 1):
            with st.container():
                try:
                    raw_title = entry.title
                    raw_summary = clean_text(entry.get('summary', '無提供摘要'))
                    
                    # 判斷是否需要翻譯 (自由時報跳過翻譯)
                    if "自由時報" in name:
                        trans_title = raw_title
                        trans_summary = raw_summary
                        is_translated = False
                    else:
                        # 執行翻譯
                        trans_title = translator.translate(raw_title, src='auto', dest='zh-tw').text
                        trans_summary = translator.translate(raw_summary[:150], src='auto', dest='zh-tw').text
                        is_translated = True
                    
                    # 網頁排版呈現
                    st.markdown(f"#### {i}. {trans_title}")
                    
                    col1, col2 = st.columns(2)
                    if is_translated:
                        with col1:
                            st.caption(f"Original Title: {raw_title}")
                            st.markdown("**[EN Summary]**")
                            st.write(f"{raw_summary[:250]}...")
                        with col2:
                            st.markdown("**[中文摘要翻譯]**")
                            st.write(f"{trans_summary}...")
                    else:
                        with col1:
                            st.markdown("**[新聞內容摘要]**")
                            st.write(f"{raw_summary[:400]}...")
                        with col2:
                            st.empty()
                    
                    st.write(f"🔗 [閱讀原文連結]({entry.link})")
                    st.divider()
                    
                    # 避免翻譯過快
                    if is_translated:
                        time.sleep(1.2)
                except Exception as e:
                    st.error(f"載入失敗：{e}")
        
        # 更新進度條
        progress_bar.progress((idx + 1) / len(selected_sources))

    # --- 關鍵改動：所有新聞列出後的完成提示 ---
    st.success("✅ 已完成本日新聞摘要，請閱讀。")
    st.balloons() # 額外加個小驚喜：噴出慶祝氣球

# --- 側邊欄介面 ---
st.sidebar.title("🛠 控制面板")

source_options = [
    "🇯🇵 日本 (NHK World)", 
    "🇨🇳 中國 (SCMP)", 
    "🇩🇪 德國 (DW News)", 
    "🇹🇼 台灣 (自由時報)", 
    "🇬🇧 英國 (BBC World)", 
    "🇺🇸 美國 (Reuters)"
]

selected_sources = st.sidebar.multiselect(
    "選擇媒體：",
    options=source_options,
    default=["🇺🇸 美國 (Reuters)","🇬🇧 英國 (BBC World)","🇩🇪 德國 (DW News)","🇹🇼 台灣 (自由時報)","🇯🇵 日本 (NHK World)"]
)

num_news = st.sidebar.slider("抓取則數", 1, 5, 3)
run_button = st.sidebar.button("🔍 更新新聞")

# --- 主畫面顯示 ---
st.title("🌍 全球重大新聞監測系統")

if run_button:
    start_scraping(selected_sources, num_news)
else:
    st.info("請在左側選擇來源並點擊「更新新聞」。")
