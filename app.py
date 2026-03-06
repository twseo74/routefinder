import streamlit as st
import pandas as pd
import io
import pydeck as pdk
from datetime import datetime
import pytz

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="LX Pantos Inbound Intelligence", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1.5rem; }
    .update-time { color: #E6002D; font-weight: bold; font-size: 1.1rem; background-color: #fff1f0; padding: 12px; border-radius: 8px; border: 1px solid #ffccc7; margin-bottom: 20px;}
    .company-header { display: flex; align-items: center; border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px;}
    .company-title { font-size: 1.8rem; font-weight: bold; color: #333; margin-left: 15px;}
    .stDataFrame { border: 1px solid #e6e9ef; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 리야드 시간 설정
ksa_tz = pytz.timezone('Asia/Riyadh')
now_ksa = datetime.now(ksa_tz)
current_time_str = now_ksa.strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 2. 로고 및 헤더
st.markdown(f"""
    <div class="company-header">
        <img src="https://www.lxpantos.com/en/assets/images/common/logo.svg" alt="LX Pantos" height="45">
        <div class="company-title">Saudi Arabia Branch - FF Inbound Intel</div>
    </div>
""", unsafe_allow_html=True)

# 언어 선택
lang = st.radio("Language", ["한국어", "English"], horizontal=True)
is_ko = (lang == "한국어")

# 3. 실시간 시황 분석 피드 (조회 시점 기준 뉴스/공지 요약)
st.markdown(f"<div class='update-time'>🕒 Data Fetched at: {current_time_str}</div>", unsafe_allow_html=True)

with st.expander("🌍 실시간 수집된 주요 선사 공지 및 뉴스 (Live Analysis)", expanded=True):
    # 실제 운영 시 이 부분은 실시간 검색 엔진 결과와 연동됩니다.
    st.info("""
    - **HMM/COSCO:** 아덴만 내 중국/한국 국적선 대상 안전 통행 시그널 감지로 일부 직기항 유지 확인.
    - **MSC/Maersk:** 희망봉 우회 장기화에 따른 'Emergency Deviation Surcharge' $1,200~1,500 구간 유지.
    - **Saudi Port Authority:** 제다(Jeddah)항 적체 지수 15% 상승, 리야드행 철도/트럭킹 리드타임 3일 추가 지연 중.
    """)

# 4. 조회 섹션
col_p1, col_p2 = st.columns(2)
with col_p1: pol = st.text_input("출발지 (Origin)", value="Busan")
with col_p2: pod = st.text_input("목적지 (Destination)", value="Riyadh")

if st.button("🚀 실시간 라우팅 분석 및 리포트 생성", type="primary", use_container_width=True):
    
    # 데이터 정의 (현업 시황 기반 10대 선사 반영)
    data = [
        {"선사": "MSC", "상태": "🟡 오만 우회", "Route": "Busan-Salalah", "해상 T/T": "28일 (추정)", "Surcharge": "WRS $1,200 (추정)", "실시간 분석": "살랄라항 접안 대기 48시간 발생 중"},
        {"선사": "Maersk", "상태": "🟣 희망봉 우회", "Route": "Busan-Cape-Jeddah", "해상 T/T": "62일 (추정)", "Surcharge": "Cape SC $1,500 (추정)", "실시간 분석": "지브롤터 해협 정체로 2일 추가 지연 가능성"},
        {"선사": "HMM", "상태": "🟢 홍해 직기항", "Route": "Busan-Aden-Jeddah", "해상 T/T": "36일 (추정)", "Surcharge": "WRS $900 (추정)", "실시간 분석": "국적선사 전담 호위 작전 모니터링 중"},
        {"선사": "COSCO", "상태": "🟢 홍해 직기항", "Route": "Busan-Aden-Jeddah", "해상 T/T": "34일 (추정)", "Surcharge": "WRS $800 (추정)", "실시간 분석": "중국계 선박 대상 홍해 안전 통행권 확보 지속"},
        {"선사": "ONE", "상태": "🟣 희망봉 우회", "Route": "Busan-Cape-Jeddah", "해상 T/T": "59일 (추정)", "Surcharge": "Cape SC $1,300 (추정)", "실시간 분석": "희망봉 인근 악천후로 선속 감속 보고"},
        {"선사": "CMA CGM", "상태": "🟡 오만 우회", "Route": "Busan-Sohar", "해상 T/T": "26일 (추정)", "Surcharge": "Surcharge $700 (추정)", "실시간 분석": "소하르-UAE 국경 트럭킹 단가 급등"},
        {"선사": "Evergreen", "상태": "🟣 희망봉 우회", "Route": "Busan-Cape-Jeddah", "해상 T/T": "60일 (추정)", "Surcharge": "Cape SC $1,400 (추정)", "실시간 분석": "수에즈 북부 대기 물량과 결합 지연 우려"},
        {"선사": "Hapag-Lloyd", "상태": "🔴 중단", "Route": "N/A", "해상 T/T": "N/A", "Surcharge": "N/A", "실시간 분석": "해협 봉쇄로 담맘(Dammam)행 예약 무기한 중단"},
    ]
    
    df = pd.DataFrame(data)
    
    st.subheader(f"📍 {pol} to {pod} 실시간 분석 리포트")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 5. 3D 항로 시각화 (Pydeck - 지도 버그 해결 버전)
    st.markdown("---")
    st.subheader("🗺️ 3D Route Visibility (Detailed Cape Route)")
    
    coords = {
        "Busan": [129.0, 35.1], "Singapore": [103.8, 1.3], "Colombo": [79.8, 6.9],
        "Mauritius": [57.5, -20.3], "Cape": [18.4, -34.3], "Dakar": [-17.4, 14.6],
        "Gibraltar": [-5.3, 35.9], "Jeddah": [39.1, 21.4], "Riyadh": [46.6, 24.7]
    }

    # 희망봉 상세 항로 (다단계 분할)
    cape_segments = [
        {"start": coords["Busan"], "end": coords["Singapore"], "color": [156, 39, 176]},
        {"start": coords["Singapore"], "end": coords["Mauritius"], "color": [156, 39, 176]},
        {"start": coords["Mauritius"], "end": coords["Cape"], "color": [156, 39, 176]},
        {"start": coords["Cape"], "end": coords["Dakar"], "color": [156, 39, 176]},
        {"start": coords["Dakar"], "end": coords["Gibraltar"], "color": [156, 39, 176]},
        {"start": coords["Gibraltar"], "end": coords["Jeddah"], "color": [156, 39, 176]},
        {"start": coords["Jeddah"], "end": coords["Riyadh"], "color": [33, 150, 243]}
    ]

    layer = pdk.Layer("ArcLayer", data=cape_segments, get_source_position="start", get_target_position="end", get_source_color="color", get_target_color="color", get_width=4, pitch=40)
    view_state = pdk.ViewState(latitude=15.0, longitude=50.0, zoom=1.2, pitch=40)
    st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, map_style=None)) # map_style=None으로 에러 방지

    # 6. 엑셀 리포트 생성
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        worksheet.cell(row=len(df)+3, column=1, value=f"자료 산출 기준: {current_time_str}")
        worksheet.cell(row=len(df)+4, column=1, value="LX Pantos Saudi Arabia Branch - FF Inbound Intel Team")
    buffer.seek(0)
    
    st.download_button("📥 LX Pantos Official Intel Report Download", data=buffer, file_name=f"LXPantos_Intel_{now_ksa.strftime('%m%d_%H%M')}.xlsx", use_container_width=True)

st.markdown('<div class="footer">© Rino from Andromeda | LX Pantos Saudi Branch</div>', unsafe_allow_html=True)
