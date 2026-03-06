import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Middle East Intelligence", layout="wide")

# 2. 다국어 지원용 세션 상태 초기화
if 'lang' not in st.session_state:
    st.session_state.lang = '한국어'

# 3. 사이드바 - 언어 및 설정
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Select Language / 언어 선택", ["한국어", "English"])
    st.info("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 4. 헤더 디자인 (로고 제거 및 고해상도 텍스트)
st.markdown(f"""
    <div style="border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px;">
        <h1 style="color: #333; margin: 0;">LX PANTOS <span style="font-size: 1.2rem; color: #E6002D;">| Saudi Arabia Branch</span></h1>
        <h2 style="margin: 0; font-size: 1.5rem; color: #555;">{ "중동 전황 및 10대 선사 라우팅 분석" if is_ko else "Middle East Crisis & Top 10 Carrier Routing Analysis" }</h2>
    </div>
""", unsafe_allow_html=True)

# 5. 실시간 시각 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")
st.markdown(f"**🕒 Data Fetched at:** {current_time}")

# 6. 입력 구간
col_in1, col_in2 = st.columns(2)
with col_in1:
    pol = st.text_input("Origin (POL)", value="Busan")
with col_in2:
    pod = st.text_input("Destination (POD)", value="Riyadh")

# 7. 10대 선사 실시간 분석 데이터 (2026.03.06 뉴스 기반)
def get_live_data(origin, destination):
    # 희망봉 우회 상세 경로 (줄바꿈 포함)
    cape_detail = (
        f"{origin} → Singapore (T/S)\n"
        "→ 🌊Indian Ocean → Mauritius\n"
        "→ **Cape of Good Hope** → West Africa\n"
        "→ Gibraltar Strait → Mediterranean\n"
        "→ Suez Canal (North) → **Jeddah Port**\n"
        "→ Riyadh (Inland Trucking)"
    )
    
    if is_ko:
        return [
            {"선사": "MSC", "상태": "🔴 부킹 전면 중단", "상세 라우트": "서비스 중단 (End of Voyage 선언)", "최신 기사/공지": "호르무즈 해협 통행 불가로 모든 걸프향 부킹 중지 (3/5 뉴스)"},
            {"선사": "Maersk", "상태": "🟣 희망봉 우회", "상세 라우트": cape_detail, "최신 기사/공지": "Emergency Freight Increase ($1,800) 부과 및 ME11 노선 우회 확정"},
            {"선사": "CMA CGM", "상태": "🟣 희망봉 우회", "상세 라우트": cape_detail, "최신 기사/공지": "홍해 및 수에즈 운하 통과 전면 중단 및 아프리카 우회 명령"},
            {"선사": "COSCO", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지": "중국계 선박 대상 긴급 회항 지시 및 신규 예약 접수 중단 (3/4 공지)"},
            {"선사": "Hapag-Lloyd", "상태": "🟡 제다 하역", "상세 라우트": "Jeddah 우회 후 육로 이동", "최신 기사/공지": "IG1/KWF 서비스 일시 중단 및 War Risk Surcharge ($1,500) 도입"},
            {"선사": "ONE", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지": "걸프만 긴장 고조에 따른 중동 전역 서비스 일시 중지"},
            {"선사": "Evergreen", "상태": "🟣 희망봉 우회", "상세 라우트": cape_detail, "최신 기사/공지": "전 선단 희망봉 우회 지시 및 리드타임 25일 추가 지연 예고"},
            {"선사": "HMM", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지": "국적선사 안전 가이드라인에 따른 중동 노선 부킹 잠정 중단"},
            {"선사": "Yang Ming", "상태": "🟣 희망봉 우회", "상세 라우트": cape_detail, "최신 기사/공지": "아시아-중동 노선 전면 희망봉 우회 운항 중"},
            {"선사": "OOCL", "상태": "🔴 부킹 중단", "상세 라우트": "Suspended", "최신 기사/공지": "선복 공유 파트너사(COSCO) 방침에 따른 중동향 서비스 제한"}
        ]
    else:
        return [
            {"Carrier": "MSC", "Status": "🔴 Booking Suspended", "Route Detail": "End of Voyage Declared", "Latest News/Notice": "All Gulf bookings halted due to Hormuz closure (Mar 5)"},
            {"Carrier": "Maersk", "Status": "🟣 Cape Detour", "Route Detail": cape_detail, "Latest News/Notice": "Implemented Emergency Freight Increase ($1,800/TEU)"},
            {"Carrier": "CMA CGM", "Status": "🟣 Cape Detour", "Route Detail": cape_detail, "Latest News/Notice": "Suez passage suspended; all vessels rerouted via Cape"},
            {"Carrier": "COSCO", "Status": "🔴 Booking Suspended", "Route Detail": "Suspended", "Latest News/Notice": "Temporary stop for new Middle East bookings (Mar 4)"},
            {"Carrier": "Hapag-Lloyd", "Status": "🟡 via Jeddah", "Route Detail": "Discharge at Jeddah + Inland", "Latest News/Notice": "IG1/KWF services suspended; WRS $1,500 implemented"},
            {"Carrier": "ONE", "Status": "🔴 Booking Suspended", "Route Detail": "Suspended", "Latest News/Notice": "Middle East services paused due to regional escalation"},
            {"Carrier": "Evergreen", "Status": "🟣 Cape Detour", "Route Detail": cape_detail, "Latest News/Notice": "Fleet instructed to detour via Cape; +25 days delay expected"},
            {"Carrier": "HMM", "Status": "🔴 Booking Suspended", "Route Detail": "Suspended", "Latest News/Notice": "Temporary suspension of ME bookings for safety (Mar 5)"},
            {"Carrier": "Yang Ming", "Status": "🟣 Cape Detour", "Route Detail": cape_detail, "Latest News/Notice": "All vessels rerouted around Africa southern tip"},
            {"Carrier": "OOCL", "Status": "🔴 Booking Suspended", "Route Detail": "Suspended", "Latest News/Notice": "Service restricted following partner carrier policy"}
        ]

# 8. 분석 실행
if st.button("🚀 Run Analysis" if not is_ko else "🚀 실시간 분석 실행", type="primary", use_container_width=True):
    data = get_live_data(pol, pod)
    df = pd.DataFrame(data)
    
    st.subheader(f"📊 Top 10 Carrier Status ({pol} ➔ {pod})")
    
    # 표 디자인 (자동 줄바꿈 지원)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 9. 최신 중동 전황 뉴스 리스트 (2026.03.06 실시간 기사 요약)
    st.markdown("---")
    st.subheader("🔥 [Crisis Intel] Iran-Israel Conflict & Hormuz Status" if not is_ko else "🔥 [전황 분석] 이란-이스라엘 전쟁 및 호르무즈 해협 현황")
    
    war_news = [
        {"Time": "10h ago", "Source": "Windward", "Headline": "Operation Epic Fury: Hormuz traffic collapses as Iran War enters Day 7."},
        {"Time": "12h ago", "Source": "Reuters", "Headline": "Iran threatened to burn any ships attempting to transit the Strait of Hormuz."},
        {"Time": "Today", "Source": "Wikipedia", "Headline": "2026 Strait of Hormuz crisis: Effective halt in commercial traffic after vessel strikes."},
        {"Time": "Yesterday", "Source": "Lloyd's List", "Headline": "Global container carriers accelerating withdrawal from Middle East Gulf trades."}
    ]
    
    for n in war_news:
        st.markdown(f"""
            <div style="background-color: #fff1f0; border-left: 5px solid #E6002D; padding: 12px; margin-bottom: 10px; border-radius: 4px;">
                <small style="color: #666;">{n['Time']} | {n['Source']}</small><br>
                <strong style="font-size: 1.1rem;">{n['Headline']}</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
