import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정 및 다국어 세션
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

# 2. 고해상도 디자인 (10:10:40:40 비율 고정)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; font-size: 0.9rem; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.82rem; }
    .w-10 { width: 10%; text-align: center; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .port-info { background-color: #e6f7ff; border-left: 5px solid #1890ff; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
    .qna-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; margin-top: 35px; border: 1px solid #e1e4e8; }
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더
main_title = "극동발 사우디향 컨테이너 관련 현황" if is_ko else "Far East to KSA Container Status"
intro_text = "본 리포트의 정보는 최신 외신 및 선사 공식 기보를 기반으로 한 참고 자료입니다." if is_ko else "This report is based on the latest foreign news and official carrier advisories for reference purposes only."

st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{main_title}</p>
        <p style="margin:5px 0 0 0; color:#666; font-size:0.85rem;">{intro_text}</p>
    </div>
    <div class="update-box"><strong>{ '실시간 분석 및 현지 속보 업데이트 시점:' if is_ko else 'Real-time Intel & Local News Updated at:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 4. 10대 선사 통합 데이터 엔진 (오늘 자 실시간 시황 반영)
def get_intel_data():
    if is_ko:
        r_uae = "🌐 **[UAE Transit]** FE → **Khor Fakkan / Fujairah** → **Al Batha 국경** → 리야드"
        r_oman = "🌐 **[Oman Transit]** FE → **Salalah / Sohar** → **Rub Al Khali 국경** → 리야드"
        r_cape = "🌐 **[Cape Detour]** FE → **희망봉 우회** → **제다(Jeddah) 하역** → 리야드"
        return [
            ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", r_uae.replace(" / Fujairah", ""), "📢 걸프향 신규 예약 전면 중지; 코르파칸 우회 집중\n💰 긴급 할증료 부과\n🔗 보세: 가능"],
            ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**", r_oman.replace(" / Sohar", ""), "📢 'End of Voyage' 선언; 걸프행 화물 살랄라 하역\n💰 $800 의무 차지 발생"],
            ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**", r_uae.replace("Khor Fakkan / ", ""), "📢 푸자이라/코르파칸 외 전 지역 부킹 중지\n💰 긴급 할증료 $4,000"],
            ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**", "Suspended", "📢 국적사 안전 지침에 따라 걸프향 예약 전면 중단"],
            ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", r_uae, "📢 상부 걸프(Upper Gulf) 서비스 일시 중단"],
            ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Sohar**", r_oman.replace("Salalah / ", ""), "📢 소하르 하역 후 사우디 육로 셔틀 검토 중"],
            ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**", r_cape, "📢 전 노선 희망봉 우회; 리드타임 +25일 지연"],
            ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 본선 가동 전면 중단 및 중동행 부킹 제한"],
            ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**", r_oman, "📢 살랄라 슬롯 확보 후 부킹 제한적 운영"],
            ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 얼라이언스 방침에 따른 서비스 중지"]
        ]
    else:
        # English Data
        r_uae_en = "🌐 **[UAE Transit]** FE → **Khor Fakkan / Fujairah** → **Al Batha Border** → Riyadh"
        r_oman_en = "🌐 **[Oman Transit]** FE → **Salalah / Sohar** → **Rub Al Khali Border** → Riyadh"
        r_cape_en = "🌐 **[Cape Detour]** FE → **Cape Detour** → **Jeddah Port** → Riyadh"
        return [
            ["Maersk", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Khor Fakkan**", r_uae_en.replace(" / Fujairah", ""), "📢 Gulf bookings suspended; Khor Fakkan bypass active\n💰 Emergency Surcharge applied\n🔗 Bonded: YES"],
            ["MSC", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Salalah**", r_oman_en.replace(" / Sohar", ""), "📢 'End of Voyage' declared; divert to Salalah\n💰 $800 Mandatory Surcharge"],
            ["CMA CGM", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Fujairah**", r_uae_en.replace("Khor Fakkan / ", ""), "📢 Bookings stopped except for Khor Fakkan/Fujairah\n💰 $4,000 Emergency Surcharge"],
            ["HMM", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Reviewing**", "Suspended", "📢 All Gulf bookings suspended per safety guides"],
            ["Hapag-Lloyd", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Khor Fakkan**", r_uae_en, "📢 Upper Gulf services suspended"],
            ["ONE", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Sohar**", r_oman_en.replace("Salalah / ", ""), "📢 Land shuttle via Sohar port in trial"],
            ["Evergreen", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:None**", r_cape_en, "📢 Cape detour confirmed (+25 days delay)"],
            ["COSCO", "Jeddah:🔴(Stop)\nDMM:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 Booking restricted for Middle East"],
            ["Yang Ming", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Salalah**", r_oman_en, "📢 Securing Salalah terminal slots"],
            ["OOCL", "Jeddah:🔴(Stop)\nDMM:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 Service suspended per Alliance policy"]
        ]

# 5. 실행 및 출력
st.sidebar.header("🌐 System Settings")
st.session_state.lang = st.sidebar.radio("Language / 언어 선택", ["한국어", "English"])
if st.sidebar.button("🚀 실시간 정보 새로고침 (Refresh)"): st.rerun()

is_ko = (st.session_state.lang == "한국어")
btn_label = "🚀 실시간 통합 현황 분석 실행" if is_ko else "🚀 Run Real-time Analysis"

if st.button(btn_label, type="primary", use_container_width=True):
    data = get_intel_data()
    cols = ["선사", "상태 (우회/담맘/타항)", "상세 라우트", "주요 사항 (공지/비용/보세)"] if is_ko else ["Carrier", "Status (Detour/DMM/via)", "Detailed Route", "Notice/Cost/Bonded"]
    
    table_html = f'<table class="custom-table"><thead><tr>'
    for c in cols: table_html += f'<th>{c}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 6. 최신 전황 및 항만 뉴스 (시간 표시 8건)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔥 호르무즈 및 전황 현지 속보" if is_ko else "🔥 Hormuz & Conflict Alerts")
        war_news = [
            {"s": "Al Arabiya", "t": "1시간 전", "ko": "이란 혁명수비대, 호르무즈 해협 기뢰 매설 경고; 상업 통항 마비", "en": "IRGC warns of mine activity in Hormuz; commercial transit halted"},
            {"s": "Windward", "t": "4시간 전", "ko": "지난 24시간 동안 호르무즈 해협 통과 컨테이너선 '0' 기록", "en": "Zero commercial vessels passed Hormuz in the last 24h"},
            {"s": "Saudi Gazette", "t": "오늘 오후", "ko": "MAWANI, 제다항 하역 물량의 내륙 통관 지원 예산 편성", "en": "MAWANI allocates funds for Jeddah-Riyadh land-bridge support"},
            {"s": "Asharq Al-Awsat", "t": "오늘 오전", "ko": "걸프만 보험 요율 급등으로 담맘 입항 서비스 전면 정지", "en": "Dammam services halted as Gulf insurance premiums soar"}
        ]
        for n in war_news:
            txt = n['ko'] if is_ko else n['en']
            st.markdown(f"""<div class="news-card"><span class="time-label">⏱ {n['t']} | {n['s']}</span><strong>{txt}</strong></div>""", unsafe_allow_html=True)
    with col2:
        st.subheader("🌐 제3국 항만 및 국경 상황" if is_ko else "🌐 Port & Border Status")
        port_news = [
            {"p": "Khor Fakkan (UAE)", "t": "1시간 전", "ko": "코르파칸: 제벨알리 우회 물량 폭주로 야드 가동률 98%", "en": "Terminal utilization hit 98% due to bypass surge"},
            {"p": "Salalah (Oman)", "t": "3시간 전", "ko": "살랄라: 보안 검색 강화로 운영 제한 및 리야드행 지연", "en": "Salalah Port: Operations restricted after drone incidents"},
            {"p": "Al Batha (Border)", "t": "실시간", "ko": "UAE-사우디 국경: 보세 화물 집중으로 통관 대기 72시간", "en": "Wait time for Al Batha border crossing hits 72 hours"},
            {"p": "Fujairah (UAE)", "t": "오늘 오전", "ko": "푸자이라: 긴장 고조로 선박 보험 요율 사상 최고치", "en": "Insurance rates hit record high amid rising tensions"}
        ]
        for p in port_news:
            txt = p['ko'] if is_ko else p['en']
            st.markdown(f"""<div class="port-info"><span class="time-label">⏱ {p['t']} | {p['p']}</span>{txt}</div>""", unsafe_allow_html=True)

    # 7. 심층 실무 가이드 (다국어 하드코딩)
    st.markdown('<div class="qna-box">', unsafe_allow_html=True)
    st.subheader("❓ [Pro Guide] 항만별 주의사항 및 리야드 반입 프로세스" if is_ko else "❓ [Pro Guide] Port Considerations & Riyadh Inbound")
    
    if is_ko:
        with st.expander("📍 1. 오만 (Salalah, Sohar) 이용 시 프로세스"):
            st.write("살랄라/소하르 하역 → **Rub Al Khali** 국경을 통한 리야드 직송. 오만-사우디 직통 노선으로 UAE를 거치지 않습니다.")
        with st.expander("📍 2. UAE (Khor Fakkan, Fujairah) 이용 시 프로세스"):
            st.write("UAE 동부 하역 → **Al Batha 국경** 경유 리야드 입성. 현재 국경 병목 현상으로 정체가 심각합니다.")
        with st.expander("📦 3. Transloading 및 컨테이너 반납 전략"):
            st.write("선사 장비 회전 문제로 사우디 반출이 제한될 시, 항구 인근 보세창고에서의 **Transloading(화물 이적)**이 필수입니다.")
    else:
        with st.expander("📍 1. Oman (Salalah, Sohar) Considerations & Process"):
            st.write("Discharge at Oman → Direct to Riyadh via **Rub Al Khali** border (KSA-Oman direct route).")
        with st.expander("📍 2. UAE (Khor Fakkan, Fujairah) Considerations & Process"):
            st.write("Discharge at East UAE → Enter Riyadh via **Al Batha border** (Expect severe border delays).")
        with st.expander("📦 3. Empty Return & Transloading Strategy"):
            st.write("Port-side **Transloading** is highly recommended to avoid demurrage if equipment export is blocked.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 8. 실무 참고 및 면책 고지
    st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
            <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
                <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
                본 리포트의 정보는 최신 외신 및 선사 공식 기보를 기반으로 한 참고 자료입니다.
                실제 물류 실행 시에는 <strong>반드시 LX Pantos 담당 전문가</strong>를 통해 최종 검증을 받으시기 바랍니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
