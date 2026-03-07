import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v120", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    # 💡 이메일 자동 입력 삭제 및 수동 입력으로 변경
    st.divider()
    st.subheader("📧 Report Export")
    target_email = st.text_input("수신자 이메일 입력", placeholder="example@lxpantos.com")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 0.88rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; text-align: center; }
    td { border: 1px solid #ddd; padding: 12px; text-align: left; line-height: 1.6; white-space: pre-line; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #E6002D;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 호르무즈 이슈 특화 분석 엔진 (v120.0)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [호르무즈 해협 위기 연계 1, 2, 3번 핵심 질문]
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 호르무즈 해협 긴장 및 담맘항 폐쇄에 따른 10대 선사별 대응을 분석하여 표로 답변하세요.
            [필수 열]: 선사명 | 호르무즈 리스크 대응 (Sailing 화물 처리) | 신규 부킹 통제 정책 | 대체 루트 가용성.
            [분석 가이드라인]:
            - Sailing 화물: 호르무즈 통과 거부 및 Salalah/Sohar/Jebel Ali 강제 하역 후 EOV 선언 여부.
            - 신규 부킹: 장기계약(LTC) 우선 배정 및 스팟 부킹 전면 중단/프리미엄 요금 적용 팩트.
            - Jebel Ali/Khalifa 및 Ocean Alliance의 선복 공유 상황 실시간 분석.
            (언어: {lang}, 불렛포인트 사용, 줄바꿈 필수)""",
            
            f"""{today} 기준, 호르무즈 이슈로 인한 주요 항구(Jebel Ali, Salalah, Sohar) 야드 혼잡도와 국경(Al Batha, Al Mazyunah) 통관 지연 요소를 분석하세요.
            - 항만별 적체 사유 및 특정 품목 내륙 운송 지연 팩트 포함. (언어: {lang}, 줄바꿈 필수)""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황(호르무즈 해협 봉쇄 위협 등) 속보를 매체 성향별로 요약하고 물류망 차단 가능성을 분석하세요. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 호르무즈 이슈 실무 분석 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 호르무즈 이슈 대응 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">호르무즈 위기 통합 관제 리포트 (v120.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 호르무즈 해협 위기 연계 실무 분석</b><br>
    1. 선사별 Sailing 화물 호르무즈 통과 여부 및 신규 부킹 통제 정책 (LTC/Spot 구분)<br>
    2. 항만별 야드 적체 지수 및 국경 통관 지연 팩트 (Al Batha, Al Mazyunah)<br>
    3. 전황 속보 및 물류망 영향도 분석
</div>
""", unsafe_allow_html=True)

if st.button("🚀 호르무즈 이슈 대응 리포트 생성 시작", type="primary", use_container_width=True):
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
        본 리포트는 호르무즈 해협 위기 상황에 근거한 실시간 분석 결과입니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
