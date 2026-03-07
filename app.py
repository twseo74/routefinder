import streamlit as st
from datetime import datetime
import pytz
import google.generativeai as genai

# 1. 페이지 설정 및 다국어 세션
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'
is_ko = (st.session_state.lang == "한국어")

# 2. 고해상도 디자인 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# ==========================================
# 🚀 4. AI (Gemini) API 연동 엔진
# ==========================================
def analyze_live_market(api_key, is_ko):
    # Gemini API 설정
    genai.configure(api_key=api_key)
    # 최신 모델 호출
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # AI에게 내릴 프롬프트 (매니저님이 저에게 하신 명령을 코드가 대신 내립니다)
    language = "Korean" if is_ko else "English"
    prompt = f"""
    You are an expert logistics analyst for LX Pantos Saudi Arabia.
    Search the latest news and provide the real-time shipping and air freight status to Saudi Arabia.
    Respond strictly in {language}. 
    
    Please provide the output in two Markdown tables:
    
    1. 해상 운송 (Ocean Freight) - Maersk, MSC, CMA CGM, Hapag-Lloyd, HMM, ONE, Evergreen, COSCO, Yang Ming, OOCL.
       Columns: 선사 (Carrier) | 상태 (Status - e.g., JED Detour, DMM Stop, via Port) | 실시간 주요 사항 (Real-time Notice based on latest news)
       
    2. 항공 운송 (Air Freight) - Saudia, Etihad, Emirates, Qatar, Cathay Pacific, Korean Air, China Southern.
       Columns: 항공사 (Airline) | 기종 (Type - PAX or Freighter) | 상태 (Status - Normal, Delayed, Suspended) | 카고 현황 및 미취항 기한 (Cargo Remarks & Resumption date based on latest news)
       
    Do not include any filler text, just output the two Markdown tables.
    """
    
    try:
        # AI가 실시간으로 판단하여 표를 생성
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI 분석 오류 발생 (API 키 또는 네트워크 확인 필요): {str(e)}"

# ==========================================
# 🚀 5. 사이드바 (API 키 입력 및 설정)
# ==========================================
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    
    st.markdown("---")
    st.header("🧠 AI Engine Setup")
    st.write("실시간 데이터 분석을 위해 Gemini API Key가 필요합니다." if is_ko else "Gemini API Key is required for real-time analysis.")
    # 사용자가 직접 API 키를 입력하거나, st.secrets에서 불러옵니다.
    user_api_key = st.text_input("Gemini API Key 입력", type="password")
    st.caption("Get your free API key at [Google AI Studio](https://aistudio.google.com/)")

# ==========================================
# 🚀 6. 메인 화면 렌더링
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 해상/항공 카고 현황 (AI 실시간 분석)" if is_ko else "Far East to KSA Ocean & Air Cargo Status (AI Live Analysis)" }</p>
        <p style="margin:5px 0 0 0; color:#666; font-size:0.85rem;">{ "본 리포트는 앱에 내장된 AI가 조회 시점의 최신 외신 및 시황을 실시간으로 분석하여 생성합니다." if is_ko else "This report is generated in real-time by an embedded AI analyzing the latest foreign news and market conditions." }</p>
    </div>
    <div class="update-box"><strong>{ 'AI 엔진 실시간 분석 시점:' if is_ko else 'AI Engine Analysis Time:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 실행 버튼
btn_text = "🚀 AI 실시간 시황 분석 실행" if is_ko else "🚀 Run AI Real-time Analysis"
if st.button(btn_text, type="primary", use_container_width=True):
    if not user_api_key:
        st.error("좌측 메뉴에 Gemini API Key를 입력해 주세요." if is_ko else "Please enter your Gemini API Key in the sidebar.")
    else:
        with st.spinner("AI가 전 세계 외신과 물류 데이터를 실시간으로 수집하고 분석 중입니다... (약 10~15초 소요)" if is_ko else "AI is gathering and analyzing real-time global logistics data..."):
            # AI 분석 결과 가져오기
            ai_result = analyze_live_market(user_api_key, is_ko)
            
            # AI가 만들어준 표를 화면에 그대로 렌더링
            st.markdown(ai_result, unsafe_allow_html=True)
            st.success("✅ AI 실시간 데이터 갱신 완료!" if is_ko else "✅ AI Real-time data update complete!")

# 하단 면책 조항
st.markdown("---")
st.markdown(f"""
    <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
            { "본 리포트의 정보는 인공지능이 최신 기보를 기반으로 생성한 자료입니다. 실제 물류 실행 시에는 반드시 LX Pantos 담당 전문가를 통해 최종 검증을 받으시기 바랍니다." if is_ko else "This report is generated by AI based on the latest advisories. Please consult with LX Pantos specialists for final verification before execution." }
        </p>
    </div>
""", unsafe_allow_html=True)
