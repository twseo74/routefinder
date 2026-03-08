import streamlit as st
import google.generativeai as genai
import feedparser
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 및 환경 설정
# ==========================================
st.set_page_config(page_title="Hormuz Crisis Monitor v170", layout="wide")

with st.sidebar:
    st.header("🌐 Language")
    lang = st.radio("언어 선택 (Language)", ["한국어", "English"])
    st.divider()
    st.success("🔄 [System] 100% 무인 스크래핑 모드 가동 중")
    st.info("프로그램이 해운 전문 매체와 글로벌 뉴스망을 스스로 탐색하여 항만 및 전황 데이터를 수집합니다.")

is_ko = (lang == "한국어")
target_language = "한국어" if is_ko else "English"
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

API_KEY = st.secrets.get("GEMINI_API_KEY")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.0rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; }
    td { border: 1px solid #ddd; padding: 10px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 2. 글로벌 전황 및 해운/항만 자동 스크래퍼 (사용자 개입 없음)
# ==========================================
@st.cache_data(ttl=1800) # 30분 주기로 자동 스크래핑 갱신
def auto_scrape_intelligence():
    """뉴스(전황)와 해운 전문지(항만 상황) RSS를 프로그램이 직접 긁어옵니다."""
    
    # 1. 일반 전황 뉴스 타겟
    news_feeds = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "Reuters": "https://www.reutersagency.com/feed/?best-topics=middle-east",
        "BBC": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml"
    }
    
    # 2. 해운/항만 전문 매체 타겟 (항만청 발표 우회 탐지)
    maritime_feeds = {
        "Splash247": "https://splash247.com/feed/",
        "gCaptain": "https://gcaptain.com/feed/"
    }
    
    scraped_data = []
    
    # 뉴스 스크래핑
    scraped_data.append("### [스크래핑: 글로벌 전황 속보] ###")
    for media, url in news_feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]:
                scraped_data.append(f"[{media}] {entry.title} ({entry.link})")
        except:
            continue
            
    # 해운/물류 데이터 스크래핑
    scraped_data.append("\n### [스크래핑: 해운/항만 물류 동향] ###")
    for media, url in maritime_feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:
                scraped_data.append(f"[{media}] {entry.title} - {entry.summary[:150]}...")
        except:
            continue
            
    return "\n".join(scraped_data)

# ==========================================
# 🚀 3. AI 분석 및 리포트 조립 엔진
# ==========================================
def generate_automated_report(api_key, target_lang, raw_scraped_data):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        prompt = f"""
        너는 최상급 물류 관제 AI다. 
        아래 내가 100% 자동으로 긁어온 [실시간 웹 스크래핑 데이터]를 바탕으로 '{target_lang}'로 리포트를 작성해라.

        [실시간 웹 스크래핑 데이터]
        {raw_scraped_data}
        
        [출력 지시사항 - 반드시 마크다운 준수]
        1. 선사 FM 현황 (이전 지시대로 표 형식 유지하되 운임 제외)
        2. 항만별 현황 (Salalah, Sohar, Jebel Ali): 위 스크래핑된 '해운/항만 물류 동향'을 읽고, 이 3개 항구와 관련된 중동 적체/피더 지연 상황을 추출하여 각 항구별로 작성.
        3. 실시간 전황: 스크래핑된 기사 제목을 번역하고 실제 URL 링크를 그대로 출력.
        """

        with st.spinner("수집된 데이터를 바탕으로 리포트를 자동 생성 중입니다..."):
            response = model.generate_content(prompt)
            st.markdown(response.text, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ API 엔진 오류: {e}")

# ==========================================
# 🚀 4. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">Hormuz Crisis Control Report (v170.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 무인 자동화 리포트 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 필요합니다.")
    else:
        # 1. 파이썬이 스스로 웹을 긁어옴 (사용자 업로드 X)
        scraped_intelligence = auto_scrape_intelligence()
        
        # 2. 긁어온 팩트로 리포트 생성
        generate_automated_report(API_KEY, target_language, scraped_intelligence)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str}</div>', unsafe_allow_html=True)
