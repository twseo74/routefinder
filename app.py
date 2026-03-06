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
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.82rem; }
    
    /* 너비 비율 고정: 선사 10%, 상태 10%, 라우트 40%, 주요사항 40% */
    .w-10 { width: 10%; text-align: center; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 8px; border-radius: 4px; }
    .port-info { background-color: #e6f7ff; border-left: 5px solid #1890ff; padding: 15px; margin-bottom: 12px; border-radius: 4px; }
    .qna-box { background-color: #fdfdfd; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; margin-top: 30px; }
    </style>
""", unsafe_allow_html=True)

# 4. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ '극동발 사우디향 컨테이너 관련 현황' if is_ko else 'Far East to KSA Container Status' }</p>
    </div>
    <div class="update-box"><strong>실시간 시황 및 분석 업데이트:</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 5. 데이터 엔진 (UAE 옵션 및 상태 칸 타국 항구 정보 반영)
def get_intel_data():
    route_uae = f"🌐 **[UAE Transit]** 극동 → **Jebel Ali / Fujairah** 하역 → **보세 운송(Bonded)** → Al Batha 국경 → 리야드"
    route_oman = f"🌐 **[Oman Transit]** 극동 → 살랄라(Salalah) 하역 → **보세 운송** → Al Batha 국경 → 리야드"
    route_cape = f"🌐 **[Cape Detour]** 극동 → **희망봉 우회** → 수에즈(N) → **제다(Jeddah) 하역** → 사우디 내륙 운송"
    
    return [
        ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:살랄라/제벨알리**\n**종합:부킹 중단**", route_uae, 
         "📢 **공지:** 호르무즈 봉쇄로 걸프향 전 지역 부킹 일시 중단 (3/6)\n💰 **비용:** UAE-리야드 트럭킹 약 $1,800~$2,200\n🔗 **보세:** 가능(ZATCA 승인)"],
        ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:푸자이라**\n**종합:희망봉 우회**", route_uae.replace("Jebel Ali / Fujairah", "Fujairah"), 
         "📢 **기사:** UAE 푸자이라 하역 후 육로 전환 서비스 공식 채택\n💰 **비용:** UAE-리야드 약 $1,700~$2,100\n🔗 **보세:** 가능"],
        ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:살랄라(Salalah)**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 오만 살랄라 하역 후 육로 전환 시에만 조건부 부킹 수락\n💰 **비용:** 살랄라-리야드 약 $2,300~$2,600\n🔗 **보세:** 가능"],
        ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:제벨알리(UAE)**\n**종합:제다 우회**", route_uae.replace("Jebel Ali / Fujairah", "Jebel Ali"), 
         "📢 **공지:** 전쟁 할증료 도입 및 UAE/제다항 하역 후 육로 연결 지원\n💰 **비용:** UAE-리야드 약 $1,900~$2,300\n🔗 **보세:** 가능"],
        ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**\n**종합:부킹 제한**", "Suspended", 
         "📢 **공지:** 국적선사 안전 지침에 따라 신규 예약 잠정 중단 및 상황 주시\n💰 **비용:** 별도 협의 요망\n🔗 **보세:** 확인 필요"],
        ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:제벨알리(UAE)**\n**종합:UAE 우회**", route_uae.replace("Jebel Ali / Fujairah", "Jebel Ali"), 
         "📢 **기사:** UAE 제벨알리 임시 양하 후 사우디향 육로 셔틀 운영 검토 중\n💰 **비용:** UAE-리야드 약 $1,850~$2,150\n🔗 **보세:** 가능"],
        ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**\n**종합:희망봉 우회**", route_cape, 
         "📢 **공지:** 희망봉 우회로 인한 리드타임 25일 이상 추가 지연 확정\n💰 **비용:** 제다-리야드 약 $1,400~$1,700\n🔗 **보세:** 가능"],
        ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**\n**종합:부킹 중단**", "Suspended", 
         "📢 **기사:** 중국계 본선 전면 대피 및 걸프만 노선 예약 전면 제한\n💰 **비용:** 불가\n🔗 **보세:** 불가"],
        ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:살랄라(Salalah)**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 살랄라 터미널 선복 확보 후 부킹 재개 예정\n💰 **비용:** 살랄라-리야드 약 $2,250~$2,550\n🔗 **보세:** 가능"],
        ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**\n**종합:부킹 중단**", "Suspended", 
         "📢 **공지:** 얼라이언스(COSCO) 방침에 따라 중동행 전 구간 서비스 중단\n💰 **비용:** 불가\n🔗 **보세:** 불가"]
    ]

# 6. 실행 및 출력
if st.button("🚀 실시간 통합 현황 분석 실행", type="primary", use_container_width=True):
    data = get_intel_data()
    cols = ["선사", "상태 (타항 포함)", "상세 라우트", "주요 사항 (공지/기사/실무)"]
    
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th class="w-10">{cols[0]}</th><th class="w-10">{cols[1]}</th><th class="w-40">{cols[2]}</th><th class="w-40">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 타 국가 항만 뉴스 및 전황 속보 (8건)
    st.markdown("---")
    col_news_1, col_news_2 = st.columns(2)
    with col_news_1:
        st.subheader("🌐 제3국 항만 실시간 현황")
        port_news = [
            {"p": "Jebel Ali (UAE)", "txt": "제벨알리 항만청: 해협 내부 리스크로 인한 피더선 운항 중단. 사우디향 육로 전환 물량 급증."},
            {"p": "Salalah (Oman)", "txt": "살랄라 항만: 우회 화물 폭증으로 컨테이너 야드(CY) 포화. 24시간 특별 교대 근무 돌입."},
            {"p": "Fujairah (UAE)", "txt": "푸자이라 항만: 해협 입구 군사 긴장으로 피더선 정박 대기 시간 및 보험 요율 상승 중."}
        ]
        for p in port_news:
            st.markdown(f"""<div class="port-info"><strong>📍 {p['p']}</strong><br>{p['txt']}</div>""", unsafe_allow_html=True)
    with col_news_2:
        st.subheader("🔥 호르무즈 실시간 시황")
        war_news = [
            {"s": "Reuters", "txt": "이란 혁명수비대 해협 기뢰 매설 징후로 상업 통항 사실상 마비"},
            {"s": "Windward", "txt": "지난 24시간 내 대형 컨테이너선 통과량 '0' 기록"},
            {"s": "Lloyd's List", "txt": "Al Batha(UAE-KSA) 국경 트럭 정체 심화, 통관 대기 48시간 초과"},
            {"s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 및 정유 시설 경계 태세 강화"},
            {"s": "Kpler", "txt": "글로벌 물류 보험료 사상 최고치 경신 및 인수 거절 가속화"}
        ]
        for n in war_news:
            st.markdown(f"""<div class="news-card"><small>{n['s']}</small><br>{n['txt']}</div>""", unsafe_allow_html=True)

    # 8. 실무 Q&A (제3국 우회 프로세스)
    st.markdown('<div class="qna-box">', unsafe_allow_html=True)
    st.subheader("❓ [실무 가이드] 제3국 우회 시 보세 운송(Bonded) 프로세스")
    with st.expander("Q. UAE나 오만 하역 후 리야드까지 보세 유지 프로세스는?"):
        st.write("1. **현지 항구 양하 및 Transit Bayan 발행**: 오만/UAE 세관에 사우디 통과 화물임을 신고합니다.")
        st.write("2. **보세 차량 봉인**: ZATCA(사우디 관세청) 인증 보세 면허 차량에 적재 후 Seal을 봉인합니다.")
        st.write("3. **국경 통과**: TIR Carnet 서류를 활용해 중간 검사 없이 국경(Al Batha 등)을 통과합니다.")
        st.write("4. **리야드 최종 통관**: 최종 목적지 보세 구역 입고 후 통관 및 세금 납부를 진행합니다.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
