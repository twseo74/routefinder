import streamlit as st
import google.generativeai as genai
import time

# ==========================================
# 1. 초기 설정 및 언어 토글
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
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 모듈형 AI 직문직답 엔진 (지식 융합 + HTML 금지)
# ==========================================
def search_and_answer(api_key, question_num, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] HTML 태그 절대 금지 및 AI 자체 물류 지식 적극 활용 지시
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI. 
        You MUST combine live Google Search results WITH your extensive expert knowledge of current global logistics (e.g., MSC's End of Voyage at Salalah, Cathay Pacific suspension).
        Respond ENTIRELY in {lang}.
        
        [CRITICAL FORMATTING RULE] 
        DO NOT use ANY HTML tags (like <table>, <tr>, <td>, <p>, or <br>). 
        You MUST use STRICT standard Markdown ONLY for tables and formatting.
        """

        if question_num == 1:
            prompt = base_prompt + """
            ### 1. 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책
            Create a standard Markdown Table for these 10 carriers ONLY: MSC, A.P. Moller-Maersk, CMA CGM, COSCO Shipping Lines, Hapag-Lloyd, ONE, Evergreen Marine, HMM, Yang Ming Marine Transport, ZIM.
            Columns: 선사 (Carrier) | 항해중인 선박 실무 정책 (Sailing vessels policy - include discharge ports if known) | 신규 부킹 정책 (New bookings policy).
            Use your expert knowledge to fill in the actual operational reality (e.g., detour to Jebel Ali, Salalah discharge, etc.).
            """
        elif question_num == 2:
            prompt = base_prompt + """
            ### 2. 리야드 공항 노선 운영 항공사 전쟁 관련 대응 조치
            Create a standard Markdown Table for these 7 airlines ONLY: 사우디아항공, 아랍에미레이트 항공, 에티하드 항공, 카타르항공, 케세이퍼시픽, 동방항공, 에어차이나.
            Columns: 항공사 (Airline) | 운항 여부 (Operating Status) | 운항 중단 시 언제까지인지 (Suspension Period).
            Be accurate. If an airline like Cathay Pacific has suspended flights, state the exact dates.
            """
        elif question_num == 3:
            prompt = base_prompt + """
            ### 3. 주변국 주요 항구 현재 상황 및 포트 당국 공지 사항
            Create a standard Markdown Table for these ports categorized by country:
            - Saudi Arabia: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
            - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah Port, Ras Al Khaimah (Rak Port), Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
            - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
            Columns: 국가 (Country) | 항구명 (Port Name) | 현재 상황 및 공지사항 (Current Situation).
            Focus on congestion, forced discharge from detoured vessels, and logistical delays.
            """
        else:
            prompt = base_prompt + """
            ### 4. 친이란 및 친미 매체들의 전쟁 상황 속보 (아랍 언론사 중심)
            Provide a bulleted list of the latest breaking military/war news from Arab media.
            For each news item, include: 1) 기사 제목 2) 내용 요약 3) 언론사 및 성향 (친이란/친미) 4) 링크 URL.
            Do not use HTML. Use standard Markdown bullets and links `[Text](URL)`.
            """
        
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI (순차적 실행)
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">실무 직문직답 릴레이 검색 보드</p></div>', unsafe_allow_html=True)

st.markdown("""
### 📋 검색 지시 사항 (Target Questions)
1. **해운**: 호르무즈 해협 위험 증가에 따른 사우디향 선박 (항해 중 / 신규 부킹) 선사별(10개사) 정책
2. **항공**: 리야드 공항 노선 운영 항공사(7개사) 운항 여부 및 중단 기한
3. **항만**: 사우디(6개), UAE(10개), 오만(5개) 주요 항구 현재 상황 및 당국 공지
4. **전황**: 친이란/친미 아랍 매체 중심 전쟁 상황 속보 (제목, 링크, 성향 포함)
""")
st.write("")

if st.button("🚀 위 4가지 질문으로 AI 지식 융합 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space, q4_space = st.empty(), st.empty(), st.empty(), st.empty()

        with st.spinner("1/4: 🚢 10대 선사의 해상 선박 및 신규 부킹 정책을 작성 중입니다..."):
            ans1 = search_and_answer(API_KEY, 1, is_ko)
            q1_space.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/4: ✈️ 7대 항공사의 리야드 노선 운영 및 결항 여부를 작성 중입니다..."):
            ans2 = search_and_answer(API_KEY, 2, is_ko)
            q2_space.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/4: ⚓ 사우디, UAE, 오만 21개 항구의 최신 상황을 작성 중입니다..."):
            ans3 = search_and_answer(API_KEY, 3, is_ko)
            q3_space.markdown(ans3)
            time.sleep(1)

        with st.spinner("4/4: 🔥 친이란/친미 매체 중심의 전쟁 상황 속보를 수집 중입니다..."):
            ans4 = search_and_answer(API_KEY, 4, is_ko)
            q4_space.markdown(ans4)
            
        st.success("✅ 모든 답변 작성이 완료되었습니다.")
