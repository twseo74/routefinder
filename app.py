import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v97", layout="wide")

# 사이드바: 언어 및 이메일 설정 복구
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")
    send_email = st.button("현재 리포트 전송")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# API Key 보안 로드
API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("email", {}).get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 통합 분석 엔진 (에러 차단 + 팩트 고정)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "3" in m.lower() or "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발] 선사별 해상화물 처리/부킹 정책 및 대체 루트
            [Dammam is BLOCKED] 다음 하드 팩트를 표로 구성하세요:
            - MSC: 살랄라(Main)/소하르(Sub) 강제 양하(EOV). 우회료 $350~$800. 살랄라 -> 알 마즈유나 국경 -> 사우디 트럭킹.
            - Maersk: 살랄라(Salalah) 하역 후 알 바타 국경 경유.
            - RCL: 소하르(Sohar) 강제 양하(EOV) 확정. 소하르 -> UAE 경유 -> 알 바타 국경 -> 사우디 트럭킹.
            - COSCO: 아부다비 칼리파(Khalifa)항 자사 터미널 활용. 아부다비 -> 알 바타 국경 -> 사우디 트럭킹.
            - CMA CGM/Hapag-Lloyd: 제벨알리(T3) 또는 코르 파칸 활용. 알 바타 국경 경유.
            - 부킹: 담맘향 전면 중단. 살랄라/제벨알리 양하 조건부 부킹만 가능.
            
            Columns: 선사 | 항해 중 화물 처리 (Sailing) | 신규 부킹 정책 (Booking) | 상세 대체 루트 (Alt Route).
            *표 내부 줄바꿈 금지.*
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월 기준)
            - Jebel Ali: 운영 재개됐으나 보안 강화 및 야드 포화로 반출 지연 심각.
            - Salalah: MSC/Maersk 물량 집중으로 적체 최고조.
            - Sohar: 대체 양하지로 활발히 이용 중.
            - Dammam: 기항 불가 상태 유지.
            
            Columns: 항구명 | 운영 및 적체 현황 | 실무 참고사항 | 기준 일시.
            """
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 속보 (최근 48시간). 보도 일시, 제목, 요약, 성향, 링크 포함."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e: return f"⚠️ 오류: {e}"

# ==========================================
# 🚀 3. 메인 대시보드 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v97.0)</p></div>', unsafe_allow_html=True)

# 💡 질문 리스트 복구
st.markdown("""
<div class="question-box">
    <b>📋 실무 검색 타겟 질문</b><br>
    1. [극동발] 담맘항 이용 불가에 따른 각 선사별(10개사) 해상 선박 처리, 신규 부킹 정책 및 상세 대체 루트<br>
    2. 사우디, UAE, 오만의 주요 항구별 최신 실시간 상황 및 적체 현황 (기준 일시 포함)<br>
    3. 친이란 및 친미 매체들의 전쟁 상황 최신 속보 (보도 일시, 링크, 성향 포함)
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 인텔리전스 즉시 생성", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 설정 필요")
    else:
        q1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
        q2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
        q3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
        
        st.markdown(q1); st.markdown(q2); st.markdown(q3)
        st.session_state['full_report'] = q1 + q2 + q3

# ==========================================
# 📜 4. 저작권 및 이메일 전송 복구
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 참고용이며, 최종 의사결정 전 선사의 Customer Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)

if send_email and 'full_report' in st.session_state:
    st.info(f"{receiver_email}로 전송 기능을 호출합니다. (SMTP 설정 연동 필요)")
