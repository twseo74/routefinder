import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v118", layout="wide")

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
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 0.85rem; }
    th { background-color: #f8f9fa; font-weight: bold; border: 1px solid #ddd; padding: 10px; text-align: center; }
    td { border: 1px solid #ddd; padding: 10px; text-align: left; line-height: 1.5; }
    .status-msg { color: #E6002D; font-weight: bold; font-size: 0.9rem; margin-bottom: 10px; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정 골격 분석 엔진 (v118.0 - 가독성 특화)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "pro" in m.lower() or "flash" in m.lower()), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [지정 1, 2, 3번 골격 + 가독성 최적화 프롬프트]
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. {today} 기준, 10대 선사(MSC, Maersk, CMA CGM, COSCO, Hapag-Lloyd, ONE, Evergreen, OOCL, ZIM, HMM)의 정책을 분석하여 '가독성 높은 표'로 답변하세요.
            [필수 열]: 선사명 | EOV 정책 (Sailing 화물) | 신규 부킹 정책 | 상세 대체 루트 및 Jebel Ali/Khalifa 가용성 (Ocean Alliance 협력 포함).
            - 셀 내 텍스트는 불필요한 수식어를 빼고 핵심 실무 위주로 요약할 것.
            - 언어: {lang}""",
            
            f"""{today} 기준, 사우디/UAE/오만 주요 항구별(Jebel Ali, Salalah, Sohar 등) 실시간 상황 및 야드 적체 현황을 분석하세요.
            국경(Al Batha, Al Mazyunah) 통관 지연 요소를 포함하여 '표'로 작성하십시오. '가상' 단어 절대 금지. (언어: {lang})""",
            
            f"""{today} 기준, 최근 48시간 내 중동 전황 속보를 리스트로 작성하세요. 매체 성향(친이란/친미)과 물류 영향도를 명확히 구분하십시오. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 데이터 시각화 중..."):
                response = model.generate_content(query)
                containers[i].markdown(response.text)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 리포트가 성공적으로 시각화되었습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v118.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 실무 리포트 자동 생성 시작 (가독성 모드)", type="primary", use_container_width=True):
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
        본 리포트는 실무 지침 기반 분석 결과이며, 최종 의사결정 전 선사의 공식 Advisory를 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
