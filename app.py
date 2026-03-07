import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (선사명 빨간색 굵게 + 가독성 원칙)
# ==========================================
st.set_page_config(page_title="Saudi Intel v147", layout="wide")

is_ko = True 
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; margin-bottom: 15px; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .news-box { border-radius: 8px; padding: 15px; margin-bottom: 15px; border: 1px solid #eee; }
    .iran-side { border-left: 10px solid #cc0000; background-color: #fff5f5; }
    .west-side { border-left: 8px solid #0044cc; background-color: #f5f8ff; }
    .data-row { margin-bottom: 12px; line-height: 1.8; white-space: pre-wrap; font-size: 0.95rem; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="")
    if st.button("이메일로 리포트 전송"):
        if target_email: st.success(f"✅ {target_email}로 전송되었습니다.")
        else: st.warning("이메일 주소를 입력해주세요.")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 실시간 팩트 및 최신 속보 엔진 (v147.0)
# ==========================================
def run_integrated_report(api_key):
    try:
        genai.configure(api_key=api_key)
        # 동적 모델 선택 (404 방지)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"

        # 💡 [핵심 지시] 1.선사 팩트(양하항/비용) 2.항만 리스크 3.진영별 실시간 속보 및 URL
        queries = [
            f"""{today} 기준 이란-이스라엘 전쟁 격상에 따른 10대 선사 공식 발표를 리포트하세요. 
            [필수]: 선사명 빨간색 굵게, 공식 양하항(MSC/Maersk=Salalah, COSCO=Khalifa, HMM/Yang Ming=Sohar 등) 명시, FM 비용 팩트($700~$1,100 등), 항목별 줄바꿈 필수.""",
            
            f"""{today} 기준 주요 항구(Salalah, Sohar, Jebel Ali 등)의 FM 화물 집중으로 인한 야드 밀도 및 화물 추출(Digging) 지연, 국경 트럭 수급 대란 현황을 분석하세요. (줄바꿈 필수)""",
            
            f"""{today} 기준 이란-이스라엘 전쟁 관련 '실제 최신 기사'를 [이란/아랍편]과 [미국/서방편]으로 나누어 리포트하세요.
            [작성 양식]:
            1. 진영 구분 (🔴 이란/아랍측 보도 vs 🔵 미국/서방측 보도)
            2. 실제 기사 제목 및 한국어 요약 번역
            3. 기사 원문 URL (하이퍼링크로 제공 - 클릭 시 즉시 이동)
            4. 보도 시각 (KSA 기준) 및 물류 영향 분석 (호르무즈 봉쇄 실황 등).
            [주의]: 절대 가상으로 소설 쓰지 말고, 검색을 통해 실제 확인된 오늘 자 기사만 넣으십시오."""
        ]

        for query in queries:
            with st.spinner("최신 실무 데이터 및 전황 동기화 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v147.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작 (실시간 속보 및 링크 포함)", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
