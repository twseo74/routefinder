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
from deep_translator import GoogleTranslator
import re

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

# 2. CSS 설정
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 4px; }
    .source-label { display: inline-block; background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; margin-right: 5px; }
    .leaning-iran { display: inline-block; background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; }
    .leaning-us { display: inline-block; background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; }
    .leaning-neutral { display: inline-block; background-color: #f3f4f6; color: #374151; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 8px; }
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    a { color: #003366; text-decoration: none; font-weight: bold; font-size: 1.1rem; }
    a:hover { text-decoration: underline; color: #E6002D; }
    .summary-text { font-size: 0.9rem; color: #444; margin-top: 8px; line-height: 1.5; }
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

def clean_html(raw_html):
    if not raw_html: return ""
    return re.sub(re.compile('<.*?>'), '', raw_html)

# ==========================================
# 🚀 5. 아랍 매체 균형 크롤러 (친미 vs 친이란 강제 5:5 배분)
# ==========================================
@st.cache_data(ttl=300)
def fetch_balanced_arab_news(is_ko):
    target_lang = 'ko' if is_ko else 'en'
    translator = GoogleTranslator(source='ar', target=target_lang)
    news_list = []

    # 💡 1. 친미/친GCC 매체 (알 아라비야, 스카이뉴스 등)
    q_us = "مضيق هرمز OR البحر الأحمر (العربية OR سكاي نيوز OR الحدث) when:7d"
    # 💡 2. 친이란/저항의 축 매체 (알 마야딘, IRNA, 알 알람 등)
    q_iran = "مضيق هرمز OR البحر الأحمر (الميادين OR العالم OR إرنا OR تسنيم) when:7d"
    # 💡 3. 중립/물류 전문 검색
    q_neutral = "الشحن البحري OR موانئ السعودية when:7d"

    urls = {
        "us": f"https://news.google.com/rss/search?q={urllib.parse.quote(q_us)}&hl=ar&gl=AE&ceid=AE:ar",
        "iran": f"https://news.google.com/rss/search?q={urllib.parse.quote(q_iran)}&hl=ar&gl=AE&ceid=AE:ar",
        "neutral": f"https://news.google.com/rss/search?q={urllib.parse.quote(q_neutral)}&hl=ar&gl=AE&ceid=AE:ar"
    }

    def parse_feed(url, base_leaning, leaning_class):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:4]: # 각 진영별 4개씩 추출
                orig_title = item.find('title').text
                link = item.find('link').text
                pub_date = item.find('pubDate').text
                
                # 언론사 이름 추출
                source_elem = item.find('source')
                source_name = source_elem.text if source_elem is not None else "Unknown"
                
                # 성향 재검증 로직 (크로스 체크)
                actual_leaning = base_leaning
                actual_class = leaning_class
                if any(x in source_name for x in ["الميادين", "إرنا", "العالم", "تسنيم", "المنار"]):
                    actual_leaning = "🔴 친이란/저항의 축" if is_ko else "🔴 Pro-Iran/Axis"
                    actual_class = "leaning-iran"
                elif any(x in source_name for x in ["العربية", "سكاي نيوز", "الحدث", "الشرق"]):
                    actual_leaning = "🔵 친미/친사우디(GCC)" if is_ko else "🔵 Pro-US/GCC"
                    actual_class = "leaning-us"
                elif any(x in source_name for x in ["رويترز", "فرانس برس", "CNN"]):
                    actual_leaning = "⚪ 서방/중립" if is_ko else "⚪ Western/Neutral"
                    actual_class = "leaning-neutral"

                desc_raw = item.find('description').text if item.find('description') is not None else ""
                desc_clean = clean_html(desc_raw)[:200] + "..."
                
                news_list.append({
                    "title": translator.translate(orig_title),
                    "summary": translator.translate(desc_clean) if desc_clean else "요약 없음",
                    "link": link,
                    "date": pub_date,
                    "orig_title": orig_title,
                    "source": source_name,
                    "leaning": actual_leaning,
                    "leaning_class": actual_class
                })
        except: pass

    parse_feed(urls["us"], "🔵 친미/친사우디(GCC)" if is_ko else "🔵 Pro-US/GCC", "leaning-us")
    parse_feed(urls["iran"], "🔴 친이란/저항의 축" if is_ko else "🔴 Pro-Iran/Axis", "leaning-iran")
    parse_feed(urls["neutral"], "⚪ 로컬/중립" if is_ko else "⚪ Local/Neutral", "leaning-neutral")
    
    return news_list

# ==========================================
# 🚀 6. AI 분석 엔진 (오직 팩트만 요약)
# ==========================================
def analyze_live_market(api_key, is_ko, news_data):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models: return "⚠️ API 오류: 모델을 찾을 수 없습니다."
            
        chosen_model = next((m for m in available_models if "flash" in m), available_models[0])
        model = genai.GenerativeModel(chosen_model) 
        
        all_news_text = "\n".join([f"- Title: {n['title']} (Source: {n['source']} / Bias: {n['leaning']})" for n in news_data])
        language = "Korean" if is_ko else "English"
        
        prompt = f"""
        You are a strict data extraction algorithm for LX Pantos.
        Read the following translated ARAB MEDIA news headlines from the past 7 days:
        <ARAB_NEWS>
        {all_news_text}
        </ARAB_NEWS>
        
        [ABSOLUTE RULES]
        1. DO NOT invent ANY status or route. 
        2. IF THERE IS NO MENTION of a specific carrier/airline in the news, you MUST write "아랍 매체 최근 노티스 없음" (No recent notice in Arab media).
        3. Only summarize explicitly mentioned logistics or shipping facts.
        
        Respond strictly in {language}. Output ONLY two Markdown tables with TWO columns each:
        
        ### 🚢 해상 운송 (Ocean Freight) - 주요 10대 선사 아랍 매체 동향
        (Include Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL)
        Columns: 선사 (Carrier) | 3월 1일 이후 아랍 언론 노티스/뉴스 요약 (Arab News Notice since Mar 1)
           
        ### ✈️ 항공 운송 (Air Freight) - 주요 항공사 아랍 매체 동향
        (Include Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern)
        Columns: 항공사 (Airline) | 3월 1일 이후 아랍 언론 노티스/뉴스 요약 (Arab News Notice since Mar 1)
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg: return "⚠️ **무료 API 사용량 초과.** 30초 후 다시 시도하세요."
        return f"⚠️ AI 분석 오류 발생: {error_msg}"

# ==========================================
# 🚀 7. 사이드바 UI 및 이메일 전송 생략 (기존과 동일하게 정상 작동)
# ==========================================

# ==========================================
# 🚀 8. 메인 화면 렌더링
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 동향 (아랍 진영별 팩트 체크)" if is_ko else "KSA Logistics Trends (Arab Media Fact Check)" }</p>
    </div>
    <div class="update-box"><strong>{ '아랍 매체 균형 검색 및 동기화 시점:' if is_ko else 'Balanced Arab Media Synced at:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 1) 진영별 아랍 뉴스 강제 분할 크롤링
news_data = fetch_balanced_arab_news(is_ko)
st.session_state.news_data = news_data

# 실행 버튼
if st.button("🚀 아랍 언론사(양측 진영) 뉴스 기반 팩트 분석 실행", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("⚠️ Streamlit Secrets에서 API Key를 찾을 수 없습니다.")
    else:
        with st.spinner("미국/사우디 진영과 이란 진영의 아랍 현지 기사를 공평하게 분석 중입니다..."):
            ai_result = analyze_live_market(API_KEY, is_ko, news_data)
            st.session_state.ai_report = ai_result 

# 결과 출력 (해상/항공 딱 2칸 표)
if 'ai_report' in st.session_state:
    st.markdown(st.session_state.ai_report, unsafe_allow_html=True)

# 💡 실시간 아랍 뉴스 출력 영역 (언론사 및 성향 라벨 적용)
st.markdown("---")
st.markdown(f'<div class="section-title" style="margin-top:0;">📡 { "아랍 언론사 진영별 실시간 물류 속보" if is_ko else "Live Arab Media Logistics News by Alignment" }</div>', unsafe_allow_html=True)

if news_data:
    for n in news_data:
        st.markdown(f"""
            <div class="news-card">
                <div>
                    <span class="source-label">📰 출처: {n['source']}</span>
                    <span class="{n['leaning_class']}">{n['leaning']}</span>
                </div>
                <span class="time-label">⏱ {n['date']}</span>
                <a href="{n['link']}" target="_blank">{n['title']}</a>
                <p class="summary-text"><strong>요약:</strong> {n['summary']}</p>
                <p style="font-size: 0.75rem; color: #aaa; margin: 0;">(아랍어 원문: {n['orig_title']})</p>
            </div>
        """, unsafe_allow_html=True)
else:
    st.write("아랍 현지 뉴스를 불러오지 못했습니다.")
