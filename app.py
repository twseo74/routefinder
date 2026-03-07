import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃 (가시성 완성판)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v130", layout="wide")

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

# 💡 선사명 빨간색 굵게 + 카드형 레이아웃 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px; text-transform: uppercase; }
    .data-row { margin-bottom: 10px; line-height: 1.7; display: flex; }
    .data-label { font-weight: bold; color: #444; min-width: 180px; display: inline-block; }
    .data-value { flex: 1; color: #333; white-space: pre-wrap; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 25px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 호르무즈 실무 분석 엔진 (v130.0)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 선사명 빨간색 굵게 + 불렛 포인트 줄바꿈 강제 지시
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. 오늘({today}) 기준, 호르무즈 해협 봉쇄에 따른 10대 선사별 대응을 분석하세요. 
            반드시 아래 [형식]을 엄수하고, 각 항목 내 내용은 반드시 줄바꿈하여 작성하십시오.
            
            [형식]:
            ### <span style='color:#E6002D'>**선사명**</span>
            • FM 및 Sailing 화물 양하지: (예: FM 선언 완료 / Salalah, Oman 강제 양하)
            • 신규 부킹 정책: (예: LTC 우선 배정 / Spot 중단 / 할증료 부과)
            • 화주 추가 부담 비용: (예: 재배송료 USD 1,200 / WRS USD 1,500)
            • 대체 루트 가용성: (예: Jebel Ali 보안 통제 / Ocean Alliance 협력 현황)
            
            10대 선사(MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, OOCL, ZIM, HMM)를 모두 포함하십시오. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 항만별(Salalah, Jeddah, Jebel Ali) 야드 적체 상태와 국경(Al Batha, Al Mazyunah) 통관 지연 요소를 분석하여 불렛 포인트로 작성하세요. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전황(호르무즈 봉쇄 실황 등) 속보를 요약 리포트하세요. (언어: {lang})"""
        ]

        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 선사명 강조 및 줄바꿈이 적용된 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v130.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 호르무즈 해협 봉쇄 및 FM 선언 실무 분석 (1, 2, 3단계)</b><br>
    1. 선사별 <b>FM 선언 여부, 강제 양하지(Salalah, Jeddah 등) 및 화주 추가 비용</b> 분석<br>
    2. 항만 야드 적체 지수 및 국경 통관 지연 팩트 (Al Batha, Al Mazyunah)<br>
    3. 실시간 전황 속보 및 물류망 영향도 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작 (가시성 최종판)", type="primary", use_container_width=True):
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
        담당: {current_date_str} 기준 실시간 분석 시스템 (v130.0)
    </div>
""", unsafe_allow_html=True)
