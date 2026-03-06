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

# --- 언어 선택 (Language Selector) ---
col_lang1, col_lang2 = st.columns([5, 1])
with col_lang2:
    lang_choice = st.selectbox("🌐 Language / 언어", ["한국어", "English"])

is_ko = (lang_choice == "한국어")

# --- 다국어 텍스트 딕셔너리 ---
t = {
    "title": "🚢 호르무즈 봉쇄 대응: 다중 포트 및 우회 항로 대시보드" if is_ko else "🚢 Hormuz Blockade Response: Multi-Port & Detour Route Dashboard",
    "warning": f"⚠️ 주의: 본 데이터는 {current_time_str} 기준 시장 동향을 반영한 <b>'추정치(Estimated)'</b>입니다. 실제 진행 시 반드시 선사 및 현지 운송사의 실시간 요율 확인이 필요합니다." if is_ko else f"⚠️ Notice: This data is an <b>'Estimate'</b> reflecting market trends as of {current_time_str}. Real-time verification with carriers and local transporters is strictly required.",
    "pol": "출발지 (POL)" if is_ko else "Origin (POL)",
    "pod": "최종 목적지 (Destination)" if is_ko else "Final Destination (POD)",
    "btn_calc": "🚀 심층 라우팅 산출 및 항로 지도 보기" if is_ko else "🚀 Calculate Deep Routing & View Map",
    "no_data": f"현재 목적지에 대한 데이터가 없습니다. Riyadh를 입력해 주세요." if is_ko else f"No data available for the destination. Please enter Riyadh or Dammam.",
    "map_title": "🗺️ 3D 가시성 지도 (선사별 우회 항로 및 내륙 운송)" if is_ko else "🗺️ 3D Visibility Map (Carrier Detour Routes & Inland Transport)",
    "map_legend": "* 🟣 보라색: 희망봉 우회 / 🟢 초록색: 아덴만 직기항 / 🟡 노란색: 오만 우회 / 🔴 빨간색: 걸프만 차단 / 🔵 파란색: 사우디 내륙 운송" if is_ko else "* 🟣 Purple: Cape Detour / 🟢 Green: Gulf of Aden Direct / 🟡 Yellow: Oman Detour / 🔴 Red: Gulf Blocked / 🔵 Blue: Saudi Inland Transport",
    "btn_dl": "📥 리포트 다운로드 (Excel)" if is_ko else "📥 Download Report (Excel)",
    "faq_title": "📌 사우디 내륙 운송 및 통관 실무 FAQ" if is_ko else "📌 Saudi Inland Transport & Customs FAQ",
    "discl1": "[⚠️ Disclaimer: 본 자료의 비용 및 소요 일정(T/T)은 특정 시점의 시장 동향을 반영한 '추정치(Estimate)'입니다.]" if is_ko else "[⚠️ Disclaimer: Costs and Transit Times (T/T) are 'Estimates' reflecting market trends at a specific time.]",
    "discl2": "[실제 선적을 위한 정확한 운임과 스케줄은 반드시 담당 포워더 및 선사에 별도 확인 바랍니다.]" if is_ko else "[Please verify exact rates and schedules with your forwarder and carrier before actual shipment.]",
    "generated_at": f"자료 산출 일시: {current_time_str}" if is_ko else f"Generated at: {current_time_str}"
}

