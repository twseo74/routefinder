import streamlit as st
from datetime import datetime
import pytz
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from deep_translator import GoogleTranslator

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
    .w-10 { width: 10%; text-align: center; }
    .w-15 { width: 15%; text-align: center; }
    .w-35 { width: 35%; background-color: #fcfcfc; }
    .w-40 { width: 40%; background-color: #fcfcfc; }
    .news-card { border-left: 5px solid #E6002D; background-color: #f9f9f9; padding: 12px; margin-bottom: 10px; border-radius: 4px; }
    .time-label { color: #E6002D; font-weight: bold; font-size: 0.75rem; margin-bottom: 5px; display: block; }
    .section-title { color: #003366; border-left: 5px solid #003366; padding-left: 10px; margin-top: 30px; margin-bottom: 15px; font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. 시간 설정 (KSA)
ksa_tz = pytz.timezone('Asia/Riyadh')
current_time = datetime.now(ksa_tz).strftime("%Y-%m-%d %H:%M:%S (KSA)")

# ==========================================
# 🚀 4. 아랍어 원문 크롤링 및 실시간 자동 번역 엔진
# ==========================================
@st.cache_data(ttl=300) # 과도한 번역 API 호출 방지를 위해 5분 캐시 적용
def fetch_and_translate_arabic_news(topic_type, is_ko, count=4):
    try:
        # 아랍어 검색 쿼리 세팅 (전황/호르무즈 vs 로컬 항만)
        if topic_type == "war":
            keyword_ar = "مضيق هرمز OR البحر الأحمر شحن" # 호르무즈 해협 OR 홍해 해운
        else:
            keyword_ar = "موانئ السعودية OR ميناء صلالة OR ميناء الفجيرة OR ميناء جبل علي" # 사우디 항만 OR 살랄라 항 OR 푸자이라 항 OR 제벨알리 항
            
        # 아랍 에미리트(AE) 구글 뉴스 RSS 접속 (아랍어 원문 추출)
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(keyword_ar)}&hl=ar&gl=AE&ceid=AE:ar"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)
        root = ET.fromstring(response.read())
        
        target_lang = 'ko' if is_ko else 'en'
        translator = GoogleTranslator(source='ar', target=target_lang)
        
        news_list = []
        for item in root.findall('./channel/item')[:count]:
            original_title = item.find('title').text
            pub_date = item.find('pubDate').text
            
            # 아랍어 -> 한국어/영어 실시간 번역 수행
            translated_title = translator.translate(original_title)
            news_list.append({"title": translated_title, "date": pub_date, "original": original_title})
            
        return news_list
    except Exception as e:
        return [{"title": f"Local Arabic feed error: {str(e)}", "date": current_time, "original": ""}]

# ==========================================
# 🚀 5. 데이터 엔진 (해상/항공)
# ==========================================
def get_sea_intel(is_ko):
    if is_ko:
        return [
            ["Maersk", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → 리야드", "📢 걸프향 신규 부킹 전면 중지; 코르파칸 우회 집중\n💰 $1,900~$2,300\n🔗 보세: 가능"],
            ["MSC", "제다:🟡(협의)\n담맘:🔴(중단)\n**타항:Salalah**", "FE → Salalah → Rub Al Khali → 리야드", "📢 'End of Voyage' 선언; 살랄라 강제 양하\n💰 $800 추가 운임 부과"],
            ["CMA CGM", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Fujairah**", "FE → Fujairah → Al Batha → 리야드", "📢 푸자이라 하역 및 Al Batha 연계 서비스 가동\n💰 긴급 할증료 $4,000 적용"],
            ["Hapag-Lloyd", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → 리야드", "📢 상부 걸프(Upper Gulf) 통항 전면 중단 공식화\n💰 전쟁 위험 할증료(WRS) 부과"],
            ["HMM", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:검토중**", "Suspended", "📢 국적사 안전 지침에 따른 걸프향 예약 전면 중단"],
            ["ONE", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Sohar**", "FE → Sohar → Al Batha → 리야드", "📢 소하르 하역 후 사우디향 육로 셔틀 검토 중"],
            ["Evergreen", "제다:🟢(우회)\n담맘:🔴(중단)\n**타항:없음**", "FE → 희망봉 우회 → 제다(Jeddah)", "📢 전 노선 희망봉 우회 결정; 리드타임 최소 25일 지연"],
            ["COSCO", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 본선 가동 전면 중단 및 중동행 부킹 예약 제한"],
            ["Yang Ming", "제다:🟡(대기)\n담맘:🔴(중단)\n**타항:Salalah**", "FE → Salalah → Rub Al Khali → 리야드", "📢 살랄라 터미널 슬롯 확보 후 부킹 제한적 재개 예정"],
            ["OOCL", "제다:🔴(중단)\n담맘:🔴(중단)\n**타항:불가**", "Suspended", "📢 얼라이언스 방침에 따른 중동행 서비스 전면 중지"]
        ]
    else:
        return [
            ["Maersk", "JED:🟢(Detour)\nDMM:🔴(Stop)\n**via:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → Riyadh", "📢 Gulf bookings suspended; Khor Fakkan bypass active\n💰 $1,900~$2,300\n🔗 Bonded: YES"],
            ["MSC", "JED:🟡(Wait)\nDMM:🔴(Stop)\n**via:Salalah**", "FE → Salalah → Rub Al Khali → Riyadh", "📢 'End of Voyage' declared; mandatory discharge at Salalah\n💰 $800 Surcharge"],
            ["CMA CGM", "JED:🟢(Detour)\nDMM:🔴(Stop)\n**via:Fujairah**", "FE → Fujairah → Al Batha → Riyadh", "📢 Fujairah discharge & Al Batha link active\n💰 $4,000 Emergency Surcharge"],
            ["Hapag-Lloyd", "JED:🟢(Detour)\nDMM:🔴(Stop)\n**via:Khor Fakkan**", "FE → Khor Fakkan → Al Batha → Riyadh", "📢 Upper Gulf transits officially suspended\n💰 War Risk Surcharge applied"],
            ["HMM", "JED:🟡(Wait)\nDMM:🔴(Stop)\n**via:Reviewing**", "Suspended", "📢 All Gulf bookings suspended per safety guidelines"],
            ["ONE", "JED:🟡(Wait)\nDMM:🔴(Stop)\n**via:Sohar**", "FE → Sohar → Al Batha → Riyadh", "📢 Land shuttle via Sohar port in trial"],
            ["Evergreen", "JED:🟢(Detour)\nDMM:🔴(Stop)\n**via:None**", "FE → Cape Detour → Jeddah", "📢 Cape detour confirmed (+25 days delay)"],
            ["COSCO", "JED:🔴(Stop)\nDMM:🔴(Stop)\n**via:N/A**", "Suspended", "📢 Booking restricted for Middle East"],
            ["Yang Ming", "JED:🟡(Wait)\nDMM:🔴(Stop)\n**via:Salalah**", "FE → Salalah → Rub Al Khali → Riyadh", "📢 Securing Salalah terminal slots"],
            ["OOCL", "JED:🔴(Stop)\nDMM:🔴(Stop)\n**via:N/A**", "Suspended", "📢 Service suspended per Alliance policy"]
        ]

def get_air_intel(is_ko):
    if is_ko:
        return [
            ["Saudia (SV)", "🟢 정상", "FE → RUH (직항)", "📢 해상 우회 수요 급증으로 카고 스페이스 극도 타이트"],
            ["Etihad (EY)", "🟢 정상", "FE → AUH → RUH", "📢 아부다비 경유 정상 운항; 파트너 트럭킹 연계 원활"],
            ["Qatar Airways (QR)", "🟢 정상", "FE → DOH → RUH", "📢 도하 허브 가동률 100%; 운임 변동성 높음"],
            ["Emirates (EK)", "🟡 지연", "FE → DXB → RUH", "📢 두바이 공항 화물 폭증으로 환승 지연(24h~48h)"],
            ["Cathay Pacific (CX)", "🔴 예약 불가", "HKG → RUH", "📢 사우디향 스페이스 할당 전면 클로즈 (현재 예약 불가)"],
            ["Korean Air (KE Cargo)", "🔴 운항 중단", "ICN → RUH (화물)", "📢 중동 영공 안전성 재검토로 **3월 15일까지 화물기 중단**"],
            ["China Southern (CZ)", "🔴 운항 중단", "CAN/PKX → RUH", "📢 이란/걸프 영공 통과 제한으로 **3월 31일까지 결항**"]
        ]
    else:
        return [
            ["Saudia (SV)", "🟢 Normal", "FE → RUH (Direct)", "📢 Cargo space extremely tight due to Sea-to-Air shift"],
            ["Etihad (EY)", "🟢 Normal", "FE → AUH → RUH", "📢 Normal via AUH; Smooth trucking connection available"],
            ["Qatar Airways (QR)", "🟢 Normal", "FE → DOH → RUH", "📢 Doha hub at 100% capacity; high freight rate volatility"],
            ["Emirates (EK)", "🟡 Delayed", "FE → DXB → RUH", "📢 Transit delays (24h-48h) due to DXB cargo congestion"],
            ["Cathay Pacific (CX)", "🔴 Unavailable", "HKG → RUH", "📢 Space allocation to KSA fully closed (No booking)"],
            ["Korean Air (KE Cargo)", "🔴 Suspended", "ICN → RUH (Cargo)", "📢 Freighter operations suspended until **March 15**"],
            ["China Southern (CZ)", "🔴 Suspended", "CAN/PKX → RUH", "📢 Flights canceled until **March 31** due to airspace restrictions"]
        ]

# ==========================================
# 🚀 6. 이메일 전체 리포트(HTML) 발송 엔진 (아랍 번역 뉴스 포함)
# ==========================================
def send_full_report_email(receiver_email, is_ko, sea_data, air_data, war_news, port_news):
    try:
        sender_email = st.secrets["email"]["sender_email"]
        sender_password = st.secrets["email"]["sender_password"]
        
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "[LX Pantos] Real-time Saudi Logistics Intel Report" if not is_ko else "[LX Pantos] 사우디향 물류 실시간 인텔리전스 리포트"
        
        title = "사우디향 컨테이너 및 항공 카고 현황" if is_ko else "KSA Ocean & Air Cargo Status"
        html_body = f"""
        <html>
        <head>
            <style>
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; font-family: Arial, sans-serif; font-size: 12px; }}
                th {{ background-color: #f2f2f2; border: 1px solid #dddddd; padding: 8px; text-align: left; }}
                td {{ border: 1px solid #dddddd; padding: 8px; white-space: pre-wrap; }}
                h2, h3 {{ color: #003366; font-family: Arial, sans-serif; }}
                .alert {{ color: #E6002D; font-weight: bold; }}
            </style>
        </head>
        <body>
            <h2>LX PANTOS | Saudi Arabia</h2>
            <p class="alert">{title}</p>
            <p><strong>Update Time (KSA):</strong> {current_time}</p>
            
            <h3>🚢 Ocean Freight - Top Carriers</h3>
            <table>
                <tr><th>Carrier</th><th>Status</th><th>Route</th><th>Notice</th></tr>
        """
        for r in sea_data: html_body += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
        html_body += "</table>"

        html_body += f"<h3>✈️ Air Freight - Riyadh (RUH) Status</h3><table><tr><th>Airline</th><th>Status</th><th>Route</th><th>Remarks</th></tr>"
        for r in air_data: html_body += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td></tr>"
        html_body += "</table>"

        html_body += f"<h3>🔥 Live Arabic News (Translated) - Hormuz/War</h3><ul>"
        for n in war_news: html_body += f"<li><strong>{n['title']}</strong> <br><small>({n['date']})</small></li>"
        html_body += "</ul>"
        
        html_body += f"<h3>🌐 Live Arabic News (Translated) - Local Ports</h3><ul>"
        for n in port_news: html_body += f"<li><strong>{n['title']}</strong> <br><small>({n['date']})</small></li>"
        html_body += "</ul>"
        
        guide_text = ("📍 오만(Salalah): Rub Al Khali 직송<br>📍 UAE(Khor Fakkan): Al Batha 경유(통관 대기 심각)<br>📦 Transloading: 선사 반출 불허 시 필수" 
                      if is_ko else 
                      "📍 Oman: Direct via Rub Al Khali<br>📍 UAE: Via Al Batha (Severe delays)<br>📦 Transloading: Mandatory if equipment export restricted")
        
        html_body += f"<h3>❓ Pro Guide</h3><p>{guide_text}</p>"
        html_body += f"<hr><p><small>{'본 리포트는 아랍 현지 매체 및 선사 기보를 바탕으로 한 참고 자료입니다.' if is_ko else 'This report is for reference based on local Arab media and latest advisories.'}</small></p>"
        html_body += "</body></html>"

        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.sidebar.error(f"Mail Error: {str(e)}")
        return False

# ==========================================
# 🚀 7. 사이드바 (UI 구성)
# ==========================================
with st.sidebar:
    st.header("🌐 System Settings")
    st.session_state.lang = st.radio("Language / 언어 선택", ["한국어", "English"])
    is_ko = (st.session_state.lang == "한국어")
    
    st.markdown("---")
    st.header("📬 Full Report Sender")
    user_email = st.text_input("수신 이메일 (Recipient Email)")
    if st.button("✉️ 전체 리포트 이메일 발송"):
        if user_email and "@" in user_email:
            with st.spinner('아랍 매체 번역 및 리포트 생성 중...'):
                war_news = fetch_and_translate_arabic_news("war", is_ko)
                port_news = fetch_and_translate_arabic_news("port", is_ko)
                sea_data = get_sea_intel(is_ko)
                air_data = get_air_intel(is_ko)
                if send_full_report_email(user_email, is_ko, sea_data, air_data, war_news, port_news):
                    st.success("✅ 풀 리포트 발송 완료!")
        else: st.error("이메일을 확인하세요.")
    if st.button("🔄 아랍 매체 실시간 번역 갱신"): st.cache_data.clear(); st.rerun()

# ==========================================
# 🚀 8. 메인 화면 렌더링
# ==========================================
st.markdown(f"""
    <div class="report-header">
        <h1 style="margin:0;">LX PANTOS <span style="font-size:1.1rem; color:#666;">| Saudi Arabia</span></h1>
        <p style="margin:5px 0 0 0; color:#E6002D; font-weight:bold;">{ "극동발 사우디향 해상/항공 카고 현황" if is_ko else "Far East to KSA Ocean & Air Cargo Status" }</p>
        <p style="margin:5px 0 0 0; color:#666; font-size:0.85rem;">{ "본 리포트의 정보는 아랍 현지 매체 번역본 및 공식 기보를 기반으로 한 참고 자료입니다." if is_ko else "This report is based on translated Arab local media and official carrier advisories." }</p>
    </div>
    <div class="update-box"><strong>{ '아랍 매체 실시간 번역 동기화 시점:' if is_ko else 'Local Arab Media Synced at:' }</strong> {current_time}</div>
""", unsafe_allow_html=True)

# 해상 표 출력
st.markdown(f'<div class="section-title">🚢 { "해상 운송 (Ocean Freight) - 주요 선사 상태" if is_ko else "Ocean Freight - Top Carriers" }</div>', unsafe_allow_html=True)
sea_data = get_sea_intel(is_ko)
sea_cols = ["선사", "상태 (우회/담맘/타항)", "상세 라우트", "주요 사항"] if is_ko else ["Carrier", "Status (Detour/DMM/via)", "Detailed Route", "Notice"]
sea_html = f'<table class="custom-table"><thead><tr><th class="w-10">{sea_cols[0]}</th><th class="w-15">{sea_cols[1]}</th><th class="w-35">{sea_cols[2]}</th><th class="w-40">{sea_cols[3]}</th></tr></thead><tbody>'
for r in sea_data: sea_html += f'<tr><td class="w-10">{r[0]}</td><td class="w-15">{r[1]}</td><td class="w-35">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
sea_html += '</tbody></table>'
st.markdown(sea_html, unsafe_allow_html=True)

# 항공 표 출력
st.markdown(f'<div class="section-title">✈️ { "항공 운송 (Air Freight) - 리야드(RUH) 취항 현황" if is_ko else "Air Freight - Riyadh (RUH) Status" }</div>', unsafe_allow_html=True)
air_data = get_air_intel(is_ko)
air_cols = ["항공사", "운항 상태", "라우트", "카고 현황 및 재개 일정"] if is_ko else ["Airline", "Status", "Route", "Cargo Remarks & Resumption"]
air_html = f'<table class="custom-table"><thead><tr><th class="w-15">{air_cols[0]}</th><th class="w-10">{air_cols[1]}</th><th class="w-35">{air_cols[2]}</th><th class="w-40">{air_cols[3]}</th></tr></thead><tbody>'
for r in air_data: air_html += f'<tr><td class="w-15">{r[0]}</td><td class="w-10">{r[1]}</td><td class="w-35">{r[2]}</td><td class="w-40">{r[3]}</td></tr>'
air_html += '</tbody></table>'
st.markdown(air_html, unsafe_allow_html=True)

# 아랍 현지 매체 실시간 번역 출력 (전황 vs 로컬 항만 분리)
st.markdown("---")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f'<div class="section-title" style="margin-top:0;">🔥 { "아랍 로컬 매체 번역: 호르무즈/전황" if is_ko else "Translated Arab Media: Hormuz/War" }</div>', unsafe_allow_html=True)
    war_news = fetch_and_translate_arabic_news("war", is_ko)
    for n in war_news:
        st.markdown(f"""
            <div class="news-card">
                <span class="time-label">⏱ Published: {n['date']}</span>
                <strong>{n['title']}</strong><br>
                <small style="color:#999;">(Original: {n['original']})</small>
            </div>
        """, unsafe_allow_html=True)

with c2:
    st.markdown(f'<div class="section-title" style="margin-top:0;">🌐 { "아랍 로컬 매체 번역: UAE/오만/사우디 항만" if is_ko else "Translated Arab Media: Local Ports" }</div>', unsafe_allow_html=True)
    port_news = fetch_and_translate_arabic_news("port", is_ko)
    for n in port_news:
        st.markdown(f"""
            <div class="news-card" style="border-left-color:#1890ff; background-color:#e6f7ff;">
                <span class="time-label">⏱ Published: {n['date']}</span>
                <strong>{n['title']}</strong><br>
                <small style="color:#999;">(Original: {n['original']})</small>
            </div>
        """, unsafe_allow_html=True)

# 가이드 및 면책
st.markdown(f'<div class="section-title">❓ { "[Pro Guide] 항만별 주의사항 및 리야드 반입 프로세스" if is_ko else "[Pro Guide] Port Considerations & Riyadh Inbound" }</div>', unsafe_allow_html=True)
if is_ko:
    st.info("**📍 오만 (Salalah, Sohar):** Rub Al Khali 국경을 통한 리야드 직송 (오만-사우디 직통 노선).\n\n**📍 UAE (Khor Fakkan):** Al Batha 국경 경유. 우회 화물 집중으로 국경 통관 72시간 대기 중.\n\n**📦 Transloading:** 선사 장비 반출 불허 시 보세창고 화물 이적(Transloading) 필수.")
else:
    st.info("**📍 Oman (Salalah, Sohar):** Direct to Riyadh via Rub Al Khali border (KSA-Oman direct route).\n\n**📍 UAE (Khor Fakkan):** Enter via Al Batha border. Expect severe 72h delays due to diverted cargo.\n\n**📦 Transloading:** Mandatory at port-side if carriers restrict equipment export.")

st.markdown(f"""
    <div style="background-color: #f8f9fa; border: 1px solid #ced4da; padding: 20px; border-radius: 8px; margin-top: 25px;">
        <p style="color: #495057; font-size: 0.85rem; line-height: 1.6; margin: 0;">
            <strong>⚠️ [{ '실무 참고 및 면책 고지' if is_ko else 'Professional Disclaimer' }]</strong><br>
            { "본 리포트의 정보는 아랍 현지 매체 번역본 및 선사/항공사 공식 기보를 기반으로 한 참고 자료입니다. 실제 물류 실행 시에는 반드시 LX Pantos 담당 전문가를 통해 최종 검증을 받으시기 바랍니다." if is_ko else "This report is based on translated Arab local media and official carrier advisories. Please consult with LX Pantos specialists for final verification before execution." }
        </p>
    </div>
""", unsafe_allow_html=True)
st.markdown('<br><div style="text-align: center; color: #999;">© Rino from Andromeda | LX Pantos Saudi Arabia</div>', unsafe_allow_html=True)
