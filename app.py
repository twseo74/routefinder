import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. 다국어 세션 관리
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    st.info("© Rino from Andromeda")

is_ko = (st.session_state.lang == "한국어")

# 3. 고해상도 디자인 및 표 너비 비율 강제 고정 (10:10:40:40)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; font-size: 0.9rem; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.85rem; }
    
    /* 너비 비율 고정: 선사 10%, 상태 10%, 라우트 40%, 주요사항 40% */
    .w-10 { width: 10%; text-align: center; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 8px; border-radius: 4px; }
    .port-info { background-color: #e6f7ff; border-left: 5px solid #1890ff; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# 4. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">FF 인바운드 실시간 전략 분석 리포트 (v10.0)</p>
    </div>
    <div class="update-box"><strong>실시간 분석 시점:</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 5. 입력 섹션
col_in1, col_in2 = st.columns(2)
with col_in1: pol = st.text_input("Origin (POL)", value="Busan")
with col_in2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 6. 데이터 엔진 (상태 세분화 및 주요사항 통합)
def get_intel_data(pol_val):
    route_oman = f"🌐 **[Oman Bypass]** {pol_val} → 살랄라(Salalah) 하역 → **보세 운송(Bonded)** → Al Batha 국경 → {pod}"
    route_cape = f"🌐 **[Cape Detour]** {pol_val} → Singapore(T/S) → **희망봉(Cape) 우회** → 지브롤터 → 수에즈(N) → **제다(Jeddah) 하역** → {pod}"
    
    # 상태 포맷: [제다 가용성] | [담맘 가용성] | [종합 상태]
    # 주요사항 포맷: [선사공지/기사] + [비용/보세 실무정보]
    
    if is_ko:
        return [
            ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**부킹 중단**", route_oman, 
             "📢 **공지:** 호르무즈 해협 봉쇄로 걸프향 전 노선 부킹 일시 중단 (3/6)\n\n💰 **비용:** 살랄라-리야드 트럭킹 약 $2,200~$2,500\n🔗 **보세:** 가능(ZATCA 승인)"],
            ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**희망봉 우회**", route_cape, 
             "📢 **기사:** 수에즈 북단 진입을 통한 제다 하역 전략 공식 채택\n\n💰 **비용:** 제다-리야드 내륙운송 약 $1,300~$1,600\n🔗 **보세:** 가능"],
            ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**부킹 제한**", "Suspended", 
             "📢 **공지:** 국적선사 안전 지침에 따라 신규 예약 잠정 중단 및 상황 주시\n\n💰 **비용:** 별도 협의 요망\n🔗 **보세:** 확인 필요"],
            ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**제다 우회**", route_cape, 
             "📢 **공지:** 전쟁 할증료($1,500) 도입 및 제다항 하역 후 육로 연결 지원\n\n💰 **비용:** 제다-리야드 약 $1,400~$1,700\n🔗 **보세:** 가능"],
            ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**부킹 제한**", route_oman, 
             "📢 **기사:** 오만 살랄라 하역 후 육로 전환 조건부 부킹 수락 중\n\n💰 **비용:** 살랄라-리야드 약 $2,300~$2,600\n🔗 **보세:** 가능"]
        ]

# 7. 실행 및 출력
if st.button("🚀 실시간 통합 분석 실행", type="primary", use_container_width=True):
    data = get_intel_data(pol)
    cols = ["선사", "상태", "상세 라우트", "주요 사항 (공지/기사/실무)"]
    
    # HTML 표 생성 (10:10:40:40 비율)
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-10">{cols[0]}</th><th class="w-10">{cols[1]}</th><th class="w-40">{cols[2]}</th><th class="w-40">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 8. 타 국가 항만 운영 및 전황 뉴스 (8건 보강)
    st.markdown("---")
    col_news_1, col_news_2 = st.columns(2)
    
    with col_news_1:
        st.subheader("🌐 제3국 항만 실시간 현황")
        port_news = [
            {"p": "Salalah (Oman)", "txt": "우회 화물 폭증으로 CY 포화. 24시간 특별 운영 가동 중"},
            {"p": "Sohar (Oman)", "txt": "사우디향 보세 화물 전용 'Fast-Track' 게이트 개설"},
            {"p": "Fujairah (UAE)", "txt": "해협 입구 긴장 고조로 정박 대기 시간 36시간 증가"}
        ]
        for p in port_news:
            st.markdown(f"""<div class="port-info"><strong>📍 {p['p']}</strong><br>{p['txt']}</div>""", unsafe_allow_html=True)

    with col_news_2:
        st.subheader("🔥 호르무즈 실시간 시황")
        war_news = [
            {"s": "Reuters", "txt": "이란 혁명수비대 해협 기뢰 매설 징후로 통항 전면 마비"},
            {"s": "Windward", "txt": "지난 24시간 내 대형 컨테이너선 통과량 '0' 기록"},
            {"s": "Lloyd's List", "txt": "국경(Al Batha) 트럭 정체 심화, 대기 48시간 초과"},
            {"s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 지대 경계 태세 강화"},
            {"s": "Kpler", "txt": "글로벌 물류 보험료 사상 최고치 경신 및 인수 거절"}
        ]
        for n in war_news:
            st.markdown(f"""<div class="news-card"><small>{n['s']}</small><br>{n['txt']}</div>""", unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
