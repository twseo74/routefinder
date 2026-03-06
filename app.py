import streamlit as st
import pandas as pd
import io
from datetime import datetime
import pytz

# --- 1. 페이지 기본 설정 및 CSS 디자인 ---
st.set_page_config(page_title="Inbound Route Analyzer", layout="wide", page_icon="🚢")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 2rem; }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: transparent;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    .update-time {
        color: #0066cc;
        font-weight: bold;
        font-size: 1.1rem;
        padding-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 데이터 기준 일시 설정 (사우디 리야드 시간 기준) ---
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y년 %m월 %d일 %H:%M")

# --- 3. 헤더 및 대시보드 요약 ---
st.title("🚢 호르무즈 봉쇄 대응: 대체 항로 및 물류비 대시보드")
st.markdown(f"<div class='update-time'>🕒 시황 업데이트 기준: {current_time} (사우디 현지시각)</div>", unsafe_allow_html=True)
st.markdown("최신 해상 시황(WRS 폭등, 우회 하역) 및 내륙 트럭킹/보세운송 실무를 종합한 인바운드 최적화 툴입니다.")
st.markdown("---")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric(label="현재 통항 상태", value="걸프만 마비", delta="전면 우회 필요", delta_color="inverse")
col_m2.metric(label="최고 Surcharge (WRS)", value="$1,500 / TEU", delta="상승 중", delta_color="inverse")
col_m3.metric(label="평균 해상 T/T (Jeddah 향)", value="45 Days", delta="+15 Days 지연", delta_color="inverse")
col_m4.metric(label="Jeddah ➔ Riyadh 트럭", value="$1,400 평균", delta="수요 폭증", delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

# --- 4. 검색 조건 입력 영역 ---
st.subheader("🔍 구간 검색")
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        pol_input = st.text_input("출발지 (POL)", value="Busan")
    with col2:
        pod_input = st.text_input("최종 목적지 (Destination)", value="Riyadh")

# --- 5. 메인 로직 및 결과 출력 ---
if st.button("🚀 최적 라우팅 및 비용 산출", type="primary", use_container_width=True):
    
    if pod_input.lower() in ["riyadh", "리야드", "dammam", "담맘"]:
        options = [
            {
                "선사": "Maersk",
                "운항 상태": "🟢 홍해 우회 중",
                "해상 루트 (POL-TS-POD)": f"{pol_input} ➔ Singapore ➔ Jeddah",
                "예상 T/T (해상)": "45~50 Days",
                "적용 Surcharge": "WRS $1,500 + Rerouting $800",
                "내륙 루트 (POD-Dest)": "Jeddah ➔ Riyadh (트럭)",
                "예상 트럭킹 비용": "$1,200 ~ $1,600",
                "보세운송 및 통관 실무": "✅ ZATCA 보세운송 승인 후 Dry Port 통관 (FASAH 사전 등록)"
            },
            {
                "선사": "HMM",
                "운항 상태": "🟢 홍해 우회 중",
                "해상 루트 (POL-TS-POD)": f"{pol_input} ➔ Colombo ➔ Jeddah",
                "예상 T/T (해상)": "42~48 Days",
                "적용 Surcharge": "WRS $1,000 + PSS $500",
                "내륙 루트 (POD-Dest)": "Jeddah ➔ Riyadh (철도 연계 트럭)",
                "예상 트럭킹 비용": "$1,000 ~ $1,300",
                "보세운송 및 통관 실무": "✅ SRO(철도청) 연계 보세 운송 (항만 체화 시 지연 우려)"
            },
            {
                "선사": "MSC",
                "운항 상태": "🟡 인접국 하역",
                "해상 루트 (POL-TS-POD)": f"{pol_input} ➔ Salalah (오만)",
                "예상 T/T (해상)": "35~40 Days",
                "적용 Surcharge": "Deviation Surcharge $800",
                "내륙 루트 (POD-Dest)": "Salalah ➔ Al Batha 국경 ➔ Riyadh",
                "예상 트럭킹 비용": "$2,500 ~ $3,500",
                "보세운송 및 통관 실무": "⚠️ 조건부 가능 (TIR Carnet 활용 통과화물. 국경 체선 리스크 높음)"
            },
            {
                "선사": "Hapag-Lloyd",
                "운항 상태": "🔴 걸프만 불가",
                "해상 루트 (POL-TS-POD)": f"{pol_input} ➔ Jebel Ali ➔ Dammam",
                "예상 T/T (해상)": "측정 불가",
                "적용 Surcharge": "N/A (부킹 제한)",
                "내륙 루트 (POD-Dest)": "Dammam ➔ Riyadh",
                "예상 트럭킹 비용": "N/A",
                "보세운송 및 통관 실무": "❌ 불가 (Dammam 항만 진입 차질로 서비스 일시 중단)"
            }
        ]
        
        df = pd.DataFrame(options)
        
        # --- [추가] 조건부 서식 함수 (위험도 하이라이트) ---
        def highlight_row(row):
            if '🔴' in row['운항 상태']:
                # 붉은색 배경과 진한 붉은 글씨로 행 전체 강조
                return ['background-color: rgba(255, 76, 76, 0.2); color: #d32f2f; font-weight: bold;'] * len(row)
            elif '🟡' in row['운항 상태']:
                return ['background-color: rgba(255, 193, 7, 0.2);'] * len(row)
            return [''] * len(row)
        
        # 스타일 적용
        styled_df = df.style.apply(highlight_row, axis=1)
        
        st.markdown("---")
        st.subheader(f"📍 {pol_input} ➔ {pod_input} 선사별 상세 가용 옵션")
        
        # 스타일이 적용된 데이터프레임 화면 출력
        st.dataframe(styled_df, hide_index=True, use_container_width=True)
        
        # --- 6. 엑셀 다운로드 (시간 정보 포함) ---
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # 원본 데이터(df)를 엑셀로 저장
            df.to_excel(writer, index=False, sheet_name='Routing_Options')
            
            worksheet = writer.sheets['Routing_Options']
            
            # 엑셀 열 너비 자동 맞춤
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 4 
                worksheet.column_dimensions[chr(65 + idx)].width = max_len
                
            # 엑셀 하단에 데이터 기준 시간 추가
            worksheet.cell(row=len(df)+3, column=1, value="[Data Market Insight]")
            worksheet.cell(row=len(df)+4, column=1, value=f"업데이트 기준: {current_time} (사우디 현지시각)")
            worksheet.cell(row=len(df)+5, column=1, value="Generated by Rino from Andromeda")

        buffer.seek(0)
        
        col_btn1, col_btn2 = st.columns([1, 3])
        with col_btn1:
            st.download_button(
                label="📥 엑셀 리포트 다운로드",
                data=buffer,
                file_name=f"Alternative_Routes_{datetime.now(ksa_tz).strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        # --- 7. 실무 경고 아코디언 ---
        with st.expander("🚨 현지 내륙 운송 및 통관 주의사항 (클릭하여 열기)", expanded=True):
            st.warning("""
            * **Jeddah 항만 병목:** 하역 물량이 평소 대비 폭증하여 트럭 수배 자체가 불가능해질 수 있습니다. 화물 ETA 최소 2주 전 현지 운송사와 스페이스 및 단가 사전 확정이 필수입니다.
            * **크로스보더 (Salalah/오만 우회 시):** 국경 통과를 위한 Bayan(세관 신고서) 및 원산지 증명서(CO)의 사우디 대사관 영사 확인이 사전에 완벽히 준비되어야 체선료(Demurrage)를 방어할 수 있습니다.
            """)

    else:
        st.warning(f"현재 '{pod_input}' 목적지에 대한 특별 시황 데이터가 없습니다. Riyadh 또는 Dammam을 입력해 주세요.")

# --- 8. 저작권 표시 ---
st.markdown('<div class="footer">© Rino from Andromeda</div>', unsafe_allow_html=True)
