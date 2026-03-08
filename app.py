import streamlit as st
import google.generativeai as genai
import feedparser
import time
from datetime import datetime
import pytz

# ==========================================
# 1. UI 및 환경 설정
# ==========================================
st.set_page_config(page_title="Hormuz Crisis Monitor v171", layout="wide")

with st.sidebar:
    st.header("🌐 Language")
    lang = st.radio("언어 선택 (Language)", ["한국어", "English"])
    st.divider()
    st.success("🔄 전황 뉴스 실시간 스크래핑 가동 중")
    st.info("항만/선사 데이터는 실무 팩트 기반으로 고정되며, 전황 뉴스는 실시간으로 업데이트됩니다.")

is_ko = (lang == "한국어")
target_language = "한국어" if is_ko else "English"
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time_str = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M (KSA)")

API_KEY = st.secrets.get("GEMINI_API_KEY")

st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-size: 1.0rem; }
    th { background-color: #f2f2f2; font-weight: bold; border: 1px solid #ddd; padding: 12px; }
    td { border: 1px solid #ddd; padding: 10px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🚀 2. 실시간 전황 뉴스 스크래퍼 (항만 데이터 제외, 뉴스만 타겟)
# ==========================================
@st.cache_data(ttl=1800)
def fetch_live_news():
    news_feeds = {
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "BBC": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml"
    }
    
    scraped_data = []
    for media, url in news_feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:2]: # 각 매체별 최신 2개 기사만 추출
                scraped_data.append(f"[{media}] {entry.title}\nURL: {entry.link}")
        except:
            continue
            
    return "\n\n".join(scraped_data)

# ==========================================
# 🚀 3. 하이브리드 리포트 생성 엔진 (고정 팩트 + 실시간 뉴스)
# ==========================================
def generate_hybrid_report(api_key, target_lang, live_news):
    try:
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model = next((m for m in available_models if "flash" in m or "pro" in m), available_models[0])
        model = genai.GenerativeModel(target_model)
        
        # [핵심] 1, 2번 섹션은 현장 팩트로 완전 고정 (LLM 망상 원천 차단)
        prompt = f"""
        너는 물류 관제 AI다. 아래 제공된 [물류 팩트]와 [실시간 전황 뉴스]를 결합하여 '{target_lang}'로 보고서를 작성해라.

        [물류 팩트 - 절대 수정/누락 금지]
        1. 선사 FM 현황 (운임 제외 표 작성)
        - MSC, Maersk, Hapag-Lloyd, ONE, Evergreen: Salalah (FM 선언: 3월 초)
        - COSCO: Khalifa (FM 선언: 3월 초)
        - HMM, Yang Ming: Sohar (FM 선언: 3월 초)
        - CMA CGM, ZIM: Jebel Ali (FM 선언: 3월 초)
        
        2. 항만별 현황 팩트
        - Salalah (Asyad): 피더선(Feeder) 운항 전면 중단 및 모선 집중. 야드 공간 포화로 화물 추출(Digging) 지연 평균 6일.
        - Sohar (Asyad): 사우디행 육상 환적(Land-bridge) 허브 지정. Al Batha 국경 트럭 정체 및 대기시간 급증.
        - Jebel Ali (DP World): 호르무즈 해협 안쪽 피더선 운항 전면 보류. 터미널 게이트 반출입 엄격 통제.

        [실시간 전황 뉴스 - 번역하여 3번 섹션에 배치]
        {live_news}

        지시사항:
        - 1번과 2번 섹션은 위 [물류 팩트] 내용을 100% 그대로 번역해서 마크다운 표/불릿으로만 정리해라. 딴소리 추가 금지.
        - 3번 섹션은 [실시간 전황 뉴스]의 기사 제목을 번역하고 URL을 그대로 출력해라.
        - '종합 분석', '결론', '정보가 없습니다' 등의 쓸데없는 말은 한 글자도 쓰지 마라.
        """

        with st.spinner("하이브리드 리포트 생성 중..."):
            response = model.generate_content(prompt)
            st.markdown(response.text, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ 엔진 오류: {e}")

# ==========================================
# 🚀 4. 메인 실행부
# ==========================================
st.markdown(f'<div class="report-header"><h1 style="margin:0;">Hormuz Crisis Control Report (v171.0)</h1></div>', unsafe_allow_html=True)

if st.button("🚀 관제 리포트 생성", type="primary", use_container_width=True):
    if not API_KEY: 
        st.error("API Key가 필요합니다.")
    else:
        # 뉴스만 스크래핑
        live_news_data = fetch_live_news()
        
        # 고정 팩트와 결합하여 리포트 생성
        generate_hybrid_report(API_KEY, target_language, live_news_data)

st.markdown(f'<div class="footer">© 2026 Integrated Logistics Monitor. {current_time_str}</div>', unsafe_allow_html=True)
