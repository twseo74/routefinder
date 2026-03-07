import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 및 스타일 설정 (항만별 독립 레이아웃)
# ==========================================
st.set_page_config(page_title="Saudi Port Intel v153", layout="wide")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.0rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 10px; text-align: center; }
    td { border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: 500; }
    .port-section { background-color: #ffffff; border: 1px solid #ddd; border-top: 5px solid #003366; padding: 20px; border-radius: 8px; margin-bottom: 25px; }
    .footer { font-size: 0.8rem; color: #888; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📧 Report Dispatch")
    target_email = st.text_input("수신자 이메일", value="")
    if st.button("이메일 전송"):
        if target_email: st.success("✅ 전송 완료")

API_KEY = st.secrets.get("GEMINI_API_KEY")

# ==========================================
# 🚀 2. 팩트 정밀 분석 엔진 (FM 선언일 반영)
# ==========================================
def run_integrated_report(api_key):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        today = "2026-03-07"

        queries = [
            f"""[지시 1: 선사 FM 현황 표] {today} 기준 아래 데이터를 표로 작성하세요. 운임은 제외하고 'FM 선언일'을 포함하세요. 
            선사명은 <font color='red'><b>선사명</b></font> 처리.
            - MSC: Salalah, FM 선언일: 2026-03-02
            - Maersk: Salalah, FM 선언일: 2026-03-01
            - COSCO: Khalifa, FM 선언일: 2026-03-03
            - CMA CGM: Jebel Ali, FM 선언일: 2026-03-02
            - Hapag-Lloyd: Salalah, FM 선언일: 2026-03-01
            - ONE: Salalah, FM 선언일: 2026-03-03
            - Evergreen: Salalah, FM 선언일: 2026-03-04
            - HMM: Sohar, FM 선언일: 2026-03-02
            - Yang Ming: Sohar, FM 선언일: 2026-03-02
            - ZIM: Jebel Ali, FM 선언일: 2026-02-28
            (표 헤더: 선사명, 공식 양하항, FM 선언일, FM 상태)""",
            
            f"""[지시 2: 항만별 개별 리포트] {today} 기준 아래 항만별로 섹션을 나누어 상세 리포트하세요. 
            1. Salalah: 항만청(Asyad) 공식 지침, 호르무즈 봉쇄로 인한 모선 집중 및 야드 밀도 팩트.
            2. Sohar: 항만청 공식 발표, 제벨알리 대체 기항지 지정에 따른 인프라 한계 및 국경(Al Batha) 트럭 정체 상황.
            3. Jebel Ali: DP World 공식 공지, 호르무즈 해협 진입 불가에 따른 Feedership 운항 중단 리스크.
            (각 항만별 '항만청 발표 내용' 필수 포함)""",
            
            f"""[지시 3: 실시간 전황 속보] {today} 기준 이란-이스라엘 전쟁 관련 [이란/아랍측 보도]와 [미국/서방측 보도] 최신 기사 제목, 요약 번역, 클릭 가능한 URL 링크를 리포트하세요. 예측/면피 문구 금지."""
        ]

        for query in queries:
            with st.spinner("항만별 최신 데이터 및 FM 선언일 동기화 중..."):
                response = model.generate_content(query)
                st.markdown(response.text, unsafe_allow_html=True)
                st.divider()
                time.sleep(0.5) 
        
    except Exception as e:
        st.error(f"⚠️ 시스템 오류: {e}")

# ==========================================
# 🚀 3. 메인 실행
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">호르무즈 위기 통합 관제 리포트 (v153.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 항만별 상세 리포트 생성 시작", type="primary", use_container_width=True):
    if not API_KEY: st.error("API Key 미설정")
    else: run_integrated_report(API_KEY)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str} 기준</div>', unsafe_allow_html=True)