st.title(t["title"])
st.markdown(f"<div class='update-time'>{t['warning']}</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    pol_input = st.text_input(t["pol"], value="Busan")
with col2:
    pod_input = st.text_input(t["pod"], value="Riyadh")

if st.button(t["btn_calc"], type="primary", use_container_width=True):
    
    if pod_input.lower() in ["riyadh", "리야드", "dammam", "담맘"]:
        
        # --- 한국어 / 영어 데이터프레임 구성 ---
        if is_ko:
            options = [
                {"기준일": base_date_short, "선사/옵션": "Maersk (희망봉 우회)", "운항 상태": "🟣 초장기 우회", "하역 포트 (POD)": "Jeddah (사우디 서안)", "해상 상세 라우트": f"{pol_input} ➔ 🌊희망봉 우회 ➔ Jeddah", "추정 해상 T/T": "약 55~65 Days", "추정 Surcharge": "WRS 약 $1,500 + Cape 약 $1,200", "내륙 트럭 구간": "Jeddah ➔ Riyadh", "추정 트럭 비용": "약 $1,300~$1,600", "보세/통관 실무": "ZATCA 보세 승인 후 Dry Port 통관"},
                {"기준일": base_date_short, "선사/옵션": "HMM (아덴만 직기항)", "운항 상태": "🟢 홍해 정상", "하역 포트 (POD)": "Jeddah (사우디 서안)", "해상 상세 라우트": f"{pol_input} ➔ 콜롬보 ➔ 🌊아덴만 ➔ Jeddah", "추정 해상 T/T": "약 35~40 Days", "추정 Surcharge": "WRS 약 $1,000 + PSS 약 $500", "내륙 트럭 구간": "Jeddah ➔ Riyadh (철도 연계)", "추정 트럭 비용": "약 $1,100~$1,400", "보세/통관 실무": "SRO(철도청) 연계 보세 운송"},
                {"기준일": base_date_short, "선사/옵션": "CMA CGM (오만 우회)", "운항 상태": "🟡 호르무즈 외곽", "하역 포트 (POD)": "Sohar (오만 북부)", "해상 상세 라우트": f"{pol_input} ➔ 싱가포르 ➔ 🌊오만만 ➔ Sohar", "추정 해상 T/T": "약 25~30 Days", "추정 Surcharge": "Gulf of Oman SC 약 $600", "내륙 트럭 구간": "Sohar ➔ Al Batha 국경 ➔ Riyadh", "추정 트럭 비용": "약 $1,800~$2,200", "보세/통관 실무": "UAE 통과화물. Al Batha 통관 (Bayan)"},
                {"기준일": base_date_short, "선사/옵션": "전 선사 (걸프만 진입)", "운항 상태": "🔴 해협 봉쇄", "하역 포트 (POD)": "Dammam (사우디 동안)", "해상 상세 라우트": f"{pol_input} ➔ 🌊호르무즈 진입 시도 ➔ Dammam", "추정 해상 T/T": "측정 불가", "추정 Surcharge": "부킹 전면 제한", "내륙 트럭 구간": "N/A", "추정 트럭 비용": "N/A", "보세/통관 실무": "Dammam 향 B/L 발행 중단"}
            ]
            table_header = f"📍 {pol_input} ➔ {pod_input} 실무 라우팅 옵션 (※ 비용/일정은 참고용 추정치입니다)"
        else:
            options = [
                {"Base Date": base_date_short, "Carrier/Option": "Maersk (Cape Detour)", "Status": "🟣 Long Detour", "Discharge Port": "Jeddah (West Coast)", "Ocean Route Detail": f"{pol_input} ➔ 🌊Cape of Good Hope ➔ Jeddah", "Est. Ocean T/T": "~55-65 Days", "Est. Surcharge": "WRS ~$1,500 + Cape ~$1,200", "Inland Truck Route": "Jeddah ➔ Riyadh", "Est. Truck Cost": "~$1,300-$1,600", "Customs/In-bond": "ZATCA In-bond to Dry Port"},
                {"Base Date": base_date_short, "Carrier/Option": "HMM (Aden Direct)", "Status": "🟢 Red Sea Normal", "Discharge Port": "Jeddah (West Coast)", "Ocean Route Detail": f"{pol_input} ➔ Colombo ➔ 🌊Gulf of Aden ➔ Jeddah", "Est. Ocean T/T": "~35-40 Days", "Est. Surcharge": "WRS ~$1,000 + PSS ~$500", "Inland Truck Route": "Jeddah ➔ Riyadh (Rail Link)", "Est. Truck Cost": "~$1,100-$1,400", "Customs/In-bond": "SRO Rail In-bond Transport"},
                {"Base Date": base_date_short, "Carrier/Option": "CMA CGM (Oman Detour)", "Status": "🟡 Hormuz Detour", "Discharge Port": "Sohar (North Oman)", "Ocean Route Detail": f"{pol_input} ➔ Singapore ➔ 🌊Gulf of Oman ➔ Sohar", "Est. Ocean T/T": "~25-30 Days", "Est. Surcharge": "Gulf of Oman SC ~$600", "Inland Truck Route": "Sohar ➔ Al Batha Border ➔ Riyadh", "Est. Truck Cost": "~$1,800-$2,200", "Customs/In-bond": "UAE Transit. Al Batha Customs"},
                {"Base Date": base_date_short, "Carrier/Option": "All Carriers (Gulf Entry)", "Status": "🔴 Strait Blocked", "Discharge Port": "Dammam (East Coast)", "Ocean Route Detail": f"{pol_input} ➔ 🌊Hormuz Attempt ➔ Dammam", "Est. Ocean T/T": "N/A", "Est. Surcharge": "Booking Restricted", "Inland Truck Route": "N/A", "Est. Truck Cost": "N/A", "Customs/In-bond": "Dammam B/L Issuance Suspended"}
            ]
            table_header = f"📍 {pol_input} ➔ {pod_input} Routing Options (※ Costs/Schedules are estimated references)"
        
        df = pd.DataFrame(options)
        
        # 색상 하이라이트 로직 (한/영 공통 적용을 위해 이모지로 판별)
        def highlight_row(row):
            status = row['운항 상태'] if is_ko else row['Status']
            if '🔴' in status: return ['background-color: rgba(255, 76, 76, 0.2); color: #d32f2f; font-weight: bold;'] * len(row)
            elif '🟣' in status: return ['background-color: rgba(156, 39, 176, 0.15); color: #6a1b9a; font-weight: bold;'] * len(row)
            elif '🟡' in status: return ['background-color: rgba(255, 193, 7, 0.15);'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_row, axis=1)
        
        st.markdown("---")
        st.subheader(table_header)
        st.dataframe(styled_df, hide_index=True, use_container_width=True)

        # --- 3D 항로 지도 (Pydeck) ---
        st.markdown("---")
        st.subheader(t["map_title"])
        
        coords = {"Busan": [129.0756, 35.1795], "Singapore": [103.8198, 1.3521], "Colombo": [79.8612, 6.9271], "Cape": [18.471, -34.356], "Jeddah": [39.1925, 21.4858], "Sohar": [56.7067, 24.3461], "Dammam": [50.1033, 26.4207], "Riyadh": [46.6753, 24.7136]}

        route_data = [
            {"start": coords["Busan"], "end": coords["Singapore"], "color": [156, 39, 176, 200]},
            {"start": coords["Singapore"], "end": coords["Cape"], "color": [156, 39, 176, 200]},
            {"start": coords["Cape"], "end": coords["Jeddah"], "color": [156, 39, 176, 200]},
            {"start": coords["Busan"], "end": coords["Colombo"], "color": [76, 175, 80, 200]},
            {"start": coords["Colombo"], "end": coords["Jeddah"], "color": [76, 175, 80, 200]},
            {"start": coords["Busan"], "end": coords["Singapore"], "color": [255, 193, 7, 200]},
            {"start": coords["Singapore"], "end": coords["Sohar"], "color": [255, 193, 7, 200]},
            {"start": coords["Busan"], "end": coords["Dammam"], "color": [244, 67, 54, 200]},
            {"start": coords["Jeddah"], "end": coords["Riyadh"], "color": [33, 150, 243, 255]},
            {"start": coords["Sohar"], "end": coords["Riyadh"], "color": [33, 150, 243, 255]},
            {"start": coords["Dammam"], "end": coords["Riyadh"], "color": [158, 158, 158, 150]}
        ]

        layer = pdk.Layer("ArcLayer", data=route_data, get_source_position="start", get_target_position="end", get_source_color="color", get_target_color="color", get_width=3, pitch=50)
        points_data = [{"name": k, "pos": v} for k, v in coords.items()]
        scatter_layer = pdk.Layer("ScatterplotLayer", data=points_data, get_position="pos", get_color=[255, 255, 255, 200], get_radius=200000)

        view_state = pdk.ViewState(latitude=20.0, longitude=60.0, zoom=2, pitch=45)
        st.pydeck_chart(pdk.Deck(layers=[layer, scatter_layer], initial_view_state=view_state, map_style="mapbox://styles/mapbox/dark-v10"))
        
        st.markdown(f"<div style='font-size:0.85em; color:gray; text-align:center;'>{t['map_legend']}</div>", unsafe_allow_html=True)
        
        # --- 엑셀 다운로드 (언어별 동적 반영) ---
        st.markdown("<br>", unsafe_allow_html=True)
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Routing_Options')
            worksheet = writer.sheets['Routing_Options']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4 
                worksheet.column_dimensions[chr(65 + idx)].width = max_len
            
            worksheet.cell(row=len(df)+3, column=1, value=t["discl1"])
            worksheet.cell(row=len(df)+4, column=1, value=t["discl2"])
            worksheet.cell(row=len(df)+5, column=1, value=t["generated_at"])
            worksheet.cell(row=len(df)+6, column=1, value="Generated by Rino from Andromeda")

        buffer.seek(0)
        
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            st.download_button(
                label=t["btn_dl"],
                data=buffer,
                file_name=f"Route_Estimate_{now_ksa.strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        # --- 통관/보세운송 실무 FAQ ---
        st.markdown("---")
        st.subheader(t["faq_title"])
        
        if is_ko:
            faq1 = st.expander("Q. 제다(Jeddah) 하역 후 리야드(Riyadh)로 보세운송(In-bond)하는 절차는?")
            faq1.write("사우디 관세청(ZATCA)의 엄격한 통제 하에 진행됩니다.\n1. **FASAH 사전 등록:** 선적 전 혹은 화물 도착 최소 3~5일 전, 사우디 통합 물류 포털인 FASAH에 선적 서류(Commercial Invoice, Packing List, CO)를 업로드하여 보세 운송 승인을 받아야 합니다.\n2. **제다 항만 반출:** 보세 승인이 떨어지면, 씰(Seal)이 봉인된 상태로 제다 항구를 빠져나와 지정된 트럭 또는 철도(SRO)를 통해 리야드 건항(Riyadh Dry Port)으로 이동합니다.\n3. **최종 통관:** 리야드 건항에 도착 후 세관의 최종 물품 검사 및 관세 납부가 이루어집니다.")
            
            faq2 = st.expander("Q. 살랄라/소하르(오만) 등 제3국 우회 시 국경 통관 주의점은?")
            faq2.write("이 루트는 해상 운송은 짧지만, 내륙에서 국가 간 국경(Cross-Border)을 넘어야 하는 리스크가 있습니다.\n1. **통과화물(Transit Cargo) 규정:** 화물은 오만에 귀속되지 않고 사우디로 통과한다는 의미의 'Bayan(세관 신고서)' 작성이 오만 하역 즉시 진행되어야 합니다.\n2. **TIR Carnet 활용:** 국제 도로 수송 증서인 TIR Carnet을 활용하면 중간 기착지에서의 세관 검사를 면제받아 국경 통과 속도를 높일 수 있습니다.\n3. **국경 체선(Congestion):** 오만-UAE, UAE-사우디 국경을 지날 때 트럭 대기료(Detention)에 대한 책임 소재를 운송사와 사전 협의해야 합니다.")
            
            faq3 = st.expander("Q. 필수 서류 및 기타 주의사항은?")
            faq3.write("* **영사 확인(Attestation):** 사우디 정부의 규정에 따라, 출발국(한국) 주재 사우디 대사관 및 상공회의소의 원산지 증명서(CO) 및 상업 송장(CI) 영사 확인이 완벽하게 되어있지 않으면 통관이 보류됩니다.\n* **SASO/SABER 인증:** 공산품 및 특정 수입 품목에 대해 사우디 표준청(SASO)의 SABER 시스템 등록 증명서가 화물 도착 전 완벽히 구비되어 있어야 합니다.")
        else:
            faq1 = st.expander("Q. What is the In-bond procedure from Jeddah to Riyadh?")
            faq1.write("It is conducted under strict control of ZATCA.\n1. **FASAH Pre-registration:** At least 3-5 days before cargo arrival, shipping documents (CI, PL, CO) must be uploaded to FASAH to get in-bond approval.\n2. **Jeddah Port Exit:** Once approved, the sealed cargo leaves Jeddah port via truck or railway (SRO) to Riyadh Dry Port.\n3. **Final Customs Clearance:** Final inspection and duty payment are processed at Riyadh Dry Port.")
            
            faq2 = st.expander("Q. Cross-border customs precautions when detouring via Oman (Salalah/Sohar)?")
            faq2.write("While ocean transit is shorter, crossing international borders poses risks.\n1. **Transit Cargo Rule:** A 'Bayan' (Customs Declaration) indicating the cargo is transiting to Saudi Arabia must be filed immediately upon discharge in Oman.\n2. **TIR Carnet:** Utilizing the TIR Carnet can waive intermediate customs inspections and speed up border crossings.\n3. **Border Congestion:** Responsibility for truck detention charges due to long queues at UAE-Saudi borders must be pre-negotiated with transporters.")
            
            faq3 = st.expander("Q. What are the mandatory documents and other precautions?")
            faq3.write("* **Attestation:** Per Saudi regulations, CI and CO must be attested by the Chamber of Commerce and the Saudi Embassy in the origin country. Otherwise, customs will be suspended.\n* **SASO/SABER:** For manufactured goods, SABER certificates from the Saudi Standards, Metrology and Quality Organization (SASO) must be secured before arrival.")

    else:
        st.warning(t["no_data"])

st.markdown('<div class="footer">© Rino from Andromeda</div>', unsafe_allow_html=True)
