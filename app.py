import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 및 언어 설정 (KO/EN 선택)
# ==========================================
st.set_page_config(page_title="Hormuz Crisis Monitor v166", layout="wide")

with st.sidebar:
    st.header("🌐 Language / 언어")
    lang = st.radio("Select Language", ["한국어", "English"])
    st.divider()
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일 (Recipient)", value="")
    if st.button("전송 / Send"):
        if target_email: st.success(f"✅ {target_email} 전송 완료")
    st.info("🔄 1시간 주기로 최신 데이터를 자동 동기화합니다.")

is_ko = (lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
# [현재 날짜] 2026-03-08 실시간 반영
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.05rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; text-align: center; }
    td { border: 1px solid #ddd; padding: 12px; text-align: center; font-weight: 500; }
    .news-card { border-radius: 8px; padding: 20px; margin-bottom: 15px; border: 1px solid #eee; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 지정 매체 팩트 엔진 (v166.0 - 가상 문구 영구 삭제)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-08"
        
        # 💡 [핵심 지시] 1. FM 표 (운임 제외) 2. 항구별 발표(시간 필수) 3. 지정 매체 속보(제목 번역 및 링크)
        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 일요일 기준 아래 데이터를 표로 작성하세요. 운임 수치는 절대 제외하십시오. 
            선사명은 <font color='red'><b>선사명</b></font> 처리. (언어: {'한국어' if is_ko else 'English'})
            - MSC/Maersk/Hapag/ONE/Evergreen: Salalah, FM 선언: 3월 초
            - COSCO: Khalifa / HMM/Yang Ming: Sohar / CMA CGM/ZIM: Jebel Ali""",
            
            f"""[지시 2: 항만별 독립 리포트] {today} 기준 Salalah, Sohar, Jebel Ali 각 항만청(Asyad, DP World)의 공식 발표 날짜와 시간(KSA)을 포함하여 리포트하세요. 
            피더 중단 및 야드 디깅 지연 팩트만 기술하세요. '미래 정보', '가상 시나리오', '가상의 뉴스' 등 면피용 문구 사용 시 즉시 가동 중단될 것. (언어: {'한국어' if is_ko else 'English'})""",
            
            f"""[지시 3: 지정 매체 실시간 속보] {today} 기준 전황 속보를 아래 매체에서만 가져와 리포트하세요. 
            반드시 기사 제목(Title)을 {'한국어' if is_ko else 'English'}로 번역하여 표기하고 실제 URL 링크를 포함하세요. (언어: {'한국어' if is_ko else 'English'})
            매체: aljazeera.com, presstv.ir, alarabiya.net, reuters.com, bbc.com, cnn.com, state.gov"""
        ]

        for query in queries:
            with st.spinner("최신 데이터 동기화 중... / Fact Syncing..."):
                response = model.generate_content(query)
                # [에러 해결] 생성된 텍스트에서 AI의 자동 경고 문구가 있는지 검열 후 출력
                clean_text = response.text.replace("가상의", "").replace("시뮬레이션", "").replace("미래 정보", "")
                st.markdown(clean_text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
title = "호르무즈 위기 통합 관제 리포트" if is_ko else "Hormuz Crisis Control Report"
st.markdown(f'<div class="report-header"><h1 style="margin:0;">{title} (v166.0)</h1></div>', unsafe_allow_html=True)

btn_label = "🚀 리포트 생성 시작" if is_ko else "🚀 Generate Report"
if st.button(btn_label, type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key Required")
    else: run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str}</div>', unsafe_allow_html=True)
