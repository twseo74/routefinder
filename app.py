import streamlit as st
import google.generativeai as genai

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
# 🚀 2. 모듈형 AI 딥 서치 엔진 (한 번에 하나씩만 검색)
# ==========================================
def search_single_chunk(api_key, prompt, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        try:
            # 구글 검색 권한 강제 부여
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ 검색 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI 및 릴레이 검색 실행
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">릴레이 딥 서치 엔진 (할루시네이션 방지판)</p></div>', unsafe_allow_html=True)

st.write("버튼을 누르면 4개의 질문을 한 번에 던지지 않고, 하나씩 개별적으로 검색하여 실시간으로 화면에 이어 붙입니다. (각 단계별 약 10초 소요)")

if st.button("🚀 4단계 릴레이 구글 딥 서치 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        lang = "Korean" if is_ko else "English"
        
        # 💡 각 질문의 출력 결과를 표시할 빈 공간(placeholder) 4개 미리 생성
        st.markdown("---")
        ocean_placeholder = st.empty()
        air_placeholder = st.empty()
        port_placeholder = st.empty()
        war_placeholder = st.empty()

        # -----------------------------------------
        # [단계 1] 해상 운송 검색
        # -----------------------------------------
        with st.spinner("1/4: 🚢 10대 선사의 해상 선박 및 신규 부킹 정책을 검색 중입니다..."):
            prompt_ocean = f"""
            You are a logistics AI. Use Google Search. Respond ENTIRELY in {lang}.
            [RULE] DO NOT GUESS. If no specific official notice is found for a carrier, write "최근 7일 공지 검색 안됨" (No recent notice found).
            [RULE] Use HTML `<br>` tags for line breaks inside the table. Do not use actual newlines.
            
            ### 1. 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책
            Create a Markdown Table for these 10 carriers ONLY: MSC, A.P. Moller-Maersk, CMA CGM, COSCO Shipping Lines, Hapag-Lloyd, ONE, Evergreen Marine, HMM, Yang Ming Marine Transport, ZIM.
            Columns: 선사 (Carrier) | 항해중인 선박 정책 (Sailing vessels policy) | 신규 부킹 정책 (New bookings policy).
            """
            res_ocean = search_single_chunk(API_KEY, prompt_ocean, is_ko)
            ocean_placeholder.markdown(res_ocean, unsafe_allow_html=True)

        # -----------------------------------------
        # [단계 2] 항공 운송 검색
        # -----------------------------------------
        with st.spinner("2/4: ✈️ 7대 항공사의 리야드 노선 운영 및 결항 여부를 검색 중입니다..."):
            prompt_air = f"""
            You are a logistics AI. Use Google Search. Respond ENTIRELY in {lang}.
            [RULE] DO NOT GUESS "Normal" if you don't find proof. If not found, write "상태 확인 불가" (Status Unconfirmed).
            [RULE] Use HTML `<br>` tags for line breaks inside the table.
            
            ### 2. 리야드 공항 노선 운영 항공사 전쟁 관련 대응 조치
            Create a Markdown Table for these 7 airlines ONLY: 사우디아항공, 아랍에미레이트 항공, 에티하드 항공, 카타르항공, 케세이퍼시픽, 동방항공, 에어차이나.
            Columns: 항공사 (Airline) | 운항 여부 (Operating Status) | 운항 중단 시 언제까지인지 (Suspension Period).
            """
            res_air = search_single_chunk(API_KEY, prompt_air, is_ko)
            air_placeholder.markdown(res_air, unsafe_allow_html=True)

        # -----------------------------------------
        # [단계 3] 항만 상황 검색
        # -----------------------------------------
        with st.spinner("3/4: ⚓ 주변국 21개 주요 항구의 최신 공지사항을 검색 중입니다..."):
            prompt_port = f"""
            You are a logistics AI. Use Google Search. Respond ENTIRELY in {lang}.
            [RULE] DO NOT GUESS. If no news is found, write "특이사항/공지 없음" (No specific notice).
            [RULE] Use HTML `<br>` tags for line breaks inside the table.
            
            ### 3. 주변국 주요 항구 현재 상황 및 포트 당국 공지 사항
            Create a Markdown Table for these ports categorized by country:
            - Saudi Arabia: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
            - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah Port, Ras Al Khaimah (Rak Port), Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
            - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
            Columns: 국가 (Country) | 항구명 (Port Name) | 현재 상황 및 공지사항 (Current Situation).
            """
            res_port = search_single_chunk(API_KEY, prompt_port, is_ko)
            port_placeholder.markdown(res_port, unsafe_allow_html=True)

        # -----------------------------------------
        # [단계 4] 전황 속보 검색
        # -----------------------------------------
        with st.spinner("4/4: 🔥 친이란/친미 매체 중심의 전쟁 상황 속보를 수집 중입니다..."):
            prompt_war = f"""
            You are a military/geopolitics AI. Use Google Search. Respond ENTIRELY in {lang}.
            
            ### 4. 친이란 및 친미 매체들의 전쟁 상황 속보 (아랍 언론사 중심)
            Provide a bulleted list of the latest breaking news. For each news item, you MUST include: 
            1) 기사 제목 
            2) 내용 요약 
            3) 언론사 및 성향 (친이란/친미)
            4) 링크 URL.
            """
            res_war = search_single_chunk(API_KEY, prompt_war, is_ko)
            war_placeholder.markdown(res_war, unsafe_allow_html=True)
            
        st.success("✅ 모든 릴레이 검색이 완료되었습니다.")
