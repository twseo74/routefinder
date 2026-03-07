import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
is_ko = (st.session_state.lang == "한국어")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.9rem; line-height: 1.6; }
    th { background-color: #f2f2f2; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 모듈형 AI 직문직답 엔진 (하드 팩트 강제)
# ==========================================
def search_and_answer(api_key, question_num, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 지능이 가장 높은 Pro 모델을 강제 선택
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "pro" in m.lower()), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 일반 뉴스식 요약을 절대 금지하고, 실무 수치/항구명/비용 전가 여부를 강제함
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI for Saudi Arabia inbound.
        [ABSOLUTE STRICT RULE - NO GENERIC ANSWERS]
        DO NOT write useless, generic statements like "홍해 통과 선박 우회 중", "상황에 따라 지연 가능", or "긴급 할증료 부과". This is useless to logistics managers.
        You MUST provide HARD OPERATIONAL FACTS combining live search and your expert knowledge.
        
        Respond ENTIRELY in {lang}. DO NOT use any HTML tags like <table> or <br>. Use STRICT Markdown tables only.
        """

        if question_num == 1:
            prompt = base_prompt + """
            ### 1. 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책
            Create a standard Markdown Table for these 10 carriers ONLY: MSC, A.P. Moller-Maersk, CMA CGM, COSCO Shipping Lines, Hapag-Lloyd, ONE, Evergreen Marine, HMM, Yang Ming Marine Transport, ZIM.
            Columns: 선사 (Carrier) | 항해중인 선박 실무 정책 (Sailing vessels policy) | 신규 부킹 정책 (New bookings policy).
            
            [CRITICAL REQUIREMENT FOR CARRIERS]
            For each carrier, you MUST explicitly state the following if applicable (Use your expert knowledge like MSC's recent actions):
            1. '항해 종료 (End of Voyage)' declarations.
            2. EXACT Forced Discharge Ports (e.g., 오만 살랄라, UAE 제벨알리 강제 양하).
            3. EXACT Surcharge Amounts (e.g., $800 Deviation Surcharge).
            4. Cost transfer to shipper (e.g., B/L 13조 발동, 화주 전액 부담).
            If MSC requires forced discharge at Salalah with an $800 surcharge, YOU MUST WRITE EXACTLY THAT. Do not be vague.
            """
        elif question_num == 2:
            prompt = base_prompt + """
            ### 2. 리야드 공항 노선 운영 항공사 전쟁 관련 대응 조치
            Create a standard Markdown Table for these 7 airlines ONLY: 사우디아항공, 아랍에미레이트 항공, 에티하드 항공, 카타르항공, 케세이퍼시픽, 동방항공, 에어차이나.
            Columns: 항공사 (Airline) | 운항 여부 (Operating Status) | 운항 중단 시 언제까지인지 (Suspension Period).
            Be exact. If Cathay Pacific is suspended until March 14, write exactly that. Do not guess "Normal" if you don't know; write "상태 확인 불가".
            """
        elif question_num == 3:
            prompt = base_prompt + """
            ### 3. 주변국 주요 항구 현재 상황 및 포트 당국 공지 사항
            Create a standard Markdown Table for ports categorized by country:
            - Saudi Arabia: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
            - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah Port, Ras Al Khaimah (Rak Port), Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
            - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
            Columns: 국가 (Country) | 항구명 (Port Name) | 현재 상황 및 공지사항 (Current Situation).
            Focus on hard facts: congestion levels, handling of forced discharge cargo, or official port authority notices.
            """
        else:
            prompt = base_prompt + """
            ### 4. 친이란 및 친미 매체들의 전쟁 상황 속보 (아랍 언론사 중심)
            Provide a bulleted list of the latest breaking military/war news.
            Include: 1) 기사 제목 2) 하드 팩트 요약 3) 언론사 및 성향 (친이란/친미) 4) 링크 URL.
            """
        
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">실무 하드 팩트 릴레이 검색 보드</p></div>', unsafe_allow_html=True)

if st.button("🚀 위 4가지 질문으로 실무 하드 팩트 검색 실행 (우회/두루뭉술 요약 금지)", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space, q4_space = st.empty(), st.empty(), st.empty(), st.empty()

        with st.spinner("1/4: 🚢 해운: 강제 양하 항구(살랄라 등), B/L 13조 발동, 서차지 금액 등 실무 팩트를 강제 추출 중입니다..."):
            ans1 = search_and_answer(API_KEY, 1, is_ko)
            q1_space.markdown(ans1, unsafe_allow_html=True)
            time.sleep(1)

        with st.spinner("2/4: ✈️ 항공: 결항 여부 및 정확한 중단 기한(케세이퍼시픽 등)을 추출 중입니다..."):
            ans2 = search_and_answer(API_KEY, 2, is_ko)
            q2_space.markdown(ans2, unsafe_allow_html=True)
            time.sleep(1)

        with st.spinner("3/4: ⚓ 항만: 사우디, UAE, 오만 주요 항구의 강제 하역 및 적체 상황을 추출 중입니다..."):
            ans3 = search_and_answer(API_KEY, 3, is_ko)
            q3_space.markdown(ans3, unsafe_allow_html=True)
            time.sleep(1)

        with st.spinner("4/4: 🔥 전황: 친이란/친미 매체 중심의 전쟁 군사 상황을 수집 중입니다..."):
            ans4 = search_and_answer(API_KEY, 4, is_ko)
            q4_space.markdown(ans4, unsafe_allow_html=True)
            
        st.success("✅ 실무 하드 팩트 조회가 완료되었습니다.")
