import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v91", layout="wide")

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
    .status-box { background-color: #fff4f4; border-left: 5px solid #E6002D; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 초정밀 실무 분석 엔진 (v91.0)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            # 💡 [핵심] 선사별 상세 루트 팩트 주입 (뇌피셜 방지)
            prompt = base_prompt + """
            ### 🚢 1. [극동발 한정] 선사별 사우디향 대체 라우팅 및 실무 정책
            [STRICT OPERATIONAL GUIDELINES]
            - MSC: 오만 살랄라(Salalah) 또는 소하르(Sohar) 강제 양하. 운항 종료(EOV) 선언. USD 350 서차지. 알 마즈유나(Al-Mazyunah) 국경 경유 사우디행 육상운송.
            - Maersk: 살랄라 허브 집중 활용. 희망봉 우회(T/T 45일+). 살랄라 하역 후 알 바타 국경 경유 트럭킹.
            - RCL: 소하르(Sohar)항 강제 양하(EOV) 확정. 이후 화주 책임 하에 사우디 인바운드 진행.
            - CMA CGM/Hapag-Lloyd: 제벨알리(Jebel Ali) T3 또는 소하르 활용. 알 바타 국경 경유 트럭킹.
            - Evergreen: 희망봉 우회 후 사우디 제다(Jeddah) 또는 킹 압둘라(KAP) 직접 기항. 이후 사우디 내륙 횡단 운송.
            
            Create a Markdown Table for 10 carriers (MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, Yang Ming, ZIM).
            Columns: 선사 | 항해중인 화물 정책 | 신규 부킹 정책 | 사우디 인바운드 상세 대체 루트(플랜 B).
            [RULE] DO NOT use line breaks (<br>) inside cells.
            """
        elif q_num == 2:
            prompt = base_prompt + "### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월). 대상: Jebel Ali(피격 여파 적체), Salalah(우회화물 포화), Dammam(기항불가), Sohar(대체항 부상). 기준 일시 포함."
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 속보 (최근 48시간). 보도 일시, 제목, 요약, 성향, 링크 포함."
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 오류: {e}"

# ==========================================
# 🚀 3. 메인 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 대체 라우팅 보드 (v91.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [실무 디테일] <b>MSC/RCL 소하르 기항 및 살랄라 알 마즈유나 루트</b> 등 하드 팩트 반영<br>
    - [규격 준수] 표 내부 줄바꿈 제거 및 극동발 타겟팅 강화
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 하드 팩트 릴레이 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1, q2, q3 = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 선사별 상세 대체 루트(소하르/살랄라/알 마즈유나 등) 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주요 항만 적체 및 운영 상태 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 및 군사 동향 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3.markdown(ans3)
            
        st.success("✅ 실무 하드 팩트 조회가 완료되었습니다.")
