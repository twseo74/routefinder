import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v110", layout="wide")

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
# 🚀 2. 전쟁 연계 동적 분석 엔진 (UAE-전쟁 우선 -> 오만 후행)
# ==========================================
def run_strategic_war_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심 지시] 1단락: 전쟁 연계 UAE/얼라이언스 분석 | 2단락: 오만 대체지 분석 | 3단락: 전황 속보
        queries = [
            f"""당신은 LX 판토스 물류 전략가입니다. {today} 기준, [중동 전쟁 연계 UAE 항만 가용성 분석]을 수행하세요:
            1. 홍해 봉쇄 및 호르무즈 해협 긴장 고조에 따른 Jebel Ali 및 Khalifa Port의 지전략적 안전성 및 접근성 분석.
            2. Ocean Alliance(COSCO, CMA CGM, Evergreen) 협력사들이 전쟁 리스크 회피를 위해 UAE 항만에서 수행 중인 선복 공유(Space Sharing) 및 피더 스케줄 변화.
            3. UAE 하역 후 알 바타(Al Batha) 국경을 통한 사우디향 육상 운송의 가용성 및 전쟁 영향도를 표로 작성하세요.
            (언어: {lang}, 하드코딩 금지, 셀 내 줄바꿈 금지)""",
            
            f"""{today} 기준, [오만(Oman) 중심 대체 루트 및 적체 분석]을 수행하세요:
            1. UAE 항만 포화 시 대안인 Salalah(살랄라) 및 Sohar(소하르)의 강제양하(EOV) 현황.
            2. 살랄라 -> 알 마즈유나 국경 루트의 야드 적체 및 화물 추출 지연 팩트 분석.
            3. 오만 항만 이용 선사들의 신규 부킹 서차지 및 전쟁 위험 할증료 현황을 리포트하세요. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황(군사 충돌, 드론 공격 등)이 오만만 및 홍해 물류망에 미치는 핵심 속보를 요약하세요. (언어: {lang})"""
        ]

        for i, query in enumerate(queries):
            status_placeholder = st.empty()
            content_placeholder = st.empty()
            status_placeholder.markdown(f'<p class="status-msg">⏳ {i+1}단계 전쟁 연계 물류 데이터 분석 중...</p>', unsafe_allow_html=True)
            
            response = model.generate_content(query)
            
            status_placeholder.empty()
            content_placeholder.markdown(response.text)
            st.divider()
            time.sleep(0.1)
        
        st.success("✅ 전쟁 연계 UAE-오만 통합 전략 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v110.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 전쟁 연계 통합 리포트 자동 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_strategic_war_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 전쟁 리스크 연계 실시간 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
