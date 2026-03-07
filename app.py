import streamlit as st
import pandas as pd
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

# ==========================================
# 1. 초기 설정 및 언어 토글
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Control Tower", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
# 사이드바에서 언어 선택
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
is_ko = (st.session_state.lang == "한국어")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .status-alert { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #cf1322; font-weight: bold;}
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    .news-card { background-color: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 4px; border-left: 5px solid #8b5cf6; }
    .source-label { background-color: #e2e8f0; color: #1e293b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-iran { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .leaning-us { background-color: #e0f2fe; color: #075985; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; margin-bottom: 5px; display: inline-block;}
    .time-label { color: #888; font-size: 0.75rem; margin-bottom: 5px; display: block; margin-top: 5px; }
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
# 🚀 2. 인바운드 실무 팩트 베이스라인 (다국어 지원)
# ==========================================
if is_ko:
    ocean_data = [
        {"선사 (Carrier)": "MSC", "담맘향 상태": "🔴 전면 중단 (End of Voyage)", "대체 양하 포트": "오만 살랄라 / UAE 아부다비", "실무 대응 방안 (Action Plan)": "살랄라 강제 양하 시 화주 비용으로 Cross-border 트럭킹 수배 필요 ($800 서차지).", "상태": "🔴 중단"},
        {"선사 (Carrier)": "Maersk", "담맘향 상태": "🔴 우회 및 양하", "대체 양하 포트": "UAE 제벨알리 / 코르파칸", "실무 대응 방안 (Action Plan)": "제벨알리 하역 후 사우디 국경(Batha) 경유 Landbridge 운송망 확보 집중.", "상태": "🔴 우회"},
        {"선사 (Carrier)": "CMA CGM", "담맘향 상태": "🔴 상부 걸프 진입 불가", "대체 양하 포트": "UAE 푸자이라", "실무 대응 방안 (Action Plan)": "푸자이라 하역 후 육로 연계. 피더(Feeder)선 수배 극도 지연 중.", "상태": "🔴 불가"},
        {"선사 (Carrier)": "Hapag-Lloyd", "담맘향 상태": "🔴 우회", "대체 양하 포트": "UAE 코르파칸", "실무 대응 방안 (Action Plan)": "희망봉 우회로 인한 T/T 25일 이상 추가. 화주 대상 공식 안내 요망.", "상태": "🔴 우회"},
        {"선사 (Carrier)": "HMM / ONE", "담맘향 상태": "🔴 부킹 접수 중단", "대체 양하 포트": "확인 불가", "실무 대응 방안 (Action Plan)": "신규 선적 절대 불가. 대체 선사 수배 요망.", "상태": "🔴 중단"}
    ]
    air_data = [
        {"항공사 (Airline)": "Cathay Pacific (CX)", "사우디향 상태": "🔴 결항 (Suspended)", "운영 재개 예상일": "3월 14일 이후 잠정", "비고": "RFS(트럭킹) 연계 스페이스 전면 차단."},
        {"항공사 (Airline)": "Korean Air (KE)", "사우디향 상태": "🔴 결항 (Suspended)", "운영 재개 예상일": "미정 (안전성 검토)", "비고": "해상 우회 화물의 항공 전환으로 두바이(DXB) 경유 수요 폭증."},
        {"항공사 (Airline)": "Saudia / Emirates", "사우디향 상태": "🟢 정상 운영 (지연 심각)", "운영 재개 예상일": "현재 운항 중", "비고": "DXB 및 RUH 허브 적체 극심. 환승 지연 발생 중."}
    ]
else:
    ocean_data = [
        {"Carrier": "MSC", "Dammam Status": "🔴 End of Voyage", "Alt Port": "Salalah (Oman) / Abu Dhabi (UAE)", "Action Plan": "Arrange cross-border trucking at cargo owner's expense ($800 surcharge).", "Status": "🔴 Suspended"},
        {"Carrier": "Maersk", "Dammam Status": "🔴 Detour / Discharge", "Alt Port": "Jebel Ali / Khor Fakkan (UAE)", "Action Plan": "Secure Landbridge network via Batha border after Jebel Ali discharge.", "Status": "🔴 Detour"},
        {"Carrier": "CMA CGM", "Dammam Status": "🔴 Upper Gulf Blocked", "Alt Port": "Fujairah (UAE)", "Action Plan": "Overland transport after Fujairah discharge. Feeder vessels heavily delayed.", "Status": "🔴 Blocked"},
        {"Carrier": "Hapag-Lloyd", "Dammam Status": "🔴 Detour", "Alt Port": "Khor Fakkan (UAE)", "Action Plan": "Cape of Good Hope detour adds 25+ days T/T. Notify clients immediately.", "Status": "🔴 Detour"},
        {"Carrier": "HMM / ONE", "Dammam Status": "🔴 Booking Suspended", "Alt Port": "N/A", "Action Plan": "No new bookings accepted. Must find alternative carriers.", "Status": "🔴 Suspended"}
    ]
    air_data = [
        {"Airline": "Cathay Pacific (CX)", "KSA Status": "🔴 Suspended", "Resumption": "Tentatively after Mar 14", "Remarks": "RFS (Trucking) space completely blocked."},
        {"Airline": "Korean Air (KE)", "KSA Status": "🔴 Suspended", "Resumption": "TBD (Safety review)", "Remarks": "DXB transit demand soaring due to Sea-Air conversion."},
        {"Airline": "Saudia / Emirates", "KSA Status": "🟢 Operating (Severe Delay)", "Resumption": "Currently operating", "Remarks": "Severe congestion at DXB and RUH hubs. Transit delays expected."}
    ]

df_ocean = pd.DataFrame(ocean_data)
df_air = pd.DataFrame(air_data)

# ==========================================
# 🚀 3. 진영별 전황 실시간 크롤러 (복구 완료)
# ==========================================
@st.cache_data(ttl=300)
def fetch_arab_war_news(is_ko):
    translator = GoogleTranslator(source='ar', target='ko' if is_ko else 'en')
    war_news = []
    
    queries = [
        ("مضيق هرمز OR البحر الأحمر (العربية OR سكاي نيوز) when:3d", "🔵 친미/친사우디(GCC)" if is_ko else "🔵 Pro-US/GCC", "leaning-us"),
        ("مضيق هرمز OR البحر الأحمر (الميادين OR العالم) when:3d", "🔴 친이란/저항의 축" if is_ko else "🔴 Pro-Iran/Axis", "leaning-iran")
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
                
                war_news.append({
                    "title": translator.translate(title),
                    "summary": translator.translate(desc) if desc else ("요약 없음" if is_ko else "No summary"),
                    "link": item.find('link').text, "date": item.find('pubDate').text, 
                    "orig_title": title, "source": source, "leaning": leaning, "l_class": l_class
                })
        except: continue
    return war_news

# ==========================================
# 🚀 4. AI 노티스 전용 분석기 
# ==========================================
def analyze_notice(api_key, notice_text, is_ko):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        lang = "Korean" if is_ko else "English"
        prompt = f"""
        You are an inbound logistics expert for LX Pantos Saudi Arabia.
        Analyze the following raw logistics notice/email:
        
        <NOTICE>
        {notice_text}
        </NOTICE>
        
        Extract the physical logistics impact specifically for Saudi Arabia (Dammam, Riyadh, Jeddah). 
        Respond strictly in {lang} with ONLY these 4 bullet points (no intro/outro):
        
        1. **발신 기관 (Carrier/Airline)**:
        2. **대상 항구/공항 상태 (Target Port/Airport Status)**: (e.g., Dammam blocked, discharging at Salalah)
        3. **비용/서차지 (Surcharges)**: (Only if mentioned)
        4. **LX Pantos 실무 대응 요약 (Action Required)**: (1 sentence of operational advice)
        """
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ 분석 오류 (Analysis Error): {e}"

# ==========================================
# 🚀 5. 대시보드 UI 렌더링
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Inbound Control Tower</span></h1></div>', unsafe_allow_html=True)

alert_msg = "🚨 [긴급 상황반] 호르무즈 해협 위기 - 담맘(DMM) 입항 전면 통제 및 대체 항만(UAE/Oman) 강제 양하 진행 중" if is_ko else "🚨 [EMERGENCY] Hormuz Crisis - Dammam (DMM) fully restricted, mandatory discharge at UAE/Oman ports"
st.markdown(f'<div class="status-alert">{alert_msg} (Update: {current_time})</div>', unsafe_allow_html=True)

# --- [섹션 1] 고정 실무 시황표 ---
st.markdown(f'<div class="section-title">🚢 {"[해상] 주요 10대 선사 담맘향 라우팅 및 대응 방안" if is_ko else "[Ocean] Top 10 Carriers Dammam Routing & Action Plans"}</div>', unsafe_allow_html=True)
st.dataframe(df_ocean, use_container_width=True, hide_index=True)

st.markdown(f'<div class="section-title">✈️ {"[항공] 리야드(RUH)향 주요 항공사 카고 현황" if is_ko else "[Air] Riyadh (RUH) Cargo Status by Major Airlines"}</div>', unsafe_allow_html=True)
st.dataframe(df_air, use_container_width=True, hide_index=True)

# --- [섹션 2] 진영별 전황 실시간 크롤링 (복구) ---
st.markdown("---")
if st.button(f"🔥 {'실시간 아랍 진영별 전황 속보 긁어오기 (클릭)' if is_ko else 'Fetch Live Arab Geopolitical News (Click)'}", type="primary"):
    with st.spinner("아랍 현지 매체(친미/친이란)의 최신 보도를 번역 중입니다..." if is_ko else "Translating latest reports from Arab media..."):
        st.session_state.war_news = fetch_arab_war_news(is_ko)

if 'war_news' in st.session_state and st.session_state.war_news:
    st.markdown(f'<div class="section-title">🔥 {"중동 지정학적 전황 속보 (아랍 로컬 매체 기반)" if is_ko else "Middle East Geopolitical News (Arab Local Media)"}</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    # 친미/친이란 뉴스 반반씩 출력
    for i, n in enumerate(st.session_state.war_news):
        with cols[i % 2]:
            st.markdown(f"""
                <div class="news-card">
                    <div>
                        <span class="source-label">📰 {n['source']}</span>
                        <span class="{n['l_class']}">{n['leaning']}</span>
                    </div>
                    <span class="time-label">{n['date']}</span>
                    <a href="{n['link']}" target="_blank">{n['title']}</a>
                    <p class="summary-text" style="font-size:0.8rem;">{n['summary']}</p>
                </div>
            """, unsafe_allow_html=True)

# --- [섹션 3] AI 노티스 분석기 ---
st.markdown("---")
st.markdown(f'<div class="section-title">🤖 {"AI 신규 노티스 해독기 (Notice Analyzer)" if is_ko else "AI Notice Analyzer"}</div>', unsafe_allow_html=True)
st.write("선사나 로컬 파트너에게 받은 긴급 이메일/왓츠앱 원문을 아래에 붙여넣으세요." if is_ko else "Paste raw urgent emails/WhatsApp messages from carriers or local partners below.")

notice_input = st.text_area("Paste Notice Here:", height=150)

if st.button(f"🚀 {'신규 노티스 실무 영향 분석' if is_ko else 'Analyze Notice Impact'}", type="secondary"):
    if not API_KEY:
        st.error("API Key is missing.")
    elif not notice_input:
        st.warning("Please enter text." if not is_ko else "텍스트를 입력해 주세요.")
    else:
        with st.spinner("Analyzing..."):
            analysis_result = analyze_notice(API_KEY, notice_input, is_ko)
            st.markdown(f"<div style='background-color: #f8f9fa; padding: 20px; border-left: 4px solid #003366; border-radius: 4px;'>{analysis_result}</div>", unsafe_allow_html=True)
