import streamlit as st
import google.generativeai as genai

# ==========================================
# 1. 초기 설정 및 언어 선택
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
# 🚀 2. 직문직답 AI 검색 엔진
# ==========================================
def ask_ai_questions(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 가용 모델 탐색 (flash 모델 우선)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "flash" in m), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 매니저님의 4가지 질문을 AI에게 그대로 전달
        prompt = f"""
        You are a logistics intelligence assistant. Use your Google Search capabilities to find the most recent facts regarding the Middle East crisis.
        Respond ENTIRELY in {lang}.
        
        Answer the following 4 questions directly and specifically. Use the questions as headers.
        If you cannot find specific operational facts, state that clearly instead of giving vague generic answers.
        
        1. 담맘항 이용 불가에 따른 각 선사별 해상 선박, 신규 부킹관련 정책 뉴스 (News on shipping lines' vessel and new booking policies due to Dammam port unavailability)
        2. 리야드공항과의 노선을 운영중인 항공사들의 전쟁관련 대응 조치 (Airlines' war-related countermeasures operating routes to Riyadh airport)
        3. 사우디, UAE, 오만의 주요 항구별 최신 뉴스 (Latest news by major ports in Saudi Arabia, UAE, and Oman)
        4. 친이란 및 친미 매체들의 전쟁 상황 뉴스 (아랍 뉴스 중심으로) (War situation news from pro-Iran and pro-US media, focusing on Arab news)
        """
        
        # 구글 검색 권한 부여 시도
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt) # SDK 버전 충돌 시 기본 검색으로 폴백
            
        return response.text
    except Exception as e:
        return f"⚠️ 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1></div>', unsafe_allow_html=True)

st.markdown("### 📋 물류/전황 핵심 4대 질문 검색")
st.write("1. 담맘항 이용 불가에 따른 각 선사별 해상 선박, 신규 부킹관련 정책 뉴스")
st.write("2. 리야드공항과의 노선을 운영중인 항공사들의 전쟁관련 대응 조치")
st.write("3. 사우디, UAE, 오만의 주요 항구별 최신 뉴스")
st.write("4. 친이란 및 친미 매체들의 전쟁 상황 뉴스 (아랍 뉴스 중심으로)")
st.write("")

# 💡 유일한 동작 버튼
if st.button("🚀 위 4가지 질문으로 최신 뉴스 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        with st.spinner("AI가 위 4가지 질문에 대한 최신 답변을 검색하여 정리 중입니다... (약 10~15초 소요)"):
            answer = ask_ai_questions(API_KEY, is_ko)
            
        st.markdown("---")
        st.markdown(answer)
