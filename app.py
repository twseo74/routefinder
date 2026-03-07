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
import markdown

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .news-card { background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 4px; border-left: 5px solid #ccc; }
    .cat-ocean { border-left-color: #0284c7; }
    .cat-air { border-left-color: #0ea5e9; }
    .cat-port { border-left-color: #f59e0b; }
    .cat-hormuz { border-left-color: #ef4444; }
    .cat-war { border-left-color: #8b5cf6; }
    .source-label { background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .leaning-iran { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .leaning-us { background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; margin-top: 5px; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    a { color: #003366; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; color: #E6002D; }
    .summary-text { font-size: 0.9rem; color: #444; margin-top: 8px; line-height: 1.5; }
    </style>
""", unsafe_allow_html=True)

API_KEY, SENDER_EMAIL, SENDER_PW = None, None, None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
    if "email" in st.secrets:
        SENDER_EMAIL = st.secrets["email"].get("sender_email")
        SENDER_PW = st.secrets["email"].get("sender_password")
except: pass

def clean_html(raw_html):
    return re.sub(re.compile('<.*?>'), '', raw_html) if raw_html else ""

# ==========================================
# 🚀 2. 5대 카테고리별 아랍 뉴스 크롤러 (when:7d)
# ==========================================
@st.cache_data(ttl=300)
def fetch_categorized_news(is_ko):
    translator = GoogleTranslator(source='ar', target='ko' if is_ko else 'en')
    news_data = {"ocean": [], "air": [], "port": [], "hormuz": [], "war": []}
    
    # 5가지 명확한 검색 쿼리 (아랍어)
    queries = {
        "ocean": ("(Maersk OR MSC OR CMA CGM OR Hapag-Lloyd OR Evergreen OR HMM) (الشحن OR البحر الأحمر) when:7d", "cat-ocean"),
        "air": ("(Saudia OR Etihad OR Emirates OR Qatar Airways OR Cathay Pacific OR Korean Air OR China Southern) الشحن الجوي when:7d", "cat-air"),
        "port": ("(موانئ السعودية OR ميناء جبل علي OR ميناء صلالة OR ميناء الفجيرة OR الدمام) when:7d", "cat-port"),
        "hormuz": ("مضيق هرمز حركة السفن when:7d", "cat-hormuz"),
        "war": ("البحر الأحمر (العربية OR سكاي نيوز OR الميادين OR العالم) when:7d", "cat-war")
    }

    for cat, (keyword, css_class) in queries.items():
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ar&gl=AE&ceid=AE:ar"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            root = ET.fromstring(urllib.request.urlopen(req).read())
            
            for item in root.findall('./channel/item')[:5]: # 카테고리별 최대 5개 속보
                title = item.find('title').text
                link = item.find('link').text
                source = item.find('source').text if item.find('source') is not None else "Unknown"
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                
                # 진영 판독기 (전황 카테고리용)
                leaning, l_class = "⚪ 로컬/중립", ""
                if any(x in source for x in ["الميادين", "العالم", "إرنا"]): 
                    leaning, l_class = "🔴 친이란/저항의 축", "leaning-iran"
                elif any(x in source for x in ["العربية", "سكاي نيوز", "الحدث"]): 
                    leaning, l_class = "🔵 친미/친사우디(GCC)", "leaning-us"

                news_data[cat].append({
                    "title": translator.translate(title),
                    "summary": translator.translate(desc) if desc else "요약 없음",
                    "link": link, "date": item.find('pubDate').text, "orig_title": title,
                    "source": source, "leaning": leaning, "l_class": l_class, "css_class": css_class
                })
        except: continue
    return news_data

# ==========================================
# 🚀 3. AI 분석 엔진 (5대 카테고리 엄격 분류 요약)
# ==========================================
def analyze_live_market(api_key, is_ko, news_data):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(next((m for m in models if "flash" in m), models[0]))
        
        # AI에게 먹일 텍스트 구조화
        feed_text = ""
        for cat, items in news_data.items():
            feed_text += f"[{cat.upper()}]\n"
            for n in items: feed_text += f"- {n['title']} (Source: {n['source']})\n  Summary: {n['summary']}\n"
            
        lang = "Korean" if is_ko else "English"
        prompt = f"""
        You are LX Pantos's strict logistics data compiler.
        Based ONLY on the following categorized news feeds from the past 7 days, generate a structured report.
        
        <NEWS_FEEDS>
        {feed_text}
        </NEWS_FEEDS>
        
        RULES:
        1. DO NOT invent facts. If a category or specific company has no news, state "3월 1일 이후 관련 아랍 매체 속보 없음" (No recent Arabic news).
        2. Output exactly 5 markdown sections as requested below.
        
        Respond in {lang}. Output format:
        
        ### 🚢 1. 해상 운송 - 10대 선사 3월 중동향 노티스
        (Table: Carrier | Notice/News Summary)
        
        ### ✈️ 2. 항공 운송 - 주요 항공사 3월 카고 노티스
        (Table: Airline | Notice/News Summary)
        
        ### ⚓ 3. 중동 로컬 항만 최신 동향 (사우디, UAE, 오만)
        (Bullet points summarizing port news)
        
        ### 🌊 4. 호르무즈 해협 실시간 통항 상황
        (Bullet points summarizing Hormuz news)
        
        ### 🔥 5. 진영별 전황 속보 요약
        (Bullet points summarizing war news, noting the source bias if mentioned)
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return "⚠️ 무료 API 초과 또는 오류 (30초 후 재시도 바랍니다.)" if "429" in str(e) else f"⚠️ 에러: {e}"

# ==========================================
# 🚀 4. 이메일 발송 엔진 (5대 구조 완벽 이식)
# ==========================================
def send_ai_report(receiver_email, is_ko, report_content, news_data):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'] = SENDER_EMAIL, receiver_email
        msg['Subject'] = "[LX Pantos] 종합 중동 물류 인텔리전스 (5대 지표)"
        
        html = f"<html><body style='font-family: Arial;'><h2 style='color: #E6002D;'>LX PANTOS | Saudi Live Intel</h2><p>Update: {current_time}</p><hr>"
        html += markdown.markdown(report_content, extensions=['tables'])
        
        html += "<hr><h3>📡 5대 지표 아랍 매체 원본 링크</h3>"
        cat_names = {"ocean": "🚢 해운 선사", "air": "✈️ 항공 카고", "port": "⚓ 항만", "hormuz": "🌊 호르무즈", "war": "🔥 전황"}
        for cat, name in cat_names.items():
            if news_data[cat]:
                html += f"<h4>{name}</h4><ul>"
                for n in news_data[cat]:
                    html += f"<li><a href='{n['link']}'>{n['title']}</a> <small>({n['source']})</small></li>"
                html += "</ul>"
                
        html += "</body></html>"
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PW)
        server.send_message(msg)
        server.quit()
        return True, "성공"
    except Exception as e: return False, str(e)

# ==========================================
# 🚀 5. 대시보드 UI 및 실행
# ==========================================
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("언어", ["한국어", "English"])
    st.markdown("---")
    email = st.text_input("수신 이메일")
    if st.button("✉️ 종합 리포트 발송"):
        if 'report' in st.session_state and email:
            success, m = send_ai_report(email, is_ko, st.session_state.report, st.session_state.news)
            if success: st.success("발송 완료!")
            else: st.error(m)

st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">중동 물류 5대 지표 종합 대시보드 (3월 속보 기반)</p></div>', unsafe_allow_html=True)

news_data = fetch_categorized_news(is_ko)
st.session_state.news = news_data

if st.button("🚀 5대 지표 실시간 분석 및 요약 생성", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key가 없습니다.")
    else:
        with st.spinner("해운/항공/항만/호르무즈/전황 데이터를 아랍 매체에서 긁어와 분석 중입니다..."):
            st.session_state.report = analyze_live_market(API_KEY, is_ko, news_data)

if 'report' in st.session_state: st.markdown(st.session_state.report, unsafe_allow_html=True)

# 하단 원본 뉴스 피드 렌더링 (5개 섹션)
st.markdown("---")
st.markdown('<div class="section-title">📡 카테고리별 아랍 실시간 원본 속보 (최근 7일)</div>', unsafe_allow_html=True)

cat_displays = [
    ("🚢 해운 선사 속보", "ocean"), ("✈️ 항공 화물 속보", "air"), 
    ("⚓ 사우디/UAE/오만 항만 속보", "port"), ("🌊 호르무즈 해협 속보", "hormuz"), 
    ("🔥 진영별 전황 속보", "war")
]

for title, cat in cat_displays:
    st.markdown(f"**{title}**")
    if not news_data[cat]: st.caption("최근 7일 이내 관련 아랍 매체 보도 없음.")
    else:
        for n in news_data[cat]:
            tags = f"<span class='source-label'>📰 {n['source']}</span>"
            if n['l_class']: tags += f"<span class='{n['l_class']}'>{n['leaning']}</span>"
            st.markdown(f"""
                <div class="news-card {n['css_class']}">
                    {tags}
                    <span class="time-label">{n['date']}</span>
                    <a href="{n['link']}" target="_blank">{n['title']}</a>
                    <p class="summary-text">{n['summary']}</p>
                </div>
            """, unsafe_allow_html=True)
