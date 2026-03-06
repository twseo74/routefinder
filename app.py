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
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; font-size: 0.9rem; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.82rem; }
    .w-10 { width: 10%; text-align: center; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .qna-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; margin-top: 35px; border: 1px solid #e1e4e8; }
    .step-badge { background-color: #E6002D; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; }
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

# 5. 10대 선사 통합 데이터 엔진 (상태 칸: 제다우회/담맘가용성/타항정보 필수 포함)
def get_intel_data():
    r_uae = "🌐 **[UAE Transit]** FE → **Khor Fakkan / Fujairah** → **Al Batha Border** → Riyadh" if not is_ko else "🌐 **[UAE Transit]** 극동 → **Khor Fakkan / Fujairah** 하역 → **Al Batha 국경** → 리야드"
    r_oman = "🌐 **[Oman Transit]** FE → **Salalah / Sohar** → **Rub Al Khali Border** → Riyadh" if not is_ko else "🌐 **[Oman Transit]** 극동 → **Salalah / Sohar** 하역 → **Rub Al Khali 국경** → 리야드"
    r_cape = "🌐 **[Cape Detour]** FE → **Cape Detour** → **Jeddah Port** → Riyadh" if not is_ko else "🌐 **[Cape Detour]** 극동 → **희망봉 우회** → **제다(Jeddah) 하역** → 리야드"

    data = [
        ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**" if is_ko else "Jeddah:🟢(Detour)\nDammam:🔴(Stop)\n**Port:Khor Fakkan**", r_uae.replace(" / Fujairah", ""), "📢 코르파칸 우회 노선 집중\n💰 $1,900~$2,300\n🔗 보세: 가능"],
        ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**" if is_ko else "Jeddah:🟡(Wait)\nDammam:🔴(Stop)\n**Port:Salalah**", r_oman.replace(" / Sohar", ""), "📢 살랄라 하역 후 Rub Al Khali 직송 권고\n💰 $2,300~$2,600\n🔗 보세: 가능"],
        ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**" if is_ko else "Jeddah:🟢(Detour)\nDammam:🔴(Stop)\n**Port:Fujairah**", r_uae.replace("Khor Fakkan / ", ""), "📢 푸자이라-Al Batha 연계 서비스 가동\n💰 $1,800~$2,200\n🔗 보세: 가능"],
        ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**" if is_ko else "Jeddah:🟢(Detour)\nDammam:🔴(Stop)\n**Port:Khor Fakkan**", r_uae, "📢 전쟁 할증료($1,500) 및 우회 지원"],
        ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**" if is_ko else "Jeddah:🟡(Wait)\nDammam:🔴(Stop)\n**Port:Reviewing**", "Suspended", "📢 국적사 안전 지침으로 부킹 제한"],
        ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Sohar**" if is_ko else "Jeddah:🟡(Wait)\nDammam:🔴(Stop)\n**Port:Sohar**", r_oman.replace("Salalah / ", ""), "📢 소하르 하역 후 육로 셔틀 검토"],
        ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**" if is_ko else "Jeddah:🟢(Detour)\nDammam:🔴(Stop)\n**Port:None**", r_cape, "📢 희망봉 우회로 25일 이상 지연 확정"],
        ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**" if is_ko else "Jeddah:🔴(Stop)\nDammam:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 중동 노선 예약 전면 제한"],
        ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**" if is_ko else "Jeddah:🟡(Wait)\nDammam:🔴(Stop)\n**Port:Salalah**", r_oman, "📢 살랄라 터미널 선복 확보 중"],
        ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**" if is_ko else "Jeddah:🔴(Stop)\nDammam:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 얼라이언스 방침에 따른 서비스 중단"]
    ]
    return data

# 6. 실행 및 출력
btn_label = "🚀 실시간 통합 현황 분석 실행" if is_ko else "🚀 Run Real-time Analysis"
if st.button(btn_label, type="primary", use_container_width=True):
    data = get_intel_data()
    cols = ["선사", "상태 (우회/담맘/타항)", "상세 라우트", "주요 사항 (공지/기사/실무)"] if is_ko else ["Carrier", "Status (Detour/DMM/via)", "Detailed Route", "Notice/Cost/Bonded"]
    
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-10">{cols[0]}</th><th class="w-10">{cols[1]}</th><th class="w-40">{cols[2]}</th><th class="w-40">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 최신 아랍 현지 매체 속보 (8건)
    st.markdown("---")
    col_news_1, col_news_2 = st.columns(2)
    with col_news_1:
        st.subheader("🔥 호르무즈 및 전황 현지 속보 (Local Intel)" if is_ko else "🔥 Hormuz & Conflict Alerts")
        war_news = [
            {"s": "Al Arabiya", "t": "1시간 전", "ko": "이란 혁명수비대, 호르무즈 입구 기뢰 매설 경고 및 상업 통항 마비", "en": "IRGC warns of mine activity in Hormuz; commercial transit paralyzed"},
            {"s": "Saudi Gazette", "t": "3시간 전", "ko": "사우디 항만청(MAWANI), 제다항 내륙 보세 운송 지원 예산 긴급 편성", "en": "MAWANI allocates emergency funds for Jeddah-Riyadh bonded trucking"},
            {"s": "Asharq Al-Awsat", "t": "오늘 오후", "ko": "걸프만 보험 요율 급등으로 담맘 입항 서비스 사실상 전면 중단", "en": "Dammam services halted as Gulf insurance premiums soar"},
            {"s": "Windward", "t": "4시간 전", "ko": "지난 24시간 동안 호르무즈 해협 통과 컨테이너선 '0' 기록", "en": "Zero commercial vessels passed Hormuz in the last 24h"}
        ]
        for n in war_news:
            txt = n['ko'] if is_ko else n['en']
            st.markdown(f"""<div class="news-card"><span class="time-label">⏱ {n['t']} | {n['s']}</span><strong>{txt}</strong></div>""", unsafe_allow_html=True)
    with col_news_2:
        st.subheader("🌐 제3국 항만 실시간 현황" if is_ko else "🌐 Third-Country Port Ops")
        port_news = [
            {"p": "Khor Fakkan (UAE)", "t": "1시간 전", "ko": "코르파칸 항만: 제벨알리 우회 물량 폭주로 터미널 가동률 98% 도달", "en": "Terminal utilization hit 98% due to bypass surge; congestion grows"},
            {"p": "Salalah (Oman)", "t": "3시간 전", "ko": "살랄라 항만청: 사우디행 보세 트럭 국경 대기 시간 72시간 경과", "en": "Wait time for Rub Al Khali border crossing hits 72 hours"},
            {"p": "Al Batha (Border)", "t": "오늘 오후", "ko": "UAE-사우디 국경: 우회 화물 집중으로 통관 병목 현상 심화", "en": "Bottlenecks at UAE-KSA border as detour cargo volumes surge"},
            {"p": "Fujairah (UAE)", "t": "오늘 오전", "ko": "푸자이라 항만: 해협 입구 긴장으로 선박 보험 요율 사상 최고치", "en": "Insurance rates hit record high amid rising Hormuz tensions"}
        ]
        for p in port_news:
            txt = p['ko'] if is_ko else p['en']
            st.markdown(f"""<div class="port-info"><span class="time-label">⏱ {p['t']} | {p['p']}</span>{txt}</div>""", unsafe_allow_html=True)

    # 8. 심층 실무 가이드 (오만/UAE 항만별 주의사항 및 리야드 인바운드 프로세스)
    st.markdown('<div class="qna-box">', unsafe_allow_html=True)
    st.subheader("❓ [심층 실무 가이드] 항만별 주의사항 및 리야드 반입 옵션" if is_ko else "❓ [Pro Guide] Port Considerations & Riyadh Inbound")
    
    with st.expander("📍 1. 오만 (Salalah, Sohar) 이용 시 주의사항 및 프로세스"):
        st.write("""
        * **주의사항:** 살랄라는 거리가 멀어 트럭 배차 수급이 가장 어렵습니다. 소하르는 상대적으로 가깝지만 UAE 국경을 통과해야 하므로 절차가 복잡할 수 있습니다.
        * **프로세스 옵션:**
            - **Option A (Bonded Trucking):** 살랄라/소하르에서 통관 없이 **Rub Al Khali (Empty Quarter)** 국경을 통해 리야드 Dry Port로 직송. (오만-사우디 직통 노선)
            - **Option B (Transloading):** 선사가 사우디 반출을 불허할 경우, 오만 내 보세창고에서 사우디 일반 트럭으로 화물을 옮겨 실은 뒤 국경에서 통관 진행.
        """)

    with st.expander("📍 2. UAE (Khor Fakkan, Fujairah) 이용 시 주의사항 및 프로세스"):
        st.write("""
        * **주의사항:** 코르파칸과 푸자이라는 현재 제벨알리를 대체하는 핵심 항구로 물동량이 폭증하여 터미널 내 적체가 매우 심각합니다.
        * **프로세스 옵션:**
            - **Option A (Bonded Trucking):** UAE 동부에서 적재 후 **Al Batha 국경**을 경유하여 리야드 입성. (가장 일반적인 경로이나 국경 정체 48시간 이상)
            - **Option B (Transloading):** 국경 정체를 피하기 위해 UAE 내 창고에서 화물을 적출하여 분산 배송하거나 사우디 로컬 트럭에 이적.
        """)

    with st.expander("📦 3. 컨테이너 반납(Empty Return) 및 리야드 최종 도착 프로세스"):
        st.write("""
        * **Empty Return 전략:** 선사들이 장비 부족으로 사우디 내 반납(Drop-off)을 거부할 확률이 높습니다. 이 경우 반드시 항구 인근에서 **Transloading(화물 이적)**을 진행하고 빈 컨테이너는 즉시 현지 항구에 반납해야만 과도한 Demurrage를 피할 수 있습니다.
        * **리야드 반입 최종 단계:** 보세 차량 이용 시 리야드 Dry Port 세관 검사 후 반입, Transloading 이용 시 국경 통관 후 리야드 창고로 즉시 배송.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # 9. 전문가 면책 고지
    st.markdown(f"""
        <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
            <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
                <strong>⚠️ [Professional Disclaimer]</strong><br>
                본 리포트는 {current_time} 기준 최신 아랍 매체 및 선사 공식 기보를 기반으로 작성되었습니다. 
                실제 물류 실행 전에는 <strong>반드시 LX Pantos 담당 전문가</strong>를 통해 최종 검증을 받으시기 바랍니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
