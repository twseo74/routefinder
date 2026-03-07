import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v107", layout="wide")

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
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 0.85rem; line-height: 1.4; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .status-msg { color: #E6002D; font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 동적 분석 엔진 (지연 방지 및 순차 렌더링)
# ==========================================
def run_integrated_dynamic_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        # 모델 자동 탐색
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [실무 포인트] UAE 접근성, Ocean Alliance 협력, 통관 지원 강화 반영
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, [극동발] 담맘항 폐쇄 대응 주요 10대 선사의 실무 정책을 분석하세요. 
            특히 Jebel Ali(UAE)와 Khalifa Port를 통한 접근성 및 Ocean Alliance(COSCO, CMA CGM, Evergreen)의 가용 스페이스와 스케줄 변화를 표로 작성하세요. (언어: {lang}, 셀 내 줄바꿈 금지)""",
            
            f"""{today} 기준, 주요 항구(Jebel Ali, Salalah, Sohar)의 실시간 야드 적체 상태와 운영 팩트를 분석하세요. 
            알 바타(Al Batha) 및 알 마즈유나 국경을 통한 특정 품목의 내륙 운송 시 통관 절차 지원 및 강화 요소를 리포트하세요. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황(홍해/호르무즈)이 물류망에 미치는 군사/정치적 속보를 실시간 데이터 기반으로 요약하세요. (언어: {lang})"""
        ]

        # 섹션별 컨테이너 및 상태 메시지 영역 생성
        for i, query in enumerate(queries):
            status_placeholder = st.empty()
            content_placeholder = st.empty()
            
            status_placeholder.markdown(f'<p class="status-msg">⏳ {i+1}단계 분석 중...</p>', unsafe_allow_html=True)
            
            # 💡 [핵심] API 호출 시 타임아웃을 방지하기 위해 각 쿼리 후 즉시 화면 업데이트
            response = model.generate_content(query)
            
            status_placeholder.empty() # 진행중 메시지 삭제
            content_placeholder.markdown(response.text)
            st.divider()
            time.sleep(0.1) # 짧은 휴식으로 브라우저 렌더링 보장
        
        st.success("✅ 실시간 동적 분석 리포트 생성이 완료되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v107.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 실시간 팩트 리포트 자동 생성 시작", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_dynamic_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실시간 물류 데이터 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
