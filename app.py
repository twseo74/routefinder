import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v93", layout="wide")

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
    .status-box { background-color: #fdf2f2; border-left: 5px solid #E6002D; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 고정밀 실무 분석 엔진 (v93.0 - 에러 원천 차단형)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [핵심] API 버전과 라이브러리 충돌을 피하기 위해 도구(Tools)를 최소화하거나 
        # 가장 안정적인 명칭인 'google_search_retrieval'을 딕셔너리로 시도
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        
        # 필드 에러를 방지하기 위해 도구 설정을 유연하게 구성
        try:
            model = genai.GenerativeModel(model_name=target_model, tools=[{"google_search_retrieval": {}}])
        except:
            model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발 한정] 선사별 사우디향 노선 및 대체 루트 (2026.03)
            [INSTRUCTION] Dammam is blocked. Provide real-world routing based on carrier-terminal contracts. 
            
            Create a Markdown Table for: MSC, Maersk, RCL, CMA CGM, COSCO, Hapag-Lloyd, HMM, Evergreen, ONE, ZIM.
            Columns: 선사 | 주력 양하항 (Discharge Hub) | 정책 및 서차지 | 상세 대체 루트 (Alt Route).
            
            [OPERATIONAL FACTS TO INCLUDE]
            - MSC: Salalah (Oman) is the main hub (EOV declared). Some vessels diverted to Sohar. Route: Salalah -> Al-Mazyunah border -> KSA.
            - RCL: Sohar (Oman) is the confirmed hub (EOV declared). Route: Sohar -> UAE transit -> Al Batha border -> KSA.
            - COSCO: Khalifa Port (Abu Dhabi, UAE). Route: Khalifa -> Al Batha border -> KSA.
            - CMA CGM: Jebel Ali (UAE) or Khor Fakkan. Route: UAE -> Al Batha border -> KSA.
            - Evergreen: Detour Cape of Good Hope -> Jeddah/KAP (KSA West).
            
            *Cell rule: SINGLE LINE only. No <br> or newlines.*
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월 기준)
            Target Ports: Jebel Ali (UAE), Salalah (Oman), Sohar (Oman), Dammam (Blocked).
            Columns: 항구명 | 운영 및 적체 현황 | 최신 팩트 | 기준 일시.
            *Mention Jebel Ali is reopened but yard is saturated.*
            """
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 및 속보 (48시간 내). 보도 일시 | 제목 | 요약 | 성향 | 링크."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 오류: {e}"

# ==========================================
# 🚀 3. 메인 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 대체 라우팅 보드 (v93.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [에러 해결] Unknown field (google_search) 우회 패치 적용<br>
    - [노선 확정] <b>MSC(살랄라), RCL(소하르), COSCO(칼리파)</b> 등 선사별 실제 기항지 매핑
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실시간 실무 인텔리전스 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1, q2, q3 = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 선사별 전용 터미널 기반 노선 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주변국 항만 적체 및 운영 상태 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 속보 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3.markdown(ans3)
            
        st.success("✅ 실무 리포트 생성이 완료되었습니다.")
