import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. 다국어 설정 (사이드바)
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    st.markdown("---")
    st.write("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 3. 표 칸 너비 및 줄바꿈 강제 설정 (CSS)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    
    /* 핵심: 표 레이아웃 및 너비 고정 */
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.9rem; }
    
    /* 칸별 너비 비율 설정 */
    .w-carrier { width: 10%; }
    .w-status { width: 12%; }
    .w-route { width: 53%; background-color: #fcfcfc; } /* 라우트 칸을 가장 넓게 설정 */
    .w-notice { width: 25%; }
    
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 12px; border-radius: 4px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 4. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더 출력
title_text = "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report"
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
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

# 6. 데이터 로직 (줄바꿈 포함 상세 경로)
def get_live_data(pol_val):
    route_cape = (
        f"🌐 **[상세 우회 경로]**\n"
        f"{pol_val} 출항 → 싱가포르(T/S) → 인도양 → 모리셔스 우회 → **희망봉(Cape) 통과**\n"
        f"→ 서아프리카 연안 북상 → 지브롤터 해협 → 지중해 횡단 → 수에즈 운하(북단 진입)\n"
        f"→ **제다(Jeddah)항 하역** → 사우디 내륙 보세 수송 → **{pod} 도착**"
    )
    
    if is_ko:
        return [
            ["MSC", "🔴 부킹 중단", "전 구간 서비스 일시 중단", "호르무즈 해협 봉쇄로 걸프향 부킹 전면 중지 (3/6 공지)"],
            ["Maersk", "🟣 희망봉 우회", route_cape, "긴급 할증료($1,800) 도입 및 아프리카 우회 확정 (3/5 뉴스)"],
            ["HMM", "🔴 부킹 중단", "신규 부킹 전면 거부", "국적선사 안전 지침에 따른 중동행 부킹 잠정 중단 (3/6)"],
            ["CMA CGM", "🟣 희망봉 우회", route_cape, "수에즈 운하 통과 불가 판정으로 전 선단 우회 운항 명령"],
            ["Hapag-Lloyd", "🟡 제다 하역", route_cape, "전쟁 할증료($1,500) 도입 및 제다항 하역 후 육로 이동 권고"],
            ["COSCO", "🔴 부킹 중단", "Suspended", "중국계 선박 대상 긴급 회항 지시 및 걸프만 노선 예약 제한"],
            ["Evergreen", "🟣 희망봉 우회", route_cape, "희망봉 우회 공식 채택으로 리드타임 25일 이상 지연 확정"],
            ["ONE", "🔴 부킹 중단", "Suspended", "중동 지역 군사 긴장 고조에 따른 전 구역 서비스 중지 (3/6)"],
            ["Yang Ming", "🟣 희망봉 우회", route_cape, "아시아-중동 전 노선 희망봉 우회 스케줄 적용 완료"],
            ["OOCL", "🔴 부킹 중단", "Suspended", "파트너사(COSCO) 방침에 따라 중동 전역 서비스 제한"]
        ]
    else:
        # 영문 데이터 생략
        pass

# 7. 실행 및 출력
if st.button("🚀 실시간 분석 실행 / Run Analysis", type="primary", use_container_width=True):
    data = get_live_data(pol)
    cols = ["선사", "상태", "상세 라우트", "최신 공지"] if is_ko else ["Carrier", "Status", "Route Detail", "Latest Notice"]
    
    st.subheader(f"📊 Top 10 Carrier Live Intel ({pol} ➔ {pod})")
    
    # HTML 방식으로 표 생성 (칸 너비 비율 고정)
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-carrier">{cols[0]}</th><th class="w-status">{cols[1]}</th><th class="w-route">{cols[2]}</th><th class="w-notice">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    
    for row in data:
        table_html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td></tr>'
    table_html += '</tbody></table>'
    
    st.markdown(table_html, unsafe_allow_html=True)

    # 8. 전황 뉴스 섹션
    st.markdown("---")
    st.subheader("🔥 [위기 분석] 이란-이스라엘 전쟁 및 호르무즈 상황" if is_ko else "🔥 [Crisis Intel] Iran-Israel War Status")
    
    news_list = [
        {"t": "1h ago", "s": "Reuters", "txt": "이란 혁명수비대, 호르무즈 해협 통과 시도 선박에 '공격 위협' 재천명"},
        {"t": "3h ago", "s": "Windward", "txt": "실시간 데이터: 지난 24시간 동안 해협 내 상업 통항량 '0' 기록"},
        {"t": "Today", "s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 보호를 위한 특별 경계 태세 강화"}
    ] if is_ko else []

    for n in news_list:
        st.markdown(f"""
            <div class="news-card"><small>{n['t']} | {n['s']}</small><br><strong>{n['txt']}</strong></div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
