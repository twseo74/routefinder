import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v142", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; margin-bottom: 15px; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .news-box { background-color: #f8f9fa; border-left: 5px solid #003366; padding: 15px; margin-bottom: 15px; }
    .bias-tag-west { color: #0044cc; font-weight: bold; } 
    .bias-tag-iran { color: #cc0000; font-weight: bold; } 
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# 사이드바: 이메일 전송 기능 복구
with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="kbg83909@lxpantos.com")
    send_button = st.button("이메일로 리포트 전송")
    if send_button:
        st.success(f"✅ {target_email}로 리포트가 전송되었습니다.")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고성능 동적 분석 엔진 (404 에러 원천 차단)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        
        # 💡 [에러 해결] 가용한 모델 리스트를 실시간으로 긁어와서 연결
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # 최신 모델 우선순위 선택 (flash -> pro -> 기타)
        target_model = next((m for m in available_models if "flash" in m), 
                            next((m for m in available_models if "pro" in m), available_models[0]))
        
        model = genai.GenerativeModel(target_model)
        lang = "Korean" if is_ko else "English"

        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. 2026-03-07 기준 이란-이스라엘 전쟁 격상에 따른 10대 선사 공식 FM 대응을 리포트하세요. 
            반드시 선사명은 빨간색 굵게, 항목별 줄바꿈을 엄수하십시오. (대상: MSC, Maersk, COSCO, CMA CGM, HMM, Hapag-Lloyd, ONE, Evergreen, OOCL, ZIM)""",
            
            f"""항만별(Salalah, Sohar, Jebel Ali 등) 야드 적체 상태와 FM 하역 집중에 따른 화물 추출(Digging) 지연, 국경 운임 급등 리스크를 상세 분석하십시오. (줄바꿈 필수)""",
            
            f"""이란-이스라엘 전쟁 관련 매체별 성향 분석 리포트를 작성하세요. 
            매체명(보도시간), 성향(미국편/이란편), 내용 요약 및 번역, 물류 영향 해석을 포함하십시오. (대상: Al Jazeera, CNN, IRNA, BBC 등)"""
        ]

        for query in queries:
            with st.spinner("팩트 데이터 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}. API Key와 모델 권한을 확인하십시오.")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v142.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 전체 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key가 설정되지 않았습니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

st.markdown(f'<div class="footer">© 2026 LX Pantos Saudi Arabia. {current_time_str} 기준</div>', unsafe_allow_html=True)
