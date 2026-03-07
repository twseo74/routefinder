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
    a { color: #003366; text-decoration: none; font-weight: bold; }
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
# 🚀 5. 실시간 뉴스 크롤러 (최근 24시간 'when:1d' 강제 적용)
# ==========================================
@st.cache_data(ttl=300)
def fetch_targeted_live_news(is_ko):
    news_results = {"war": [], "carrier": [], "port": []}
    
    # 검색 쿼리 세분화 (최근 24시간 이내 기사만 강제 추출)
    queries = {
        "war": "호르무즈 해협 OR 홍해 사태 when:1d" if is_ko else "Strait of Hormuz OR Red Sea conflict when:1d",
        "carrier": "글로벌 해운 선사 노티스 OR 항공 카고 결항 when:1d" if is_ko else "Ocean carriers notice OR Air freight suspended when:1d",
        "port": "사우디 항만 OR 제벨알리 OR 살랄라 항구 OR 푸자이라 when:1d" if is_ko else "Saudi ports OR Jebel Ali OR Salalah port when:1d"
    }
    
    for category, keyword in queries.items():
        try:
            url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword)}&hl={'ko' if is_ko else 'en-US'}&gl={'KR' if is_ko else 'US'}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            root = ET.fromstring(response.read())
            
            for item in root.findall('./channel/item')[:3]: # 카테고리별 3개씩, 총 9개 최신 기사
                news_results[category].append({
                    "title": item.find('title').text, 
                    "date": item.find('pubDate').text, 
                    "link": item.find('link').text
                })
        except: continue
    return news_results

