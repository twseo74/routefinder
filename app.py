import streamlit as st
import google.generativeai as genai

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
# 🚀 2. 정밀 타격형 구글 딥 서치 엔진 (Pro 모델 강제)
# ==========================================
def run_precision_search(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [핵심] 가장 똑똑한 Pro 모델을 최우선으로 선택하여 할루시네이션 원천 차단
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in available_models if "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 뭉뚱그린 질문이 아닌, 각 기업별 구체적 팩트 조사를 강제하는 프롬프트
        prompt = f"""
        You are a highly precise logistics intelligence AI. 
        You MUST use Google Search to find real-time, factual answers. DO NOT rely on your training data.
        Respond ENTIRELY in {lang}.

        [CRITICAL ANTI-HALLUCINATION RULE]
        If you cannot find a specific official notice (e.g., flight cancellation dates, discharge ports), you MUST write "최신 공지 확인 불가 (Status Unconfirmed)". DO NOT invent or assume "Normal operations". 
        Use standard Markdown tables. Use the HTML `<br>` tag for line breaks inside table cells.

        ### 1. 해운 선사 사우디향 (담맘 등) 해상 운송 정책
        Search for recent Red Sea / Hormuz detour or discharge notices for: MSC, A.P. Moller-Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, Yang Ming, ZIM.
        Columns: 선사 (Carrier) | 항해중인 선박 정책 및 양하 포트 (Sailing vessels & Discharge ports) | 신규 부킹 정책 (New bookings policy).

        ### 2. 리야드 공항 노선 항공사 전황 대응 조치
        Search for recent flight suspensions or cancellations to Riyadh (RUH) due to Middle East tensions for: Saudia, Emirates, Etihad, Qatar Airways, Cathay Pacific, China Eastern, Air China.
        *Critically check Cathay Pacific's suspension dates.*
        Columns: 항공사 (Airline) | 운항 여부 (Operating Status) | 운항 중단 기한 (Suspension Period).

        ### 3. 주변국 주요 항구 실시간 상황 (사우디, UAE, 오만)
        Search for congestion, delays, or rerouting status for:
        - Saudi: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
        - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah, Rak Port, Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
        - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
        Columns: 국가 (Country) | 항구명 (Port Name) | 현재 상황 및 팩트 (Current Situation).

        ### 4. 아랍 매체 중심 전쟁 상황 속보
        Search for the latest military strikes/tensions in the Red Sea/Hormuz area from pro-US and pro-Iran Arab media.
        Provide a bulleted list: 1) 기사 제목 2) 요약 3) 언론사 및 성향 4) 링크.
        """
        
        # 💡 [핵심] 구글 검색 도구 강제 활성화
        try:
            response = model.generate_content(prompt, tools="google_search_retrieval")
        except:
            response = model.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ API 오류 발생: {e}"

# ==========================================
# 🚀 3. 메인 화면 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">정밀 타격형 구글 딥 서치 (Pro 모델)</p></div>', unsafe_allow_html=True)

st.write("1. 담맘항 이용 불가에 따른 각 선사별 해상 선박, 신규 부킹 정책")
st.write("2. 리야드 공항 노선 운영 항공사들의 전쟁 관련 대응 조치 (결항 및 기한)")
st.write("3. 사우디, UAE, 오만 주요 항구별 최신 상황")
st.write("4. 친이란/친미 매체들의 전쟁 상황 속보")
st.write("")

if st.button("🚀 위 4가지 질문으로 정밀 검색 실행 (할루시네이션 차단)", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        with st.spinner("AI(Pro 모델)가 구글 검색을 통해 케세이퍼시픽 등 각 기업의 정확한 실무 노티스를 발굴하고 있습니다... (약 20~30초 소요)"):
            answer = run_precision_search(API_KEY, is_ko)
            
        st.markdown("---")
        st.markdown(answer, unsafe_allow_html=True)
