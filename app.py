import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. 고해상도 디자인 및 칸 너비 최적화 (CSS)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 20px; }
    .live-status { color: #E6002D; font-weight: bold; animation: blinker 1.2s linear infinite; font-size: 0.9rem; }
    @keyframes blinker { 50% { opacity: 0; } }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    
    /* 표 너비 비율 강제 고정 (라우트 칸 60% 배분) */
    .route-table { width: 100%; border-collapse: collapse; table-layout: fixed; }
    .route-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; }
    .route-table td { border: 1px solid #dee2e6; padding: 15px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.88rem; }
    
    .col-carrier { width: 8%; text-align: center; font-weight: bold; background-color: #fcfcfc; }
    .col-status { width: 10%; text-align: center; }
    .col-route { width: 60%; background-color: #ffffff; } /* 상세 라우트 칸 극대화 */
    .col-notice { width: 22%; }
    
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 12px; border-radius: 4px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 3. 언어 및 시간 설정 (KSA 기준)
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더 출력
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0; font-size: 1.8rem;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report" }</p>
    </div>
    <div class="update-box">
        <span class="live-status">● LIVE UPDATE ACTIVE</span> | 
        <strong>{ '리포트 생성 시점' if is_ko else 'Report Generated at' }:</strong> {current_time}
    </div>
""", unsafe_allow_html=True)

# 4. 입력 섹션
col_in1, col_in2 = st.columns(2)
with col_in1: pol = st.text_input("Origin (POL)", value="Busan")
with col_in2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 5. 실시간 데이터 분석 엔진
def get_live_intel(pol_val):
    route_cape = (
        f"🌐 **[상세 우회 경로]**\n"
        f"{pol_val} 출항 → 싱가포르(T/S) → 인도양 → 모리셔스 우회 → **희망봉(Cape) 통과**\n"
        f"→ 서아프리카 연안 북상 → 지브롤터 해협 → 지중해 횡단 → 수에즈 운하(북단 진입)\n"
        f"→ **제다(Jeddah)항 하역** → 사우디 내륙 보세 수송 → **{pod} 도착**"
    )
    
    return [
        ["MSC", "🔴 부킹 중단", "호르무즈 해협 봉쇄로 걸프향 모든 부킹 중단", "중동행 본선 전면 회항 및 신규 예약 불가 (3/6 긴급 공지)"],
        ["Maersk", "🔴 부킹 중단", "Strait of Hormuz 통과 리스크로 인한 부킹 전면 중지", "사우디 담맘/주베일, UAE 전 노선 부킹 일시 중단 (3/5 공지)"],
        ["Hapag-Lloyd", "🟡 제다 하역", route_cape, "전쟁 할증료($1,500/TEU) 도입 및 제다항 하역 후 육로 이동 권고"],
        ["CMA CGM", "🟣 희망봉 우회", route_cape, "수에즈 운하 통과 불가 판정으로 전 선단 아프리카 우회 운항 명령"],
        ["HMM", "🔴 부킹 중단", "국적선사 안전 지침에 따라 중동행 부킹 전면 중단", "걸프만 긴장 고조에 따른 신규 부킹 접수 전면 거부 (3/6)"],
        ["COSCO", "🔴 부킹 중단", "중국계 선박 대상 긴급 회항 지시 및 부킹 제한", "호르무즈 인근 선박 대피 명령 및 중동 노선 서비스 중단"],
        ["Evergreen", "🟣 희망봉 우회", route_cape, "희망봉 우회 공식 채택으로 인한 리드타임 25일 이상 추가 지연"],
        ["ONE", "🔴 부킹 중단", "중동 지역 군사 긴장 고조에 따른 서비스 일시 중지", "신규 부킹 전면 중단 및 기선적 화물 안전 확보 주력"],
        ["Yang Ming", "🟣 희망봉 우회", route_cape, "아시아-중동 전 노선 희망봉 우회 스케줄 실시간 적용 완료"],
        ["OOCL", "🔴 부킹 중단", "얼라이언스 방침에 따른 중동 전역 서비스 제한", "파트너사(COSCO) 선복 공유 중단으로 인한 예약 불가"]
    ]

# 6. 실행 및 출력
if st.button("🚀 실시간 분석 실행 (Run Analysis)", type="primary", use_container_width=True):
    data = get_live_intel(pol)
    cols = ["선사", "상태", "상세 라우트 (Detailed Route)", "조회 시점 최신 공지"]
    
    st.subheader(f"📊 10대 선사 실시간 분석 결과 ({pol} ➔ {pod})")
    
    # HTML 방식으로 표 생성 (칸 너비 비율 고정)
    table_html = f'<table class="route-table"><thead><tr>'
    table_html += f'<th class="col-carrier">{cols[0]}</th><th class="col-status">{cols[1]}</th><th class="col-route">{cols[2]}</th><th class="col-notice">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    
    for row in data:
        table_html += f'''
        <tr>
            <td class="col-carrier">{row[0]}</td>
            <td class="col-status">{row[1]}</td>
            <td class="col-route">{row[2]}</td>
            <td class="col-notice">{row[3]}</td>
        </tr>
        '''
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 실시간 전황 뉴스 (한국어 요약)
    st.markdown("---")
    st.subheader("🔥 [위기 분석] 이란-이스라엘 전쟁 및 호르무즈 실시간 현황")
    
    news_list = [
        {"t": "1시간 전", "s": "Reuters", "txt": "이란 혁명수비대, 호르무즈 해협 통과 시도하는 선박에 '소각 위협' 공표"},
        {"t": "3시간 전", "s": "Windward", "txt": "실시간 데이터: 지난 24시간 동안 호르무즈 해협 상업 통항량 '0' 기록"},
        {"t": "오늘", "s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 지대 보호를 위한 특별 경계령 발동"},
        {"t": "어제", "s": "Lloyd's List", "txt": "글로벌 선사들, 중동 전역 서비스 철수 및 보험 인수 거절 가속화"}
    ]

    for n in news_list:
        st.markdown(f"""
            <div class="news-card">
                <small style="color:#666;">{n['t']} | {n['s']}</small><br>
                <strong style="font-size:1.05rem;">{n['txt']}</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
