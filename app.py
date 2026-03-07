import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 설정 (선사명 빨간색 굵게 + 매체 성향 가시성)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v141", layout="wide")

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
    .bias-tag-west { color: #0044cc; font-weight: bold; font-size: 0.85rem; } /* 미국/서방 편 */
    .bias-tag-iran { color: #cc0000; font-weight: bold; font-size: 0.85rem; } /* 이란/아랍 편 */
    .data-row { margin-bottom: 12px; line-height: 1.8; white-space: pre-wrap; font-size: 0.95rem; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 전황 성향 분석 엔진 (v141.0)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 이란-이스라엘 전쟁 격상에 따른 10대 선사별 공식 FM 대응(강제 양하지, 비용)을 분석하세요. (언론 보도 팩트 기반, 선사명 빨간색 굵게, 줄바꿈 필수)""",
            
            f"""오늘({today}) 기준, Salalah, Sohar, Jebel Ali 등 FM 하역 집중 항구의 적체 리스크와 국경 운임 급등 현황을 리포트하세요. (줄바꿈 필수)""",
            
            f"""오늘({today}) 기준, 이란-이스라엘 전쟁 관련 [매체별 성향 분석 리포트]를 작성하세요.
            [작성 양식]:
            1. **매체명 (보도 시각 KSA 기준)**
            2. **성향**: [미국/이스라엘 지지] 또는 [이란/아랍 입장 대변] 명시
            3. **핵심 보도 내용 요약 및 번역**
            4. **물류적 관점의 해석**: (예: 호르무즈 봉쇄 실현 가능성 및 담맘항 폐쇄 리스크)
            
            [분석 대상 매체]: Al Jazeera, CNN, IRNA(이란 국영), Al Arabiya, BBC 등 최소 4개 이상. (언어: {lang}, 줄바꿈 필수)"""
        ]

        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 및 매체 성향 분석 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v141.0)</p></div>', unsafe_allow_html=True)

st.info(f"📅 리포트 기준 시각: {current_time_str}")

if st.button("🚀 매체 성향 분석 포함 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 이란-이스라엘 전쟁 성향 분석 및 선사 공식 Advisory에 근거한 팩트 리포트입니다.
    </div>
""", unsafe_allow_html=True)
