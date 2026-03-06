import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz
import pydeck as pdk

st.set_page_config(page_title="Advanced Route Analyzer", layout="wide", page_icon="🚢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .footer { position: relative; width: 100%; text-align: center; padding: 20px; color: #6c757d; font-size: 0.9rem; font-weight: bold; margin-top: 50px; }
    .update-time { color: #d32f2f; font-weight: bold; font-size: 1.1rem; padding-bottom: 5px; background-color: #ffebee; padding: 10px; border-radius: 5px; border-left: 5px solid #d32f2f; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# 사우디 리야드 기준 현재 시간 세팅
ksa_tz = pytz.timezone('Asia/Riyadh')
now_ksa = datetime.now(ksa_tz)
current_time_str = now_ksa.strftime("%Y-%m-%d %H:%M (KSA)")
base_date_short = now_ksa.strftime("%y.%m.%d")

st.title("🚢 호르무즈 봉쇄 대응: 다중 포트 및 우회 항로 대시보드")

# 🚨 강한 추정치 경고 문구 삽입
st.markdown(f"<div class='update-time'>⚠️ 주의: 본 데이터는 {current_time_str} 기준 시장 동향을 반영한 <b>'추정치(Estimated)'</b>입니다. 실제 진행 시 반드시 선사 및 현지 운송사의 실시간 요율 확인이 필요합니다.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    pol_input = st.text_input("출발지 (POL)", value="Busan")
with col2:
    pod_input = st.text_input("최종 목적지 (Destination)", value="Riyadh")

if st.button("🚀 심층 라우팅 산출 및 항로 지도 보기", type="primary", use_container_width=True):
    
    if pod_input.lower() in ["riyadh", "리야드", "dammam", "담맘"]:
        # --- 1. 라우팅 데이터 정의 ---
        options = [
            {
                "기준일": base_date_short,
                "선사/옵션": "Maersk (희망봉 우회)",
                "운항 상태": "🟣 초장기 우회",
                "하역 포트 (POD)": "Jeddah (사우디 서안)",
                "해상 상세 라우트": f"{pol_input} ➔ 🌊희망봉 우회 ➔ Jeddah",
                "추정 해상 T/T": "약 55~65 Days",
                "추정 Surcharge": "WRS 약 $1,500 + Cape 약 $1,200",
                "내륙 트럭 구간": "Jeddah ➔ Riyadh",
                "추정 트럭 비용": "약 $1,300~$1,600",
                "보세/통관 실무": "ZATCA 보세 승인 후 Dry Port 통관"
            },
            {
                "기준일": base_date_short,
                "선사/옵션": "HMM (아덴만 직기항)",
                "운항 상태": "🟢 홍해 정상",
                "하역 포트 (POD)": "Jeddah (사우디 서안)",
                "해상 상세 라우트": f"{pol_input} ➔ 콜롬보 ➔ 🌊아덴만 ➔ Jeddah",
                "추정 해상 T/T": "약 35~40 Days",
                "추정 Surcharge": "WRS 약 $1,000 + PSS 약 $500",
                "내륙 트럭 구간": "Jeddah ➔ Riyadh (철도 연계)",
                "추정 트럭 비용": "약 $1,100~$1,400",
                "보세/통관 실무": "SRO(철도청) 연계 보세 운송"
            },
            {
                "기준일": base_date_short,
                "선사/옵션": "CMA CGM (오만 우회)",
                "운항 상태": "🟡 호르무즈 외곽",
                "하역 포트 (POD)": "Sohar (오만 북부)",
                "해상 상세 라우트": f"{pol_input} ➔ 싱가포르 ➔ 🌊오만만 ➔ Sohar",
                "추정 해상 T/T": "약 25~30 Days",
                "추정 Surcharge": "Gulf of Oman SC 약 $600",
                "내륙 트럭 구간": "Sohar ➔ Al Batha 국경 ➔ Riyadh",
                "추정 트럭 비용": "약 $1,800~$2,200",
                "보세/통관 실무": "UAE 통과화물. Al Batha 통관 (Bayan)"
            },
            {
                "기준일": base_date_short,
                "선사/옵션": "전 선사 (걸프만 진입)",
                "운항 상태": "🔴 해협 봉쇄",
                "하역 포트 (POD)": "Dammam (사우디 동안)",
                "해상 상세 라우트": f"{pol_input} ➔ 🌊호르무즈 진입 시도 ➔ Dammam",
                "추정 해상 T/T": "측정 불가",
                "추정 Surcharge": "부킹 전면 제한",
                "내륙 트럭 구간": "N/A",
                "추정 트럭 비용": "N/A",
                "보세/통관 실무": "Dammam 향 B/L 발행 중단"
            }
        ]
        
        df = pd.DataFrame(options)
        
        def highlight_row(row):
            if '🔴' in row['운항 상태']: return ['background-color: rgba(255, 76, 76, 0.2); color: #d32f2f; font-weight: bold;'] * len(row)
            elif '🟣' in row['운항 상태']: return ['background-color: rgba(156, 39, 176, 0.15); color: #6a1b9a; font-weight: bold;'] * len(row)
            elif '🟡' in row['운항 상태']: return ['background-color: rgba(255, 193, 7, 0.15);'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_row, axis=1)
        
        st.markdown("---")
        st.subheader(f"📍 {pol_input} ➔ {pod_input} 실무 라우팅 옵션 (※ 비용/일정은 참고용 추정치입니다)")
        st.dataframe(styled_df, hide_index=True, use_container_width=True)

        # --- 2. 3D 항로 지도 (Pydeck) ---
        st.markdown("---")
        st.subheader("🗺️ 3D 가시성 지도 (선사별 우회 항로 및 내륙 운송)")
        
        # 항구 및 거점 좌표 (경도, 위도)
        coords = {
            "Busan": [129.0756, 35.1795],
            "Singapore": [103.8198, 1.3521],
            "Colombo": [79.8612, 6.9271],
            "Cape": [18.471, -34.356],      # 희망봉 근해
            "Jeddah": [39.1925, 21.4858],
            "Sohar": [56.7067, 24.3461],
            "Dammam": [50.1033, 26.4207],
            "Riyadh": [46.6753, 24.7136]
        }

        # 라우트 데이터 설정 (출발지 -> 도착지, 색상 RGB)
        route_data = [
            # 🟣 Maersk (희망봉 우회: 보라색)
            {"start": coords["Busan"], "end": coords["Singapore"], "color": [156, 39, 176, 200], "name": "Maersk (to TS)"},
            {"start": coords["Singapore"], "end": coords["Cape"], "color": [156, 39, 176, 200], "name": "Maersk (Cape Route)"},
            {"start": coords["Cape"], "end": coords["Jeddah"], "color": [156, 39, 176, 200], "name": "Maersk (to Jeddah)"},
            # 🟢 HMM (홍해 정상: 초록색)
            {"start": coords["Busan"], "end": coords["Colombo"], "color": [76, 175, 80, 200], "name": "HMM (to TS)"},
            {"start": coords["Colombo"], "end": coords["Jeddah"], "color": [76, 175, 80, 200], "name": "HMM (Red Sea)"},
            # 🟡 CMA CGM (오만 소하르 우회: 노란색)
            {"start": coords["Busan"], "end": coords["Singapore"], "color": [255, 193, 7, 200], "name": "CMA (to TS)"},
            {"start": coords["Singapore"], "end": coords["Sohar"], "color": [255, 193, 7, 200], "name": "CMA (to Oman)"},
            # 🔴 Dammam (차단/실패: 빨간색)
            {"start": coords["Busan"], "end": coords["Dammam"], "color": [244, 67, 54, 200], "name": "Blocked Route"},
            
            # 🚚 내륙 운송 (Jeddah, Sohar, Dammam -> Riyadh: 파란색 계열)
            {"start": coords["Jeddah"], "end": coords["Riyadh"], "color": [33, 150, 243, 255], "name": "Inland: Jeddah-Riyadh"},
            {"start": coords["Sohar"], "end": coords["Riyadh"], "color": [33, 150, 243, 255], "name": "Inland: Sohar-Riyadh"},
            {"start": coords["Dammam"], "end": coords["Riyadh"], "color": [158, 158, 158, 150], "name": "Inland: Blocked"}
        ]

        # Pydeck Arc Layer (항로 그리기)
        layer = pdk.Layer(
            "ArcLayer",
            data=route_data,
            get_source_position="start",
            get_target_position="end",
            get_source_color="color",
            get_target_color="color",
            get_width=3,
            pitch=50
        )
        
        # 거점 Point Layer (도시/항구 마커)
        points_data = [{"name": k, "pos": v} for k, v in coords.items()]
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=points_data,
            get_position="pos",
            get_color=[255, 255, 255, 200],
            get_radius=200000, # 마커 크기
        )

        # 지도 초기 시점 설정 (사우디/중동 중심)
        view_state = pdk.ViewState(latitude=20.0, longitude=60.0, zoom=2, pitch=45)
        st.pydeck_chart(pdk.Deck(layers=[layer, scatter_layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/dark-v10"))
        
        st.markdown("<div style='font-size:0.85em; color:gray; text-align:center;'>* 🟣 보라색: 희망봉 우회 / 🟢 초록색: 아덴만 직기항 / 🟡 노란색: 오만 우회 / 🔴 빨간색: 걸프만 차단 / 🔵 파란색: 사우디 내륙 운송</div>", unsafe_allow_html=True)
        
        # --- 3. 엑셀 다운로드 ---
        st.markdown("<br>", unsafe_allow_html=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Routing_Options')
            worksheet = writer.sheets['Routing_Options']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4 
                worksheet.column_dimensions[chr(65 + idx)].width = max_len
            
            worksheet.cell(row=len(df)+3, column=1, value="[⚠️ Disclaimer: 본 자료의 비용 및 소요 일정(T/T)은 특정 시점의 시장 동향을 반영한 '추정치(Estimate)'입니다.]")
            worksheet.cell(row=len(df)+4, column=1, value="[실제 선적을 위한 정확한 운임과 스케줄은 반드시 담당 포워더 및 선사에 별도 확인 바랍니다.]")
            worksheet.cell(row=len(df)+5, column=1, value=f"자료 산출 일시: {current_time_str}")
            worksheet.cell(row=len(df)+6, column=1, value="Generated by Rino from Andromeda")

        buffer.seek(0)
        
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            st.download_button(
                label="📥 리포트 다운로드 (Excel)",
                data=buffer,
                file_name=f"Route_Estimate_{now_ksa.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # --- 4. 통관/보세운송 실무 FAQ ---
        st.markdown("---")
        st.subheader("📌 사우디 내륙 운송 및 통관 실무 FAQ")
        
        faq1 = st.expander("Q. 제다(Jeddah) 하역 후 리야드(Riyadh)로 보세운송(In-bond)하는 절차는?")
        faq1.write("""
        사우디 관세청(ZATCA)의 엄격한 통제 하에 진행됩니다. 
        1. **FASAH 사전 등록:** 선적 전 혹은 화물 도착 최소 3~5일 전, 사우디 통합 물류 포털인 FASAH에 선적 서류(Commercial Invoice, Packing List, CO)를 업로드하여 보세 운송 승인을 받아야 합니다.
        2. **제다 항만 반출:** 보세 승인이 떨어지면, 씰(Seal)이 봉인된 상태로 제다 항구를 빠져나와 지정된 트럭 또는 철도(SRO)를 통해 리야드 건항(Riyadh Dry Port)으로 이동합니다.
        3. **최종 통관:** 리야드 건항에 도착 후 세관의 최종 물품 검사 및 관세 납부가 이루어집니다. 제다 항만 병목 시 철도 스페이스 확보가 매우 어렵다는 점을 유의해야 합니다.
        """)
        
        faq2 = st.expander("Q. 살랄라/소하르(오만) 등 제3국 우회 시 국경 통관 주의점은?")
        faq2.write("""
        이 루트는 해상 운송은 짧지만, 내륙에서 국가 간 국경(Cross-Border)을 넘어야 하는 리스크가 있습니다.
        1. **통과화물(Transit Cargo) 규정:** 화물은 오만에 귀속되지 않고 사우디로 통과한다는 의미의 'Bayan(세관 신고서)' 작성이 오만 하역 즉시 진행되어야 합니다.
        2. **TIR Carnet 활용:** 국제 도로 수송 증서인 TIR Carnet을 활용하면 중간 기착지에서의 세관 검사를 면제받아 국경 통과 속도를 높일 수 있습니다.
        3. **국경 체선(Congestion):** 오만-UAE, UAE-사우디(Al Batha 국경 등)을 지날 때 트럭 대기 줄이 길어지면 며칠씩 지연될 수 있으며, 이때 발생하는 트럭 대기료(Detention)에 대한 책임 소재를 운송사와 사전 협의해야 합니다.
        """)
        
        faq3 = st.expander("Q. 필수 서류 및 기타 주의사항은?")
        faq3.write("""
        * **영사 확인(Attestation):** 사우디 정부의 원산지 증명서(CO) 및 상업 송장(CI) 규정에 따라, 출발국(한국) 주재 사우디 대사관 및 상공회의소의 영사 확인이 완벽하게 되어있지 않으면 우회 포트이건 직기항이건 통관이 100% 보류됩니다.
        * **SASO/SABER 인증:** 공산품 및 특정 수입 품목에 대해 사우디 표준청(SASO)의 SABER 시스템 등록 증명서가 화물 도착 전 완벽히 구비되어 있어야 합니다.
        """)

    else:
        st.warning(f"현재 '{pod_input}' 목적지에 대한 데이터가 없습니다. Riyadh를 입력해 주세요.")

# --- 5. 저작권 표시 ---
st.markdown('<div class="footer">© Rino from Andromeda</div>', unsafe_allow_html=True)
