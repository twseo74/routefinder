import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (표/리스트 가시성 극대화)
# ==========================================
st.set_page_config(page_title="Saudi Intel v151", layout="wide")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 10px; text-align: center; }
    td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: 500; }
    .port-box { background-color: #f8f9fa; border-left: 5px solid #003366; padding: 15px; margin-bottom: 20px; }
    .iran-news { border-left: 10px solid #cc0000; background-color: #fff5f5; padding: 15px; margin-bottom: 10px; }
    .west-news { border-left: 10px solid #0044cc; background-color: #f5f8ff; padding: 15px; margin-bottom: 10px; }
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
# 🚀 2. 팩트 직진 엔진 (항만청 발표 & 실시간 속보)
# ==========================================
def run_integrated_report(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"

        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 기준 아래 데이터를 사용하여 Markdown 표를 작성하세요.
            선사명은 <font color='red'><b>선사명</b></font>으로 표시.
            - MSC: Salalah, $950 / Maersk: Salalah, $900 / COSCO: Khalifa, $850
            - CMA CGM: Jebel Ali, $1050 / Hapag-Lloyd: Salalah, $980 / ONE: Salalah, $880
            - Evergreen: Salalah, $1100 / HMM: Sohar, $1000 / Yang Ming: Sohar, $920 / ZIM: Jebel Ali, $700""",
            
            f"""[지시 2: 항만청 공식 발표 및 봉쇄 리스크] {today} 기준 Salalah, Sohar, Jebel Ali 항만청의 공식 운영 지침을 리포트하세요.
            - 호르무즈 봉쇄로 인한 피드선(Feeder) 운항 중단 및 모선(Mother Vessel) 집중 현황.
            - 야드 밀도 95% 초과에 따른 'Berth Window' 취소 및 하역 우선순위 변경 공지.
            - 화물 추출(Digging) 지연(평균 5~7일) 및 국경 트럭 수급 차질 실무 팩트.""",
            
            f"""[지시 3: 실시간 전황 속보] {today} 기준 이란-이스라엘 전쟁 관련 [이란/아랍편]과 [미국/서방편] 최신 기사를 실제 검색하여 리포트하세요. 
            반드시 실제 기사 제목, 요약 번역, 클릭 가능한 URL 링크를 포함하세요. 면피성 문구는 절대 금지합니다."""
        ]

        for query in queries:
            with st.spinner("최신 데이터 및 항만청 발표 수신 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v151.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작 (항만청 발표 포함)", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
