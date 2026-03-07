import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v96", layout="wide")

# 사이드바 설정
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")
    st.caption("※ SMTP 설정 후 전송 가능")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_date_str = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 0.85rem; line-height: 1.5; }
    th { background-color: #f8f9fa; font-weight: bold; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# API Key 로드
API_KEY = st.secrets.get("GEMINI_API_KEY") or st.secrets.get("email", {}).get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 고정밀 분석 엔진 (v96.0 - No Tools, Fast Response)
# ==========================================
def run_logistics_intel(api_key, q_num, is_ko, today_date):
    try:
        genai.configure(api_key=api_key)
        # 💡 [핵심] 404/400 에러를 방지하기 위해 가용한 최신 모델 자동 선택
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "3" in m.lower() or "pro" in m.lower()), available_models[0])
        model = genai.GenerativeModel(model_name=target_model)
        
        lang = "Korean" if is_ko else "English"
        # 💡 [핵심] 검색 도구(google_search)를 빼고 프롬프트에 실무 팩트를 직접 주입하여 딜레이 제거
        base_prompt = f"You are LX Pantos's Top Logistics Intelligence AI. TODAY IS {today_date}. Respond ENTIRELY in {lang}."

        if q_num == 1:
            prompt = base_prompt + """
            ### 🚢 1. [극동발] 선사별 해상화물 처리/부킹 정책 및 대체 루트
            [Dammam is BLOCKED] 다음 팩트를 기반으로 표를 작성하세요:
            - MSC/Maersk: 살랄라(Salalah) 강제 양하(EOV). 우회료 $350~$800. 살랄라 -> 알 마즈유나 국경 -> 사우디 트럭킹.
            - RCL: 소하르(Sohar) 강제 양하(EOV) 확정. 소하르 -> UAE 경유 -> 알 바타 국경 -> 사우디 트럭킹.
            - COSCO: 아부다비 칼리파(Khalifa)항 자사 터미널 활용. 아부다비 -> 알 바타 국경 -> 사우디 트럭킹.
            - CMA CGM: 제벨알리(T3) 또는 코르 파칸 활용. 알 바타 국경 경유.
            - 신규 부킹: 담맘향 전면 중단. 살랄라/제벨알리 양하 조건부 부킹만 가능.
            
            Columns: 선사 | 항해 중 화물 처리 (Sailing) | 신규 부킹 정책 (Booking) | 상세 대체 루트 (Alt Route).
            *표 내부 줄바꿈 금지.*
            """
        elif q_num == 2:
            prompt = base_prompt + """
            ### ⚓ 2. 주변국 항만 실시간 상황 (2026년 3월)
            - Jebel Ali: 미사일 피격 후 운영 재개됐으나 야드 포화로 반출 지연 심각.
            - Salalah: MSC/Maersk 물량 집중으로 적체 심화.
            - Sohar: 대체항으로 부상 중이나 보안 검색 강화됨.
            - Dammam: 전면 폐쇄 유지.
            
            Columns: 항구명 | 운영 및 적체 현황 | 실무 참고사항 | 기준 일시.
            """
        else:
            prompt = base_prompt + "### 🔥 3. 최신 전황 속보 (최근 48시간). 보도 일시, 제목, 요약, 성향, 링크 포함."
        
        # 💡 도구 없이 즉시 생성
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 시스템 오류: {e}"

# ==========================================
# 🚀 3. 메인 대시보드
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v96.0)</p></div>', unsafe_allow_html=True)

if st.button("🚀 실무 인텔리전스 즉시 생성", type="primary", use_container_width=True):
    if not API_KEY:
        st.error("Streamlit Secrets에 GEMINI_API_KEY를 설정해주세요.")
    else:
        # 진행 바 표시
        progress_bar = st.progress(0)
        q1_container = st.empty()
        q2_container = st.empty()
        q3_container = st.empty()

        # 1번 섹션
        progress_bar.progress(33)
        res1 = run_logistics_intel(API_KEY, 1, is_ko, current_date_str)
        q1_container.markdown(res1)

        # 2번 섹션
        progress_bar.progress(66)
        res2 = run_logistics_intel(API_KEY, 2, is_ko, current_date_str)
        q2_container.markdown(res2)

        # 3번 섹션
        progress_bar.progress(100)
        res3 = run_logistics_intel(API_KEY, 3, is_ko, current_date_str)
        q3_container.markdown(res3)
        
        st.success("✅ 리포트 생성이 완료되었습니다.")

# ==========================================
# 📜 4. 저작권 표기
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 참고용이며, 최종 의사결정 전 선사의 Customer Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템 (v96.0)
    </div>
""", unsafe_allow_html=True)
