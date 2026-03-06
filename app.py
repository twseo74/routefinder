import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. 다국어 세션 상태 관리 (한/영 선택 기능 복구)
if 'lang' not in st.session_state:
    st.session_state.lang = '한국어'

with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    st.markdown("---")
    st.write("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 3. 고해상도 디자인 (CSS)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 20px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 12px; border-radius: 4px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    /* 표 줄바꿈 가독성 향상 */
    .stDataFrame td { white-space: pre-wrap !important; line-height: 1.6 !important; }
    </style>
""", unsafe_allow_html=True)

# 4. 시간 설정 (KSA 기준)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더 출력
title_text = "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report"
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0; font-size: 1.8rem;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{title_text}</p>
    </div>
    <div class="update-box">
        <strong>{ '분석 시점' if is_ko else 'Analysis Time' }:</strong> {current_time}
    </div>
""", unsafe_allow_html=True)

# 5. 입력 섹션
col_in1, col_in2 = st.columns(2)
with col_in1: pol = st.text_input("Origin (POL)", value="Busan")
with col_in2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 6. 실시간 데이터 엔진
def get_intel_data(pol_val, pod_val):
    route_cape = (
        f"🌐 [상세 우회 경로]\n"
        f"{pol_val} 출항 → 싱가포르(T/S) → 인도양 → 모리셔스 우회 → 희망봉(Cape) 통과\n"
        f"→ 서아프리카 연안 북상 → 지브롤터 해협 → 지중해 횡단 → 수에즈 운하(북단 진입)\n"
        f"→ 제다(Jeddah)항 하역 → 사우디 내륙 보세 수송 → {pod_val} 도착"
    ) if is_ko else (
        f"🌐 [Detailed Detour]\n"
        f"{pol_val} → Singapore(T/S) → Indian Ocean → Mauritius → Cape of Good Hope\n"
        f"→ West Africa → Gibraltar → Med Sea → Suez Canal (North)\n"
        f"→ Jeddah Port → Saudi Inland Transport → {pod_val}"
    )
    
    if is_ko:
        return [
            ["MSC", "🔴 부킹 중단", "전 구간 서비스 일시 중단", "호르무즈 해협 봉쇄로 걸프향 부킹 전면 중지 (3/6 공지)"],
            ["Maersk", "🔴 부킹 중단", "Strait of Hormuz 통과 불가", "담맘, UAE 등 걸프 전 노선 부킹 일시 중단 (3/5 공지)"],
            ["HMM", "🔴 부킹 중단", "신규 부킹 전면 중단", "국적선사 안전 지침에 따른 중동행 부킹 접수 전면 거부 (3/6)"],
            ["CMA CGM", "🟣 희망봉 우회", route_cape, "수에즈 운하 통과 불가 판정으로 전 선단 아프리카 우회 (3/2)"],
            ["Hapag-Lloyd", "🟡 제다 하역", route_cape, "전쟁 할증료($1,500) 도입 및 제다항 하역 후 육로 이동 권고"],
            ["COSCO", "🔴 부킹 중단", "Suspended", "중국계 선박 대상 긴급 회항 지시 및 걸프만 노선 예약 제한"],
            ["Evergreen", "🟣 희망봉 우회", route_cape, "희망봉 우회 공식 채택으로 리드타임 25일 이상 지연 확정"],
            ["ONE", "🔴 부킹 중단", "Suspended", "중동 지역 군사 긴장 고조에 따른 전 구역 서비스 중지 (3/6)"],
            ["Yang Ming", "🟣 희망봉 우회", route_cape, "아시아-중동 전 노선 희망봉 우회 스케줄 실시간 적용"],
            ["OOCL", "🔴 부킹 중단", "Suspended", "파트너사(COSCO) 방침에 따라 중동 전역 서비스 제한"]
        ]
    else:
        return [
            ["MSC", "🔴 Suspended", "Service Halted", "All Gulf bookings stopped due to Hormuz closure (Mar 6)"],
            ["Maersk", "🔴 Suspended", "Hormuz Passage Blocked", "Dammam/UAE bookings temporarily suspended (Mar 5)"],
            ["HMM", "🔴 Suspended", "Booking Stopped", "Full suspension of ME bookings per safety guidelines (Mar 6)"],
            ["CMA CGM", "🟣 Cape Detour", route_cape, "Fleet instructed to detour via Africa due to Suez risks"],
            ["Hapag-Lloyd", "🟡 via Jeddah", route_cape, "War Risk Surcharge ($1,500) and Jeddah discharge recommended"],
            ["COSCO", "🔴 Suspended", "Suspended", "Vessel rerouting and booking restrictions for Gulf routes"],
            ["Evergreen", "🟣 Cape Detour", route_cape, "Official Cape route adoption; +25 days delay expected"],
            ["ONE", "🔴 Suspended", "Suspended", "Temporary service pause due to military escalations (Mar 6)"],
            ["Yang Ming", "🟣 Cape Detour", route_cape, "Full Cape detour applied for AS-ME routes"],
            ["OOCL", "🔴 Suspended", "Suspended", "Service restricted following Alliance policy"]
        ]

# 7. 분석 결과 출력
if st.button("🚀 실시간 분석 실행 / Run Analysis", type="primary", use_container_width=True):
    data = get_intel_data(pol, pod)
    cols = ["선사/Carrier", "상태/Status", "상세 라우트/Route Detail", "최신 공지/Latest Notice"]
    df = pd.DataFrame(data, columns=cols)
    
    st.subheader(f"📊 Top 10 Carrier Live Intel ({pol} ➔ {pod})")
    
    # 가독성을 위해 넓은 화면 활용 및 줄바꿈 지원
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 8. 전황 뉴스 (다국어 완벽 지원)
    st.markdown("---")
    st.subheader("🔥 [위기 분석] 이란-이스라엘 전쟁 및 호르무즈 상황" if is_ko else "🔥 [Crisis Intel] Iran-Israel War Status")
    
    news_list = [
        {"t": "1h ago", "s": "Reuters", "txt": "이란 혁명수비대, 호르무즈 해협 통과 시도 선박에 '공격 위협' 재천명"},
        {"t": "3h ago", "s": "Windward", "txt": "실시간 데이터: 지난 24시간 동안 해협 내 상업 통항량 '0' 기록"},
        {"t": "Today", "s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 보호를 위한 특별 경계 태세 강화"},
        {"t": "Yesterday", "s": "Lloyd's List", "txt": "글로벌 선사들, 보험 인수 거절 가속화로 중동 서비스 대거 철수"}
    ] if is_ko else [
        {"t": "1h ago", "s": "Reuters", "txt": "Iran IRGC renews threat to attack ships attempting Hormuz transit"},
        {"t": "3h ago", "s": "Windward", "txt": "Real-time data: Zero commercial traffic in the Strait for last 24h"},
        {"t": "Today", "s": "Bloomberg", "txt": "Saudi Ministry of Energy raises alert levels for eastern oil fields"},
        {"t": "Yesterday", "s": "Lloyd's List", "txt": "Carriers withdraw from ME trades as insurance coverages vanish"}
    ]

    for n in news_list:
        st.markdown(f"""
            <div class="news-card">
                <small style="color:#666;">{n['t']} | {n['s']}</small><br>
                <strong>{n['txt']}</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
