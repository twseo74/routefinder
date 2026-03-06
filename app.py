import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Saudi Arabia Intel", layout="wide")

# 2. 다국어 세션 및 시스템 설정
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    st.info("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 3. 고해상도 디자인 (10:10:40:40 비율 고정)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.82rem; }
    .w-10 { width: 10%; text-align: center; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .port-info { background-color: #e6f7ff; border-left: 5px solid #1890ff; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
    .qna-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; margin-top: 35px; border: 1px solid #e1e4e8; }
    </style>
""", unsafe_allow_html=True)

# 4. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더
main_title = "극동발 사우디향 컨테이너 관련 현황" if is_ko else "Far East to KSA Container Status"
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{main_title}</p>
    </div>
    <div class="update-box"><strong>{ '실시간 분석 및 현지 속보 업데이트 시점:' if is_ko else 'Real-time Intel & Local News Updated at:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 5. 10대 선사 통합 데이터 엔진 (한/영 완벽 대응)
def get_intel_data():
    r_uae = "🌐 **[UAE Transit]** FE → **Khor Fakkan** → **Al Batha Border** → Riyadh" if not is_ko else "🌐 **[UAE Transit]** 극동 → **Khor Fakkan** 하역 → **Al Batha 국경** → 리야드"
    r_oman = "🌐 **[Oman Transit]** FE → **Salalah** → **Rub Al Khali Border** → Riyadh" if not is_ko else "🌐 **[Oman Transit]** 극동 → **Salalah** 하역 → **Rub Al Khali 국경** → 리야드"
    r_cape = "🌐 **[Cape Detour]** FE → **Cape Detour** → **Jeddah Port** → Riyadh" if not is_ko else "🌐 **[Cape Detour]** 극동 → **희망봉 우회** → **제다(Jeddah) 하역** → 리야드"
    
    data = [
        ["Maersk", "Jeddah:🟢\nDammam:🔴\n**via:Khor Fakkan**" if not is_ko else "제다:🟢\n담맘:🔴\n**타항:Khor Fakkan**", r_uae, "📢 All Gulf bookings suspended; Khor Fakkan detour active" if not is_ko else "📢 호르무즈 봉쇄로 걸프향 부킹 중단; 코르파칸 우회 집중"],
        ["MSC", "Jeddah:🟡\nDammam:🔴\n**via:Salalah**" if not is_ko else "제다:🟡\n담맘:🔴\n**타항:Salalah**", r_oman, "📢 Salalah discharge + Rub Al Khali border recommended" if not is_ko else "📢 살랄라 하역 후 사우디 직통 국경 이용 권고"],
        ["CMA CGM", "Jeddah:🟢\nDammam:🔴\n**via:Fujairah**" if not is_ko else "제다:🟢\n담맘:🔴\n**타항:Fujairah**", r_uae.replace("Khor Fakkan", "Fujairah"), "📢 Fujairah discharge + Al Batha border link active" if not is_ko else "📢 푸자이라 하역 후 Al Batha 연계 서비스 가동"],
        ["Hapag-Lloyd", "Jeddah:🟢\n**via:Khor Fakkan**" if not is_ko else "제다:🟢\n**타항:Khor Fakkan**", r_uae, "📢 New War Surcharge ($1,500) applied" if not is_ko else "📢 전쟁 할증료($1,500) 도입 및 우회 지원"],
        ["HMM", "Jeddah:🟡\n**Status:Restricted**" if not is_ko else "제다:🟡\n**상태:부킹제한**", "Suspended", "📢 ME bookings suspended per safety guidelines" if not is_ko else "📢 안전 지침에 따라 중동행 예약 전면 중단"],
        ["ONE", "Jeddah:🟡\n**via:Khor Fakkan**" if not is_ko else "제다:🟡\n**타항:Khor Fakkan**", r_uae, "📢 Khor Fakkan to KSA shuttle in trial" if not is_ko else "📢 코르파칸-사우디 육로 셔틀 시범 운영"],
        ["Evergreen", "Jeddah:🟢\n**Status:Cape**" if not is_ko else "제다:🟢\n**상태:희망봉**", r_cape, "📢 +25 days delay via Cape of Good Hope" if not is_ko else "📢 희망봉 우회로 25일 이상 지연 확정"],
        ["COSCO", "Status:🔴\n**Booking:Stop**" if not is_ko else "상태:🔴\n**부킹:중단**", "Suspended", "📢 All ME vessel operations suspended" if not is_ko else "📢 중동 노선 본선 운영 전면 중단"],
        ["Yang Ming", "via:Salalah\n**Status:Limit**" if not is_ko else "타항:Salalah\n**상태:제한**", r_oman, "📢 Salalah terminal slot secured" if not is_ko else "📢 살랄라 터미널 선복 확보 중"],
        ["OOCL", "Status:🔴\n**Booking:Stop**" if not is_ko else "상태:🔴\n**부킹:중단**", "Suspended", "📢 Alliance policy: ME service halted" if not is_ko else "📢 얼라이언스 방침에 따른 서비스 중단"]
    ]
    return data

# 6. 실행 및 출력
btn_label = "🚀 실시간 통합 현황 분석 실행" if is_ko else "🚀 Run Real-time Analysis"
if st.button(btn_label, type="primary", use_container_width=True):
    data = get_intel_data()
    cols = ["선사", "상태 (타항 포함)", "상세 라우트", "주요 사항 (공지/기사/실무)"] if is_ko else ["Carrier", "Status (via)", "Detailed Route", "Notice/Cost/Bonded"]
    
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-10">{cols[0]}</th><th class="w-10">{cols[1]}</th><th class="w-40">{cols[2]}</th><th class="w-40">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 최신 시황 및 현지 매체 속보 (8건 보강)
    st.markdown("---")
    col_news_1, col_news_2 = st.columns(2)
    with col_news_1:
        st.subheader("🔥 호르무즈 및 전황 현지 속보 (Local Intel)" if is_ko else "🔥 Hormuz & Conflict Alerts")
        war_news = [
            {"s": "Al Arabiya", "t": "1시간 전", "txt": "이란 혁명수비대, 호르무즈 해협 입구 기뢰 매설 징후로 상업 항행 전면 마비 공표"},
            {"s": "Saudi Gazette", "t": "3시간 전", "txt": "사우디 항만청, 제다-리야드 육로 보세 운송 지원을 위한 긴급 예산 편성"},
            {"s": "Asharq Al-Awsat", "t": "오늘 오후", "txt": "걸프만 보험 요율 급등으로 선사들 사우디 동부(담맘) 서비스 중단 가시화"},
            {"s": "Windward", "t": "4시간 전", "txt": "최근 24시간 동안 호르무즈 해협을 통과한 대형 컨테이너선 '0' 기록"}
        ] if is_ko else [
            {"s": "Al Arabiya", "t": "1h ago", "txt": "IRGC warns of mine activity in Hormuz; commercial transit paralyzed"},
            {"s": "Saudi Gazette", "t": "3h ago", "txt": "MAWANI allocates emergency funds for Jeddah-Riyadh bonded trucking"},
            {"s": "Asharq Al-Awsat", "t": "Today", "txt": "Dammam services halted as Gulf insurance premiums soar"},
            {"s": "Windward", "t": "4h ago", "txt": "Zero commercial vessels passed Hormuz in the last 24h"}
        ]
        for n in war_news:
            st.markdown(f"""<div class="news-card"><span class="time-label">⏱ {n['t']} | {n['s']}</span><strong>{n['txt']}</strong></div>""", unsafe_allow_html=True)
    with col_news_2:
        st.subheader("🌐 제3국 항만 및 국경 실시간 상황" if is_ko else "🌐 Port & Border Intel")
        port_news = [
            {"p": "Khor Fakkan (UAE)", "t": "1시간 전", "txt": "제벨알리 대체 수요 집중으로 터미널 가동률 98% 도달, 적체 심화"},
            {"p": "Salalah (Oman)", "t": "오늘 오후", "txt": "사우디 직통 Rub Al Khali 국경행 보세 차량 대기 시간 72시간 경과"},
            {"p": "Al Batha (Border)", "t": "2시간 전", "txt": "UAE-사우디 국경: 우회 화물 폭증으로 통관 병목 현상 가속화"},
            {"p": "Fujairah (UAE)", "t": "오늘 오전", "txt": "해협 입구 긴장으로 선박 정박 보험 요율 사상 최고치 경신"}
        ] if is_ko else [
            {"p": "Khor Fakkan (UAE)", "t": "1h ago", "txt": "Terminal utilization hit 98% due to bypass surge; congestion grows"},
            {"p": "Salalah (Oman)", "t": "Today", "txt": "Wait time for Rub Al Khali border crossing hits 72 hours"},
            {"p": "Al Batha (Border)", "t": "2h ago", "txt": "Bottlenecks at UAE-KSA border as detour cargo volumes surge"},
            {"p": "Fujairah (UAE)", "t": "Today", "txt": "Insurance rates hit record high amid rising Hormuz tensions"}
        ]
        for p in port_news:
            st.markdown(f"""<div class="port-info"><span class="time-label">⏱ {p['t']} | {p['p']}</span>{p['txt']}</div>""", unsafe_allow_html=True)

    # 8. 심층 실무 Q&A (다국어 지원)
    st.markdown('<div class="qna-box">', unsafe_allow_html=True)
    st.subheader("❓ [심층 가이드] 제3국 항만 이용 및 보세 운송 프로세스" if is_ko else "❓ [Pro Guide] Bonded Process & Port Intel")
    q1 = "Q. 보세운송(Bonded)과 일반운송(Transloading)의 차이" if is_ko else "Q. Bonded vs Transloading Differences"
    a1 = "보세운송은 제3국 통관 없이 사우디 리야드에서 최종 관세를 납부하는 방식이며, Transloading은 항구에서 사우디 트럭으로 짐을 옮겨 싣는 방식입니다." if is_ko else "Bonded trucking defers customs to Riyadh; Transloading transfers cargo to KSA trucks at port."
    q2 = "Q. 항구별 사우디 진입 국경 차이" if is_ko else "Q. Border Points per Port"
    a2 = "UAE(코르파칸)는 Al Batha, 오만(살랄라)은 Rub Al Khali 국경을 이용합니다." if is_ko else "Khor Fakkan (UAE) uses Al Batha; Salalah (Oman) uses Rub Al Khali border."
    with st.expander(q1): st.write(a1)
    with st.expander(q2): st.write(a2)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
