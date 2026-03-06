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
    .qna-box { background-color: #fdfdfd; padding: 25px; border-radius: 12px; margin-top: 35px; border: 1px solid #e1e4e8; }
    .step-badge { background-color: #E6002D; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; }
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
    <div class="update-box"><strong>실무 검증 시점:</strong> {current_time} (KSA)</div>
""", unsafe_allow_html=True)

# 5. 10대 선사 통합 데이터 엔진 (고정)
def get_intel_data():
    route_uae = "🌐 **[UAE Transit]** 극동 → **Khor Fakkan / Fujairah** 하역 → **Al Batha 국경** → 리야드"
    route_oman = "🌐 **[Oman Transit]** 극동 → **Salalah** 하역 → **Rub Al Khali 국경** → 리야드"
    route_cape = "🌐 **[Cape Detour]** 극동 → **희망봉 우회** → 수에즈(N) → **제다(Jeddah) 하역** → 사우디 내륙 횡단"
    
    return [
        ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:부킹 중단**", route_uae.replace(" / Fujairah", ""), 
         "📢 **공지:** 호르무즈 해협 내 제벨알리 진입 불가로 코르파칸 우회 집중\n💰 **비용:** UAE-리야드 육로 약 $1,900~$2,300\n🔗 **보세:** 가능"],
        ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 살랄라 하역 후 Rub Al Khali 직통 노선 이용 권고\n💰 **비용:** 살랄라-리야드 약 $2,300~$2,600\n🔗 **보세:** 가능"],
        ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**\n**종합:희망봉 우회**", route_uae.replace("Khor Fakkan / ", ""), 
         "📢 **기사:** UAE 동부 푸자이라 하역 후 Al Batha 국경 연계 서비스 가동\n💰 **비용:** UAE-리야드 약 $1,800~$2,200\n🔗 **보세:** 가능"],
        ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:제다 우회**", route_uae.replace(" / Fujairah", ""), 
         "📢 **공지:** 코르파칸/제다 하역 후 육로 전환 서비스 제공 중\n💰 **비용:** UAE-리야드 약 $2,000~$2,400\n🔗 **보세:** 가능"],
        ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**\n**종합:부킹 제한**", "Suspended", 
         "📢 **공지:** 국적선사 안전 지침에 따라 걸프향 신규 예약 전면 중단\n💰 **비용:** 확인 요망\n🔗 **보세:** 협의 필요"],
        ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Khor Fakkan**\n**종합:부킹 제한**", route_uae.replace(" / Fujairah", ""), 
         "📢 **기사:** UAE 동부항 임시 양하 후 사우디향 육로 셔틀 검토 중\n💰 **비용:** UAE-리야드 약 $2,000~$2,300\n🔗 **보세:** 가능"],
        ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**\n**종합:희망봉 우회**", route_cape, 
         "📢 **공지:** 희망봉 우회로 인한 리드타임 25일 이상 지연 확정\n💰 **비용:** 제다-리야드 약 $1,400~$1,700\n🔗 **보세:** 가능"],
        ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**\n**종합:부킹 중단**", "Suspended", 
         "📢 **기사:** 중국계 본선 전면 대피 및 걸프만 노선 예약 제한\n💰 **비용:** 불가\n🔗 **보세:** 불가"],
        ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**\n**종합:부킹 제한**", route_oman, 
         "📢 **기사:** 살랄라 터미널 선복 확보 후 부킹 재개 예정\n💰 **비용:** 살랄라-리야드 약 $2,250~$2,550\n🔗 **보세:** 가능"],
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

    # 7. 제3국 항만 이용 실무 Q&A (보세/일반/Transloading)
    st.markdown('<div class="qna-box">', unsafe_allow_html=True)
    st.subheader("❓ [실무 가이드] 제3국 항만 이용 시 육로 운송 및 컨테이너 반납 프로세스")
    
    with st.expander("Q1. 보세운송(Bonded)과 일반운송(Normal)의 차이점과 선택 기준은?", expanded=True):
        st.write("""
        * **보세운송(Bonded Trucking):** 제3국 항구에서 통관하지 않고 사우디 리야드 Dry Port까지 세관 봉인(Seal) 상태로 운송하는 방식입니다. 수입 통관을 리야드에서 진행하므로 제3국 관세 지불이 필요 없습니다.
        * **일반운송(Transloading 후):** 제3국 항구 근처 보세창고에서 짐을 빼서 일반 사우디 트럭에 옮겨 싣는 방식입니다. 국경에서 통관을 마친 후 리야드까지 일반 국내 화물처럼 이동합니다.
        * **선택 기준:** 긴급 화물이고 리야드 세관 화물이 많다면 **보세운송**을, 리야드 외 지역 분산 배송이 필요하다면 **Transloading**이 유리합니다.
        """)

    with st.expander("Q2. 컨테이너 반납지(Empty Return)에 따른 Transloading(적출입) 필요성은?"):
        st.write("""
        * **Case 1: 사우디 내 반납 가능 시(Inter-country Drop-off):** 선사 컨테이너를 트레일러에 실은 채 사우디로 입국하여 리야드 Empty Depot에 반납합니다. Transloading 비용이 없으나, 선사 승인이 어렵고 높은 Drop-off Charge가 발생할 수 있습니다.
        * **Case 2: 제3국 반납 조건(Mandatory Third-country Return):** 선사가 컨테이너의 사우디 반출을 불허할 경우입니다. 반드시 항만 인근에서 **Transloading(화물 적출 후 일반 트럭 이적)**을 해야 하며, 선사 빈 컨테이너는 즉시 해당 항구 Depot에 반납합니다.
        * **실무 권고:** 현재 중동 전쟁 시황으로 선복 부족이 심해 선사들이 컨테이너 반출을 극도로 꺼립니다. 따라서 **제3국 항구 인근 Transloading** 시나리오를 기본으로 준비해야 합니다.
        """)

    with st.expander("Q3. 각 항구별 사우디 인바운드 육로 프로세스 상세"):
        st.markdown("""
        * <span class="step-badge">UAE (Khor Fakkan/Fujairah)</span>
            * **국경:** Al Batha Border 이용.
            * **프로세스:** 항만 양하 → UAE 내 보세 창고 이동 → Transloading(사우디 트럭) → Al Batha 통관 → 리야드 도착.
            * **특징:** 인프라가 가장 좋으나 현재 우회 화물 집중으로 국경 정체 심각(48시간 이상).
        * <span class="step-badge">Oman (Salalah/Sohar)</span>
            * **국경:** Rub Al Khali (Empty Quarter) Border 이용.
            * **프로세스:** 항만 양하 → 오만 보세 운송 면허 차량 적재 → 사막 횡단 직통 노선 → 리야드 Dry Port 도착.
            * **특징:** UAE를 거치지 않아 국경 통과가 1회로 단축되나, 장거리 사막 운전으로 인해 보세 차량 수급이 제한적임.
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
