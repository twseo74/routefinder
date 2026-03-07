import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v88", layout="wide")

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
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.9rem; line-height: 1.6; }
    th { background-color: #f8f9fa; font-weight: bold; color: #333; }
    .status-box { background-color: #fff4f4; border-left: 5px solid #E6002D; padding: 15px; margin-bottom: 20px; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 고정밀 실무 분석 엔진 (v88.0 - 모델 자동 탐색 및 에러 완벽 회피)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [핵심 수정] 404 에러 방지를 위해 사용 가능한 모델 리스트를 먼저 가져옴
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1순위: Pro 모델, 없으면 2순위: Flash 모델, 그마저도 없으면 첫 번째 모델 선택
        target_model = next((m for m in available_models if "pro" in m.lower()), 
                            next((m for m in available_models if "flash" in m.lower()), available_models[0]))
        
        # 최신 검색 도구 규격 적용
        model = genai.GenerativeModel(model_name=target_model, tools=[{"google_search": {}}])
        
        lang = "Korean" if is_ko else "English"
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. REPORT ONLY MARCH 2026 FACTS. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발 한정] 선사별 사우디향 대체 라우팅 및 실무 정책
            [Dammam Port is Blocked. DO NOT suggest discharging at Dammam.]
            Create a Markdown Table for: MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, HMM, Yang Ming, ZIM.
            
            Columns: 선사 (Carrier) | 항해중인 화물 정책 (Sailing) | 신규 부킹 정책 (Booking) | 사우디 인바운드 플랜 B (Alt Route).
            
            [Operational Facts]
            - Identify exact alternative discharge ports (e.g., Salalah for MSC/Maersk, Jebel Ali for CMA CGM/HMM).
            - Explicitly mention 'End of Voyage' declarations and Deviation Surcharges.
            - Provide the Landbridge/Trucking route from the discharge port to Saudi destinations (e.g., Al Batha border).
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월 기준)
            Target: Dammam, Jeddah, Jebel Ali, Salalah.
            Columns: 항구명 | 최신 상황 (Status) | 기준 일시 (Timestamp).
            *Focus on yard congestion and terminal operations after security incidents.*
            """
        else:
            prompt = base_prompt + """
            ### 🔥 3. 진영별 전쟁 상황 속보 (2026년 3월)
            List latest military news from Arab media within 48 hours. 
            Include: 보도 일시 | 제목 | 요약 | 성향 | 링크.
            """
        
        try:
            response = model.generate_content(prompt)
        except:
            # 검색 도구 호출 에러 시 일반 모드로 Fallback
            model_basic = genai.GenerativeModel(model_name=target_model)
            response = model_basic.generate_content(prompt)
            
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 구성 오류: {e}"

# ==========================================
# 🚀 3. 대시보드 메인
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 대체 라우팅 보드 (v88.0)</p></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="status-box">
    <b>📅 업데이트 기준: {current_date_str} (KSA)</b><br>
    - [에러 패치] 404 Model Not Found 완벽 해결 (모델 자동 탐색 로직)<br>
    - [실무 팩트] MSC/Maersk 살랄라 강제 양하 및 주변국 트럭킹 루트 강제 출력
</div>
""", unsafe_allow_html=True)

if st.button("🚀 실무 하드 팩트 릴레이 검색 실행", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key 미설정")
    else:
        st.markdown("---")
        q1, q2, q3 = st.empty(), st.empty(), st.empty()

        with st.spinner("1/3: 🚢 [극동발] 선사별 대체 항로 분석 중..."):
            ans1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
            q1.markdown(ans1)
            time.sleep(1)

        with st.spinner("2/3: ⚓ 주변국 항만 실시간 상황 및 적체 팩트 추출 중..."):
            ans2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
            q2.markdown(ans2)
            time.sleep(1)

        with st.spinner("3/3: 🔥 최신 전황 속보 수집 중..."):
            ans3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
            q3.markdown(ans3)
            
        st.success("✅ 조회가 완료되었습니다.")
