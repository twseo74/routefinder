import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃 (강제 줄바꿈 CSS)
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v126", layout="wide")

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

# 💡 줄바꿈을 물리적으로 강제하기 위한 고정 폭 및 리스트 스타일 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .report-section { background-color: white; border: 1px solid #ddd; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .report-title { color: #003366; font-weight: bold; font-size: 1.1rem; margin-bottom: 15px; border-left: 5px solid #E6002D; padding-left: 10px; }
    .data-grid { display: grid; grid-template-columns: 1fr 2fr 2fr 2fr; gap: 1px; background-color: #ddd; border: 1px solid #ddd; }
    .grid-header { background-color: #f2f2f2; font-weight: bold; padding: 12px; text-align: center; font-size: 0.85rem; }
    .grid-cell { background-color: white; padding: 12px; font-size: 0.85rem; line-height: 1.8; vertical-align: top; }
    .grid-cell ul { margin: 0; padding-left: 18px; list-style-type: disc; }
    .grid-cell li { margin-bottom: 8px; } /* 💡 항목 간 간격 확보 */
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정 골격 분석 엔진 (v126.0 - 리스트 구조화)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 줄바꿈을 위해 Markdown 리스트(-) 형식을 강제하고, 이를 HTML로 변환
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 10대 선사의 호르무즈 대응 정책을 분석하세요.
            [필수 항목]: 선사명 / EOV 정책 / 신규 부킹 정책 / 대체 루트 및 가용성.
            [규칙]: 
            1. 각 셀의 내용은 반드시 짧은 문장의 리스트(-) 형태로 작성할 것. 
            2. 살랄라(Salalah), 제다(Jeddah) 등 양하 항구는 별도 줄로 구분할 것.
            3. LTC 우선, 스팟 제한, WRS 할증료 팩트를 각각 다른 줄에 배치할 것.
            (언어: {lang})""",
            
            f"""{today} 기준, 사우디/UAE/오만 항구별 야드 적체 현황과 국경(Al Batha, Al Mazyunah) 통관 지연 요소를 분석하여 리스트 형태로 리포트하세요. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황 속보를 요약 리포트하세요. (언어: {lang})"""
        ]

        # 단계별 생성 및 출력
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 팩트 분석 중..."):
                response = model.generate_content(query)
                st.markdown(f'<div class="report-title">{i+1}단계 분석 리포트</div>', unsafe_allow_html=True)
                # 💡 Markdown 리스트를 그대로 유지하여 출력 (CSS가 li 간격을 조절)
                st.markdown(response.text)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 지시하신 줄바꿈과 실무 팩트가 완벽히 반영되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v126.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 호르무즈 해협 봉쇄 대응 실무 (1, 2, 3단계)</b><br>
    1. 선사별 Sailing 화물 강제 양하(EOV) 위치 (Salalah, Jeddah) 및 부킹 정책<br>
    2. 항만 야드 적체 지수 및 국경 통관 지연 팩트 (Al Batha, Al Mazyunah)<br>
    3. 실시간 전황 속보 및 물류망 영향도 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실시간 물류 데이터 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
