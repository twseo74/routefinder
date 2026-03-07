import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import pytz

# ==========================================
# 1. 초기 설정 및 디자인
# ==========================================
st.set_page_config(page_title="LX Pantos Saudi Control Tower", layout="wide")

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .status-alert { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 15px; border-radius: 5px; margin-bottom: 20px; color: #cf1322; font-weight: bold;}
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

API_KEY = None
try:
    if "GEMINI_API_KEY" in st.secrets: API_KEY = st.secrets["GEMINI_API_KEY"]
    elif "email" in st.secrets and "GEMINI_API_KEY" in st.secrets["email"]: API_KEY = st.secrets["email"]["GEMINI_API_KEY"]
except: pass

# ==========================================
# 🚀 2. 인바운드 실무 팩트 베이스라인 (절대 깨지지 않는 고정 DB)
# ==========================================
# 매니저님이 실무에서 확인하신 팩트를 바탕으로 언제든 여기서 텍스트만 수정하시면 됩니다.
ocean_data = [
    {"선사 (Carrier)": "MSC", "담맘향 상태": "🔴 전면 중단 (End of Voyage)", "대체 양하 포트 (Alt Port)": "오만 살랄라 (Salalah) / UAE 아부다비", "LX Pantos 실무 대응 방안 (Action Plan)": "살랄라 강제 양하 시 화주 비용으로 Cross-border 트럭킹 수배 필요. (건당 서차지 발생)"},
    {"선사 (Carrier)": "Maersk", "담맘향 상태": "🔴 부킹 중단 / 우회", "대체 양하 포트 (Alt Port)": "UAE 제벨알리 (Jebel Ali)", "LX Pantos 실무 대응 방안 (Action Plan)": "제벨알리 하역 후 사우디 국경(Batha) 경유 Landbridge 운송망 확보 집중."},
    {"선사 (Carrier)": "CMA CGM", "담맘향 상태": "🔴 상부 걸프 진입 불가", "대체 양하 포트 (Alt Port)": "UAE 푸자이라 (Fujairah) / 코르파칸", "LX Pantos 실무 대응 방안 (Action Plan)": "푸자이라 하역 후 육로 연계. 피더(Feeder)선 수배 극도 지연 중."},
    {"선사 (Carrier)": "Hapag-Lloyd", "담맘향 상태": "🔴 우회", "대체 양하 포트 (Alt Port)": "UAE 코르파칸 (Khor Fakkan)", "LX Pantos 실무 대응 방안 (Action Plan)": "희망봉 우회로 인한 T/T 25일 이상 추가. 화주 대상 납기 지연 공식 안내 요망."},
    {"선사 (Carrier)": "HMM / ONE", "담맘향 상태": "🔴 부킹 접수 중단", "대체 양하 포트 (Alt Port)": "확인 불가 (기존 화물 억류 중)", "LX Pantos 실무 대응 방안 (Action Plan)": "신규 선적 절대 불가. 대체 선사 수배 요망."},
    {"선사 (Carrier)": "COSCO / OOCL", "담맘향 상태": "🟡 제한적 운영", "대체 양하 포트 (Alt Port)": "제다 (Jeddah) 경유 가능성", "LX Pantos 실무 대응 방안 (Action Plan)": "중국계 선사 일부 홍해 통과 시도 중이나 리스크 매우 높음. 스페이스 개별 확인 필수."}
]

air_data = [
    {"항공사 (Airline)": "Cathay Pacific (CX)", "사우디향 상태": "🔴 결항 (Suspended)", "운영 재개 예상일": "3월 14일 이후 잠정", "실무 비고": "RFS(트럭킹) 연계 스페이스 전면 차단."},
    {"항공사 (Airline)": "Korean Air (KE)", "사우디향 상태": "🔴 결항 (Suspended)", "운영 재개 예상일": "미정 (안전성 검토 중)", "실무 비고": "해상 우회 화물의 항공 전환(Sea-Air) 수요 폭증으로 두바이(DXB) 경유 루트 타진 필요."},
    {"항공사 (Airline)": "Saudia / Emirates", "사우디향 상태": "🟢 정상 운영 (지연 심각)", "운영 재개 예상일": "현재 운항 중", "실무 비고": "DXB 및 RUH 허브 적체 극심. 최소 24~48시간 환승 지연 발생 중."}
]

df_ocean = pd.DataFrame(ocean_data)
df_air = pd.DataFrame(air_data)

# ==========================================
# 🚀 3. AI 노티스 전용 분석기 (새로운 공지문 해독)
# ==========================================
def analyze_notice(api_key, notice_text):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash') # 안정적인 기본 모델
        
        prompt = f"""
        당신은 LX Pantos 사우디 법인의 인바운드 물류 전문가입니다.
        아래는 선사나 항공사, 또는 현지 파트너로부터 방금 수신한 물류 노티스(공지) 원문입니다.
        
        <NOTICE>
        {notice_text}
        </NOTICE>
        
        이 내용을 분석하여 사우디(특히 담맘, 리야드, 제다)로 들어오는 화물에 어떤 영향이 있는지 아래 4가지 항목으로 짧고 명확하게 한국어로 요약해 주십시오. 
        인사말이나 불필요한 서론은 절대 쓰지 마십시오.
        
        1. **발신 기관 (선사/항공사)**:
        2. **대상 항구/공항 및 현재 상태**: (예: 담맘항 진입 불가, 살랄라 양하)
        3. **추가 비용/할증료 (Surcharge)**: (언급된 경우만)
        4. **LX Pantos 실무 대응 필요 사항**: (본문 내용을 기반으로 트럭킹 수배, 화주 안내 등 실무적 조언 1줄)
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ 분석 오류 발생: {e}"

# ==========================================
# 🚀 4. 메인 대시보드 UI
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Inbound Control Tower</span></h1></div>', unsafe_allow_html=True)

st.markdown(f'<div class="status-alert">🚨 [긴급 상황반] 호르무즈 해협 위기 - 담맘(DMM) 입항 전면 통제 및 대체 항만(UAE/Oman) 강제 양하 진행 중 (기준: {current_time})</div>', unsafe_allow_html=True)

# --- [TAB 1] 전체 상황판 (항상 100% 뜨는 고정 데이터) ---
st.markdown('<div class="section-title">🚢 [해상] 주요 10대 선사 담맘향 라우팅 및 대응 방안</div>', unsafe_allow_html=True)
st.dataframe(df_ocean, use_container_width=True, hide_index=True)

st.markdown('<div class="section-title">✈️ [항공] 리야드(RUH)향 주요 항공사 카고 현황</div>', unsafe_allow_html=True)
st.dataframe(df_air, use_container_width=True, hide_index=True)

# --- [TAB 2] AI 노티스 분석기 (이메일/왓츠앱 공지 해독) ---
st.markdown("---")
st.markdown('<div class="section-title">🤖 AI 신규 노티스 해독기 (Notice Analyzer)</div>', unsafe_allow_html=True)
st.write("선사나 로컬 파트너에게 받은 긴급 영문 이메일이나 왓츠앱 메시지를 아래에 붙여넣으세요. AI가 사우디 인바운드 실무에 미치는 영향을 즉시 해독합니다.")

notice_input = st.text_area("여기에 노티스 원문을 복사해서 붙여넣으세요 (Paste Notice Here):", height=150)

if st.button("🚀 신규 노티스 실무 영향 분석", type="primary"):
    if not API_KEY:
        st.error("API Key가 설정되지 않았습니다.")
    elif not notice_input:
        st.warning("분석할 노티스 텍스트를 입력해 주세요.")
    else:
        with st.spinner("AI가 노티스 내용을 분석하여 사우디향 인바운드 타격 및 대응 방안을 추출하고 있습니다..."):
            analysis_result = analyze_notice(API_KEY, notice_input)
            st.success("분석 완료!")
            st.markdown(f"<div style='background-color: #f8f9fa; padding: 20px; border-left: 4px solid #003366; border-radius: 4px;'>{analysis_result}</div>", unsafe_allow_html=True)
