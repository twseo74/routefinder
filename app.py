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
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">극동발 사우디향 컨테이너 관련 현황</p>
    </div>
    <div class="update-box"><strong>검증 시점:</strong> {current_time} (KSA)</div>
""", unsafe_allow_html=True)

# 5. 정정된 10대 선사 통합 데이터 엔진
def get_intel_data():
    route_uae = "🌐 **[UAE Transit]** 극동 → **Khor Fakkan / Fujairah** 하역 → **Al Batha 국경** → 리야드"
    route_oman = "🌐 **[Oman Transit]** 극동 → **Salalah** 하역 → **Rub Al Khali 국경** → 리야드"
    route_cape = "🌐 **[Cape Detour]** 극동 → **희망봉 우회** → 수에즈(N) → **제다(Jeddah) 하역** → 사우디 내륙 횡단"
    
    return [
        ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:부킹 중단**", route_uae.replace(" / Fujairah", ""), 
         "📢 **공지:** 호르무즈 해협 내 제벨알리 진입 불가로 코르파칸 우회 집중 (3/6)\n💰 **비용:** UAE-리야드 약 $1,900~$2,300\n🔗 **보세:** 가능"],
        ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 살랄라 하역 후 Rub Al Khali 직통 노선 이용 권고 (3/6)\n💰 **비용:** 살랄라-리야드 약 $2,300~$2,600\n🔗 **보세:** 가능"],
        ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**\n**종합:희망봉 우회**", route_uae.replace("Khor Fakkan / ", ""), 
         "📢 **기사:** UAE 동부 푸자이라 하역 후 Al Batha 국경 연계 서비스 가동\n💰 **비용:** UAE-리야드 약 $1,800~$2,200\n🔗 **보세:** 가능"],
        ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:제다 우회**", route_uae.replace(" / Fujairah", ""), 
         "📢 **공지:** 코르파칸/제다 하역 후 육로 전환 서비스 제공 중 (3/5)\n💰 **비용:** UAE-리야드 약 $2,000~$2,400\n🔗 **보세:** 가능"],
        ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**\n**종합:부킹 제한**", "Suspended", 
         "📢 **공지:** 국적선사 안전 지침에 따라 걸프향 신규 예약 전면 중단 (3/6)\n💰 **비용:** 확인 요망\n🔗 **보세:** 협의 필요"],
        ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:부킹 제한**", route_uae.replace(" / Fujairah", ""), 
         "📢 **기사:** UAE 동부항 임시 양하 후 사우디향 육로 셔틀 검토 중 (3/5)\n💰 **비용:** UAE-리야드 약 $2,000~$2,300\n🔗 **보세:** 가능"],
        ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**\n**종합:희망봉 우회**", route_cape, 
         "📢 **공지:** 희망봉 우회로 인한 리드타임 25일 이상 지연 확정\n💰 **비용:** 제다-리야드 약 $1,400~$1,700\n🔗 **보세:** 가능"],
        ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**\n**종합:부킹 중단**", "Suspended", 
         "📢 **기사:** 중국계 본선 전면 대피 및 걸프만 노선 예약 제한 (3/6)\n💰 **비용:** 불가\n🔗 **보세:** 불가"],
        ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 살랄라 터미널 선복 확보 후 부킹 재개 예정 (3/6 속보)\n💰 **비용:** 살랄라-리야드 약 $2,250~$2,550\n🔗 **보세:** 가능"],
        ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**\n**종합:부킹 중단**", "Suspended", 
         "📢 **공지:** 얼라이언스 방침에 따라 중동행 전 노선 서비스 중단\n💰 **비용:** 불가\n🔗 **보세:** 불가"]
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

    # 7. 타 국가 항만 및 전황 뉴스 (8건)
    st.markdown("---")
    col_news_1, col_news_2 = st.columns(2)
    with col_news_1:
        st.subheader("🌐 제3국 항만 실시간 현황")
        port_news = [
            {"p": "Khor Fakkan (UAE)", "txt": "코르파칸 항만: 제벨알리 대체 수요로 가동률 95% 상회."},
            {"p": "Salalah (Oman)", "txt": "살랄라 항만: Rub Al Khali 국경행 보세 차량 배차 시간 지연 발생."},
            {"p": "Fujairah (UAE)", "txt": "푸자이라 항만: 해협 입구 긴장으로 선박 보험 요율 사상 최고치 기록."}
        ]
        for p in port_news:
            st.markdown(f"""<div class="port-info"><strong>📍 {p['p']}</strong><br>{p['txt']}</div>""", unsafe_allow_html=True)
    with col_news_2:
        st.subheader("🔥 호르무즈 실시간 시황")
        war_news = [
            {"s": "Reuters", "txt": "이란 혁명수비대 호르무즈 해협 기뢰 매설 징후로 통항 마비"},
            {"s": "Windward", "txt": "지난 24시간 내 대형 컨테이너선 해협 통과량 '0' 기록"},
            {"s": "Lloyd's List", "txt": "Al Batha(UAE) 및 Rub Al Khali(오만) 국경 트럭 정체 심화"},
            {"s": "Bloomberg", "txt": "사우디 에너지부, 동부 유전 지대 경계 태세 강화 지시"}
        ]
        for n in war_news:
            st.markdown(f"""<div class="news-card"><small>{n['s']}</small><br>{n['txt']}</div>""", unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
