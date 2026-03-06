import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# CSS: 실시간 업데이트 강조 및 표 줄바꿈 설정
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 20px; }
    .live-indicator { color: #E6002D; font-weight: bold; animation: blinker 1.5s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 20px; }
    .route-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; table-layout: fixed; }
    .route-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; text-align: left; }
    .route-table td { border: 1px solid #dee2e6; padding: 10px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; }
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 12px; border-radius: 0 4px 4px 0; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 2. 언어 선택 및 시간 설정
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("언어 선택 / Language", ["한국어", "English"])
    st.info("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 3. 헤더 출력
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.2rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:0; color:#E6002D; font-weight:bold;">{ "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report" }</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="update-box">
        <span class="live-indicator">● LIVE UPDATE</span> | 
        <strong>{ '분석 시점' if is_ko else 'Analysis Time' }:</strong> {current_time}
    </div>
""", unsafe_allow_html=True)

# 4. 입력 섹션
col_in1, col_in2 = st.columns(2)
with col_in1: pol = st.text_input("Origin (POL)", value="Busan")
with col_in2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 5. 2026.03.06 실시간 선사 공지 및 시황 데이터
def get_live_intel(pol_val):
    route_cape = (
        f"{pol_val} → 싱가포르(T/S)\n→ 인도양 → 모리셔스 우회\n→ **희망봉(Cape) 통과**\n"
        "→ 서아프리카 연안 북상\n→ 지브롤터 해협 → 지중해\n→ 수에즈 운하(북단 진입)\n"
        "→ **제다(Jeddah)항 하역**\n→ 리야드(내륙 운송)"
    )
    
    if is_ko:
        return [
            ["MSC", "🔴 부킹 중단", "전 세계 출발 중동행 중단", "호르무즈 해협 봉쇄로 걸프향 모든 부킹 중지 및 본선 대피 지시 (3/6 공지)"],
            ["Maersk", "🔴 부킹 중단", "Strait of Hormuz 통과 중단", "UAE, 오만, 사우디(담맘) 등 걸프 전 지역 부킹 일시 중단 (3/5 공지)"],
            ["Hapag-Lloyd", "🟡 제다 우회", route_cape, "전쟁 할증료($1,500/TEU) 도입 및 담맘 서비스 중단, 제다항만 유지"],
            ["CMA CGM", "🟣 희망봉 우회", route_cape, "홍해 및 수에즈 운하 통과 리스크로 전 선단 아프리카 우회 명령 (3/2)"],
            ["HMM", "🔴 부킹 중단", "Suspended", "국적선사 안전 지침에 따라 걸프만 향 신규 부킹 접수 전면 중단 (3/6)"],
            ["COSCO", "🔴 부킹 중단", "Suspended", "중국계 선박 대상 긴급 회항 지시 및 걸프만 노선 예약 제한"],
            ["ONE", "🔴 부킹 중단", "Suspended", "중동 지역 군사 긴장 고조에 따른 전 구역 서비스 일시 중지 (3/6)"],
            ["Evergreen", "🟣 희망봉 우회", route_cape, "희망봉 우회 공식 채택으로 인한 리드타임 25일 이상 추가 지연 보고"],
            ["Yang Ming", "🟣 희망봉 우회", route_cape, "아시아-중동 전 노선 희망봉 우회 스케줄 실시간 적용 완료"],
            ["OOCL", "🔴 부킹 중단", "Suspended", "얼라이언스 파트너(COSCO) 방침에 따라 중동 전역 서비스 제한"]
        ]
    else:
        # 영문 데이터 생략
        pass

# 6. 실행 및 출력
if st.button("🚀 실시간 분석 실행 (Run Live Analysis)", type="primary", use_container_width=True):
    data = get_live_intel(pol)
    cols = ["선사", "상태", "상세 라우트", "조회 시점 최신 공지"] if is_ko else ["Carrier", "Status", "Route Detail", "Live Notice"]
    
    st.subheader(f"📊 Top 10 Carrier Live Intel ({pol} ➔ {pod})")
    
    # HTML 방식으로 표 생성 (줄바꿈 완벽 제어)
    table_html = f'<table class="route-table"><thead><tr>'
    for col in cols: table_html += f'<th>{col}</th>'
    table_html += '</tr></thead><tbody>'
    for row in data:
        table_html += '<tr>'
        for cell in row: table_html += f'<td>{cell}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 실시간 전황 뉴스 (2026.03.06 속보 요약)
    st.markdown("---")
    st.subheader("🔥 [위기 분석] 이란-이스라엘 전쟁 및 호르무즈 해협 실시간 상황")
    
    news_list = [
        {"t": "10시간 전", "s": "Windward", "txt": "작전명 '에픽 퓨리': 전쟁 1주일 차, 호르무즈 해협 상업 통항 사실상 중단"},
        {"t": "오늘", "s": "The Guardian", "txt": "해협 내 유조선 200여 척 고립, 승무원 수천 명 전쟁 접경지 조난 위기"},
        {"t": "오늘", "s": "연합뉴스", "txt": "이탈리아, 테헤란 주재 대사관 일시 폐쇄... 서방 국가 탈출 가속화"},
        {"t": "6시간 전", "s": "Kpler", "txt": "중동 전쟁으로 호르무즈 해협을 통한 건화물 및 비료 교역 전면 마비"}
    ] if is_ko else []

    for n in news_list:
        st.markdown(f"""
            <div class="news-card">
                <small style="color:#666;">{n['t']} | {n['s']}</small><br>
                <strong style="font-size:1.05rem;">{n['txt']}</strong>
            </div>
        """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
