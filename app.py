import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v105", layout="wide")

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
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 동적 분석 엔진 (Ocean Alliance & UAE 루트 강화)
# ==========================================
def run_integrated_auto_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 하드코딩 배제: 선사별 터미널 입지 및 얼라이언스 협력을 동적으로 분석
        queries = [
            f"""당신은 LX 판토스 사우디 법인의 물류 전문가입니다. 오늘({today}) 기준 다음을 분석하여 표로 작성하세요:
            1. [극동발] 담맘항 폐쇄 대응 선사별(MSC, Maersk, RCL, COSCO, CMA CGM 등) 해상 화물 처리 및 신규 부킹 정책.
            2. 특히 Jebel Ali(UAE) 및 Khalifa Port(Abu Dhabi)를 통한 접근성 분석.
            3. Ocean Alliance(COSCO, CMA CGM, Evergreen) 협력사의 가용 스페이스 및 스케줄 변화 추이.
            4. 상세 대체 루트(Salalah/Sohar/Jebel Ali -> 국경 경유 사우디 내륙) 매칭. (언어: {lang}, 셀 내 줄바꿈 금지)""",
            
            f"""오늘({today}) 기준, 주요 항만(Jebel Ali, Salalah, Sohar, Dammam)의 실시간 야드 적체 지수와 운영 상태를 분석하세요.
            특히 특정 품목에 대한 내륙 운송 시 국경(Al Batha, Al Mazyunah) 통관 절차 지원 및 지연 요소를 리포트하세요. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전쟁 상황이 홍해 및 호르무즈 해협 물류망에 미치는 군사적/정치적 속보를 분석 요약하세요. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 실시간 분석 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                time.sleep(0.5) 
        
        st.success("✅ 실시간 동적 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v105.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 분석 타겟 (실시간 동적 분석)</b><br>
    - Jebel Ali 및 Khalifa Port를 통한 UAE 루트 접근성 및 가용성 분석<br>
    - Ocean Alliance 내 협력사 스페이스 및 대체 스케줄 실시간 확인<br>
    - 국경 통관 절차 및 내륙 운송 지원 강화 요소 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 순차 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_auto_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실시간 물류 데이터 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
