import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v108", layout="wide")

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
# 🚀 2. 동적 실무 분석 엔진 (Oman Port Focus)
# ==========================================
def run_oman_route_intel(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심 지시] 오만 살랄라/소하르 및 국경 루트를 실시간 분석하도록 구성
        queries = [
            f"""오늘({today}) 기준, [오만(Oman) 루트] 중심의 선사별 대응 정책을 분석하세요:
            1. MSC와 Maersk의 Salalah(살랄라) 강제양하(EOV) 및 피더 연결 현황.
            2. RCL 및 기타 선사의 Sohar(소하르) 기항 및 대체 부킹 정책.
            3. Salalah -> Al Mazyunah 국경 및 Sohar -> Al Batha 국경을 통한 사우디 내륙 운송 가용성.
            4. Ocean Alliance의 UAE/Oman 스페이스 공유 현황을 표로 작성하세요. (언어: {lang}, 줄바꿈 금지)""",
            
            f"""{today} 기준, 오만 주요 항구(Salalah, Sohar) 및 UAE 항구의 야드 적체(Yard Density)를 분석하세요.
            특히 살랄라항의 포화 상태로 인한 화물 추출 지연과 소하르항 경유 시 통관 지원 강화 요소를 실시간 데이터로 리포트하세요. (언어: {lang})""",
            
            f"""오늘 기준, 최근 48시간 내 중동 전황이 오만만(Gulf of Oman) 및 아라비아해 물류망에 미치는 영향을 군사/정치적 관점에서 요약하세요. (언어: {lang})"""
        ]

        for i, query in enumerate(queries):
            status_placeholder = st.empty()
            content_placeholder = st.empty()
            status_placeholder.markdown(f'<p class="status-msg">⏳ {i+1}단계 오만 루트 및 실무 데이터 분석 중...</p>', unsafe_allow_html=True)
            
            response = model.generate_content(query)
            
            status_placeholder.empty()
            content_placeholder.markdown(response.text)
            st.divider()
            time.sleep(0.1)
        
        st.success("✅ 오만 루트 중심 실시간 동적 분석 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 대시보드
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v108.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box" style="background-color:#fff5f5; border-left:5px solid #E6002D; padding:15px; border-radius:5px;">
    <b>📋 오만(Oman) 및 UAE 루트 집중 분석</b><br>
    - Salalah & Sohar 항만 적체 지수 및 선사별 EOV 처리 정책 분석<br>
    - Al Mazyunah & Al Batha 국경 통관 절차 및 내륙 운송 강화 요소<br>
    - Ocean Alliance 내 협력사 스페이스 및 실시간 전황 영향도
</div>
""", unsafe_allow_html=True)

if st.button("🚀 오만 루트 중심 전체 리포트 자동 생성", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_oman_route_intel(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 및 꼬리말
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실시간 물류 데이터 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