# ==========================================
# 🚀 6. AI (Gemini) API 분석 엔진 (실무 팩트 강제)
# ==========================================
def analyze_live_market(api_key, is_ko, news_data):
    try:
        genai.configure(api_key=api_key)
        
        # 가용 모델 자동 탐색 (404 에러 방지)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if not available_models: return "⚠️ 사용할 수 있는 생성형 모델이 없습니다."
            
        chosen_model = available_models[0]
        for m in available_models:
            if "flash" in m: chosen_model = m; break
        model = genai.GenerativeModel(chosen_model) 
        
        # 카테고리별 뉴스 텍스트 병합
        all_news_text = ""
        for cat, items in news_data.items():
            for n in items: all_news_text += f"- {n['title']} ({n['date']})\n"
        
        language = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 매니저님 지시사항을 AI의 절대 규칙으로 삽입
        prompt = f"""
        You are an expert logistics analyst for LX Pantos Saudi Arabia.
        Read the following TODAY's news headlines to understand the current situation:
        <TODAYS_NEWS>
        {all_news_text}
        </TODAYS_NEWS>
        
        [CRITICAL BUSINESS RULES - MUST OBEY]
        1. 항공 (Cathay Pacific - CX): MUST state "3월 14일까지 잠정 중단" (Suspended until March 14). Do not say April 30.
        2. 해상 (Jeddah Port): Do not just say "Detour". You MUST explicitly specify the routing based on the news (e.g., "수에즈 우회(희망봉)" [Cape of Good Hope detour] OR "아덴만 통과" [Gulf of Aden transit]).
        3. 해상 (Dammam Port): MUST state "전면 중단 (🔴 Suspended)".
        
        Respond strictly in {language}. Output ONLY two Markdown tables:
        
        ### 🚢 해상 운송 (Ocean Freight) - 주요 10대 선사 최신 동향
        (Include Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL)
        Columns: 선사 (Carrier) | 상태 (Status - MUST specify DMM 🔴 / JED routing) | 타국가 포트 (Alt Foreign Port) | 실시간 주요 사항 (Real-time Notice from News)
           
        ### ✈️ 항공 운송 (Air Freight) - 리야드(RUH) 취항 현황
        (Include Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern)
        Columns: 항공사 (Airline) | 기종 (Type - PAX/Freighter) | 상태 (Status - Apply CX March 14 rule) | 최신 카고 현황 및 미취항 기한 (Remarks)
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg: return "⚠️ **무료 API 1분 사용량을 초과했습니다.** 30초 후 다시 시도하세요."
        return f"⚠️ AI 분석 오류 발생: {error_msg}"

# ==========================================
# 🚀 7. 이메일 발송 엔진
# ==========================================
def send_ai_report(receiver_email, is_ko, report_content, news_data):
    try:
        if not SENDER_EMAIL or not SENDER_PW: return False, "이메일 정보가 Secrets에 없습니다."
            
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "[LX Pantos] AI Real-time Logistics Intel Report"
        
        html_body = f"<html><body style='font-family: Arial, sans-serif;'><h2 style='color: #E6002D;'>LX PANTOS | Saudi Arabia Live Intel</h2><p><strong>Update Time (KSA):</strong> {current_time}</p><hr>"
        
        import markdown
        html_body += markdown.markdown(report_content, extensions=['tables'])
        
        html_body += "<h3>📡 오늘의 실시간 타겟 뉴스 (Today's News)</h3><ul>"
        for cat, items in news_data.items():
            for n in items: html_body += f"<li><a href='{n['link']}'>{n['title']}</a> <small>({n['date']})</small></li>"
        html_body += "</ul><hr><p><small>본 리포트는 실시간 API 뉴스 크롤링 및 AI 분석을 통해 작성되었습니다.</small></p></body></html>"
        
        msg.attach(MIMEText(html_body, 'html'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PW)
        server.send_message(msg)
        server.quit()
        return True, "발송 성공"
    except Exception as e: return False, str(e)

# ==========================================
# 🚀 8. 사이드바 UI
# ==========================================
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    
    st.markdown("---")
    st.header("📬 Send AI Report")
    user_email = st.text_input("수신 이메일 (Recipient Email)")
    if st.button("✉️ AI 리포트 발송"):
        if 'ai_report' not in st.session_state or 'news_data' not in st.session_state:
            st.error("먼저 우측 화면에서 'AI 실시간 시황 분석'을 실행해주세요.")
        elif user_email and "@" in user_email:
            with st.spinner("메일 발송 중..."):
                success, msg = send_ai_report(user_email, is_ko, st.session_state.ai_report, st.session_state.news_data)
                if success: st.success("✅ 발송 완료!")
                else: st.error(f"❌ 발송 실패: {msg}")
        else: st.error("유효한 이메일을 입력하세요.")

# ==========================================
# 🚀 9. 메인 화면 렌더링
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 해상/항공 카고 현황 (AI 실시간 분석)" if is_ko else "Far East to KSA Ocean & Air Cargo Status (AI Live Analysis)" }</p>
    </div>
    <div class="update-box"><strong>{ 'AI 엔진 실시간 분석 시점:' if is_ko else 'AI Engine Analysis Time:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 1) 실시간 타겟 뉴스 (24시간 이내) 가져오기
news_data = fetch_targeted_live_news(is_ko)
st.session_state.news_data = news_data

# 실행 버튼
if st.button("🚀 AI 실시간 시황 분석 실행 (새로고침)", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("⚠️ Streamlit Secrets에서 API Key를 찾을 수 없습니다.")
    else:
        with st.spinner("AI가 오늘 자 최신 뉴스를 긁어와 분석 중입니다... (약 10~15초 소요)"):
            ai_result = analyze_live_market(API_KEY, is_ko, news_data)
            st.session_state.ai_report = ai_result 

# 결과 출력
if 'ai_report' in st.session_state:
    st.markdown(st.session_state.ai_report, unsafe_allow_html=True)

# 실시간 뉴스 화면 출력
st.markdown("---")
st.markdown(f'<div class="section-title" style="margin-top:0;">📡 { "오늘의 글로벌 물류 실시간 속보 (최근 24시간)" if is_ko else "Today\'s Live Global Logistics News (Last 24h)" }</div>', unsafe_allow_html=True)
if news_data:
    cols = st.columns(3)
    categories = [("🔥 전쟁/호르무즈", "war"), ("🚢 선사/항공사 노티스", "carrier"), ("🌐 타국가/사우디 항만", "port")]
    for i, (title, cat) in enumerate(categories):
        with cols[i]:
            st.markdown(f"**{title}**")
            for n in news_data[cat]:
                st.markdown(f"""<div class="news-card"><span class="time-label">⏱ {n['date']}</span><a href="{n['link']}" target="_blank">{n['title']}</a></div>""", unsafe_allow_html=True)
else:
    st.write("실시간 뉴스를 불러오지 못했습니다.")

st.markdown("---")
st.markdown(f"""
    <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
            { "본 리포트는 최근 24시간 이내의 실시간 뉴스를 바탕으로 AI가 생성했습니다. 실제 물류 실행 전 반드시 담당자를 통해 교차 검증하시기 바랍니다." if is_ko else "This report is generated by AI based on news from the last 24 hours. Cross-verify before execution." }
        </p>
    </div>
""", unsafe_allow_html=True)
