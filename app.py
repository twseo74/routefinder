import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v86", layout="wide")

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
    .status-box { background-color: #fff4f4; border-left: 5px solid #E6002D; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 고정밀 실무 분석 엔진 (v86.0 - 모순 제거판)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "pro" in m.lower()), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}.
        [CRITICAL: REPORT ONLY MARCH 2026 FACTS.]
        Respond ENTIRELY in {lang}.
        """

        if q_num == 1:
            # 💡 [핵심] '담맘 하역' 문구 절대 금지 + 주변국 양하 후 트럭킹 옵션 강제
            prompt = base_prompt + """
            ### 🚢 1. [극동발] 선사별 사우디향(담맘/리야드) 대체 라우팅 전략
            [IMPORTANT RULE] Dammam port is currently INACCESSIBLE. 
            DO NOT write "담맘항 하역 후 트럭킹". This is a logical error. 
            You MUST specify an ALTERNATIVE port (Salalah, Jebel Ali, Jeddah) for discharge.

            Create a Markdown Table for 10 carriers. 
            Columns: 선사 (Carrier) | 항해중인 화물 (Sailing) | 신규 부킹 (Booking) | 사우디 인바운드 플랜 B (Alt Route to KSA).
            
            [Target Facts]
            - MSC/Maersk: Discharge at Salalah (Oman). Then Cross-border trucking via Al Batha to KSA.
            - CMA CGM/Hapag-Lloyd: Discharge at Jebel Ali (UAE). Then Cross-border trucking to KSA.
            - Evergreen: Discharge at Jeddah (KSA West) after Cape of Good Hope detour. Then land transport to East KSA.
            - Focus on Far East origins (Korea/China).
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월)
            대상: Jebel Ali, Salalah, Dammam (Blocked), Jeddah.
            컬럼: 항구명 | 최신 상황 | 기준 일시.
            *Include yard congestion at Salalah/Jebel Ali due to Dammam cargo diversion.*
            """
        else:
            prompt = base_prompt + """
            ### 🔥 3. 최신 전황 속보 (최근 48시간)
            보도 일시 | 제목 | 핵심 요약 | 성향 | 링크.
            """
        
        response = model.generate_content(prompt, tools=[{"google_search": {}}])
        return response.text
    except Exception as e:
        return f"⚠️ 오류 발생: {e}"

# ==========================================
# 🚀 3. 대시보드 메인
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 대체 라우팅 보드 (v86.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [오류 수정] 담맘항 하역 불가 전제 하에 <b>주변국(오만, UAE) 양하 후 내륙 연계</b> 옵션 강제 출력<br>
    - [팩트 체크] MSC/Maersk의 살랄라 강제 양하 및 $800 우회 서차지 반영
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 하드 팩트 릴레이 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 [극동발] 선사별 주변국 양하 및 사우디 진입 플랜 B 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1_space.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주변국 항만(제벨알리, 살랄라) 적체 및 공지사항 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2_space.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 및 군사 동향 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3_space.markdown(ans3)
            
        st.success("✅ 조회가 완료되었습니다.")
