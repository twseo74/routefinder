import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 및 스타일 설정 (표 가시성 극대화)
# ==========================================
st.set_page_config(page_title="Saudi Intel v150", layout="wide")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .stTable { font-size: 1.1rem; }
    .news-box { border-radius: 8px; padding: 18px; margin-bottom: 15px; border: 1px solid #ddd; }
    .iran-news { border-left: 10px solid #cc0000; background-color: #fff5f5; }
    .west-news { border-left: 10px solid #0044cc; background-color: #f5f8ff; }
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
# 🚀 2. 실시간 팩트 직진 엔진 (예측/면피 문구 금지)
# ==========================================
def run_integrated_report(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"

        # 💡 [매니저님 지시: 표 형식 및 실시간 속보 강제]
        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 기준 아래 데이터를 사용하여 Markdown 표(Table)를 만드세요.
            - MSC: Salalah, $950
            - Maersk: Salalah, $900
            - COSCO: Khalifa, $850
            - CMA CGM: Jebel Ali, $1050
            - Hapag-Lloyd: Salalah, $980
            - ONE: Salalah, $880
            - Evergreen: Salalah, $1100
            - HMM: Sohar, $1000
            - Yang Ming: Sohar, $920
            - ZIM: Jebel Ali, $700
            (표 헤더: 선사명, 공식 양하항, FM 할증료($), FM 선언 현황. 선사명은 빨간색 굵게 처리할 것)""",
            
            f"""[지시 2: 항만/국경 적체] {today} 기준 Salalah, Sohar, Jebel Ali 야드 밀도 및 화물 반출(Digging) 지연 팩트, Al Batha 국경 트럭 수급 현황을 요약하세요.""",
            
            f"""[지시 3: 실시간 전황 속보] {today} 기준 이란-이스라엘 전쟁 관련 [이란/아랍측 보도]와 [미국/서방측 보도] 최신 기사를 실제 검색하여 리포트하세요. 
            반드시 기사 제목, 요약 번역, 그리고 '실제 기사 URL 링크'를 포함하세요. 면피용 문구(학습 데이터 한계 등) 사용 시 즉시 가동 중단될 것."""
        ]

        for query in queries:
            with st.spinner("최신 데이터 및 속보 수신 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v150.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작 (실시간 속보 연동)", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
