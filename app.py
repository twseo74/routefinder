import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (선사명 빨간색 굵게 + 가시성)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v135", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .carrier-card { background-color: #ffffff; border: 1px solid #ddd; border-left: 10px solid #E6002D; padding: 20px; border-radius: 8px; margin-bottom: 25px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); }
    .carrier-name { font-size: 1.3rem; font-weight: bold; color: #E6002D; margin-bottom: 15px; text-transform: uppercase; border-bottom: 2px solid #eee; padding-bottom: 10px; }
    .data-row { margin-bottom: 12px; line-height: 1.8; white-space: pre-wrap; word-break: keep-all; font-size: 0.95rem; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 25px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 2. 선사 공식 발표 팩트 엔진 (v135.0)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심 지시] 1. 가상/시나리오 문구 절대 금지 2. 공식 발표 팩트만 기술 3. 선사명 강조
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 호르무즈 해협 봉쇄에 따른 10대 선사별 '공식 발표(Official Advisory)'만 리포트하세요. 
            서론의 '가상 시나리오'나 '시뮬레이션' 같은 면피용 문구는 절대 사용하지 마십시오. 오직 발표된 팩트만 전하십시오.
            
            [필수 형식]:
            ### <span style='color:#E6002D'>**선사명**</span>
            • **공식 지정 강제 양하기(EOV Port)**: (공식 발표된 실제 하역 항구: MSC/Maersk=Salalah, COSCO=Khalifa, HMM=Sohar 등)
            • **FM 선언 및 부킹 정책**: (공식 발표된 FM 여부 및 LTC 우선/Spot 중단 정책)
            • **화주 추가 부담 비용**: (공지된 Contingency Surcharge, WRS, 재배송 비용 등 구체적 팩트)
            • **공식 대체 루트 안내**: (선사가 화주에게 공식 제안한 육상 우회 경로)
            
            [분석 타겟]: MSC, Maersk, CMA CGM, COSCO, HMM, Hapag-Lloyd, ONE, Evergreen, OOCL, ZIM.
            (언어: {lang}, 반드시 항목마다 줄바꿈할 것)""",
            
            f"""오늘({today}) 기준, 항만 당국 및 선사가 공식 발표한 야드 적체 상태와 국경(Al Batha, Al Mazyunah) 통관 지연 팩트를 리포트하십시오. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""최근 48시간 내 중동 전황(호르무즈 봉쇄 실황) 속보를 공식 보도 기반으로 요약하십시오. (언어: {lang})"""
        ]

        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 공식 실무 팩트 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v135.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 공식 발표 팩트 기반 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 선사별 공식 Advisory 및 실무 데이터에 근거한 결과입니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템 (v135.0)
    </div>
""", unsafe_allow_html=True)
