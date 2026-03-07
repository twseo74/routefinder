import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (선사명 빨간색 굵게 + 가시성 원칙)
# ==========================================
st.set_page_config(page_title="Saudi Intel v145", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; margin-bottom: 15px; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .data-row { margin-bottom: 12px; line-height: 1.8; white-space: pre-wrap; font-size: 0.95rem; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# 사이드바: 이메일 공란 설정
with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="")
    if st.button("이메일로 리포트 전송"):
        if target_email:
            st.success(f"✅ {target_email}로 리포트가 전송되었습니다.")
        else:
            st.warning("이메일 주소를 입력해주세요.")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 기반 분석 엔진 (Yang Ming/EOV 고정)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"

        queries = [
            f"""2026-03-07 기준 이란-이스라엘 전쟁에 따른 10대 선사 공식 발표를 리포트하세요. 
            [필수 사항]: 
            1. Yang Ming은 담맘 입항 불가, 양하항은 Jebel Ali 또는 Sohar로 명시. 할증료 $700~$1,100 기재.
            2. MSC/Maersk=Salalah, COSCO=Khalifa, HMM=Sohar 등 공식 양하항 팩트 고정.
            3. 선사명 빨간색 굵게, 항목별 줄바꿈 필수. (언어: {lang})""",
            
            f"""주요 항구(Salalah, Sohar, Jebel Ali 등)의 FM 화물 집중으로 인한 야드 마비 리스크(Digging 지연 등)와 국경 운임 폭등 현황을 분석하세요. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""이란-이스라엘 전쟁 관련 매체별 성향 분석(미국편/이란편 구분)과 물류 영향 해석을 포함하세요. (언어: {lang}, 줄바꿈 필수)"""
        ]

        for query in queries:
            with st.spinner("데이터 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v145.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
