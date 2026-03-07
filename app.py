import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v85", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
is_ko = (st.session_state.lang == "한국어")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.9rem; line-height: 1.6; }
    th { background-color: #f8f9fa; font-weight: bold; color: #333; }
    .status-box { background-color: #f0f7ff; border-left: 5px solid #0056b3; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 고정밀 실무 분석 엔진 (v85.0 - 최신 API 규격 적용)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [핵심] Pro 모델 강제 선택
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "pro" in m.lower()), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}.
        [CRITICAL: REPORT ONLY MARCH 2026 FACTS. DO NOT USE 2024/2025 DATA.]
        Respond ENTIRELY in {lang}. Use standard Markdown tables only.
        """

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발 한정] 해상 선사별 사우디향 운송 정책 및 대체 루트 (2026년 3월)
            대상 선사: MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, Yang Ming, ZIM.
            
            다음 4가지 컬럼을 포함한 표를 작성하세요:
            1. 선사 (Carrier)
            2. 항해중인 화물 정책 (Sailing Cargo): 'End of Voyage' 선언 여부와 강제 양하 포트(살랄라, 제벨알리 등) 명시.
            3. 신규 부킹 정책 (New Booking): 부킹 중단 여부 및 정확한 할증료 금액(예: $800 등).
            4. 사우디 인바운드 대체 루트 (Alternative Routing): 극동(한/중/일)에서 사우디로 보내기 위한 대체 항로 및 내륙 연계 옵션(알 바타 국경 트럭킹 등).
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 주요 항구 실시간 상황 및 공지 (2026년 3월 기준)
            표 형식 작성. 대상: Dammam, Jeddah, Jebel Ali, Salalah, Khalifa Port, Fujairah.
            컬럼: 항구명 | 국가 | 최신 상황 및 공지 (Status) | 기준 일시 (Date/Time - MUST BE MARCH 2026).
            *요격 사태 후 운영 재개 여부, 우회 화물로 인한 야드 적체 팩트 포함.*
            """
        else:
            prompt = base_prompt + """
            ### 🔥 3. 진영별 전쟁 상황 속보 (2026년 3월 최신)
            항목: 보도 일시 | 제목 | 하드 팩트 요약 | 언론사 및 성향 | 링크(URL).
            """
        
        # 💡 [핵심 수정] google_search_retrieval 대신 google_search 도구 사용
        try:
            response = model.generate_content(prompt, tools=[{"google_search": {}}])
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ API 오류 발생: {e}"

# ==========================================
# 🚀 3. 대시보드 메인
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 인바운드 상황판 (v85.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [API 패치 완료] google_search 최신 규격 적용<br>
    - 10대 선사의 극동발 대체 라우팅(Trucking/Landbridge) 옵션 포함
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 하드 팩트 릴레이 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 선사별 대체 항로 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1_space.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 항만 실시간 적체 및 공지사항 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2_space.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 진영별 최신 전황 속보 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3_space.markdown(ans3)
            
        st.success("✅ 모든 조회가 완료되었습니다.")
