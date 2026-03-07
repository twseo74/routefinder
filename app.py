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
    .source-label { background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-iran { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-us { background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; margin-top: 5px; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    a { color: #003366; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; color: #E6002D; }
    .summary-text { font-size: 0.9rem; color: #444; margin-top: 8px; line-height: 1.5; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background-color: #f2f2f2; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# API 키 및 이메일 로드
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
# 🚀 2. 글로벌 물류 뉴스 크롤러 (1~4번용: 영문/국문)
# ==========================================
def fetch_global_logistics_news(is_ko):
    news_data = {"ocean": [], "air": [], "port": [], "hormuz": []}
    
    # 💡 글로벌 선사/항공사 노티스 및 실질적 물류 뉴스 검색 (배경지식 배제어 추가)
    queries = {
        "ocean": ("(Maersk OR MSC OR CMA CGM OR Hapag-Lloyd OR HMM OR ONE OR Evergreen OR COSCO) (운항 OR 우회 OR 공지 OR notice OR advisory OR suspend) when:7d", "cat-ocean"),
        "air": ("(Saudia OR Etihad OR Emirates OR Qatar Airways OR Cathay Pacific OR Korean Air OR China Southern) (카고 OR 결항 OR cargo OR flight OR suspend) when:7d", "cat-air"),
        "port": ("(제다 OR 담맘 OR 제벨알리 OR 푸자이라 OR 살랄라 OR Jeddah OR Dammam OR Jebel Ali OR Fujairah OR Salalah) (물류 OR 지연 OR 하역 OR logistics OR operations OR delay) when:7d", "cat-port"),
        "hormuz": ("호르무즈 해협 (통항 OR 나포 OR 선박 OR Strait of Hormuz OR shipping OR vessel) when:7d", "cat-hormuz")
    }

    hl = 'ko' if is_ko else 'en-US'
    gl = 'KR' if is_ko else 'US'

    for cat, (keyword, css_class) in queries.items():
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl={hl}&gl={gl}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:4]:
                title = item.find('title').text
                source = item.find('source').text if item.find('source') is not None else "Global News"
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                
                news_data[cat].append({
                    "title": title, "summary": desc if desc else "요약 없음",
                    "link": item.find('link').text, "date": item.find('pubDate').text, 
                    "orig_title": title, "source": source, "leaning": "🌐 글로벌 매체", "l_class": "", "css_class": css_class
                })
        except: continue
    return news_data

# ==========================================
# 🚀 3. 아랍 전황 뉴스 크롤러 (5번용: 아랍어)
# ==========================================
def fetch_arab_war_news(is_ko):
    translator = GoogleTranslator(source='ar', target='ko' if is_ko else 'en')
    news_data = {"war": []}
    
    # 💡 진영별 아랍어 뉴스 검색
    queries = [
        ("مضيق هرمز OR البحر الأحمر (العربية OR سكاي نيوز OR الحدث) when:7d", "🔵 친미/친사우디(GCC)", "leaning-us"),
        ("مضيق هرمز OR البحر الأحمر (الميادين OR العالم OR إرنا OR تسنيم) when:7d", "🔴 친이란/저항의 축", "leaning-iran")
    ]

    for keyword, leaning, l_class in queries:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl=ar&gl=AE&ceid=AE:ar"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:3]:
                title = item.find('title').text
                source = item.find('source').text if item.find('source') is not None else "Arab News"
                desc = clean_html(item.find('description').text if item.find('description') is not None else "")[:200]
                
                news_data["war"].append({
                    "title": translator.translate(title),
                    "summary": translator.translate(desc) if desc else "요약 없음",
                    "link": item.find('link').text, "date": item.find('pubDate').text, 
                    "orig_title": title, "source": source, "leaning": leaning, "l_class": l_class, "css_class": "cat-war"
                })
        except: continue
    return news_data

# ==========================================
# 🚀 4. AI 분석 엔진
# ==========================================
def analyze_live_market(api_key, is_ko, global_news, arab_news):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        model = genai.GenerativeModel(next((m for m in models if "flash" in m), models[0]))
        
        feed_text = ""
        # 1~4번 글로벌 뉴스 주입
        for cat, items in global_news.items():
            feed_text += f"[{cat.upper()}]\n"
            for n in items: feed_text += f"- {n['title']} (Source: {n['source']})\n  Summary: {n['summary']}\n"
        # 5번 아랍 전황 뉴스 주입
        feed_text += "[WAR]\n"
        for n in arab_news["war"]: feed_text += f"- {n['title']} (Source: {n['source']} / Bias: {n['leaning']})\n"
            
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 쓰레기 문장 필터링 및 팩트 기반 요약 강제 지침
        prompt = f"""
        You are LX Pantos's strict logistics data compiler.
        Based ONLY on the following news feeds from the past 7 days, generate a structured report.
        
        <NEWS_FEEDS>
        {feed_text}
        </NEWS_FEEDS>
        
        CRITICAL RULES FOR FILTERING GARBAGE INFO:
        1. DO NOT include generic background information (e.g., "Fujairah is an artery for global oil", "The Red Sea is an important trade route"). Ignore these completely.
        2. ONLY extract actual recent events, delays, notices, suspensions, or attacks.
        3. If there is no specific actionable news or notice for a company/port, MUST write "3월 1일 이후 관련 최신 노티스/특이사항 없음" (No actionable recent notice).
        
        Respond in {lang}. Output format:
        
        ### 🚢 1. 해상 운송 - 10대 선사 3월 중동향 노티스/뉴스
        (Table: 선사 (Carrier) | 3월 최신 뉴스/노티스 요약 (Recent Notices/Events only))
        
        ### ✈️ 2. 항공 운송 - 주요 항공사 3월 카고 노티스/뉴스
        (Table: 항공사 (Airline) | 3월 최신 카고/결항 뉴스 요약 (Recent Cargo Notices only))
        
        ### ⚓ 3. 중동 로컬 항만 최신 동향 (사우디, UAE, 오만)
        (Bullet points. Filter out encyclopedia descriptions. Only list real events/delays.)
        
        ### 🌊 4. 호르무즈 해협 실시간 통항 상황
        (Bullet points. Only actual maritime incidents or rerouting news.)
        
        ### 🔥 5. 진영별 전황 속보 요약 (아랍 매체 기반)
        (Bullet points summarizing war news, noting the source bias if mentioned.)
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return "⚠️ 무료 API 호출량 초과 (약 30초 후 다시 시도해 주세요.)" if "429" in str(e) else f"⚠️ 에러: {e}"

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
        
        html += "<hr><h3>📡 5대 지표 원본 뉴스 링크 (Source)</h3>"
        cat_names = {"ocean": "🚢 해운 선사", "air": "✈️ 항공 카고", "port": "⚓ 로컬 항만", "hormuz": "🌊 호르무즈", "war": "🔥 전황 (아랍 현지 매체)"}
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
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("언어", ["한국어", "English"])
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

st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">중동 물류 5대 지표 종합 대시보드 (글로벌 팩트 + 아랍 전황)</p></div>', unsafe_allow_html=True)

if st.button("🚀 5대 지표 실시간 분석 및 요약 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 없습니다. Secrets 설정을 확인하세요.")
    else:
        with st.spinner("1/3단계: 글로벌 매체에서 선사/항공사/항만 최신 뉴스를 긁어오는 중입니다..."):
            st.session_state.global_news = fetch_global_logistics_news(is_ko)
            
        with st.spinner("2/3단계: 아랍 현지 매체에서 양측 진영의 전황 뉴스를 긁어오고 번역 중입니다..."):
            st.session_state.arab_news = fetch_arab_war_news(is_ko)
            
        with st.spinner("3/3단계: AI가 의미 없는 백과사전식 기사를 필터링하고 팩트만 요약 중입니다..."):
            st.session_state.report = analyze_live_market(API_KEY, is_ko, st.session_state.global_news, st.session_state.arab_news)

# 결과 출력
if st.session_state.report: 
    st.markdown(st.session_state.report, unsafe_allow_html=True)

# 하단 원본 뉴스 피드 렌더링
if st.session_state.global_news and st.session_state.arab_news:
    st.markdown("---")
    st.markdown('<div class="section-title">📡 카테고리별 실시간 원본 속보 (최근 7일)</div>', unsafe_allow_html=True)
    
    combined_news = {**st.session_state.global_news, **st.session_state.arab_news}

    cat_displays = [
        ("🚢 해운 선사 속보 (글로벌/국내)", "ocean"), ("✈️ 항공 화물 속보 (글로벌/국내)", "air"), 
        ("⚓ 항만 물류 속보 (글로벌/국내)", "port"), ("🌊 호르무즈 해협 속보 (글로벌/국내)", "hormuz"), 
        ("🔥 진영별 전황 속보 (아랍 현지 매체)", "war")
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
