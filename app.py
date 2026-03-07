import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pytz
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
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
is_ko = (st.session_state.lang == "한국어")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .news-card { background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 4px; border-left: 5px solid #dc2626; }
    .source-label { background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-iran { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-us { background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; margin-top: 5px; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    a { color: #003366; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; color: #E6002D; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.9rem; }
    th { background-color: #f2f2f2; font-weight: bold; }
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
# 🚀 2. 진영별 로컬 항만 및 전황 크롤러 (아랍 매체)
# ==========================================
def fetch_arab_news(is_ko):
    translator = GoogleTranslator(source='ar', target='ko' if is_ko else 'en')
    news_data = {"port": [], "war": []}
    
    queries = {
        "port": ("(موانئ السعودية OR ميناء الدمام OR جبل علي OR صلالة OR الفجيرة) (تأخير OR شحن) when:7d", "⚪ 중립/로컬", ""),
        "war_us": ("(صواريخ OR هجوم OR الحوثي OR قصف) (البحر الأحمر OR مضيق هرمز) (العربية OR سكاي نيوز) when:7d", "🔵 친미/친사우디(GCC)", "leaning-us"),
        "war_iran": ("(صواريخ OR هجوم OR الحوثي OR قصف) (البحر الأحمر OR مضيق هرمز) (الميادين OR العالم OR إرنا) when:7d", "🔴 친이란/저항의 축", "leaning-iran")
    }

    for key, (keyword, leaning, l_class) in queries.items():
        cat = "port" if key == "port" else "war"
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ar&gl=AE&ceid=AE:ar"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:3]:
                title = item.find('title').text
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                source = item.find('source').text if item.find('source') is not None else "Arab News"
                
                news_data[cat].append({
                    "title": translator.translate(title), "summary": translator.translate(desc) if desc else "요약 없음",
                    "link": item.find('link').text, "date": item.find('pubDate').text, 
                    "orig_title": title, "source": source, "leaning": leaning, "l_class": l_class
                })
        except: continue
    return news_data

# ==========================================
# 🚀 3. AI 딥 서치 엔진 (쓰레기 뉴스 원천 차단)
# ==========================================
def analyze_live_market(api_key, is_ko, arab_news):
    try:
        genai.configure(api_key=api_key)
        # Search Grounding을 지원하는 최신 모델 자동 탐색
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        feed_text = "[ARAB LOCAL NEWS (Ports & War)]\n"
        for cat in ["port", "war"]:
            for n in arab_news[cat]: feed_text += f"- {n['title']} (Bias: {n['leaning']})\n"
            
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 일반 뉴스가 아닌 'AI 자체 검색' 명령 하달. '심층 분석' 등 헛소리 절대 금지.
        prompt = f"""
        You are LX Pantos's top logistics intelligence AI. 
        You MUST use your internal Google Search capabilities to find the specific B2B operational notices for the carriers and airlines listed below. 
        
        [ABSOLUTE RULES TO PREVENT GARBAGE OUTPUT]
        1. NEVER write generic statements like "심층 분석되고 있음" (In-depth analysis is underway), "대응 중" (responding), or "영향을 미치고 있음" (impacting). I will fire you if you write this.
        2. You MUST ONLY extract physical facts: "Discharging at Salalah", "Suspended until March 14", "$800 surcharge", "Cape detour".
        3. If you cannot find a SPECIFIC operational notice or routing change for a company via your search, you MUST explicitly write: "최근 7일 구체적인 실무 노티스 검색 안됨" (No specific operational notice found).
        
        Read the provided Arab Local News feed for Port and War summaries:
        {feed_text}
        
        Output strictly in {lang} using this exact structure:
        
        ### 🚢 1. 해상 운송 - 주요 10대 선사 최신 실무 라우팅 (AI 딥 서치 기반)
        | 선사 (Carrier) | 구체적 실무 라우팅/노티스 팩트 (Specific Routing/Notices) |
        |---|---|
        | Maersk | (e.g., Jebel Ali discharge / No specific notice) |
        | MSC | ... |
        | CMA CGM | ... |
        | Hapag-Lloyd | ... |
        | HMM | ... |
        | ONE | ... |
        | Evergreen | ... |
        | COSCO | ... |
        | Yang Ming | ... |
        | OOCL | ... |
        
        ### ✈️ 2. 항공 운송 - 주요 7대 항공사 최신 카고 노티스 (AI 딥 서치 기반)
        | 항공사 (Airline) | 구체적 카고 결항/지연 팩트 (Specific Cargo Notices) |
        |---|---|
        | Saudia | ... |
        | Etihad | ... |
        | Emirates | ... |
        | Qatar | ... |
        | Cathay Pacific | ... |
        | Korean Air | ... |
        | China Southern | ... |
        
        ### ⚓ 3. 주변국 로컬 항만 상황 (사우디, UAE, 오만)
        (Summarize port congestion/delays from the Arab news feed. Only facts.)
        
        ### 🔥 4. 중동 전황 (미사일/공격 등 실제 군사 충돌)
        (Summarize military attacks/missiles from the Arab news feed, citing the bias.)
        """
        
        # 💡 [핵심] AI에게 구글 검색 권한(tools)을 부여하여 스스로 웹을 뒤지게 만듦
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt) # SDK 버전 충돌 대비 폴백
            
        return response.text
    except Exception as e:
        return f"⚠️ 에러: {e}"

# ==========================================
# 🚀 4. 이메일 발송 엔진
# ==========================================
def send_ai_report(receiver_email, is_ko, report_content, arab_news):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'] = SENDER_EMAIL, receiver_email
        msg['Subject'] = "[LX Pantos] 종합 중동 물류 인텔리전스 (AI 딥서치 & 아랍 전황)"
        
        html = f"<html><body style='font-family: Arial;'><h2 style='color: #E6002D;'>LX PANTOS | Saudi Live Intel</h2><p>Update: {current_time}</p><hr>"
        html += markdown.markdown(report_content, extensions=['tables'])
        
        html += "<hr><h3>📡 수집된 아랍 로컬 속보 링크 (Source)</h3>"
        cat_names = {"port": "⚓ 항만 (아랍 매체)", "war": "🔥 전황 (아랍 매체)"}
        for cat, name in cat_names.items():
            if arab_news.get(cat):
                html += f"<h4>{name}</h4><ul>"
                for n in arab_news[cat]:
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
if 'arab_news' not in st.session_state: st.session_state.arab_news = None
if 'report' not in st.session_state: st.session_state.report = None

with st.sidebar:
    st.markdown("---")
    email = st.text_input("수신 이메일")
    if st.button("✉️ 종합 리포트 발송"):
        if st.session_state.report and email:
            success, m = send_ai_report(email, is_ko, st.session_state.report, st.session_state.arab_news)
            if success: st.success("발송 완료!")
            else: st.error(m)
        else:
            st.error("먼저 우측에서 분석을 실행하세요.")

st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">중동 물류 5대 지표 (AI 실시간 구글 딥 서치 연동)</p></div>', unsafe_allow_html=True)

st.info("💡 **엔진 업데이트 안내:** 선사/항공사 동향은 더 이상 부정확한 뉴스 RSS를 긁어오지 않습니다. AI가 직접 해운 전문지와 공식 노티스를 검색하여 '양하/결항/서차지' 등 물리적 팩트만 추출합니다.")

if st.button("🚀 AI 딥 서치 및 전황 분석 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 없습니다. Secrets 설정을 확인하세요.")
    else:
        with st.spinner("1/2: 아랍 매체에서 로컬 항만 및 실제 군사적 타격/전황 뉴스를 교차 번역 중입니다..."):
            st.session_state.arab_news = fetch_arab_news(is_ko)
            
        with st.spinner("2/2: AI가 스스로 구글 검색을 돌려 10대 선사/7대 항공사의 '실무 라우팅 팩트'만 캐내고 있습니다..."):
            st.session_state.report = analyze_live_market(API_KEY, is_ko, st.session_state.arab_news)

# 결과 출력
if st.session_state.report: 
    st.markdown(st.session_state.report, unsafe_allow_html=True)

# 하단 원본 뉴스 피드 렌더링
if st.session_state.arab_news:
    st.markdown("---")
    st.markdown(f'<div class="section-title">📡 {"아랍 로컬 원본 속보 (최근 7일)" if is_ko else "Live Arab Source News (Last 7 Days)"}</div>', unsafe_allow_html=True)
    
    cat_displays = [("⚓ 주변국 항만(사우디/UAE/오만) 상황", "port"), ("🔥 진영별 전황 (군사 타격/미사일)", "war")]

    for title, cat in cat_displays:
        st.markdown(f"**{title}**")
        if not st.session_state.arab_news.get(cat): 
            st.caption("최근 7일 이내 관련 아랍 매체 보도 없음.")
        else:
            for n in st.session_state.arab_news[cat]:
                tags = f"<span class='source-label'>📰 {n['source']}</span>"
                if n['l_class']: tags += f"<span class='{n['l_class']}'>{n['leaning']}</span>"
                st.markdown(f"""
                    <div class="news-card">
                        <div>{tags}</div>
                        <span class="time-label">{n['date']}</span>
                        <a href="{n['link']}" target="_blank">{n['title']}</a>
                        <p class="summary-text" style="font-size:0.8rem;">{n['summary']}</p>
                    </div>
                """, unsafe_allow_html=True)
