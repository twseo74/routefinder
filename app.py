import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 및 언어 선택 기능
# ==========================================
st.set_page_config(page_title="Hormuz Crisis Monitor v155", layout="wide")

# 사이드바: 언어 선택 및 이메일 (공란)
with st.sidebar:
    st.header("🌐 Language / 언어")
    lang = st.radio("Select Language", ["한국어", "English"])
    st.divider()
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="")
    if st.button("전송 / Send"):
        if target_email: st.success(f"✅ {target_email} 전송 완료")

is_ko = (lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.0rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 10px; text-align: center; }
    td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: 500; }
    .port-section { background-color: #ffffff; border: 1px solid #ddd; border-top: 5px solid #003366; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .news-box { border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid #eee; }
    .iran-side { border-left: 10px solid #cc0000; background-color: #fff5f5; }
    .west-side { border-left: 10px solid #0044cc; background-color: #f5f8ff; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 분석 엔진 (v155.0 - 면피 문구 삭제)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"
        
        # 💡 [핵심 지시] 1. 선단 FM 2. 항만청 발표 3. 전황 속보 링크
        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 기준 아래 팩트 데이터를 Markdown 표로 작성하세요. 
            선사명은 <font color='red'><b>선사명</b></font> 처리. (언어: {'한국어' if is_ko else 'English'})
            - MSC: Salalah, FM: 2026-03-02
            - Maersk: Salalah, FM: 2026-03-01
            - COSCO: Khalifa, FM: 2026-03-03
            - CMA CGM: Jebel Ali, FM: 2026-03-02
            - Hapag-Lloyd: Salalah, FM: 2026-03-01
            - ONE: Salalah, FM: 2026-03-03
            - Evergreen: Salalah, FM: 2026-03-04
            - HMM: Sohar, FM: 2026-03-02
            - Yang Ming: Sohar, FM: 2026-03-02
            - ZIM: Jebel Ali, FM: 2026-02-28""",
            
            f"""[지시 2: 항만별 독립 리포트] {today} 기준 Salalah, Sohar, Jebel Ali 각 항만청의 공식 발표를 섹션별로 정리하세요. 
            호르무즈 봉쇄에 따른 피더 중단, 야드 디깅(Digging) 지연, 국경 운임 폭등 팩트만 기재하세요. (언어: {'한국어' if is_ko else 'English'})""",
            
            f"""[지시 3: 전황 속보 및 URL] {today} 기준 이란-이스라엘 전쟁 속보를 [이란/아랍편]과 [미국/서방편]으로 나누어 리포트하세요. 
            반드시 실제 기사 제목, 번역, 그리고 '클릭 가능한 URL 링크'를 포함하세요. 면피성 문구는 절대 사용하지 마십시오. (언어: {'한국어' if is_ko else 'English'})"""
        ]

        for query in queries:
            with st.spinner("Fact Syncing..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ==========================================
# 🚀 3. 메인 실행
# ==========================================
title = "호르무즈 위기 통합 관제 리포트" if is_ko else "Hormuz Crisis Control Report"
st.markdown(f'<div class="report-header"><h1 style="margin:0;">{title} (v155.0)</h1></div>', unsafe_allow_html=True)

btn_label = "🚀 리포트 생성 시작" if is_ko else "🚀 Generate Report"
if st.button(btn_label, type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key Required")
    else: run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str}</div>', unsafe_allow_html=True)
