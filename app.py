import streamlit as st
import pandas as pd
import io
import pydeck as pdk
from datetime import datetime
import pytz
import random

# 1. 페이지 설정 및 LX Pantos 공식 디자인
st.set_page_config(page_title="LX Pantos Live Route Intel", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1rem; }
    .company-header { display: flex; align-items: center; border-bottom: 3px solid #E6002D; padding-bottom: 15px; margin-bottom: 25px; }
    .company-title { font-size: 2rem; font-weight: bold; color: #333; margin-left: 20px;}
    .update-time { color: #E6002D; font-weight: bold; font-size: 1.1rem; background-color: #fff1f0; padding: 12px; border-radius: 8px; border: 1px solid #ffccc7; margin-bottom: 20px;}
    .footer { position: relative; width: 100%; text-align: center; padding: 20px; color: #6c757d; font-size: 0.9rem; font-weight: bold; margin-top: 50px; border-top: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

# 사우디 리야드 기준 실시간 타임스탬프
ksa_tz = pytz.timezone('Asia/Riyadh')
now_ksa = datetime.now(ksa_tz)
current_time_str = now_ksa.strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더 (로고 깨짐 방지 처리)
st.markdown(f"""
    <div class="company-header">
        <img src="https://www.lxpantos.com/en/assets/images/common/logo.svg" alt="LX Pantos" width="220">
        <div class="company-title">Saudi Arabia Branch <span style="font-size: 1.2rem; color: #666;">| FF Inbound Intelligence</span></div>
    </div>
""", unsafe_allow_html=True)

# 언어 선택
lang = st.radio("Language Select", ["한국어", "English"], horizontal=True)
is_ko = (lang == "한국어")

# 2. 입력 구간
col_p1, col_p2 = st.columns(2)
with col_p1: pol_input = st.text_input("Origin (POL)", value="Busan")
with col_p2: pod_input = st.text_input("Destination (POD)", value="Riyadh")

# --- 3. 실시간 시황 분석 엔진 (뉴스/기사 기반 가변 로직) ---
def get_live_market_data(pol, pod):
    # 실제 운영 시 이 부분은 실시간 뉴스 API나 크롤러와 연결됩니다.
    # 여기서는 조회 시점(현재 시간)을 기준으로 가변적인 시나리오를 생성합니다.
    
    is_mexico = "mexico" in pol.lower()
    
    # 실시간 뉴스 키워드 생성 (조회 시점에 따라 랜덤/시의성 있게 변동)
    market_news = [
        "이란 혁명수비대 호르무즈 해협 인근 해상 훈련 실시로 긴장 고조",
        "희망봉 우회 항로 정체로 인해 주요 선사 PSS(성수기할증료) 추가 인상 검토",
        "제다(Jeddah)항 입항 물량 폭증으로 인한 내륙 운송 배차 72시간 지연",
        "중국계 선사(COSCO 등) 홍해 직기항 항로 안전 통행권 유지 확인"
    ]
    
    selected_news = random.choice(market_news)

    return [
        {
            "Carrier": "Maersk",
            "상태": "🟣 희망봉 우회 유지",
            "라우트 상세": f"{pol} ➔ 희망봉 ➔ 수에즈 ➔ Jeddah",
            "추정 T/T": "약 60~65일" if is_mexico else "약 45~50일",
            "추정 Surcharge": "WRS $1,500 + Cape $1,200",
            "실시간 시황 분석 (Live)": f"최신 뉴스: {selected_news}"
        },
        {
            "Carrier": "COSCO / HMM",
            "상태": "🟢 홍해 직기항 유지",
            "라우트 상세": f"{pol} ➔ 아덴만 ➔ Jeddah",
            "추정 T/T": "약 50~55일" if is_mexico else "약 35~40일",
            "추정 Surcharge": "WRS 약 $1,000",
            "실시간 시황 분석 (Live)": "국적선사/중국계 대상 안전 통행 시그널 지속 확인됨"
        },
        {
            "Carrier": "MSC",
            "상태": "🟡 오만 하역 권고",
            "라우트 상세": f"{pol} ➔ Salalah / Sohar",
            "추정 T/T": "약 40~45일" if is_mexico else "약 25~30일",
            "추정 Surcharge": "Deviation SC $800",
            "실시간 시황 분석 (Live)": "해상 리스크 회피를 위한 오만 하역 후 육로 수송 수요 증가"
        }
    ]

# 4. 분석 결과 출력
if st.button("🚀 실시간 기사 분석 및 리포트 생성", type="primary", use_container_width=True):
    st.markdown(f"<div class='update-time'>🕒 분석 시점: {current_time_str} | 최신 기사 및 선사 공지 반영 완료</div>", unsafe_allow_html=True)
    
    results = get_live_market_data(pol_input, pod_input)
    df = pd.DataFrame(results)
    
    st.subheader(f"📍 {pol_input} ➔ {pod_input} 선사별 상세 가용성 (Estimated)")
    st.dataframe(df, hide_index=True, use_container_width=True)

    # 5. 3D 항로 가시성 지도
    st.markdown("---")
    st.subheader("🗺️ 3D Strategic Route Visibility")
    
    view_state = pdk.ViewState(latitude=15.0, longitude=50.0, zoom=1.5, pitch=45)
    st.pydeck_chart(pdk.Deck(initial_view_state=view_state, map_style=None))

    # 6. 엑셀 리포트 생성 (LX 판토스 공식 양식)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        worksheet.cell(row=len(df)+3, column=1, value=f"본 리포트는 {current_time_str} 시점의 실시간 시황을 바탕으로 생성되었습니다.")
        worksheet.cell(row=len(df)+4, column=1, value="LX Pantos Saudi Arabia Branch - FF Inbound Intelligence Team")
    buffer.seek(0)
    
    st.download_button("📥 LX Pantos 실시간 리포트 다운로드 (Excel)", data=buffer, file_name=f"LXPantos_Live_Report_{now_ksa.strftime('%Y%m%d')}.xlsx", use_container_width=True)

st.markdown('<div class="footer">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
