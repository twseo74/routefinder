import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃 (표 대신 카드 레이아웃 도입)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v129", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Report Export")
    target_email = st.text_input("수신자 이메일 입력", placeholder="example@lxpantos.com")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

# 💡 줄바꿈 문제를 원천 차단하기 위한 카드형 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 8px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .carrier-name { font-size: 1.2rem; font-weight: bold; color: #003366; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
    .data-item { margin-bottom: 12px; line-height: 1.6; }
    .data-label { font-weight: bold; color: #555; display: inline-block; width: 160px; }
    .data-value { display: inline-block; vertical-align: top; color: #333; }
    .fm-alert { color: #E6002D; font-weight: bold; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정 골격 분석 엔진 (v129.0 - 카드형 데이터 구조화)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 표가 아닌 '카드 섹션' 형태로 답변하도록 지시 (줄바꿈 강제)
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. 오늘({today}) 기준, 호르무즈 해협 봉쇄에 따른 10대 선사 정책을 아래 [카드 형식]으로 리포트하세요. 
            절대 표(Table) 형식을 사용하지 마세요.
            
            [형식 예시]:
            선사명: MSC
            • FM 및 양하지: FM 선언 완료 / 강제 양하(Salalah, Oman)
            • 부킹 정책: LTC 우선, Spot 중단, WRS 부과
            • 추가 비용: 재배송료(USD 1,200), 추가 THC(USD 350)
            
            이 형식으로 10대 선사를 분석하십시오. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 항만별(Salalah, Jeddah, Jebel Ali) 야드 적체 상태와 국경 통관 지연 요소를 리스트 형태로 작성하세요. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전황 속보를 요약 리포트하세요. (언어: {lang})"""
        ]

        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text) # Markdown 리스트로 깔끔하게 출력
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 이제 텍스트 뭉치 없이 모든 항목이 줄바꿈되어 나타납니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v129.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작 (가시성 완성판)", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 및 꼬리말
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 호르무즈 해협 위기 상황에 근거한 실물 데이터 분석 결과입니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
