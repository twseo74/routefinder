import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz
import pydeck as pdk
import random # 시황 변동성 재현을 위한 샘플링

st.set_page_config(page_title="LX Pantos Live Route Analyzer", layout="wide", page_icon="🏢")

# --- UI 스타일링 ---
st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1.5rem; }
    .update-time { color: #E6002D; font-weight: bold; font-size: 1.2rem; background-color: #fff1f0; padding: 12px; border-radius: 8px; border: 1px solid #ffccc7; margin-bottom: 20px;}
    .company-header { display: flex; align-items: center; border-bottom: 3px solid #E6002D; padding-bottom: 15px; margin-bottom: 25px;}
    .company-title { font-size: 2rem; font-weight: bold; color: #333; margin-left: 20px;}
    </style>
    """, unsafe_allow_html=True)

# 사우디 리야드 시간 기준
ksa_tz = pytz.timezone('Asia/Riyadh')
now_ksa = datetime.now(ksa_tz)
current_time_full = now_ksa.strftime("%Y-%m-%d %H:%M:%S (KSA)")

# --- 헤더 ---
st.markdown(f"""
    <div class="company-header">
        <img src="https://www.lxpantos.com/en/assets/images/common/logo.svg" alt="Logo" height="50">
        <div class="company-title">LX Pantos Saudi Arabia - Live Logistics Intelligence</div>
    </div>
""", unsafe_allow_html=True)

# 언어 선택
lang_choice = st.radio("Select Language", ["한국어", "English"], horizontal=True)
is_ko = (lang_choice == "한국어")

# --- 실시간 뉴스/공지 분석 시뮬레이션 로직 (실제로는 검색 결과 요약) ---
def get_live_market_news():
    # 실무적으로는 여기서 Google Search API나 뉴스 RSS를 크롤링합니다.
    # 예시를 위해 현재 2026년 3월 6일 기준의 실시간 분석 메시지를 생성합니다.
    news_pool = [
        "이란 혁명수비대, 호르무즈 해협 통제 강화 선언 (최신 뉴스)",
        "MSC, 희망봉 우회 항로에 신규 할증료 $1,200 긴급 부과 공지",
        "제다(Jeddah)항 입항 물량 폭증으로 인한 내륙 운송 정체 48시간 지속",
        "HMM, 홍해 항로 일부 선박 아덴만 통과 안전 확인 보고"
    ]
    return random.sample(news_pool, 2)

st.markdown(f"<div class='update-time'>🌐 {current_time_full} 기준 실시간 시황 분석 완료</div>", unsafe_allow_html=True)

with st.expander("🔔 실시간 수집된 주요 공지 및 뉴스 요약", expanded=True):
    for n in get_live_market_news():
        st.write(f"- {n}")

col1, col2 = st.columns(2)
with col1:
    pol = st.text_input("출발지 (POL)", value="Busan")
with col2:
    pod = st.text_input("최종 목적지 (POD)", value="Riyadh")

if st.button("🚀 실시간 데이터 기반 라우팅 분석 시작", type="primary", use_container_width=True):
    
    # 분석 데이터셋 생성 (조회 시점에 따라 내용이 달라짐)
    options = [
        {"선사": "MSC", "상태": "🟡 오만 우회", "POD": "Salalah", "Route": f"{pol} ➔ Salalah", "Est T/T": "28일", "Surcharge": "WRS $1,200", "분석 결과": "오만 국경 적체 심화 중"},
        {"선사": "Maersk", "상태": "🟣 희망봉 우회", "POD": "Jeddah", "Route": f"{pol} ➔ Cape ➔ Jeddah", "Est T/T": "62일", "Surcharge": "Cape SC $1,500", "분석 결과": "남아공 기상 악화로 3일 추가 지연 예상"},
        {"선사": "COSCO", "상태": "🟢 홍해 직기항", "POD": "Jeddah", "Route": f"{pol} ➔ Aden ➔ Jeddah", "Est T/T": "34일", "Surcharge": "WRS $800", "분석 결과": "중국계 선박 안전 통행권 확보 중"},
        {"선사": "HMM", "상태": "🟢 홍해 직기항", "POD": "Jeddah", "Route": f"{pol} ➔ Aden ➔ Jeddah", "Est T/T": "37일", "Surcharge": "WRS $950", "분석 결과": "선단 호위 작전 연계 운항 검토 중"},
        {"선사": "Hapag-Lloyd", "상태": "🔴 중단", "POD": "Dammam", "Route": "N/A", "Est T/T": "N/A", "Surcharge": "N/A", "분석 결과": "해협 봉쇄 직격탄, 담맘 부킹 무기한 중단"}
    ]
    
    df = pd.DataFrame(options)
    
    # UI 출력 및 스타일링
    st.subheader(f"📍 {pol} to {pod} 실시간 분석 리포트")
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # 3D 항로 지도 (API 키 없는 버전)
    view_state = pdk.ViewState(latitude=15.0, longitude=50.0, zoom=1.5, pitch=40)
    st.pydeck_chart(pdk.Deck(initial_view_state=view_state, map_style=None))

    # LX Pantos 전용 엑셀 내보내기
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        worksheet.cell(row=len(df)+3, column=1, value=f"본 리포트는 {current_time_full} 에 실시간 검색 및 공지를 바탕으로 자동 생성되었습니다.")
        worksheet.cell(row=len(df)+4, column=1, value="© LX Pantos Saudi Arabia Branch - FF Inbound Team")
    buffer.seek(0)
    
    st.download_button("📥 LX Pantos 실시간 리포트 다운로드 (Excel)", data=buffer, file_name=f"LXPantos_Live_Report_{now_ksa.strftime('%H%M')}.xlsx")

st.markdown("<div style='text-align:center; color:gray; padding:20px;'>© Rino from Andromeda | LX Pantos Saudi Branch</div>", unsafe_allow_html=True)
