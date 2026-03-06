import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz

st.set_page_config(page_title="Advanced Route Analyzer", layout="wide", page_icon="🚢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 10px; color: #6c757d; font-size: 0.9rem; font-weight: bold; }
    .update-time { color: #0066cc; font-weight: bold; font-size: 1.1rem; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

st.title("🚢 호르무즈 봉쇄 대응: 다중 포트 및 희망봉 우회 분석")
st.markdown(f"<div class='update-time'>🕒 시황 업데이트 기준: {current_time} (사우디 현지시각)</div>", unsafe_allow_html=True)
st.markdown("호르무즈 외곽 항만(오만, UAE 동해안) 및 아프리카 희망봉 우회 등 딥레벨(Deep-level) 라우팅 옵션을 제공합니다.")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    pol_input = st.text_input("출발지 (POL)", value="Busan")
with col2:
    pod_input = st.text_input("최종 목적지 (Destination)", value="Riyadh")

if st.button("🚀 심층 라우팅 옵션 산출", type="primary", use_container_width=True):
    
    if pod_input.lower() in ["riyadh", "리야드", "dammam", "담맘"]:
        options = [
            {
                "선사/옵션": "Maersk (희망봉 우회)",
                "운항 상태": "🟣 초장기 우회",
                "하역 포트 (POD)": "Jeddah (사우디 서안)",
                "해상 상세 라우트": f"{pol_input} ➔ 싱가포르 ➔ 🌊희망봉(남아공) ➔ 지브롤터 ➔ 지중해 ➔ 수에즈 ➔ Jeddah",
                "해상 T/T": "55~65 Days (홍해 남단 진입 불가 시)",
                "적용 Surcharge": "WRS $1,500 + Cape Routing $1,200",
                "내륙 트럭킹 구간": "Jeddah ➔ Riyadh",
                "트럭킹 비용/T_T": "$1,300~$1,600 (3~5일)",
                "통관/보세 실무": "ZATCA 보세운송 승인 후 Riyadh Dry Port 통관"
            },
            {
                "선사/옵션": "HMM (아덴만 직기항)",
                "운항 상태": "🟢 홍해 정상",
                "하역 포트 (POD)": "Jeddah (사우디 서안)",
                "해상 상세 라우트": f"{pol_input} ➔ 콜롬보 ➔ 🌊아덴만(Bab el-Mandeb) ➔ Jeddah",
                "해상 T/T": "35~40 Days",
                "적용 Surcharge": "WRS $1,000 + PSS $500",
                "내륙 트럭킹 구간": "Jeddah ➔ Riyadh (철도 연계)",
                "트럭킹 비용/T_T": "$1,100~$1,400 (5~7일)",
                "통관/보세 실무": "SRO(철도청) 연계 보세 운송 (열차 스페이스 확보 필수)"
            },
            {
                "선사/옵션": "CMA CGM (오만 우회)",
                "운항 상태": "🟡 호르무즈 외곽 하역",
                "하역 포트 (POD)": "Sohar (오만 북부)",
                "해상 상세 라우트": f"{pol_input} ➔ 싱가포르 ➔ 🌊오만만 ➔ Sohar",
                "해상 T/T": "25~30 Days",
                "적용 Surcharge": "Gulf of Oman Surcharge $600",
                "내륙 트럭킹 구간": "Sohar ➔ UAE (Al Ain) ➔ Al Batha 국경 ➔ Riyadh",
                "트럭킹 비용/T_T": "$1,800~$2,200 (4~6일)",
                "통관/보세 실무": "UAE 경유 통과화물. Al Batha 국경 통관 (Bayan 사전 준비)"
            },
            {
                "선사/옵션": "MSC (UAE 동해안)",
                "운항 상태": "🟡 호르무즈 외곽 하역",
                "하역 포트 (POD)": "Khor Fakkan / Fujairah (UAE)",
                "해상 상세 라우트": f"{pol_input} ➔ 콜롬보 ➔ 🌊오만만 ➔ Khor Fakkan",
                "해상 T/T": "24~28 Days",
                "적용 Surcharge": "Discharge Premium $800",
                "내륙 트럭킹 구간": "Khor Fakkan ➔ UAE Landbridge ➔ Al Batha ➔ Riyadh",
                "트럭킹 비용/T_T": "$1,500~$1,900 (3~5일)",
                "통관/보세 실무": "UAE 랜드브릿지 활용. 국경 체선 리스크 대비 필요"
            },
            {
                "선사/옵션": "통합 (남부 오만 하역)",
                "운항 상태": "🟡 롱디스턴스 트럭킹",
                "하역 포트 (POD)": "Salalah (오만 남부)",
                "해상 상세 라우트": f"{pol_input} ➔ 싱가포르 ➔ 🌊아라비아해 ➔ Salalah",
                "해상 T/T": "22~26 Days (가장 짧은 해상)",
                "적용 Surcharge": "N/A",
                "내륙 트럭킹 구간": "Salalah ➔ 룹알할리 외곽 ➔ 사우디 국경(Empty Quarter) ➔ Riyadh",
                "트럭킹 비용/T_T": "$3,000~$4,000 (7~10일)",
                "통관/보세 실무": "초장거리 국경 트럭킹. 운송사 수배 난이도 최상. TIR Carnet 필수"
            },
            {
                "선사/옵션": "전 선사 (걸프만 진입)",
                "운항 상태": "🔴 해협 봉쇄",
                "하역 포트 (POD)": "Jebel Ali / Dammam",
                "해상 상세 라우트": f"{pol_input} ➔ 🌊호르무즈 해협 통과 시도 ➔ Jebel Ali/Dammam",
                "해상 T/T": "측정 불가",
                "적용 Surcharge": "부킹 전면 제한",
                "내륙 트럭킹 구간": "N/A",
                "트럭킹 비용/T_T": "N/A",
                "통관/보세 실무": "현재 Dammam 향 B/L 발행 중단"
            }
        ]
        
        df = pd.DataFrame(options)
        
        # 조건부 서식 함수
        def highlight_row(row):
            if '🔴' in row['운항 상태']: return ['background-color: rgba(255, 76, 76, 0.2); color: #d32f2f; font-weight: bold;'] * len(row)
            elif '🟣' in row['운항 상태']: return ['background-color: rgba(156, 39, 176, 0.15); color: #6a1b9a; font-weight: bold;'] * len(row)
            elif '🟡' in row['운항 상태']: return ['background-color: rgba(255, 193, 7, 0.15);'] * len(row)
            return [''] * len(row)
        
        styled_df = df.style.apply(highlight_row, axis=1)
        
        st.markdown("---")
        st.subheader(f"📍 {pol_input} ➔ {pod_input} 다중 포트 라우팅 상세 옵션")
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        
        # 엑셀 다운로드
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Deep_Routing_Options')
            worksheet = writer.sheets['Deep_Routing_Options']
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4 
                worksheet.column_dimensions[chr(65 + idx)].width = max_len
                
            worksheet.cell(row=len(df)+3, column=1, value="[Data Market Insight - Routing Dept.]")
            worksheet.cell(row=len(df)+4, column=1, value=f"업데이트 기준: {current_time} (사우디 현지시각)")
            worksheet.cell(row=len(df)+5, column=1, value="Generated by Rino from Andromeda")

        buffer.seek(0)
        
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            st.download_button(
                label="📥 상세 라우팅 리포트 다운로드 (Excel)",
                data=buffer,
                file_name=f"Deep_Routing_{datetime.now(ksa_tz).strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

    else:
        st.warning(f"현재 '{pod_input}' 목적지에 대한 데이터가 없습니다. Riyadh를 입력해 주세요.")

st.markdown('<div class="footer">© Rino from Andromeda</div>', unsafe_allow_html=True)
