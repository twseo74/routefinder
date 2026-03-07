import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 UI
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Intel v98", layout="wide")

if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 Settings")
    st.session_state.lang = st.radio("Language / 언어", ["한국어", "English"])
    st.divider()
    st.subheader("📧 Email Report")
    receiver_email = st.text_input("수신 이메일", "byeonggeol.kang@lxpantos.com")
    if st.button("현재 리포트 전송"):
        st.info("SMTP 연동 시 전송 가능합니다.")

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
    .section-btn { margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 엔진 (v98.0 - 섹션별 독립 호출)
# ==========================================
def get_intel(api_key, q_num, is_ko):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro') # 💡 Pro 모델 고정
        lang = "Korean" if is_ko else "English"
        
        prompts = {
            1: f"TODAY IS {current_date_str}. [극동발] 담맘항 폐쇄에 따른 MSC, Maersk, RCL, COSCO, CMA CGM 등 10대 선사의 해상화물(EOV/강제양하) 및 신규부킹 정책을 표로 작성하세요. 상세 대체루트에 살랄라/소하르 및 알 마즈유나/알 바타 국경 정보를 반드시 포함하세요. (셀 내 줄바꿈 금지, 언어: {lang})",
            2: f"TODAY IS {current_date_str}. 제벨알리(운영재개/적체), 살랄라(포화), 소하르(대체지), 담맘(폐쇄) 등 주변국 항만의 실시간 상황과 야드 적체 팩트를 표로 작성하세요. (언어: {lang})",
            3: f"TODAY IS {current_date_str}. 최근 48시간 내 중동 전쟁 관련 속보를 보도일시, 제목, 요약, 성향, 링크를 포함해 리스트로 작성하세요. (언어: {lang})"
        }
        
        response = model.generate_content(prompts[q_num])
        return response.text
    except Exception as e: return f"⚠️ 오류: {e}"

# ==========================================
# 🚀 3. 메인 화면 (섹션별 끊어서 생성)
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1><p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">인바운드 통합 관제 리포트 (v98.0)</p></div>', unsafe_allow_html=True)

st.info("💡 데이터 과부하 방지를 위해 각 섹션을 순서대로 클릭하여 생성해 주세요.")

# --- 섹션 1 ---
if st.button("🚢 1단계: 선사별 정책 및 대체 루트 생성", use_container_width=True):
    with st.spinner("선사별 실무 데이터 분석 중..."):
        st.session_state['res1'] = get_intel(API_KEY, 1, is_ko)
if 'res1' in st.session_state: st.markdown(st.session_state['res1'])

# --- 섹션 2 ---
if st.button("⚓ 2단계: 항만별 실시간 적체 상황 생성", use_container_width=True):
    with st.spinner("주변국 항만 실시간 팩트 추출 중..."):
        st.session_state['res2'] = get_intel(API_KEY, 2, is_ko)
if 'res2' in st.session_state: st.markdown(st.session_state['res2'])

# --- 섹션 3 ---
if st.button("🔥 3단계: 최신 전황 및 속보 생성", use_container_width=True):
    with st.spinner("군사/정치 매체 속보 수집 중..."):
        st.session_state['res3'] = get_intel(API_KEY, 3, is_ko)
if 'res3' in st.session_state: st.markdown(st.session_state['res3'])

# ==========================================
# 📜 4. 하단 정보 (저작권 복구)
# ==========================================
st.markdown(f"""
    <div class="footer">
        © 2026 LX Pantos Saudi Arabia. All Rights Reserved.<br>
        본 리포트는 실무 참고용이며, 최종 의사결정 전 선사의 공식 Advisory를 반드시 재확인하시기 바랍니다.<br>
        담당: {current_date_str} 기준 실시간 분석 시스템
    </div>
""", unsafe_allow_html=True)
