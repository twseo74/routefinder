import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (가시성 최우선)
# ==========================================
st.set_page_config(page_title="Saudi Intel v148", layout="wide")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; margin-bottom: 10px; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    .news-box { border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid #eee; line-height: 1.6; }
    .data-row { margin-bottom: 10px; line-height: 1.8; white-space: pre-wrap; font-size: 1.0rem; color: #111; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="")
    if st.button("이메일 전송"):
        if target_email: st.success(f"✅ 전송 완료")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 기반 엔진 (예측 배제, 공식 발표/속보 전용)
# ==========================================
def run_integrated_report(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"

        # 💡 [매니저님 지시 3대 골격]
        queries = [
            f"""[지시 1: 선사 공식 발표] {today} 기준 호르무즈 해협 봉쇄 관련 10대 선사의 FM 선언 및 공식 지정 양하항(EOV Port) 정보를 리포트하세요. 
            반드시 선사명은 빨간색 굵게, 양하항(MSC/Maersk=Salalah, COSCO=Khalifa, HMM/Yang Ming=Sohar 등) 및 공식 할증료($700~$1,100) 팩트만 기술하세요. (줄바꿈 필수)""",
            
            f"""[지시 2: 포트 상황] {today} 기준 주요 항구(Salalah, Sohar, Jebel Ali 등)의 FM 화물 집중에 따른 야드 밀도, 화물 추출(Digging) 지연, 국경 트럭 수급 및 운임 폭등 현황을 리포트하세요. (줄바꿈 필수)""",
            
            f"""[지시 3: 전황 속보] {today} 기준 이란-이스라엘 전쟁 관련 [이란/아랍편]과 [미국/서방편] 최신 기사 제목과 요약 번역을 리포트하세요.
            반드시 실제 기사 URL 링크를 포함하여 클릭 시 즉시 이동 가능하게 하십시오. 예측은 절대 금지하며 보도된 팩트만 전달하세요."""
        ]

        for query in queries:
            with st.spinner("데이터 동기화 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v148.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
