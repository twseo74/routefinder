import streamlit as st
from datetime import datetime
import pytz
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. 페이지 설정 및 다국어 세션
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

# 2. 고해상도 디자인 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# ==========================================
# 🚀 4. Secrets 안전 추출 로직
# ==========================================
API_KEY = None
SENDER_EMAIL = None
SENDER_PW = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]:
        API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
        
    if "email" in st.secrets:
        SENDER_EMAIL = st.secrets["email"].get("sender_email")
        SENDER_PW = st.secrets["email"].get("sender_password")
except Exception:
    pass

# ==========================================
# 🚀 5. AI (Gemini) API 연동 엔진 (자동 모델 탐색 로직 적용)
# ==========================================
def analyze_live_market(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [에러 원천 차단] 404 에러를 막기 위해 사용 가능한 최신 모델 리스트를 서버에서 직접 받아옵니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            return "⚠️ API 키는 정상이나 사용할 수 있는 생성형 모델이 할당되지 않았습니다. Google AI Studio 설정을 확인해주세요."
            
        # 가장 빠르고 최신인 flash 모델을 우선적으로 찾아서 자동 할당
        chosen_model = available_models[0]
        for m in available_models:
            if "flash" in m:
                chosen_model = m
                break
                
        model = genai.GenerativeModel(chosen_model) 
        
        language = "Korean" if is_ko else "English"
        prompt = f"""
        You are an expert logistics analyst for LX Pantos Saudi Arabia.
        Search the latest news today and provide the real-time shipping and air freight status to Saudi Arabia.
        Respond strictly in {language}. 
        
        Please output ONLY two Markdown tables and nothing else:
        
        ### 🚢 해상 운송 (Ocean Freight) - 주요 10대 선사
        Columns: 선사 (Carrier) | 상태 (Status - e.g., JED Detour, DMM Stop) | 실시간 주요 사항 (Real-time Notice from news)
        (Include Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL)
           
        ### ✈️ 항공 운송 (Air Freight) - 리야드(RUH) 취항 현황
        Columns: 항공사 (Airline) | 기종 (Type - PAX/Freighter) | 상태 (Status) | 카고 현황 및 미취항 기한 (Cargo Remarks & Resumption date)
        (Include Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern)
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "Quota" in error_msg:
            return "⚠️ **무료 API 1분 사용량을 초과했습니다.** 약 30초 대기 후 새로고침 버튼을 다시 눌러주세요."
        return f"⚠️ AI 분석 오류 발생: {error_msg}"

# ==========================================
# 🚀 6. 이메일 발송 엔진 (AI 결과 전송)
# ==========================================
def send_ai_report(receiver_email, report_content):
    try:
        if not SENDER_EMAIL or not SENDER_PW:
            return False, "이메일 발신자 정보가 Secrets에 없습니다."
            
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "[LX Pantos] AI Real-time Logistics Intel Report"
        
        body = f"LX Pantos Saudi Arabia 실시간 시황 업데이트 ({current_time})\n\n"
        body += report_content
        body += "\n\n* 본 리포트는 AI가 실시간으로 분석한 참고용 데이터입니다."
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PW)
        server.send_message(msg)
        server.quit()
        return True, "발송 성공"
    except Exception as e:
        return False, str(e)

# ==========================================
# 🚀 7. 사이드바 (이메일 발송 UI)
# ==========================================
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    
    st.markdown("---")
    st.header("📬 Send AI Report")
    user_email = st.text_input("수신 이메일 (Recipient Email)")
    if st.button("✉️ 생성된 AI 리포트 메일로 보내기"):
        if 'ai_report' not in st.session_state:
            st.error("먼저 우측 화면에서 'AI 실시간 시황 분석'을 실행해주세요.")
        elif user_email and "@" in user_email:
            with st.spinner("메일 발송 중..."):
                success, msg = send_ai_report(user_email, st.session_state.ai_report)
                if success:
                    st.success("✅ AI 리포트 발송 완료!")
                else:
                    st.error(f"❌ 발송 실패: {msg}")
        else:
            st.error("유효한 이메일을 입력하세요.")

# ==========================================
# 🚀 8. 메인 화면 렌더링
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 해상/항공 카고 현황 (AI 실시간 분석)" if is_ko else "Far East to KSA Ocean & Air Cargo Status (AI Live Analysis)" }</p>
    </div>
    <div class="update-box"><strong>{ 'AI 엔진 실시간 분석 시점:' if is_ko else 'AI Engine Analysis Time:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 실행 버튼
if st.button("🚀 AI 실시간 시황 분석 실행 (새로고침)", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("⚠️ Streamlit Secrets에서 API Key를 찾을 수 없습니다.")
    else:
        with st.spinner("AI가 사용 가능한 최신 모델을 검색하여 실시간 물류 데이터를 분석 중입니다... (약 10~15초 소요)"):
            ai_result = analyze_live_market(API_KEY, is_ko)
            st.session_state.ai_report = ai_result 

# 결과가 있으면 출력
if 'ai_report' in st.session_state:
    st.markdown(st.session_state.ai_report, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"""
    <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
            { "본 리포트의 정보는 인공지능이 최신 기보를 기반으로 생성한 자료입니다. 실제 물류 실행 시에는 반드시 LX Pantos 담당 전문가를 통해 최종 검증을 받으시기 바랍니다." if is_ko else "This report is generated by AI based on the latest advisories. Please consult with LX Pantos specialists for final verification before execution." }
        </p>
    </div>
""", unsafe_allow_html=True)
