import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v117", layout="wide")

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
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정 골격 분석 엔진 (v117.0)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [매니저님 지정 1, 2, 3번 기본 골격 사수]
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 다음 1번 질문에 대해 10대 선사 모두에 동일 로직을 적용하여 표로 답변하세요:
            1. [극동발] 담맘항 폐쇄 대응 각 선사별(MSC, Maersk, RCL, COSCO, CMA CGM 등) 해상 선박 처리(EOV), 신규 부킹 정책 및 상세 대체 루트(전용 터미널 기반 Salalah/Sohar/Jebel Ali 등 매칭). 
            특히 전쟁 상황과 연계한 Jebel Ali & Khalifa Port의 가용성 및 Ocean Alliance 협력 분석을 포함하십시오. (언어: {lang}, 줄바꿈 금지)""",
            
            f"""{today} 기준, 다음 2번 질문에 대해 답변하세요:
            2. 사우디, UAE, 오만 주요 항구별(Jebel Ali, Salalah, Sohar 등) 실시간 상황 및 야드 적체 현황. 
            특히 특정 품목의 내륙 운송 시 국경(Al Batha, Al Mazyunah) 통관 절차 지원 및 지연 요소를 포함하십시오. '가상' 단어 절대 금지. (언어: {lang})""",
            
            f"""{today} 기준, 다음 3번 질문에 대해 답변하세요:
            3. 친이란 및 친미 매체들의 전쟁 상황 최신 속보 (최근 48시간 내 군사/정치 상황이 물류망에 미치는 영향). 보도 일시, 제목, 요약, 성향, 링크를 포함하십시오. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 골격 데이터 생성 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 지시하신 1, 2, 3번 기본 골격 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v117.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 분석 기본 골격 (순차 자동 생성)</b><br>
    1. 선사별 해상 선박 처리, 신규 부킹 정책 및 상세 대체 루트 (얼라이언스 협력 포함)<br>
    2. 주요 항구별 실시간 상황 및 야드 적체 현황 (국경 통관 지연 요소 포함)<br>
    3. 전황 최신 속보 (매체 성향 및 링크 포함)
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 순차 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 지침 기반 실시간 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템 (v117.0)
    </div>
""", unsafe_allow_html=True)
