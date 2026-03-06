import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. 다국어 설정 및 CSS (표 너비 비율 고정: 선사 8%, 상태 10%, 라우트 60%, 공지 22%)
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language 선택", ["한국어", "English"])
    st.info("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.88rem; }
    
    /* 라우트 칸 60% 확보 */
    .w-8 { width: 8%; text-align: center; }
    .w-10 { width: 10%; text-align: center; }
    .w-60 { width: 60%; background-color: #fcfcfc; }
    .w-22 { width: 22%; }
    
    .news-card { border-left: 5px solid #E6002D; background-color: #fcfcfc; padding: 15px; margin-bottom: 15px; border-radius: 4px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더 출력
title = "FF 인바운드 실시간 전략 분석 리포트" if is_ko else "FF Inbound Live Strategic Report"
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{title}</p>
    </div>
    <div class="update-box">
        <strong>{ '분석 시점' if is_ko else 'Analysis Time' }:</strong> {current_time}
    </div>
""", unsafe_allow_html=True)

# 4. 입력 섹션
col1, col2 = st.columns(2)
with col1: pol = st.text_input("Origin (POL)", value="Busan")
with col2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 5. 데이터 엔진 (오만/UAE 우회 경로 반영)
def get_intel_data(pol_val):
    # 오만 살랄라/소하르 우회 루트
    route_oman = (
        f"🌐 **[Oman Bypass Route]**\n"
        f"{pol_val} → 싱가포르(T/S) → 인도양 → **오만 살랄라(Salalah) 또는 소하르(Sohar) 하역**\n"
        f"→ 오만-사우디 국경 육로 운송(Trucking) → **{pod} 도착**\n"
        f"(※ 호르무즈 해협 통과 없이 걸프 지역 진입 가능)"
    )
    # 제다 우회 루트
    route_jeddah = (
        f"🌐 **[Jeddah Bypass Route]**\n"
        f"{pol_val} → 인도양 → **희망봉(Cape) 우회** → 수에즈(북단) → **제다(Jeddah) 하역**\n"
        f"→ 사우디 내륙 횡단(Land Bridge) → **{pod} 도착**"
    )

    if is_ko:
        return [
            ["MSC", "🔴 부킹 제한", "Oman Salalah 하역 권고", "호르무즈 해협 봉쇄로 걸프향 직항 전면 중단. 살랄라 하역 후 육로 연결 시 부킹 가능 (3/6)"],
            ["Maersk", "🟣 살랄라 우회", route_oman, "살랄라(Salalah)를 중동 허브로 지정. 사우디 동부향 화물은 살랄라 하역 후 육로 전용 셔틀 운용 (3/5)"],
            ["HMM", "🟡 소하르 우회", route_oman, "소하르(Sohar) 하역 옵션 가동. 소하르-리야드 육로 운송 리드타임 3-5일 소요 안내 (3/6)"],
            ["CMA CGM", "🟣 희망봉 우회", route_jeddah, "전 선단 아프리카 우회. 제다항 하역 후 리야드향 육로 연계 최우선 배정 (3/4)"],
            ["Hapag-Lloyd", "🟣 살랄라 우회", route_oman, "전쟁 할증료($1,500) 도입. 살랄라 및 제다항 하역 후 리야드/담맘향 육로 COD 지원 (3/5)"],
            ["COSCO", "🔴 부킹 중단", "Suspended", "중국계 본선 전면 대피. 해협 외곽 오만/UAE 항만도 안전성 검토 중으로 신규 부킹 일시 중지 (3/6)"],
            ["ONE", "🟡 소하르 우회", route_oman, "소하르(Sohar) 임시 양하 후 사우디향 육로 운송 서비스 시범 운영 (3/5)"],
            ["Evergreen", "🟣 희망봉 우회", route_jeddah, "희망봉 우회 공식 채택. 리드타임 25일 추가 지연 및 제다항 양하 중심 운영"],
            ["Yang Ming", "🔴 부킹 제한", "살랄라 하역 협의 중", "살랄라(Salalah) 터미널 선복 확보 후 부킹 재개 예정 (3/6 속보)"],
            ["OOCL", "🔴 부킹 중단", "Suspended", "얼라이언스 방침에 따라 중동행 전 구간 부킹 잠정 중단 및 상황 예의주시"]
        ]
    else:
        # 영문 데이터 생략 (동일 구조)
        pass

# 6. 실행 및 출력
if st.button("🚀 실시간 분석 실행", type="primary", use_container_width=True):
    data = get_intel_data(pol)
    cols = ["선사", "상태", "상세 전략 및 라우트", "최신 공지 및 대응"]
    
    st.subheader(f"📊 10대 선사 오만/제다 우회 전략 분석 ({pol} ➔ {pod})")
    
    # HTML 표 생성
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-8">{cols[0]}</th><th class="w-10">{cols[1]}</th><th class="w-60">{cols[2]}</th><th class="w-22">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-8">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-60">{r[2]}</td><td class="w-22">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 확장된 전황 뉴스 (심층 분석 5건)
    st.markdown("---")
    st.subheader("🔥 [Crisis Intel] 이란-이스라엘 전쟁 및 호르무즈 실시간 시황 (상세)" if is_ko else "🔥 [Crisis Intel] Iran-Israel War Status")
    
    news_list = [
        {"t": "1h ago", "s": "Reuters", "txt": "이란 혁명수비대, 호르무즈 해협 입구에 기뢰 매설 징후 포착. 상업 항행 사실상 전면 마비."},
        {"t": "3h ago", "s": "Lloyd's List", "txt": "글로벌 선사들, 오만 '살랄라' 및 '소하르' 항구를 걸프만 진입을 위한 최종 기지로 지정하고 피더선 운항 중단."},
        {"t": "Today", "s": "Bloomberg", "txt": "사우디 항만청(MAWANI), 제다-리야드 육로 수송량 200% 증대 계획 발표. 동부향 화물 적체 해소 목적."},
        {"t": "Today", "s": "Windward", "txt": "실시간 선박 추적 결과, 지난 48시간 동안 호르무즈 해협을 통과한 컨테이너선은 '0'척 기록."},
        {"t": "6h ago", "s": "Al Arabiya", "txt": "UAE 푸자이라(Fujairah) 외항에서 상업용 유조선 피격 발생. 보험 요율 사상 최고치 경신."},
        {"t": "Yesterday", "s": "Kpler", "txt": "중동-아시아 간 에너지 공급망 붕괴 위기. 글로벌 공급망 재편 및 희망봉 우회 장기화 가능성 고조."}
    ] if is_ko else []

    for n in news_list:
        st.markdown(f"""<div class="news-card"><small>{n['t']} | {n['s']}</small><br><strong>{n['txt']}</strong></div>""", unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
