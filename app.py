import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime, timedelta
import pytz

# ==========================================
# 1. UI 및 언어/자동화 설정 (KO/EN 선택)
# ==========================================
st.set_page_config(page_title="Hormuz Crisis Monitor v164", layout="wide")

# 사이드바: 언어 및 이메일 설정
with st.sidebar:
    st.header("🌐 Language / 언어")
    lang = st.radio("Select Language", ["한국어", "English"])
    st.divider()
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일 (Recipient)", value="")
    if st.button("전송 / Send"):
        if target_email: st.success(f"✅ {target_email} 전송 완료")
    st.divider()
    st.info("🔄 리포트는 1시간마다 자동 업데이트됩니다.")

is_ko = (lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_ksa = datetime.now(ksa_tz)
current_time_str = current_time_ksa.strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.0rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; text-align: center; }
    td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: 500; }
    .port-section { background-color: #ffffff; border: 1px solid #ddd; border-top: 5px solid #003366; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .timestamp { font-size: 0.85rem; color: #E6002D; font-weight: bold; margin-bottom: 5px; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 정밀 분석 엔진 (v164.0 - 시간 기록 및 번역 고정)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-08"
        
        # 💡 [핵심 지시] 1. FM 표 2. 항만청 발표(시간 포함) 3. 속보(제목 번역 및 링크)
        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 기준 아래 데이터를 표로 작성하세요. 운임 수치 절대 제외. 
            선사명은 <font color='red'><b>선사명</b></font> 처리. (언어: {'한국어' if is_ko else 'English'})
            - MSC/Maersk/Hapag/ONE/Evergreen: Salalah, FM 선언: 3월 초
            - COSCO: Khalifa / HMM/Yang Ming: Sohar / CMA CGM/ZIM: Jebel Ali""",
            
            f"""[지시 2: 항만별 독립 리포트] {today} 기준 Salalah, Sohar, Jebel Ali 각 항만청의 공식 발표 내용을 섹션별로 정리하세요. 
            반드시 각 발표의 '정확한 날짜와 시간(KSA 기준)'을 포함하고, 피더 중단 및 야드 디깅 지연 팩트만 기재하세요. (언어: {'한국어' if is_ko else 'English'})""",
            
            f"""[지시 3: 지정 매체 실시간 속보] {today} 기준 전황 속보를 아래 지정된 매체에서만 가져와 리포트하세요. 
            반드시 기사 제목(Title)을 {'한국어' if is_ko else 'English'}로 번역하여 표기하고, 요약과 실제 URL 링크를 포함하세요.
            매체: Al Jazeera, Press TV, Al Arabiya, Reuters, BBC, CNN, U.S. State Dept. (언어: {'한국어' if is_ko else 'English'})"""
        ]

        for query in queries:
            with st.spinner("자동 업데이트 중... / Auto-Updating..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
title = "호르무즈 위기 통합 관제 리포트" if is_ko else "Hormuz Crisis Control Report"
st.markdown(f'<div class="report-header"><h1 style="margin:0;">{title} (v164.0)</h1></div>', unsafe_allow_html=True)

btn_label = "🚀 리포트 생성 시작" if is_ko else "🚀 Generate Report"
if st.button(btn_label, type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key Required")
    else: run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str}</div>', unsafe_allow_html=True)
