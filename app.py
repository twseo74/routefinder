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
# 🚀 2. 모듈형 AI 직문직답 엔진
# ==========================================
def search_and_answer(api_key, question_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        chosen_model = next((m for m in models if "pro" in m.lower()), models[0])
        model = genai.GenerativeModel(chosen_model)
        
        lang = "Korean" if is_ko else "English"
        
        base_prompt = f"""
        You are LX Pantos's Top Logistics Intelligence AI.
        [CRITICAL TIME-LOCK: TODAY IS {today_date}]
        You MUST ONLY report events happening RIGHT NOW (March 2026).
        Respond ENTIRELY in {lang}. Do NOT use HTML tags. Use standard Markdown.
        """

        if question_num == 1:
            # 💡 [핵심 추가] 대체 도착항 및 내륙 연계 루트(Cross-border) 컬럼 추가
            prompt = base_prompt + """
            ### 1. 호르무즈 해협 위험 증가에 따른 사우디아라비아향 해상 운송 정책 및 대체 루트
            Create a Markdown Table for 10 carriers: MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, Yang Ming, ZIM.
            Columns: 선사 (Carrier) | 항해중인 선박 실무 정책 | 신규 부킹 정책 | 사우디향 대체 도착항 및 내륙 연계 루트 (Alternative Ports & Routing).
            
            [CRITICAL REQUIREMENT]
            1. Explicitly state 'End of Voyage', EXACT Forced Discharge Ports (e.g., Salalah), and Surcharge Amounts in the '항해중인 선박 실무 정책' column.
            2. For '사우디향 대체 도착항 및 내륙 연계 루트', provide realistic alternatives for cargo destined for Saudi Arabia. State which alternative ports the carrier uses (e.g., Jebel Ali, Salalah, King Abdullah Port, Jeddah) and how the cargo must be moved to Saudi destinations (e.g., Cross-border trucking, Landbridge via Batha border). Do not leave this empty. If unknown, estimate based on industry standards.
            """
        elif question_num == 2:
            prompt = base_prompt + """
            ### 2. 주변국 주요 항구 심층 실무 브리핑 (2026년 3월 기준)
            DO NOT use a table for this section. Select the MOST CRITICALLY AFFECTED ports right now (specifically Dammam, Jebel Ali, and Salalah) and write a DEEP, DETAILED operational briefing for each.
            
            For EACH heavily affected port, use this EXACT structure:
            #### ⚓ [항구명, 국가] (e.g., Jebel Ali, UAE)
            * **최신 공지 일자:** (Must be March 2026)
            * **1. 공식 운영 상태 및 사건:** (Detail specific incidents like intercepted missiles, fires, terminal shutdowns, and resumptions.)
            * **2. 실무적 항만 적체 및 지연:** (Detail yard congestion, diverted cargo from Dammam, vessel delays.)
            * **3. 실무 대응 요약:** (Actionable advice for the forwarder, e.g., securing cross-border trucking.)
            
            After the detailed briefings, list the other normal ports under a heading "🟢 특이사항 없는 정상 운영 항만" separated by commas.
            """
        else:
            prompt = base_prompt + """
            ### 3. 친이란 및 친미 매체들의 전쟁 상황 속보 (2026년 3월 최신)
            Provide a bulleted list of the latest breaking military/war news. Include:
            1) 보도 일시
            2) 기사 제목
            3) 하드 팩트 요약
            4) 언론사 및 성향
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
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">실무 3대 지표 (대체 라우팅 솔루션 탑재)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 검색 타겟 질문 (3대 지표)</b><br>
    1. 담맘항 이용 불가에 따른 각 선사별(10개사) 정책 및 <b>사우디향 대체 도착항/내륙 연계 루트</b><br>
    2. 사우디, UAE, 오만의 주요 항구별 최신 심층 동향 (제벨알리 등 집중 타격 항만 중심)<br>
    3. 친이란 및 친미 매체들의 전쟁 상황 최신 속보 (보도 일시, 링크, 성향 포함)
</div>
""", unsafe_allow_html=True)

if st.button("🚀 위 3가지 질문으로 심층 실무 브리핑 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 설정되지 않았습니다.")
    else:
        st.markdown("---")
        q1_space, q2_space, q3_space = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 해운 선사별 정책 및 사우디 진입을 위한 '대체 항로/트럭킹 루트' 작성 중..."):
            ans1 = search_and_answer(API_KEY, 1, is_ko, current_date_str)
            q1_space.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 제벨알리/살랄라 등 핵심 타격 항만 심층 브리핑 작성 중..."):
            ans2 = search_and_answer(API_KEY, 2, is_ko, current_date_str)
            q2_space.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 진영별 전황 최신 속보 수집 중..."):
            ans3 = search_and_answer(API_KEY, 3, is_ko, current_date_str)
            q3_space.markdown(ans3)
            
        st.success(f"✅ 조회가 완료되었습니다. (기준 일시: {current_date_str})")
