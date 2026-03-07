import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v111", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.85rem; line-height: 1.4; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .status-msg { color: #E6002D; font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 통합 단계별 분석 엔진 (v111.0)
# ==========================================
def run_integrated_full_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [지시사항 통합] 1: 선사별 데이터 | 2: 항구별 데이터(UAE/오만) | 3: 전쟁 연계 분석
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, [극동발] 담맘항 폐쇄 대응 주요 10대 선사(MSC, Maersk, RCL, COSCO, CMA CGM, Hapag-Lloyd 등)의 
            실시간 해상 화물 처리(EOV) 및 신규 부킹 정책을 표로 작성하세요. 
            Ocean Alliance 내 선복 공유 현황과 대체 루트(UAE/Oman 경유)를 선사별로 상세히 포함하세요. (언어: {lang}, 셀 내 줄바꿈 금지)""",
            
            f"""{today} 기준, 홍해 봉쇄 및 전쟁 상황과 연계하여 Jebel Ali, Khalifa, Salalah, Sohar 항만의 실시간 적체 상태를 분석하세요. 
            특히 각 항구의 야드 혼잡도와 알 바타(Al Batha), 알 마즈유나 국경을 통한 내륙 운송 지연 팩트를 표로 작성하세요. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황이 호르무즈 해협 및 오만만 물류망에 미치는 군사/정치적 속보를 요약하세요. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        
        for i, query in enumerate(queries):
            status_placeholder = st.empty()
            status_placeholder.markdown(f'<p class="status-msg">⏳ {i+1}단계 실무 데이터 및 전황 분석 중...</p>', unsafe_allow_html=True)
            
            response = model.generate_content(query)
            
            status_placeholder.empty()
            containers[i].markdown(response.text)
            st.divider()
            time.sleep(0.5) 
        
        st.success("✅ 선사/항구/전황 통합 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v111.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 선사/항구/전황 통합 리포트 자동 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_full_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 데이터 기반 실시간 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
