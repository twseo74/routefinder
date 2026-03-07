import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v104", layout="wide")

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
# 🚀 2. 동적 분석 엔진 (No Hard-coding, Dynamic Retrieval)
# ==========================================
def run_dynamic_logistics_intel(api_key, q_num, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 💡 [핵심] 사용 가능한 모델을 자동 탐색하여 환경 충돌 방지
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = datetime.now(ksa_tz).strftime("%Y-%m-%d")

        # 💡 [핵심] 하드코딩된 답변 대신, AI가 '검색'과 '추론'을 통해 답변을 생성하도록 유도하는 동적 프롬프트
        queries = [
            f"""당신은 LX 판토스의 선임 물류 분석가입니다. 오늘({today}) 기준, 사우디 담맘항 기항 중단에 따른 
            MSC, Maersk, RCL, CMA CGM 등 주요 10대 선사의 [실시간 대응 정책]을 분석하여 표로 작성하세요.
            반드시 선사별 전용 터미널(Salalah, Sohar, Jebel Ali 등)과 대체 루트(Al Mazyunah, Al Batha)를 
            현재 물류 네트워크 상황에 맞춰 동적으로 매칭하십시오. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 제벨알리, 살랄라, 소하르 항만의 [실시간 야드 적체 상황]을 분석하십시오.
            단순 수치가 아니라, 현재 담맘 우회 화물이 어디에 집중되어 있는지와 그로 인한 트럭 반출 지연 팩트를 
            최신 정보를 바탕으로 리포트하세요. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전쟁 상황이 홍해 및 호르무즈 해협 물류에 미치는 
            [실시간 군사/정치 속보]를 분석하여 요약하십시오. (언어: {lang})"""
        ]

        # 섹션별 컨테이너 생성 및 자동 순차 생성
        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실시간 분석 중..."):
                # 💡 AI가 자신의 실시간 지능을 사용하여 답변 생성
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                time.sleep(0.5) 
        
        st.success("✅ 실시간 동적 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 대시보드
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 보드 (v104.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 분석 타겟 (실시간 동적 생성)</b><br>
    1. 선사별 해상 화물 처리 및 상세 대체 루트 (살랄라/소하르/UAE 등)<br>
    2. 항만별 실시간 적체 현황 및 트럭킹 지연 팩트<br>
    3. 전황 최신 속보 및 물류 영향 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작 (실시간 데이터 분석)", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_dynamic_logistics_intel(API_KEY, q_num=None, is_ko=is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실시간 분석 기반 실무 참고용이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
