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
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 딥 서치 기반 직문직답 엔진
# ==========================================
def ask_ai_search(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        # Search Grounding을 지원하는 모델 선택
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 매니저님이 작성해주신 완벽한 질문 리스트를 그대로 AI에게 명령으로 전달
        prompt = f"""
        You are an expert logistics intelligence AI. 
        You MUST use your internal Google Search capabilities to find the ABSOLUTE LATEST facts regarding the Middle East crisis and its impact on logistics.
        
        Answer the following 4 specific questions directly. Respond ENTIRELY in {lang}. 
        If you cannot find specific information for a company or port, explicitly state "검색된 최신 노티스/정보 없음" (No latest information found) instead of guessing.
        
        ### Question 1: 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책
        Create a Markdown Table for the following carriers: MSC, A.P. Moller-Maersk, CMA CGM, COSCO Shipping Lines, Hapag-Lloyd, ONE, Evergreen Marine, HMM, Yang Ming Marine Transport, ZIM.
        Columns must be: 선사 (Carrier) | 항해중인 선박 정책 (Policy for currently sailing vessels) | 신규 부킹 정책 (Policy for new bookings).
        
        ### Question 2: 리야드 공항 노선 운영 항공사 전쟁 관련 대응 조치
        Create a Markdown Table for the following airlines: 사우디아항공 (Saudia), 아랍에미레이트 항공 (Emirates), 에티하드 항공 (Etihad), 카타르항공 (Qatar Airways), 케세이퍼시픽 (Cathay Pacific), 동방항공 (China Eastern), 에어차이나 (Air China).
        Columns must be: 항공사 (Airline) | 운항 여부 (Operating Status) | 운항 중단 시 언제까지인지 (Suspension Period if applicable).
        
        ### Question 3: 주변국 주요 항구 현재 상황 및 포트 당국 공지 사항
        Create a Markdown Table for the following ports categorized by country.
        Columns must be: 국가 (Country) | 항구명 (Port Name) | 현재 상황 및 공지사항 (Current Situation & Port Authority Notices).
        - Saudi Arabia: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
        - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah Port, Ras Al Khaimah (Rak Port), Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
        - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
        
        ### Question 4: 친이란 및 친미 매체들의 전쟁 상황 속보 (아랍 언론사 중심)
        Provide a bulleted list of the latest breaking news regarding the actual war/military situation.
        For each news item, you MUST include: 
        1) 기사 제목 (Headline) 
        2) 내용 요약 (Summary)
        3) 언론사 및 성향 (Media Source & Bias - e.g., 친이란/Pro-Iran or 친미/Pro-US)
        4) 기사 링크 URL (Link to the article).
        """
        
        # 구글 검색 권한 부여
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ API 검색 중 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">실시간 물류/전황 딥 서치 엔진</p></div>', unsafe_allow_html=True)

# 매니저님의 질문 리스트를 화면에 그대로 표시
st.markdown("""
### 📋 검색 지시 사항 (Target Questions)
1. **해운**: 호르무즈 해협 위험 증가에 따른 사우디향 선박 (항해 중 / 신규 부킹) 선사별(10개사) 정책
2. **항공**: 리야드 공항 노선 운영 항공사(7개사) 운항 여부 및 중단 기한
3. **항만**: 사우디(6개), UAE(10개), 오만(5개) 주요 항구 현재 상황 및 당국 공지
4. **전황**: 친이란/친미 아랍 매체 중심 전쟁 상황 속보 (제목, 링크, 성향 포함)
""")
st.write("")

# 💡 단 하나의 직관적인 실행 버튼
if st.button("🚀 위 4가지 질문으로 구글 딥 서치(Deep Search) 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다. Streamlit Secrets를 확인하세요.")
    else:
        with st.spinner("AI가 매니저님의 4가지 상세 질문을 바탕으로 전 세계 웹을 실시간으로 검색하여 답변을 작성 중입니다... (약 15~20초 소요)"):
            answer = ask_ai_search(API_KEY, is_ko)
            
        st.markdown("---")
        st.markdown(answer)
