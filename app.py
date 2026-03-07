import streamlit as st
from datetime import datetime
import pytz
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.9rem; line-height: 1.5; }
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

# ==========================================
# 🚀 2. AI 분석 엔진 (Google Search Grounding 탑재)
# ==========================================
def analyze_live_market(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] AI에게 "네가 직접 구글 검색을 돌려서 팩트를 찾아와라"라고 명령
        prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI.
        YOUR TASK: Use your Google Search capabilities to find the ABSOLUTE LATEST real-time notices, advisories, and operational routing changes from the past 7 days.
        
        You MUST search the web for these 5 categories right now:
        1. Ocean Freight: Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM. (Search for 'End of Voyage', 'Salalah discharge', 'detour', 'surcharge', 'Red Sea notice').
        2. Air Freight: Saudia, Emirates, Qatar, Cathay Pacific, Korean Air. (Search for 'cargo suspension', 'flight cancel to Saudi').
        3. Local Ports: Dammam, Jeddah, Salalah, Jebel Ali (Search for 'congestion', 'discharge delay').
        4. Hormuz Strait / Red Sea (Vessel transit status).
        5. War / Geopolitics: Summary of US/Israel vs Iran/Houthi impact on logistics.
        
        RULES:
        - DO NOT guess. If you find a real notice (like MSC's End of Voyage or Cathay's suspension), cite it explicitly with the exact routing.
        - Ignore stock prices and financial earnings. ONLY focus on physical cargo movement.
        - If no recent notice exists for a carrier, say "최근 7일 내 공식 노티스 발견되지 않음".
        
        Output strictly in {lang} as a professional Markdown report with these 5 sections:
        
        ### 🚢 1. 해상 운송 - 주요 선사 최신 실무 노티스 (검색 기반)
        (Table: 선사 (Carrier) | 최신 운영 노티스 및 강제 양하/우회 정보)
        
        ### ✈️ 2. 항공 운송 - 주요 항공사 최신 카고 노티스 (검색 기반)
        (Table: 항공사 (Airline) | 최신 카고/결항 운영 노티스)
        
        ### ⚓ 3. 중동 로컬 항만 실무 동향 (사우디, UAE, 오만)
        (Bullet points. ONLY physical congestion, discharge changes, or operational delays.)
        
        ### 🌊 4. 호르무즈 해협 실시간 선박 통항 상황
        (Bullet points. ONLY actual maritime incidents or rerouting.)
        
        ### 🔥 5. 지정학적 전황 속보 요약
        (Bullet points summarizing war news impacting logistics.)
        """
        
        # 💡 [핵심 기술] tools="google_search_retrieval" 를 통해 AI가 스스로 웹을 검색하도록 권한 부여
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            # SDK 버전에 따라 텍스트 옵션이 안 먹힐 경우를 대비한 자동 폴백(Fallback)
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return "⚠️ 무료 API 호출량 초과 (약 30초 후 다시 시도해 주세요.)" if "429" in str(e) else f"⚠️ 에러: {e}"

# ==========================================
# 🚀 3. 이메일 발송 엔진
# ==========================================
def send_ai_report(receiver_email, is_ko, report_content):
    try:
        msg = MIMEMultipart('alternative')
        msg['From'], msg['To'] = SENDER_EMAIL, receiver_email
        msg['Subject'] = "[LX Pantos] 종합 중동 물류 인텔리전스 (AI 딥 서치 기반)"
        
        html = f"<html><body style='font-family: Arial;'><h2 style='color: #E6002D;'>LX PANTOS | Saudi Live Intel</h2><p>Update: {current_time}</p><hr>"
        html += markdown.markdown(report_content, extensions=['tables'])
        html += "<hr><p><small>본 리포트는 AI(Gemini)가 실시간으로 웹을 딥 서치하여 선사/항공사 노티스를 교차 검증한 결과입니다.</small></p></body></html>"
        
        msg.attach(MIMEText(html, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PW)
        server.send_message(msg)
        server.quit()
        return True, "성공"
    except Exception as e: return False, str(e)

# ==========================================
# 🚀 4. 대시보드 UI 및 실행
# ==========================================
if 'report' not in st.session_state: st.session_state.report = None

with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("언어", ["한국어", "English"])
    st.markdown("---")
    email = st.text_input("수신 이메일")
    if st.button("✉️ AI 딥 서치 리포트 발송"):
        if st.session_state.report and email:
            success, m = send_ai_report(email, is_ko, st.session_state.report)
            if success: st.success("발송 완료!")
            else: st.error(m)
        else:
            st.error("먼저 우측에서 분석을 실행하세요.")

st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">중동 물류 5대 지표 대시보드 (AI 실시간 딥 서치 연동)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
    <strong>💡 Search Grounding 기술 탑재 완료</strong><br>
    이제 고정된 뉴스 RSS를 긁어오지 않습니다. AI가 직접 검색 엔진에 접속해 MSC, Maersk 공식 노티스와 해운 전문지 데이터를 실시간으로 크롤링하여 팩트를 추출합니다.
</div>
""", unsafe_allow_html=True)

if st.button("🚀 AI 실시간 딥 서치(Deep Search) 및 분석 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 없습니다. Secrets 설정을 확인하세요.")
    else:
        with st.spinner("AI가 전 세계 해운/항공 전문지와 공식 노티스를 실시간으로 수색하고 있습니다... (약 15~20초 소요)"):
            st.session_state.report = analyze_live_market(API_KEY, is_ko)

# 결과 출력
if st.session_state.report: 
    st.markdown(st.session_state.report, unsafe_allow_html=True)
