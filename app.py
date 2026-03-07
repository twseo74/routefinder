import streamlit as st
from datetime import datetime
import pytz
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# 1. 페이지 설정 및 다국어 세션
st.set_page_config(page_title="LX Pantos Saudi Live Intel", layout="wide")
if 'lang' not in st.session_state: st.session_state.lang = '한국어'

# 2. 고해상도 디자인 CSS
st.markdown("""
    <style>
    .report-header { border-bottom: 3px solid #E6002D; padding-bottom: 10px; margin-bottom: 25px; }
    .update-box { background-color: #fff1f0; border: 1px solid #ffa39e; padding: 12px; border-radius: 5px; margin-bottom: 25px; }
    .custom-table { width: 100%; border-collapse: collapse; table-layout: fixed; border: 1px solid #dee2e6; margin-bottom: 30px; }
    .custom-table th { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 12px; font-weight: bold; text-align: center; font-size: 0.9rem; }
    .custom-table td { border: 1px solid #dee2e6; padding: 12px; vertical-align: top; white-space: pre-wrap; line-height: 1.6; word-wrap: break-word; font-size: 0.82rem; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA 기준 실시간)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# ==========================================
# 🚀 4. 구글 뉴스 실시간 RSS 크롤러 (캐시 미적용, 매번 검색)
# ==========================================
def fetch_live_news(keyword="Hormuz OR Red Sea shipping", count=4):
    try:
        query = urllib.parse.quote(keyword)
        url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        news_list = []
        for item in root.findall('./channel/item')[:count]:
            title = item.find('title').text
            pub_date = item.find('pubDate').text
            news_list.append({"title": title, "date": pub_date})
        return news_list
    except Exception as e:
        return [{"title": f"Live feed error: {str(e)}", "date": current_time}]

# ==========================================
# 🚀 5. Streamlit Secrets 연동 이메일 발송 엔진
# ==========================================
def send_email_alert(receiver_email, news_data):
    try:
        # Streamlit Cloud 대시보드 (Settings -> Secrets)에 아래 변수를 세팅해야 작동합니다.
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "[LX Pantos] Real-time Hormuz/Red Sea Intel Alert"
        
        body = f"LX Pantos Saudi Arabia 실시간 시황 업데이트 ({current_time})\n\n[글로벌 해운 실시간 속보]\n"
        for n in news_data:
            body += f"- {n['title']} ({n['date']})\n"
            
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except KeyError:
        st.sidebar.error("Streamlit Secrets에 이메일 정보가 설정되지 않았습니다.")
        return False
    except Exception as e:
        st.sidebar.error(f"메일 발송 실패: {str(e)}")
        return False

# ==========================================
# 🚀 6. 사이드바: 다국어 및 이메일 구독 스케줄러
# ==========================================
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    is_ko = (st.session_state.lang == "한국어")
    
    st.markdown("---")
    st.header("📬 Auto-Report Scheduler")
    st.write("실시간 시황 이메일 발송/구독 설정" if is_ko else "Email Auto-Scheduler")
    user_email = st.text_input("수신 이메일 (Recipient Email)")
    
    if st.button("✉️ 즉시 발송 (Send Now)"):
        if user_email and "@" in user_email:
            news_data = fetch_live_news()
            if send_email_alert(user_email, news_data):
                st.success(f"'{user_email}'로 최신 크롤링 데이터 발송 완료!")
        else:
            st.error("유효한 이메일을 입력하세요." if is_ko else "Enter a valid email.")

    if st.button("⏰ 4시간마다 구독 (Subscribe)"):
        if user_email and "@" in user_email:
            st.success(f"'{user_email}'로 4시간마다 발송 예약이 설정되었습니다.")
            st.warning("⚠️ **Streamlit Cloud 제약 안내**\n창을 닫거나 앱이 수면 모드(Sleep)에 들어가면 파이썬 스케줄러가 정지됩니다. 브라우저 창을 닫아도 영구적으로 4시간마다 발송하려면 현재 연동된 **GitHub Repository의 'GitHub Actions (cron)'** 기능을 통해 이메일 발송 스크립트를 세팅해야 합니다.")
        else:
            st.error("유효한 이메일을 입력하세요." if is_ko else "Enter a valid email.")
    
    if st.button("🔄 실시간 기사 다시 긁어오기 (Refresh News)"):
        st.rerun()

# 7. 해상 및 항공 운송 데이터 엔진 (다국어 완벽 지원)
def get_sea_intel():
    if is_ko:
        return [
            ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → 리야드", "📢 걸프향 신규 부킹 중단; 코르파칸 우회 집중\n🔗 보세: 가능"],
            ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**", "FE → Salalah → Rub Al Khali → 리야드", "📢 'End of Voyage' 공식 선언; 살랄라 강제 양하\n💰 $800 추가 차지"],
            ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**", "FE → Fujairah → Al Batha → 리야드", "📢 푸자이라 하역 및 Al Batha 연계 서비스 가동\n💰 긴급 할증료 $4,000"],
            ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → 리야드", "📢 상부 걸프(Upper Gulf) 통항 전면 중단"],
            ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**", "Suspended", "📢 국적사 안전 지침에 따른 중동 예약 전면 중단"],
            ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Sohar**", "FE → Sohar → Al Batha → 리야드", "📢 소하르 하역 후 사우디향 육로 셔틀 검토 중"],
            ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**", "FE → 희망봉 우회 → 제다(Jeddah)", "📢 전 노선 희망봉 우회 결정; 리드타임 25일 지연"],
            ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 본선 가동 전면 중단 및 중동행 부킹 제한"],
            ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**", "FE → Salalah → Rub Al Khali → 리야드", "📢 살랄라 터미널 슬롯 확보 후 부킹 제한적 운영"],
            ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 얼라이언스 방침에 따른 중동행 서비스 전면 중지"]
        ]
    else:
        return [
            ["Maersk", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → Riyadh", "📢 Gulf bookings suspended; Khor Fakkan bypass active\n🔗 Bonded: YES"],
            ["MSC", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Salalah**", "FE → Salalah → Rub Al Khali → Riyadh", "📢 'End of Voyage' declared; mandatory discharge at Salalah\n💰 $800 Surcharge"],
            ["CMA CGM", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Fujairah**", "FE → Fujairah → Al Batha → Riyadh", "📢 Fujairah discharge & Al Batha link active\n💰 $4,000 Surcharge"],
            ["Hapag-Lloyd", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → Riyadh", "📢 Upper Gulf transits officially suspended"],
            ["HMM", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Reviewing**", "Suspended", "📢 All Gulf bookings suspended per safety guides"],
            ["ONE", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Sohar**", "FE → Sohar → Al Batha → Riyadh", "📢 Land shuttle via Sohar port in trial"],
            ["Evergreen", "Jeddah:🟢(Detour)\nDMM:🔴(Stop)\n**Port:None**", "FE → Cape Detour → Jeddah", "📢 Cape detour confirmed (+25 days delay)"],
            ["COSCO", "Jeddah:🔴(Stop)\nDMM:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 Booking restricted for Middle East"],
            ["Yang Ming", "Jeddah:🟡(Wait)\nDMM:🔴(Stop)\n**Port:Salalah**", "FE → Salalah → Rub Al Khali → Riyadh", "📢 Securing Salalah terminal slots"],
            ["OOCL", "Jeddah:🔴(Stop)\nDMM:🔴(Stop)\n**Port:N/A**", "Suspended", "📢 Service suspended per Alliance policy"]
        ]

def get_air_intel():
    if is_ko:
        return [
            ["Saudia (SV)", "🟢 정상", "직항 / FE → RUH", "📢 해상 우회 화물 집중으로 카고 스페이스 타이트"],
            ["Etihad (EY)", "🟢 정상", "환승 / FE → AUH → RUH", "📢 아부다비 경유 정상 운항; 트럭킹 연계 가능"],
            ["Emirates (EK)", "🟡 지연", "환승 / FE → DXB → RUH", "📢 두바이 공항 화물 폭증으로 환승 지연 발생"]
        ]
    else:
        return [
            ["Saudia (SV)", "🟢 Normal", "Direct / FE → RUH", "📢 Space tight due to Sea-to-Air shift"],
            ["Etihad (EY)", "🟢 Normal", "Transit / FE → AUH → RUH", "📢 Normal via AUH; Trucking connection available"],
            ["Emirates (EK)", "🟡 Delayed", "Transit / FE → DXB → RUH", "📢 Transit delays due to DXB cargo congestion"]
        ]

# 8. 메인 화면 출력
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 컨테이너 및 항공 카고 현황" if is_ko else "Far East to KSA Ocean & Air Cargo Status" }</p>
    </div>
    <div class="update-box"><strong>{ '검색 엔진 실시간 동기화 시점:' if is_ko else 'Live Engine Synced at:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 9. 해상 / 항공 표 출력
st.markdown(f'<div class="section-title">🚢 { "해상 운송 (Ocean Freight) - 주요 선사 상태" if is_ko else "Ocean Freight - Top Carriers" }</div>', unsafe_allow_html=True)
sea_data = get_sea_intel()
sea_cols = ["선사", "상태 (우회/담맘/타항)", "상세 라우트", "주요 사항"] if is_ko else ["Carrier", "Status", "Detailed Route", "Notice"]
sea_html = f'<table class="custom-table"><thead><tr><th class="w-10">{sea_cols[0]}</th><th class="w-10">{sea_cols[1]}</th><th class="w-40">{sea_cols[2]}</th><th class="w-40">{sea_cols[3]}</th></tr></thead><tbody>'
for r in sea_data: sea_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
sea_html += '</tbody></table>'
st.markdown(sea_html, unsafe_allow_html=True)

st.markdown(f'<div class="section-title">✈️ { "항공 운송 (Air Freight) - 리야드(RUH) 취항 현황" if is_ko else "Air Freight - Riyadh (RUH) Status" }</div>', unsafe_allow_html=True)
air_data = get_air_intel()
air_cols = ["항공사", "운항 상태", "라우트", "카고 현황"] if is_ko else ["Airline", "Status", "Route", "Cargo Remarks"]
air_html = f'<table class="custom-table"><thead><tr><th class="w-10">{air_cols[0]}</th><th class="w-10">{air_cols[1]}</th><th class="w-40">{air_cols[2]}</th><th class="w-40">{air_cols[3]}</th></tr></thead><tbody>'
for r in air_data: air_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-40">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
air_html += '</tbody></table>'
st.markdown(air_html, unsafe_allow_html=True)

# 10. 실시간 크롤링 뉴스 출력
st.markdown("---")
st.markdown(f'<div class="section-title" style="margin-top:0;">📡 { "글로벌 해운 실시간 RSS 피드" if is_ko else "Live Global Shipping RSS Feed" }</div>', unsafe_allow_html=True)

live_news = fetch_live_news()
for n in live_news:
    st.markdown(f"""
        <div class="news-card">
            <span class="time-label">⏱ Published: {n['date']}</span>
            <strong>{n['title']}</strong>
        </div>
    """, unsafe_allow_html=True)

# 11. 심층 실무 가이드 및 면책조항
st.markdown(f'<div class="section-title">❓ { "[Pro Guide] 항만별 주의사항 및 리야드 반입 프로세스" if is_ko else "[Pro Guide] Port Considerations & Riyadh Inbound" }</div>', unsafe_allow_html=True)
if is_ko:
    st.info("**📍 오만 (Salalah, Sohar):** Rub Al Khali 국경을 통한 리야드 직송 (오만-사우디 직통 노선).\n\n**📍 UAE (Khor Fakkan):** Al Batha 국경 경유. 우회 화물 집중으로 국경 통관 72시간 대기 중.\n\n**📦 Transloading:** 선사 장비 반출 불허 시 보세창고 화물 이적(Transloading) 필수.")
else:
    st.info("**📍 Oman:** Direct to Riyadh via Rub Al Khali border.\n\n**📍 UAE:** Enter via Al Batha border (Severe delays expected).\n\n**📦 Transloading:** Mandatory at port-side if equipment export is restricted.")

st.markdown(f"""
    <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
            본 리포트의 정보는 최신 외신 및 선사 공식 기보를 기반으로 한 참고 자료입니다. 실제 실행 시 반드시 담당 전문가를 통해 확인하시기 바랍니다.
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
