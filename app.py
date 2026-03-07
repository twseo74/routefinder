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
    .news-card { background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 4px; border-left: 5px solid #ccc; }
    .cat-ocean { border-left-color: #0284c7; }
    .cat-air { border-left-color: #0ea5e9; }
    .cat-port { border-left-color: #f59e0b; }
    .cat-war { border-left-color: #dc2626; }
    .source-label { background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-iran { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-us { background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; margin-top: 5px; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    a { color: #003366; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; color: #E6002D; }
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
# 🚀 2. 글로벌 물류 및 항만 뉴스 크롤러
# ==========================================
def fetch_global_news(is_ko):
    news_data = {"ocean": [], "air": [], "port": []}
    
    if is_ko:
        queries = {
            "ocean": ("(Maersk OR MSC OR CMA CGM OR Hapag-Lloyd OR HMM OR ONE OR Evergreen OR COSCO OR Yang Ming OR OOCL) (운항 OR 우회 OR 결항 OR 지연 OR 노티스) when:7d", "cat-ocean"),
            "air": ("(Saudia OR Etihad OR Emirates OR Qatar OR Cathay OR Korean Air OR China Southern) (카고 OR 화물 OR 결항 OR 지연) when:7d", "cat-air"),
            "port": ("(사우디 OR UAE OR 오만) (항구 OR 항만 OR 담맘 OR 제다 OR 살랄라 OR 제벨알리 OR 푸자이라) (하역 OR 지연 OR 물류) when:7d", "cat-port")
        }
        hl, gl = 'ko', 'KR'
    else:
        queries = {
            "ocean": ("(Maersk OR MSC OR CMA CGM OR Hapag-Lloyd OR HMM OR ONE OR Evergreen OR COSCO OR Yang Ming OR OOCL) (detour OR suspend OR delay OR notice) when:7d", "cat-ocean"),
            "air": ("(Saudia OR Etihad OR Emirates OR Qatar OR Cathay OR Korean Air OR China Southern) (cargo OR freight OR cancel OR delay) when:7d", "cat-air"),
            "port": ("(Saudi OR UAE OR Oman) (port OR Dammam OR Jeddah OR Salalah OR Jebel Ali OR Fujairah) (congestion OR delay OR logistics) when:7d", "cat-port")
        }
        hl, gl = 'en-US', 'US'

    for cat, (keyword, css_class) in queries.items():
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl={hl}&gl={gl}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                source = item.find('source').text if item.find('source') is not None else "Global News"
                
                news_data[cat].append({
                    "title": title, "summary": desc if desc else "요약 없음", "link": item.find('link').text, 
                    "date": item.find('pubDate').text, "orig_title": title, "source": source, 
                    "leaning": "🌐 글로벌 매체", "l_class": "", "css_class": css_class
                })
        except: continue
    return news_data

# ==========================================
# 🚀 3. 아랍 진영별 '진짜 전황(미사일/공격)' 크롤러
# ==========================================
def fetch_arab_war_news(is_ko):
    translator = GoogleTranslator(source='ar', target='ko' if is_ko else 'en')
    news_data = {"war": []}
    
    # 💡 [핵심] 미사일(صواريخ), 공격(هجوم), 후티(الحوثي), 폭격(قصف) 키워드 강제 삽입
    queries = [
        ("(صواريخ OR هجوم OR الحوثي OR قصف) (البحر الأحمر OR مضيق هرمز) (العربية OR سكاي نيوز) when:7d", "🔵 친미/친사우디(GCC)" if is_ko else "🔵 Pro-US/GCC", "leaning-us"),
        ("(صواريخ OR هجوم OR الحوثي OR قصف) (البحر الأحمر OR مضيق هرمز) (الميادين OR العالم OR إرنا) when:7d", "🔴 친이란/저항의 축" if is_ko else "🔴 Pro-Iran/Axis", "leaning-iran")
    ]

    for keyword, leaning, l_class in queries:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ar&gl=AE&ceid=AE:ar"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:4]:
                title = item.find('title').text
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                source = item.find('source').text if item.find('source') is not None else "Arab News"
                
                news_data["war"].append({
                    "title": translator.translate(title),
                    "summary": translator.translate(desc) if desc else "요약 없음",
                    "link": item.find('link').text, "date": item.find('pubDate').text, 
                    "orig_title": title, "source": source, "leaning": leaning, "l_class": l_class, "css_class": "cat-war"
                })
        except: continue
    return news_data

# ==========================================
# 🚀 4. AI 분석 엔진 (10대 선사/항공사 무조건 출력 강제)
# ==========================================
def analyze_live_market(api_key, is_ko, global_news, arab_news):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(next((m for m in models if "flash" in m), models[0]))
        
        feed_text = ""
        for cat, items in global_news.items():
            feed_text += f"[{cat.upper()}]\n"
            for n in items: feed_text += f"- {n['title']}\n"
        feed_text += "[WAR]\n"
        for n in arab_news["war"]: feed_text += f"- {n['title']} (Bias: {n['leaning']})\n"
            
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 10개 선사, 7개 항공사 리스트를 템플릿으로 박아버림
        prompt = f"""
        You are LX Pantos's logistics analyst. 
        Read the following news feeds:
        <NEWS_FEEDS>
        {feed_text}
        </NEWS_FEEDS>
        
        [CRITICAL INSTRUCTIONS]
        1. Ocean Freight: You MUST output a Markdown table with EXACTLY 10 rows for these carriers: Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL.
        2. Air Freight: You MUST output a Markdown table with EXACTLY 7 rows for these airlines: Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern.
        3. If there is NO news for a specific carrier or airline in the feed, you MUST write "최근 7일 관련 뉴스/노티스 없음" (No recent news/notices) in their summary column. DO NOT SKIP ANY COMPANY.
        4. Port News: Summarize events regarding Saudi, UAE, and Oman ports.
        5. War News: Summarize military actions (missiles, strikes, Houthi attacks) based on the Arab news feed.
        
        Output strictly in {lang} using this exact structure:
        
        ### 🚢 1. 해상 운송 - 주요 10대 선사 최신 동향
        | 선사 (Carrier) | 최근 7일 뉴스 및 실무 요약 (Recent News/Notices) |
        |---|---|
        | Maersk | ... |
        | MSC | ... |
        | CMA CGM | ... |
        | Hapag-Lloyd | ... |
        | HMM | ... |
        | ONE | ... |
        | Evergreen | ... |
        | COSCO | ... |
        | Yang Ming | ... |
        | OOCL | ... |
        
        ### ✈️ 2. 항공 운송 - 주요 7대 항공사 최신 동향
        | 항공사 (Airline) | 최근 7일 뉴스 및 실무 요약 (Recent News/Notices) |
        |---|---|
        | Saudia | ... |
        | Etihad | ... |
        | Emirates | ... |
        | Qatar | ... |
        | Cathay Pacific | ... |
        | Korean Air | ... |
        | China Southern | ... |
        
        ### ⚓ 3. 주변국 로컬 항만 상황 (사우디, UAE, 오만)
        (Bullet points summarizing port/logistics news)
        
        ### 🔥 4. 중동 전황 (미사일/공격 등 실제 군사 충돌)
        (Bullet points summarizing actual military actions from Arab media, mentioning the bias/source)
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ 에러: {e}"

# ==========================================
# 🚀 5. 이메일 발송 엔진
# ==========================================
def send_ai_report(receiver_email, is_ko, report_content, combined_news):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'] = SENDER_EMAIL, receiver_email
        msg['Subject'] = "[LX Pantos] 종합 중동 물류 인텔리전스 (5대 지표)"
        
        html = f"<html><body style='font-family: Arial;'><h2 style='color: #E6002D;'>LX PANTOS | Saudi Live Intel</h2><p>Update: {current_time}</p><hr>"
        html += markdown.markdown(report_content, extensions=['tables'])
        
        html += "<hr><h3>📡 수집된 원본 속보 링크 (Source)</h3>"
        cat_names = {"ocean": "🚢 해운", "air": "✈️ 항공", "port": "⚓ 항만", "war": "🔥 전황 (아랍 현지)"}
        for cat, name in cat_names.items():
            if combined_news.get(cat):
                html += f"<h4>{name}</h4><ul>"
                for n in combined_news[cat]:
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
# 🚀 6. 대시보드 UI 및 실행
# ==========================================
if 'global_news' not in st.session_state: st.session_state.global_news = None
if 'arab_news' not in st.session_state: st.session_state.arab_news = None
if 'report' not in st.session_state: st.session_state.report = None

with st.sidebar:
    st.markdown("---")
    email = st.text_input("수신 이메일")
    if st.button("✉️ 종합 리포트 발송"):
        if st.session_state.report and email:
            combined = {**st.session_state.global_news, **st.session_state.arab_news}
            success, m = send_ai_report(email, is_ko, st.session_state.report, combined)
            if success: st.success("발송 완료!")
            else: st.error(m)
        else:
            st.error("먼저 우측에서 분석을 실행하세요.")

st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">중동 물류 5대 지표 대시보드 (전황/항만 포함 최종판)</p></div>', unsafe_allow_html=True)

if st.button("🚀 5대 지표 실시간 분석 및 요약 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 없습니다. Secrets 설정을 확인하세요.")
    else:
        with st.spinner("1/3: 글로벌 매체에서 선사/항공사/주변국 항만(사우디, UAE, 오만) 뉴스를 검색 중입니다..."):
            st.session_state.global_news = fetch_global_news(is_ko)
            
        with st.spinner("2/3: 아랍 매체에서 실제 군사적 타격/전황(미사일, 후티) 뉴스를 교차 번역 중입니다..."):
            st.session_state.arab_news = fetch_arab_war_news(is_ko)
            
        with st.spinner("3/3: 10대 선사 및 7대 항공사 리스트를 생성하고 팩트를 조립 중입니다..."):
            st.session_state.report = analyze_live_market(API_KEY, is_ko, st.session_state.global_news, st.session_state.arab_news)

# 결과 출력
if st.session_state.report: 
    st.markdown(st.session_state.report, unsafe_allow_html=True)

# 하단 원본 뉴스 피드 렌더링
if st.session_state.global_news and st.session_state.arab_news:
    st.markdown("---")
    st.markdown(f'<div class="section-title">📡 {"카테고리별 실시간 원본 속보 (최근 7일)" if is_ko else "Live Source News by Category (Last 7 Days)"}</div>', unsafe_allow_html=True)
    
    combined_news = {**st.session_state.global_news, **st.session_state.arab_news}

    cat_displays = [
        ("🚢 해운 선사 노티스", "ocean"), ("✈️ 항공 화물 결항/지연", "air"), 
        ("⚓ 주변국 항만(사우디/UAE/오만) 상황", "port"), ("🔥 진영별 전황 (군사 타격/미사일)", "war")
    ]

    for title, cat in cat_displays:
        st.markdown(f"**{title}**")
        if not combined_news.get(cat): 
            st.caption("최근 7일 이내 관련 매체 보도 없음.")
        else:
            for n in combined_news[cat]:
                tags = f"<span class='source-label'>📰 {n['source']}</span>"
                if n['l_class']: tags += f"<span class='{n['l_class']}'>{n['leaning']}</span>"
                st.markdown(f"""
                    <div class="news-card {n['css_class']}">
                        <div>{tags}</div>
                        <span class="time-label">{n['date']}</span>
                        <a href="{n['link']}" target="_blank">{n['title']}</a>
                        <p class="summary-text">{n['summary']}</p>
                    </div>
                """, unsafe_allow_html=True)
