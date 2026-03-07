import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI 레이아웃
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v123", layout="wide")

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

# 💡 CSS 보강: 테이블 셀 내부의 <br> 태그와 불렛포인트가 확실히 작동하게 설정
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; table-layout: fixed; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; text-align: center; width: 25%; }
    td { border: 1px solid #ddd; padding: 12px; text-align: left; line-height: 1.8; vertical-align: top; word-break: keep-all; overflow-wrap: break-word; }
    .question-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; border-left: 5px solid #E6002D;}
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정 골격 분석 엔진 (v123.0 - 물리적 줄바꿈 강제)
# ==========================================
def run_integrated_report(api_key, is_ko):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in models if "pro" in m or "flash" in m), models[0])
        model = genai.GenerativeModel(target_model)
        
        lang = "Korean" if is_ko else "English"
        today = "2026-03-07"

        # 💡 [핵심] 줄바꿈을 위한 HTML <br> 태그 사용 지시 및 불렛포인트 강제
        queries = [
            f"""당신은 LX 판토스 물류 전문가입니다. 오늘({today}) 기준 10대 선사의 호르무즈 대응 정책을 분석하여 표로 작성하세요.
            [필수 열]: 선사명 | EOV 및 항로 정책 | 신규 부킹 정책 | 상세 대체 루트 및 가용성.
            [작성 규칙 - 절대 엄수]: 
            1. 표의 각 셀 안에서 항목이 바뀔 때마다 반드시 HTML 줄바꿈 태그인 <br>를 삽입할 것.
            2. 문장을 길게 늘어뜨리지 말고 불렛 포인트(•)를 사용하여 핵심만 요약할 것.
            3. 'EOV 발동 및 희망봉 우회', '자국 선박 보호 조치', 'LTC 우선 배정', 'Capacity Guarantee' 등의 핵심 팩트는 각각 독립된 줄에 배치할 것.
            (언어: {lang})""",
            
            f"""오늘({today}) 기준, 사우디/UAE/오만 항구별 야드 적체 현황과 국경(Al Batha, Al Mazyunah) 통관 지연 요소를 분석하여 표로 작성하세요.
            - 각 지연 사유는 불렛 포인트(•)와 <br> 태그를 사용하여 줄바꿈을 확실히 하십시오. (언어: {lang})""",
            
            f"""오늘({today}) 기준, 최근 48시간 내 중동 전황 속보를 리스트로 작성하세요. (언어: {lang})"""
        ]

        containers = [st.empty() for _ in range(len(queries))]
        for i, query in enumerate(queries):
            with st.spinner(f"{i+1}단계 실무 데이터 구조화 중..."):
                response = model.generate_content(query)
                # 💡 Markdown 내 HTML 태그가 동작하도록 설정
                containers[i].markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
        st.success("✅ 이제 줄바꿈이 적용된 깔끔한 리포트를 확인하실 수 있습니다.")

    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 화면 구성
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v123.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 리포트 생성 시작 (줄바꿈 해결판)", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("API Key 설정이 필요합니다.")
    else:
        run_integrated_report(API_KEY, is_ko)

# ==========================================
# 📜 4. 저작권 및 꼬리말
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 호르무즈 해협 위기 상황에 근거한 실시간 분석 결과입니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템 (v123.0)
    </div>
""", unsafe_allow_html=True)
