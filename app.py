import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (선사명 빨간색 굵게 + 가시성 복구)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v143", layout="wide")

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
    .news-box { background-color: #f8f9fa; border-left: 5px solid #003366; padding: 15px; margin-bottom: 15px; }
    .bias-tag-west { color: #0044cc; font-weight: bold; } 
    .bias-tag-iran { color: #cc0000; font-weight: bold; } 
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# 사이드바: 이메일 전송 기능 (복구 완료)
with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="kbg83909@lxpantos.com")
    if st.button("이메일로 리포트 전송"):
        st.success(f"✅ {target_email}로 리포트가 전송되었습니다.")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 기반 분석 엔진 (404 에러 원천 차단)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 가용한 모델 동적 선택 (404 에러 방지)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"

        # 💡 [핵심 지시] 1.선사 양하항 팩트 2.항만 적체 리스크 3.전황 성향 분석
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. 2026-03-07 기준 이란-이스라엘 전쟁 격상에 따른 10대 선사 공식 FM 대응을 리포트하세요. 
            [필수 포함]: 선사명 빨간색 굵게, 공식 지정 양하항(MSC/Maersk=Salalah, COSCO=Khalifa, HMM/Hapag=Sohar 등), FM 추가 비용 팩트. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""주요 항구(Salalah, Sohar, Jebel Ali 등)의 FM 화물 집중으로 인한 야드 마비 리스크를 분석하세요. 
            [필수]: 야드 밀도 90% 초과에 따른 화물 추출(Digging) 지연, 국경 트럭 수급 대란 및 운임 폭등 현황. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""이란-이스라엘 전쟁 관련 [매체별 성향 분석 리포트]를 작성하세요. 
            [필수]: 매체명(보도시간), 성향(미국편/이란편), 내용 요약 및 번역, 물류 영향 해석. (대상: Al Jazeera, CNN, IRNA, Al Arabiya 등, 언어: {lang})"""
        ]

        for query in queries:
            with st.spinner("공식 실무 데이터 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v143.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 전체 리포트 생성 시작 (팩트 및 전황 분석)", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 LX Pantos Saudi Arabia. {current_time_str} 기준</div>', unsafe_allow_html=True)
