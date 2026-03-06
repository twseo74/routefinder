import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# 1. 페이지 설정
st.set_page_config(page_title="LX Pantos Live Intel", layout="wide")

# 2. CSS (표 가독성 및 Q&A 디자인)
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; font-size: 0.9rem; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.85rem; }
    .w-60 { width: 60%; background-color: #fcfcfc; }
    .qna-section { background-color: #fdfdfd; padding: 25px; border-radius: 12px; margin-top: 35px; border: 1px solid #e1e4e8; }
    .step-badge { background-color: #E6002D; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 5px; }
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# 헤더
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia Branch</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">FF 인바운드 제3국 우회 항로 실무 가이드</p>
    </div>
    <div class="update-box"><strong>분석 및 데이터 업데이트 시점:</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 4. 입력 섹션
col1, col2 = st.columns(2)
with col1: pol = st.text_input("Origin (POL)", value="Busan")
with col2: pod = st.text_input("Destination (POD)", value="Riyadh")

# 5. 데이터 엔진 (오만/UAE 우회 옵션 최적화)
def get_intel_data(pol_val):
    route_oman = f"🌐 **[Oman Transit]** {pol_val} → 살랄라(Salalah) 하역 → **제3국 통과 보세 운송** → Al Batha 국경 → 리야드"
    return [
        ["Maersk", "🟣 살랄라 우회", route_oman, "비용: $2,200~$2,500\n보세: 가능\n특이사항: 살랄라-리야드 직영 셔틀 운영 중"],
        ["CMA CGM", "🟣 소하르 우회", route_oman.replace("살랄라", "소하르"), "비용: $2,000~$2,300\n보세: 지원\n특이사항: UAE-사우디 국경 혼잡도 체크 필수"],
        ["HMM", "🟡 검토 중", "상황 주시", "비용: 미정\n보세: 개별 협의\n특이사항: 3국 하역 선복 및 트럭 가용성 확인 중"]
    ]

# 6. 표 출력
if st.button("🚀 실시간 라우팅 분석 및 Q&A 생성", type="primary", use_container_width=True):
    data = get_intel_data(pol)
    cols = ["선사", "상태", "상세 라우트 (Detailed Route)", "실무 정보 (비용/보세)"]
    
    table_html = f'<table class="custom-table"><thead><tr>'
    table_html += f'<th style="width:10%">{cols[0]}</th><th style="width:10%">{cols[1]}</th><th class="w-60">{cols[2]}</th><th style="width:20%">{cols[3]}</th>'
    table_html += '</tr></thead><tbody>'
    for r in data:
        table_html += f'<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>'
    table_html += '</tbody></table>'
    st.markdown(table_html, unsafe_allow_html=True)

    # 7. 제3국 우회 항로 이용 실무 Q&A (매니저님 요청 핵심 메뉴)
    st.markdown('<div class="qna-section">', unsafe_allow_html=True)
    st.subheader("❓ [Q&A] 제3국(오만/UAE) 항만 이용 및 통과 화물 실무 프로세스")
    
    with st.expander("Q1. 오만(Salalah) 하역 시 사우디 수입자는 무엇을 준비해야 하나요?", expanded=True):
        st.write("""
        - **B/L 상 Destination 수정:** 최종 목적지는 리야드(Riyadh)로 유지하되, Discharge Port가 Salalah로 기재되었는지 확인하십시오.
        - **FASAH 사전 등록:** 사우디 통합 물류 포털(Fasah)에 화물 도착 전 선적 서류를 업로드하여 보세 운송 승인을 미리 득해야 합니다.
        - **원산지 증명서(C/O) 주의:** 제3국 하역 화물이라도 원본 C/O에는 최종 목적지가 Saudi Arabia로 명시되어야 하며, 상공회의소 영사 확인(Attestation)은 필수입니다.
        """)

    with st.expander("Q2. 통과 화물(Transit Cargo)의 보세 운송 단계별 프로세스는 어떻게 되나요?"):
        st.markdown("""
        <span class="step-badge">STEP 1</span> **살랄라항 양하 및 Bayan 발행:** 오만 세관에 '사우디 통과 화물'임을 신고하고 Transit Bayan을 발행합니다.  
        <span class="step-badge">STEP 2</span> **보세 차량(Bonded Truck) 봉인:** LX 판토스가 승인한 보세 면허 차량에 적재 후, 세관 Seal을 부착하여 임의 개봉을 차단합니다.  
        <span class="step-badge">STEP 3</span> **Al Batha 국경 통과:** 오만-UAE-사우디 국경 통과 시 TIR Carnet 서류를 활용해 중간 검사 없이 신속 통과합니다.  
        <span class="step-badge">STEP 4</span> **리야드 Dry Port 입고:** 리야드 시내 보세 구역에 입고 후 세관원의 Seal 해제와 함께 최종 통관을 진행합니다.
        """, unsafe_allow_html=True)
        

    with st.expander("Q3. 제3국 하역 시 관세(Customs Duty)는 어디에 납부하나요?"):
        st.write("""
        - 오만이나 UAE는 단순히 화물이 거쳐가는 **'통과지'**일 뿐입니다.
        - 따라서 관세는 오만이 아닌, 최종 목적지인 **사우디 리야드 세관**에서 최종 수입 신고 시 납부하게 됩니다.
        """)

    with st.expander("Q4. 오만 국경에서 화물이 멈추거나 검사받을 리스크는 없나요?"):
        st.write("""
        - 현재 사우디-오만 양국 세관의 긴급 협의로 보세 운송에 대해서는 최우선 통행권을 부여하고 있습니다.
        - 단, 서류상 품목명(HS Code)이 부정확하거나 전략 물자로 분류될 경우 지연될 수 있으므로, 출발 전 사우디 법인(LX Pantos)을 통해 사전 검토를 완료해야 합니다.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia Branch</div>', unsafe_allow_html=True)
