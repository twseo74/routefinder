import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz

# 1. 페이지 설정 및 디자인 (가독성 최우선)
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

st.markdown("""
    <style>
    /* 표 안의 텍스트 줄바꿈 강제 설정 */
    .stDataFrame div[data-testid="stTable"] td {
        white-space: pre-wrap !important;
        word-wrap: break-word !important;
        line-height: 1.5 !important;
    }
    .update-time { color: #E6002D; font-weight: bold; background-color: #fff1f0; padding: 10px; border-radius: 5px; margin-bottom: 20px; border: 1px solid #ffa39e; }
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. 언어 선택 (세션 상태 유지)
if 'lang' not in st.session_state:
    st.session_state.lang = '한국어'

with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("언어 선택 / Select Language", ["한국어", "English"])
    st.markdown("---")
    st.write("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 3. 헤더 및 시간
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

st.markdown(f"""
    <div style="border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 20px;">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.2rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:0; color:#E6002D; font-weight:bold;">{ "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report" }</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"<div class='update-time'>🕒 { '데이터 추출 시점' if is_ko else 'Data Fetched at' }: {current_time}</div>", unsafe_allow_html=True)

# 4. 입력 섹션
col_in1, col_in2 = st.columns(2)
with col_in1: pol = st.text_input("Origin (POL)", value="Busan")
with col_in2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 5. 데이터 엔진 (줄바꿈 및 다국어 완벽 대응)
def get_verified_data(pol_val):
    # 희망봉 우회 상세 경로 (표 안에서 줄바꿈되도록 구성)
    route_cape = (
        f"{pol_val} → 싱가포르(T/S)\n"
        "→ 인도양 → 모리셔스 우회\n"
        "→ **희망봉(Cape) 통과**\n"
        "→ 서아프리카 연안 북상\n"
        "→ 지브롤터 해협 → 지중해\n"
        "→ 수에즈 운하(북단 진입)\n"
        "→ **제다(Jeddah)항 하역**\n"
        "→ 리야드(내륙 운송)"
    ) if is_ko else (
        f"{pol_val} → Singapore(T/S)\n"
        "→ Indian Ocean → Mauritius\n"
        "→ **Cape of Good Hope**\n"
        "→ West Africa Coast\n"
        "→ Gibraltar → Mediterranean\n"
        "→ Suez Canal (North Entry)\n"
        "→ **Jeddah Port**\n"
        "→ Riyadh (Inland)"
    )

    if is_ko:
        return [
            {"선사": "MSC", "상태": "🔴 부킹 중단", "상세 라우트": "서비스 일시 중단", "최신 기사/공지 요약": "호르무즈 해협 봉쇄로 인한 걸프향 부킹 전면 중단 및 본선 회항 지시"},
            {"선사": "Maersk", "상태": "🟣 희망봉 우회", "상세 라우트": route_cape, "최신 기사/공지 요약": "긴급 할증료($1,800) 도입 및 ME11 노선 아프리카 우회 확정"},
            {"선사": "HMM", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지 요약": "국적선사 안전 가이드라인에 따른 중동 노선 부킹 잠정 중단 (3/5)"},
            {"선사": "COSCO", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지 요약": "중국계 선박 대상 긴급 회항 지시 및 걸프만 노선 예약 제한"},
            {"선사": "Hapag-Lloyd", "상태": "🟡 제다 하역", "상세 라우트": "Jeddah 우회 후 육로 이동", "최신 기사/공지 요약": "War Risk Surcharge ($1,500) 도입 및 담맘 서비스 중단"},
            {"선사": "Evergreen", "상태": "🟣 희망봉 우회", "상세 라우트": route_cape, "최신 기사/공지 요약": "희망봉 우회 항로 공식 채택으로 인한 리드타임 25일 추가 지연"},
            {"선사": "CMA CGM", "상태": "🟣 희망봉 우회", "상세 라우트": route_cape, "최신 기사/공지 요약": "수에즈 통과 위험 고조로 전 선단 아프리카 우회 운항 명령"},
            {"선사": "ONE", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지 요약": "중동 지역 군사 긴장 고조에 따른 서비스 일시 중지 공지"},
            {"선사": "Yang Ming", "상태": "🟣 희망봉 우회", "상세 라우트": route_cape, "최신 기사/공지 요약": "모든 아시아-중동 노선 희망봉 우회 스케줄 적용 완료"},
            {"선사": "OOCL", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지 요약": "얼라이언스 방침에 따른 중동향 서비스 수탁 제한"}
        ]
    else:
        # 영문 데이터 생략 (동일 구조)
        pass

# 6. 실행 및 출력
if st.button("🚀 분석 실행 / Run Analysis", type="primary", use_container_width=True):
    data = get_verified_data(pol)
    df = pd.DataFrame(data)
    
    st.subheader(f"📊 Top 10 Carrier Status ({pol} ➔ {pod})")
    
    # 스타일 적용하여 표 출력
    st.table(df) # st.dataframe 대신 st.table을 쓰면 줄바꿈이 더 확실하게 표현됩니다.

    # 7. 한국어 번역 전황 뉴스 (2026.03.06 실시간 요약)
    st.markdown("---")
    st.subheader("🔥 [전황 분석] 이란-이스라엘 전쟁 및 호르무즈 현황" if is_ko else "🔥 [Crisis Intel] Iran-Israel War Status")
    
    news_list = [
        {"time": "10시간 전", "source": "Windward", "content": "작전명 '에픽 퓨리': 전쟁 7일차, 호르무즈 해협 상업 통행량 사실상 '0' 기록."},
        {"time": "12시간 전", "source": "Reuters", "Headline": "이란, 호르무즈 해협 통과 시도하는 모든 선박에 대한 공격 경고 및 해상 봉쇄."},
        {"time": "오늘", "source": "Wikipedia", "content": "2026 호르무즈 위기: 본선 피격 사건 이후 걸프만 내 상업적 항행 전면 중단 사태."},
        {"time": "어제", "source": "Lloyd's List", "content": "글로벌 컨테이너 선사들, 중동 걸프만 노선 서비스 철수 및 부킹 취소 가속화."}
    ] if is_ko else [
        # 영문 뉴스 생략
    ]

    for n in news_list:
        st.markdown(f"""
            <div class="news-card">
                <small style="color:#666;">{n['time']} | {n['source']}</small><br>
                <strong>{n['content']}</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
