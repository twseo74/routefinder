import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v128", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Report Export")
    target_email = st.text_input("수신자 이메일 입력", placeholder="example@lxpantos.com")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; table-layout: fixed; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 10px; text-align: center; font-size: 0.85rem; }
    td { border: 1px solid #ddd; padding: 12px; text-align: left; line-height: 1.8; vertical-align: top; white-space: pre-wrap; word-break: keep-all; font-size: 0.85rem; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #E6002D;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. FM 비용 분석 엔진 (v128.0 - 비용 상세 추가)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] FM 선언 시 화주 부담 추가 비용(Re-forwarding, WRS 등) 상세 분석 지시
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 호르무즈 해협 봉쇄에 따른 10대 선사의 FM 대응 및 [화주 추가 비용]을 표로 작성하세요.
            [필수 열]: 선사명 | FM 선언 및 강제 양하지(EOV Port) | 신규 부킹 정책 | FM 선언 시 화주 추가 부담 비용 상세.
            [작성 지침]:
            • FM 비용: 강제 하역 후 재배송 비용(Re-forwarding), 추가 터미널 핸들링(THC), 전쟁 할증료(WRS/WSC) 금액대 등을 상세히 명시.
            • 양하지: Salalah, Jeddah 등 실제 EOV 포트를 첫 줄에 배치.
            • 가독성을 위해 항목마다 반드시 줄바꿈할 것. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 주요 항구(Salalah, Jeddah, Jebel Ali 등) 야드 적체 상태와 국경(Al Batha, Al Mazyunah) 통관 지연 요소를 분석하여 표로 작성하세요. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전황 속보를 리스트로 요약 리포트하세요. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 FM 비용 및 실무 데이터 분석 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ FM 추가 비용 내역이 포함된 통합 리포트가 완성되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v128.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 호르무즈 해협 봉쇄 및 FM 선언 실무 분석 (비용 상세 포함)</b><br>
    1. 선사별 FM 선언 여부, 강제 양하지 및 화주 추가 부담 비용 (Re-forwarding/WRS 등)<br>
    2. 항만 야드 적체 지수 및 국경 통관 지연 팩트 (Al Batha, Al Mazyunah)<br>
    3. 실시간 전황 속보 및 물류망 영향도 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작 (비용 분석 강화판)", type="primary", use_container_width=True):
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
        본 리포트는 호르무즈 해협 위기 상황에 근거한 실시간 분석 결과입니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템 (v128.0)
    </div>
""", unsafe_allow_html=True)
