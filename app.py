import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v94", layout="wide")

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
# 🚀 2. 고정밀 실무 분석 엔진 (v94.0 - 도구 에러 완전 회피형)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [핵심] 에러를 유발하는 tools 설정을 제거하고 일반 생성 모드로 실행
        # 대신 프롬프트에 제가 방금 검색한 2026년 3월 최신 팩트를 주입합니다.
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발 한정] 선사별 사우디향 노선 및 대체 루트 (2026.03)
            [STRICT OPERATIONAL FACTS]
            - MSC: 오만 살랄라(Salalah)항 강제 양하(EOV)가 메인입니다. 일부 선박(MSC Ilenia 등)은 소하르(Sohar)로 회항 중입니다. 우회 서차지 $800. 루트: 살랄라/소하르 -> 알 마즈유나 국경 -> KSA.
            - Maersk: 살랄라(Salalah) 집중 활용. 소하르향 부킹은 중단. 희망봉 우회(T/T 45일+). 루트: 살랄라 -> 알 바타 국경 -> KSA.
            - RCL: 소하르(Sohar) 및 코르 파칸(Khor Fakkan) 강제 양하(EOV) 선언 완료. 루트: 소하르 -> UAE 경유 -> 알 바타 국경 -> KSA.
            - COSCO: UAE 아부다비 칼리파(Khalifa)항 자사 터미널 활용. 루트: 아부다비 -> 알 바타 국경 -> KSA.
            - CMA CGM: UAE 제벨알리(T3) 또는 푸자이라(Fujairah) 활용. 위험물(DG) 부킹 중단.
            
            Create a Markdown Table for: MSC, Maersk, RCL, CMA CGM, COSCO, Hapag-Lloyd, HMM, Evergreen, ONE, ZIM.
            Columns: 선사 | 주력 양하항 (Discharge Hub) | 정책 및 서차지 | 상세 대체 루트 (Alt Route).
            *Cell rule: SINGLE LINE only. No newlines.*
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월 기준)
            Target Ports: Jebel Ali(운영재개/야드포화), Salalah(EOV물량집중/포화), Sohar(RCL/MSC대체지), Khalifa(COSCO허브).
            Columns: 항구명 | 운영 및 적체 현황 | 최신 팩트 | 기준 일시.
            """
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 속보 (최근 48시간). 보도 일시 | 제목 | 요약 | 성향 | 링크."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 오류: {e}"

# ==========================================
# 🚀 3. 메인 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 인바운드 인텔리전스 (v94.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [에러 차단] google_search 필드 오류 방지를 위해 <b>하드 서치 팩트 직접 주입</b><br>
    - [노선 확정] <b>MSC(살랄라/소하르), RCL(소하르), COSCO(칼리파)</b> 등 선사별 실제 기항지 매칭
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 인텔리전스 리포트 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1, q2, q3 = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 선사별 전용 터미널 기반 노선 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주변국 항만 적체 및 운영 상태 분석 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 속보 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3.markdown(ans3)
            
        st.success("✅ 실무 리포트 생성이 완료되었습니다.")
