import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
is_ko = (st.session_state.lang == "한국어")

ksa_tz = pytz.timezone('Asia/Riyadh')
# 💡 [핵심] 오늘 날짜를 AI에게 주입하기 위해 변수 생성
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.9rem; line-height: 1.6; }
    th { background-color: #f2f2f2; font-weight: bold; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 모듈형 AI 직문직답 엔진 (타임락 강제)
# ==========================================
def search_and_answer(api_key, question_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "pro" in m.lower()), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        # 💡 [핵심] 프롬프트 최상단에 현재 날짜를 박아넣고, 과거 데이터 사용을 엄격히 금지
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI.
        [CRITICAL TIME-LOCK: TODAY IS {today_date}]
        You MUST ONLY search for and report events happening RIGHT NOW (March 2026).
        ABSOLUTELY DO NOT output any news, notices, or data from 2024 or 2025. 
        If you only find old news for a specific port or carrier, you MUST write "2026년 3월 기준 최근 특이동향 검색 안됨" (No recent 2026 updates found).
        
        Respond ENTIRELY in {lang}. 
        ALWAYS insert a blank newline before starting a Markdown table. Do NOT use HTML tags.
        """

        if question_num == 1:
            prompt = base_prompt + """
            ### 1. 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책
            Create a Markdown Table for these 10 carriers ONLY: MSC, A.P. Moller-Maersk, CMA CGM, COSCO Shipping Lines, Hapag-Lloyd, ONE, Evergreen Marine, HMM, Yang Ming Marine Transport, ZIM.
            Columns: 선사 (Carrier) | 항해중인 선박 실무 정책 (Sailing vessels policy) | 신규 부킹 정책 (New bookings policy).
            
            Explicitly state 'End of Voyage' declarations, EXACT Forced Discharge Ports (e.g., Jebel Ali, Salalah), and Surcharge Amounts.
            """
        elif question_num == 2:
            prompt = base_prompt + """
            ### 2. 주변국 주요 항구 현재 상황 및 포트 당국 공지 사항 (2026년 3월 기준)
            Create a Markdown Table for ports categorized by country:
            - Saudi Arabia: Dammam, Jeddah, Jubail, King Abdullah Port, Neom, Riyadh
            - UAE: Jebel Ali, Khalifa Port, Mina Rashid, Fujairah, Hamriyah Port, Ras Al Khaimah (Rak Port), Ajman, Mina Zayed, Mina Saeed, Umm al Quwain
            - Oman: Salalah, Sohar, Mina Qaboos, Muscat, Qalhat
            Columns: 국가 (Country) | 항구명 (Port Name) | 최신 공지 일자 (Exact Date/Time - MUST BE IN 2026) | 2026년 3월 현재 상황 (Current 2026 Situation).
            
            Focus on recent missile intercepts, terminal suspensions, forced discharge cargo congestion. DO NOT MENTION 2024 events.
            """
        else:
            prompt = base_prompt + """
            ### 3. 친이란 및 친미 매체들의 전쟁 상황 속보 (아랍 언론사 중심, 2026년 3월 최신)
            Provide a bulleted list of the latest breaking military/war news from the last 48 hours.
            
            For each news item, you MUST include:
            1) 2026년 보도 일시 (Exact 2026 Date & Time)
            2) 기사 제목
            3) 하드 팩트 요약
            4) 언론사 및 성향 (친이란/친미)
            5) 링크 URL.
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
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">실무 3대 지표 릴레이 검색 보드 (Time-Lock 적용)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 검색 타겟 질문 (3대 지표)</b><br>
    1. 담맘항 이용 불가에 따른 각 선사별(10개사) 해상 선박, 신규 부킹 정책 뉴스<br>
    2. 사우디, UAE, 오만의 주요 항구별 최신 뉴스 및 당국 공지 (기준 일시 포함)<br>
    3. 친이란 및 친미 매체들의 전쟁 상황 최신 속보 (보도 일시, 링크, 성향 포함)
</div>
""", unsafe_allow_html=True)

if st.button("🚀 위 3가지 질문으로 실무 검색 실행 (2026년 최신 팩트 강제)", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 해운 선사별 강제 양하 항구 및 서차지 팩트 (2026년 최신) 추출 중..."):
            ans1 = search_and_answer(API_KEY, 1, is_ko, current_date_str)
            q1_space.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주변국 항만 실시간 상황 (2024년 배제, 2026년 피격/적체 팩트) 추출 중..."):
            ans2 = search_and_answer(API_KEY, 2, is_ko, current_date_str)
            q2_space.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 진영별 전황 최신 속보 (최근 48시간 내 보도) 수집 중..."):
            ans3 = search_and_answer(API_KEY, 3, is_ko, current_date_str)
            q3_space.markdown(ans3)
            
        st.success(f"✅ 조회가 완료되었습니다. (기준 일시: {current_date_str})")
