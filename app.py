import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v101", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #003366;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 자동 순차 생성 엔진 (v101.0)
# ==========================================
def run_integrated_auto_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 모델 자동 탐색 (404 방지)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = datetime.now(ksa_tz).strftime("%Y-%m-%d")

        # 💡 [핵심] 가상 시나리오 단어 삭제 및 실무 팩트 고정 프롬프트
        queries = [
            f"오늘 {today} 기준, [극동발] 담맘항 폐쇄 대응 MSC, Maersk, RCL, COSCO, CMA CGM 등 10대 선사의 해상화물(EOV/강제양하) 및 신규부킹 정책을 표로 작성. 상세 대체루트에 살랄라/소하르 및 알 마즈유나/알 바타 국경 정보 필수 포함. (셀 내 줄바꿈 금지, 언어: {lang})",
            f"오늘 {today} 기준, 제벨알리(운영재개/적체), 살랄라(포화), 소하르(대체지), 담맘(폐쇄) 등 주변국 항만의 실시간 상황과 야드 적체 팩트를 표로 작성. (언어: {lang})",
            f"오늘 {today} 기준, 최근 48시간 내 중동 전쟁 관련 속보를 보도일시, 제목, 요약, 성향, 링크 포함해 리스트로 작성. (언어: {lang})"
        ]

        # 섹션별 컨테이너 생성
        containers = [st.empty() for _ in range(len(queries))]
        
        # 💡 [핵심] 단계별 자동 생성 및 화면 출력
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 생성 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                time.sleep(0.5) # 딜레이를 주어 끊김 방지
        
        st.success("✅ 모든 리포트 섹션이 자동으로 생성되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v101.0)</p></div>', unsafe_allow_html=True)

st.markdown("""
<div class="question-box">
    <b>📋 실무 분석 타겟 (순차 자동 생성)</b><br>
    1. 선사별 해상 선박 처리(EOV), 신규 부킹 정책 및 상세 대체 루트(살랄라/소하르/UAE 등)<br>
    2. 주요 항구별 실시간 상황 및 적체 현황 (가상 단어 배제)<br>
    3. 전황 최신 속보
</div>
""", unsafe_allow_html=True)

if st.button("🚀 전체 리포트 자동 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_auto_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 참고용이며, 최종 의사결정 전 선사의 공식 Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
