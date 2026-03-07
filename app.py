import streamlit as st
from datetime import datetime
import pytz
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

# 2. CSS 설정
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. 시간 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 4. Secrets API 로드
API_KEY, SENDER_EMAIL, SENDER_PW = None, None, None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
    if "email" in st.secrets:
        SENDER_EMAIL = st.secrets["email"].get("sender_email")
        SENDER_PW = st.secrets["email"].get("sender_password")
except: pass

# ==========================================
# 🚀 5. 실시간 뉴스 크롤러 (데이터 소스)
# ==========================================
@st.cache_data(ttl=300)
def fetch_live_news(is_ko, count=10): # 데이터 풀을 넓히기 위해 10개로 증가
    try:
        if is_ko:
            keyword = "호르무즈 해협 물류 OR 사우디 항만 OR 글로벌 해운 항공"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ko&gl=KR&ceid=KR:ko"
        else:
            keyword = "Hormuz shipping OR Saudi ports logistics OR global air freight"
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=en-US&gl=US&ceid=US:en"
            
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        news_list = []
        for item in root.findall('./channel/item')[:count]:
            news_list.append({"title": item.find('title').text, "date": item.find('pubDate').text, "link": item.find('link').text})
        return news_list
    except: return []

# ==========================================
# 🚀 6. AI 분석 엔진 (할루시네이션 원천 차단 알고리즘 탑재)
# ==========================================
def analyze_live_market(api_key, is_ko, news_data):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        chosen_model = available_models[0]
        for m in available_models:
            if "flash" in m: chosen_model = m; break
                
        model = genai.GenerativeModel(chosen_model) 
        news_text = "\n".join([f"- {n['title']} ({n['date']})" for n in news_data])
        language = "Korean" if is_ko else "English"
        
        # 💡 [핵심 알고리즘] 추측을 금지하고 '데이터 없음'을 허용하는 엄격한 규칙
        prompt = f"""
        [SYSTEM RULES - EXTREMELY STRICT ALGORITHM]
        You are a data extraction algorithm for LX Pantos. 
        You MUST ONLY use the provided <NEWS_FEED> below to determine status.
        DO NOT use your pre-trained knowledge to guess. DO NOT output "Normal(정상)" just because there is no bad news.
        
        <NEWS_FEED>
        {news_text}
        </NEWS_FEED>
        
        [EVALUATION ALGORITHM]
        1. Check each specified Carrier and Airline against the <NEWS_FEED>.
        2. If the <NEWS_FEED> explicitly mentions a status (e.g., Detour, Suspended, Delay) for that entity, extract it.
        3. If the <NEWS_FEED> explicitly mentions an alternative port (e.g., Salalah, Khor Fakkan), extract it.
        4. IF AN ENTITY IS NOT MENTIONED IN THE <NEWS_FEED>, YOU MUST SET ITS STATUS TO "🟡 데이터 없음 (No Data in Feed)". DO NOT GUESS "NORMAL".
        
        [OUTPUT FORMAT]
        Output strictly in {language} as two Markdown tables. No introductory or concluding text.
        
        ### 🚢 해상 운송 (Ocean Freight) - 주요 10대 선사
        (Include: Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL)
        Columns: 선사 (Carrier) | 상태 (Status) | 타국가 포트 (Alt Foreign Port) | 최신 뉴스 팩트 (News Fact)
           
        ### ✈️ 항공 운송 (Air Freight) - 리야드(RUH) 취항 현황
        (Include: Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern)
        Columns: 항공사 (Airline) | 상태 (Status) | 뉴스 기반 현황 (News Based Remarks)
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg: return "⚠️ 무료 API 호출량 제한 초과. 30초 후 다시 시도하세요."
        return f"⚠️ 분석 알고리즘 오류: {error_msg}"

# ==========================================
# 🚀 7. 메인 렌더링 및 실행
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 인텔리전스 (Zero-Hallucination Algorithm)" if is_ko else "KSA Logistics Intel (Zero-Hallucination Algorithm)" }</p>
    </div>
    <div class="update-box"><strong>{ '데이터 소싱 시점:' if is_ko else 'Data Sourcing Time:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

news_data = fetch_live_news(is_ko)

if st.button("🚀 AI 팩트 기반 시황 분석 실행", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("⚠️ Streamlit Secrets에 API Key가 없습니다.")
    else:
        with st.spinner("알고리즘이 뉴스 텍스트와 선사/항공사 데이터를 대조 검증 중입니다..."):
            st.session_state.ai_report = analyze_live_market(API_KEY, is_ko, news_data)

if 'ai_report' in st.session_state:
    st.markdown(st.session_state.ai_report, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f'<div class="section-title" style="margin-top:0;">📡 { "알고리즘이 분석한 원본 데이터 (구글 뉴스)" if is_ko else "Source Data Analyzed by Algorithm" }</div>', unsafe_allow_html=True)
if news_data:
    for n in news_data:
        st.markdown(f"""<div class="news-card"><span class="time-label">⏱ {n['date']}</span><a href="{n['link']}" target="_blank">{n['title']}</a></div>""", unsafe_allow_html=True)
else:
    st.write("실시간 뉴스를 불러오지 못했습니다.")
