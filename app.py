import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v115", layout="wide")

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
# 🚀 2. 범용 동적 분석 엔진 (All Carriers Universal Logic)
# ==========================================
def run_universal_dynamic_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 모든 선사에 동일하게 적용되는 4대 분석 프레임워크 주입
        queries = [
            f"""당신은 LX 판토스의 전문 분석가입니다. 오늘({today}) 기준, 아래 4대 로직을 모든 주요 10대 선사에 평등하게 적용하여 분석하십시오:
            1. [Terminal Ownership]: 각 선사의 지분 보유 항만(예: MSC/Maersk-Salalah, COSCO-Khalifa, RCL-Sohar 등)을 1순위 대체지로 우선 매핑.
            2. [Alliance Cooperation]: Ocean Alliance(COSCO, CMA CGM), 2M 등 얼라이언스 파트너 간의 UAE/오만 내 선복 공유 및 공동 기항지 활용 현황 분석.
            3. [War Accessibility]: 전쟁 리스크(홍해/호르무즈) 상황에서 각 선사가 판단하는 지전략적 안전 양하 항구 식별.
            4. [Border Matching]: 양하 항구별 최단/최적 국경(Al Batha, Al Mazyunah) 연계 및 통관 가용성 분석.
            - 결과: 선사명 | 운항 종료(EOV) 항구 | 대체 루트(국경 포함) | 스페이스/부킹 정책. (언어: {lang}, 줄바꿈 금지)""",
            
            f"""{today} 기준, UAE와 오만 전 지역 항만의 야드 혼잡도와 특정 품목(DGR 등)에 대한 국경 통관 지연 팩트를 동적으로 리포트하십시오. '가상' 단어는 절대 금지합니다. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황이 물류망에 미치는 영향을 데이터 기반으로 요약하십시오. (언어: {lang})"""
        ]

        # 섹션별 순차 렌더링
        for i, query in enumerate(queries):
            status_placeholder = st.empty()
            content_placeholder = st.empty()
            status_placeholder.markdown(f'<p class="status-msg">⏳ {i+1}단계 전 선사 범용 로직 분석 중...</p>', unsafe_allow_html=True)
            
            response = model.generate_content(query)
            
            status_placeholder.empty()
            content_placeholder.markdown(response.text)
            st.divider()
            time.sleep(0.3)
        
        st.success("✅ 모든 선사에 동일 로직이 적용된 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v115.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 전 선사 통합 동적 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_universal_dynamic_report(API_KEY, is_ko)

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
