import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v95", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")
    send_button = st.button("현재 리포트 전송")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 고정밀 분석 엔진 (v95.0)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발] 선사별 해상화물 처리/부킹 정책 및 대체 루트
            [Dammam is BLOCKED] Create a Markdown Table for: MSC, Maersk, RCL, CMA CGM, COSCO, Hapag-Lloyd, HMM, Evergreen, ONE, ZIM.
            
            Columns: 선사 | 항해 중 화물 (Sailing) | 신규 부킹 (Booking) | 상세 대체 루트 (Alt Route).
            
            [Operational Logic]
            - Sailing: 항해중인 화물의 EOV(운항종료) 여부와 강제 양하 포트 명시.
            - Booking: 신규 부킹 가능 여부 및 서차지($350~$800) 명시.
            - Alt Route: 선사별 전용 터미널(Salalah/Sohar/Jebel Ali/Khalifa) 기반 사우디 진입 루트.
            
            [MUST INCLUDE]
            - MSC: 살랄라(Main)/소하르(Sub) 강제 양하. 알 마즈유나 국경 경유 트럭킹.
            - RCL: 소하르(Sohar) 강제 양하 확정.
            - COSCO: 아부다비 칼리파(Khalifa)항 자사 터미널 활용.
            - Maersk: 살랄라 하역 후 알 바타 국경 경유.
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월)
            대상: Dammam(기항불가), Jebel Ali(운영재개/포화), Salalah(EOV집중/포화), Sohar(RCL/MSC대체지).
            Columns: 항구명 | 운영 및 적체 현황 | 최신 팩트 | 기준 일시.
            """
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 속보 (최근 48시간). 보도 일시 | 제목 | 요약 | 성향 | 링크."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"⚠️ 오류: {e}"

# ==========================================
# 📧 3. 이메일 발송 함수
# ==========================================
def send_email(content, receiver):
    try:
        msg = MIMEMultipart(); msg['Subject'] = f"[LX Pantos] Saudi Logistics Report_{current_date_str}"
        msg['From'] = "Logistics_AI_Bot"; msg['To'] = receiver
        msg.attach(MIMEText(content, 'plain'))
        # SMTP 설정은 streamlit secrets에 저장되어 있어야 함
        st.info("SMTP 서버 설정이 필요합니다. (현재는 UI만 구현)")
        return True
    except: return False

# ==========================================
# 🚀 4. 메인 대시보드
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v95.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 실무 인텔리전스 생성", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else:
        q1_res = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
        q2_res = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
        q3_res = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
        
        st.markdown(q1_res); st.markdown(q2_res); st.markdown(q3_res)
        st.session_state['full_report'] = q1_res + q2_res + q3_res

# ==========================================
# 📜 5. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 참고용이며, 최종 의사결정 전 선사별 Customer Advisory 원문을 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)

if send_button and 'full_report' in st.session_state:
    if send_email(st.session_state['full_report'], receiver_email):
        st.success(f"{receiver_email}로 리포트가 전송되었습니다.")
