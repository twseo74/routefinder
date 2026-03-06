import streamlit as st
import pandas as pd
import io
import pydeck as pdk
from datetime import datetime
import pytz

# 1. 페이지 설정 및 다국어 대응 CSS
st.set_page_config(page_title="LX Pantos Inbound Intelligence", layout="wide", page_icon="🏢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1rem; }
    .update-time { color: #E6002D; font-weight: bold; font-size: 1.1rem; background-color: #fff1f0; padding: 12px; border-radius: 8px; border: 1px solid #ffccc7; margin-bottom: 20px;}
    .company-header { display: flex; align-items: center; border-bottom: 3px solid #E6002D; padding-bottom: 15px; margin-bottom: 25px; background-color: #fcfcfc;}
    .company-title { font-size: 2rem; font-weight: bold; color: #333; margin-left: 20px;}
    .pantos-red { color: #E6002D; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 리야드 현지 시각 (조회 시점 자동 업데이트)
ksa_tz = pytz.timezone('Asia/Riyadh')
now_ksa = datetime.now(ksa_tz)
current_time_str = now_ksa.strftime("%Y-%m-%d %H:%M:%S (KSA)")
base_date = now_ksa.strftime("%y.%m.%d")

# 2. 고화질 로고 및 법인 헤더
st.markdown(f"""
    <div class="company-header">
        <img src="https://www.lxpantos.com/en/assets/images/common/logo.svg" alt="LX Pantos" width="220">
        <div class="company-title">Saudi Arabia Branch <span style="font-size: 1.2rem; color: #666;">| FF Inbound Team</span></div>
    </div>
""", unsafe_allow_html=True)

lang = st.radio("Select Language", ["한국어", "English"], horizontal=True)
is_ko = (lang == "한국어")

st.markdown(f"<div class='update-time'>🕒 {t['report_time'] if not is_ko else '리포트 생성 시점'}: {current_time_str}</div>", unsafe_allow_html=True)

# 3. 데이터 정의 (선사별 상세 라우트 및 포트 옵션 고증)
def get_route_data(pol, pod):
    return [
        {
            "Carrier": "Maersk",
            "Status": "🟣 Cape Detour",
            "Route Detail": f"{pol} → Singapore → 🌊Cape of Good Hope → Dakar → Gibraltar → Suez → Jeddah",
            "T/T (Est)": "58~65 Days",
            "Surcharge": "WRS $1,500 + Cape $1,200",
            "Inland Option": "Jeddah Port ➔ Riyadh (Bonded Trucking)",
            "Remarks": "아프리카 전역 우회로 인한 리드타임 극대화"
        },
        {
            "Carrier": "MSC",
            "Status": "🟡 Oman Transit",
            "Route Detail": f"{pol} → Colombo → Salalah (Oman) → Port Discharge",
            "T/T (Est)": "26~30 Days",
            "Surcharge": "Deviation SC $800",
            "Inland Option": "Salalah ➔ Al Batha Border ➔ Riyadh (Cross-Border)",
            "Remarks": "해상 구간 최소화, 국경 통관(Bayan) 리스크 관리 필수"
        },
        {
            "Carrier": "HMM / COSCO",
            "Status": "🟢 Aden Direct",
            "Route Detail": f"{pol} → Colombo → 🌊Gulf of Aden → Jeddah",
            "T/T (Est)": "34~38 Days",
            "Surcharge": "WRS $1,000",
            "Inland Option": "Jeddah ➔ Riyadh (SRO Rail / Trucking)",
            "Remarks": "국적선/중국계 대상 홍해 안전 통행로 활용 시도"
        },
        {
            "Carrier": "CMA CGM",
            "Status": "🟡 Oman Transit",
            "Route Detail": f"{pol} → Singapore → Sohar (Oman)",
            "T/T (Est)": "24~28 Days",
            "Surcharge": "Surcharge $700",
            "Inland Option": "Sohar ➔ Al Ain ➔ Al Batha ➔ Riyadh",
            "Remarks": "오만 북부 하역 후 UAE 경유 육로 수송"
        },
        {
            "Carrier": "Common (Local)",
            "Status": "🔴 Gulf Entry",
            "Route Detail": f"{pol} → 🌊Strait of Hormuz → Dammam Port",
            "T/T (Est)": "N/A",
            "Surcharge": "N/A",
            "Inland Option": "Dammam Port ➔ Riyadh (Shortest)",
            "Remarks": "호르무즈 해협 봉쇄 시 담맘항 입항 전면 불가"
        }
    ]

# 4. 조회 및 결과 출력
col_p1, col_p2 = st.columns(2)
with col_p1: pol_val = st.text_input("Origin (POL)", value="Busan")
with col_p2: pod_val = st.text_input("Destination (POD)", value="Riyadh")

if st.button("🚀 Generate Real-time Intel Report", type="primary", use_container_width=True):
    raw_data = get_route_data(pol_val, pod_val)
    df = pd.DataFrame(raw_data)
    df.insert(0, "Base Date", base_date)

    st.subheader(f"📍 {pol_val} ➔ {pod_val} Carrier-specific Routing Analysis")
    
    # 스타일링 (위험도 강조)
    def style_rows(row):
        if '🔴' in row['Status']: return ['background-color: #ffebee; color: #b71c1c; font-weight: bold;'] * len(row)
        if '🟣' in row['Status']: return ['background-color: #f3e5f5; color: #4a148c; font-weight: bold;'] * len(row)
        return [''] * len(row)

    st.dataframe(df.style.apply(style_rows, axis=1), hide_index=True, use_container_width=True)

    # 5. 3D 항로 가시성 지도 (Cape Route 상세 분할)
    st.markdown("---")
    st.subheader("🗺️ 3D Strategic Route Visibility")
    
    # 고증된 좌표계
    coords = {
        "Busan": [129.0, 35.1], "Singapore": [103.8, 1.3], "Colombo": [79.8, 6.9],
        "Cape": [18.4, -34.3], "Dakar": [-17.4, 14.6], "Gibraltar": [-5.3, 35.9],
        "Suez": [32.3, 31.2], "Jeddah": [39.1, 21.4], "Salalah": [54.0, 16.9],
        "Sohar": [56.7, 24.3], "Dammam": [50.1, 26.4], "Riyadh": [46.6, 24.7]
    }

    # 레이어 데이터 (선사별 실제 궤적)
    paths = [
        # Maersk 희망봉 루트 (상세 분할)
        {"start": coords["Busan"], "end": coords["Singapore"], "color": [156, 39, 176]},
        {"start": coords["Singapore"], "end": coords["Cape"], "color": [156, 39, 176]},
        {"start": coords["Cape"], "end": coords["Dakar"], "color": [156, 39, 176]},
        {"start": coords["Dakar"], "end": coords["Gibraltar"], "color": [156, 39, 176]},
        {"start": coords["Gibraltar"], "end": coords["Suez"], "color": [156, 39, 176]},
        {"start": coords["Suez"], "end": coords["Jeddah"], "color": [156, 39, 176]},
        # 살랄라/소하르 루트
        {"start": coords["Busan"], "end": coords["Salalah"], "color": [255, 193, 7]},
        {"start": coords["Busan"], "end": coords["Sohar"], "color": [255, 193, 7]},
        # 내륙 운송
        {"start": coords["Jeddah"], "end": coords["Riyadh"], "color": [33, 150, 243]},
        {"start": coords["Salalah"], "end": coords["Riyadh"], "color": [33, 150, 243]},
        {"start": coords["Sohar"], "end": coords["Riyadh"], "color": [33, 150, 243]}
    ]

    arc_layer = pdk.Layer("ArcLayer", data=paths, get_source_position="start", get_target_position="end", get_source_color="color", get_target_color="color", get_width=4, pitch=45)
    view_state = pdk.ViewState(latitude=15.0, longitude=55.0, zoom=1.5, pitch=45)
    
    # 맵 스타일을 None으로 설정하여 기본 테마 사용 (API 키 문제 해결)
    st.pydeck_chart(pdk.Deck(layers=[arc_layer], initial_view_state=view_state, map_style=None))

    # 6. 엑셀 리포트 (LX 판토스 공식 양식)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
        worksheet = writer.sheets['Sheet1']
        worksheet.cell(row=len(df)+3, column=1, value=f"Generated at: {current_time_str}")
        worksheet.cell(row=len(df)+4, column=1, value="LX Pantos Saudi Arabia Branch - FF Inbound Intelligence")
    buffer.seek(0)
    
    st.download_button("📥 Download LX Pantos Official Intel Report", data=buffer, file_name=f"LXPantos_Hormuz_Report_{now_ksa.strftime('%H%M')}.xlsx", use_container_width=True)

# 7. FAQ 및 저작권
with st.expander("📌 Inbound Logistics FAQ (Bonded Trucking / Cross-border)"):
    st.info("사우디 ZATCA 규정에 따른 FASAH 사전 등록 및 Al Batha 국경 통관 시 TIR Carnet 활용 지침을 확인하십시오.")

st.markdown('<div class="footer">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
