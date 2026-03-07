import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v92", layout="wide")

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
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .status-box { background-color: #f0f7ff; border-left: 5px solid #0056b3; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 선사-터미널 매핑 기반 분석 엔진 (v92.0)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        
        # 💡 [핵심] 최신 검색 도구 적용
        model = genai.GenerativeModel(model_name=target_model, tools=[{"google_search": {}}])
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            # 💡 [핵심] 선사별 전용 터미널 기반 대체 루트 강제 (하드코딩 방지 로직)
            prompt = base_prompt + """
            ### 🚢 1. [극동발] 선사별 전용 터미널 기반 사우디향 대체 루트 (2026.03)
            Analyze the relationship between carriers and their hub terminals. Dammam is BLOCKED. 
            Specify if they use OMAN (Salalah/Sohar) or UAE (Jebel Ali/Khalifa).
            
            Create a Markdown Table for: MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, RCL, ZIM.
            Columns: 선사 | 주력 대체 양하항 (Main Hub) | 신규 부킹 및 서차지 | 사우디 인바운드 상세 루트 (Routing).
            
            [Operational Logic]
            - MSC/Maersk: Use Salalah (Oman) as main hub due to dedicated terminals. Discharge there (EOV). Route: Salalah -> Al-Mazyunah border -> KSA.
            - RCL: Use Sohar (Oman). Discharge there (EOV). Route: Sohar -> UAE transit -> Al Batha border -> KSA.
            - COSCO: Use Khalifa Port (UAE). Route: Abu Dhabi -> Al Batha border -> KSA.
            - CMA CGM/Hapag-Lloyd: Use Jebel Ali (UAE) or Khor Fakkan. Route: UAE -> Al Batha border -> KSA.
            - Evergreen: Route via Cape of Good Hope to Jeddah (KSA West).
            
            *Cell rule: DO NOT use line breaks inside cells.*
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (UAE/오만/사우디)
            Target: Dammam(Blocked), Jebel Ali(Reopened but congested), Salalah(Saturated), Sohar(Active alternative), Khalifa Port(Normal).
            Columns: 항구명 | 운영 상태 및 적체 수준 | 최신 팩트 및 공지사항 | 기준 일시.
            *Mention terminal congestion in Salalah and Jebel Ali specifically.*
            """
        else:
            prompt = base_prompt + """
            ### 🔥 3. 최신 전황 및 속보 (최근 48시간)
            보도 일시 | 제목 | 핵심 요약 | 성향 | 링크.
            """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 오류: {e}"

# ==========================================
# 🚀 3. 메인 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 인바운드 상황판 (v92.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 실시간 분석 기준: {current_date_str} (KSA)</b><br>
    - [노선 매핑] 선사별 전용 터미널(Salalah, Sohar, Jebel Ali, Khalifa) 기반 대체 루트 추적<br>
    - [UAE 활용] 제벨알리 운영 재개 및 아부다비 칼리파 항을 통한 사우디 진입 옵션 포함
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실시간 실무 하드 팩트 검색 및 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1, q2, q3 = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 선사-터미널 매핑 기반 대체 노선 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ UAE/오만 항만별 적체 및 운영 상태 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 속보 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3.markdown(ans3)
            
        st.success("✅ 실시간 실무 인텔리전스 생성이 완료되었습니다.")
