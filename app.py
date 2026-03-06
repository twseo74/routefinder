import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# --- 1. Selenium 스크래핑 핵심 로직 ---
def scrape_schedule(pol, pod, carrier):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 봇 탐지 우회용 User-Agent
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    driver = webdriver.Chrome(options=options)
    
    # 실패 시 기본 출력값 설정
    result = {
        '선사': carrier,
        '운송 루트 (POL-TS-POD)': '확인불가',
        '소요시간(일)': '확인불가',
        '상태': '조회실패 / 우회항로 없음'
    }

    try:
        # TODO: 실무 적용 시 각 선사별 실제 스케줄 조회 URL 패턴으로 변경해야 합니다.
        url = f"https://www.example-{carrier.lower()}.com/schedule?origin={pol}&dest={pod}"
        driver.get(url)

        # 최대 10초 대기 (선사 사이트 로딩 고려)
        wait = WebDriverWait(driver, 10)
        
        # TODO: 실제 선사 웹페이지의 F12(개발자도구)를 눌러 결과값이 뜨는 클래스명으로 변경해야 합니다.
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "schedule-row")))

        # 데이터 추출 (예시 클래스명)
        route_text = driver.find_element(By.CLASS_NAME, "routing-path").text
        tt_text = driver.find_element(By.CLASS_NAME, "transit-time").text
        
        # 성공 시 데이터 업데이트
        result['운송 루트 (POL-TS-POD)'] = route_text
        result['소요시간(일)'] = tt_text.replace(' days', '')
        result['상태'] = '조회성공'

    except TimeoutException:
        pass # 로딩 지연 또는 검색 결과 없음 -> '확인불가' 유지
    except NoSuchElementException:
        pass # 요소 찾기 실패 -> '확인불가' 유지
    finally:
        driver.quit() # 메모리 확보를 위해 반드시 브라우저 종료

    return result

# --- 2. Streamlit UI 화면 구성 ---
st.set_page_config(page_title="선사 스케줄/루트 조회기", layout="wide")

st.title("🚢 실시간 선사 스케줄 및 루트 조회")
st.markdown("출발지와 목적지를 입력하면 각 선사 웹사이트를 스크래핑하여 가용한 라우팅을 리스트업합니다.")

# 입력 폼 구성
col1, col2 = st.columns(2)
with col1:
    pol_input = st.text_input("출발지 (POL)", value="Busan")
with col2:
    pod_input = st.text_input("도착지 (Destination / POD)", value="Riyadh")

# 조회할 선사 리스트 (필요시 추가/수정)
target_carriers = ['HMM', 'Maersk', 'MSC', 'CMA CGM']

# 검색 버튼 클릭 시 동작
if st.button("🚀 스케줄 조회 시작", type="primary"):
    
    # 프로그래스바 및 상태 메시지 띄우기
    progress_text = "선사 사이트 스크래핑 중입니다. 잠시만 기다려주세요..."
    my_bar = st.progress(0, text=progress_text)
    
    results = []
    
    # 각 선사별로 스크래핑 실행
    for idx, carrier in enumerate(target_carriers):
        # 현재 어떤 선사를 조회 중인지 UI에 표시
        st.toast(f"{carrier} 스케줄 조회 중...")
        
        # 스크래핑 함수 호출
        data = scrape_schedule(pol_input, pod_input, carrier)
        results.append(data)
        
        # 프로그래스바 업데이트
        progress_percentage = int(((idx + 1) / len(target_carriers)) * 100)
        my_bar.progress(progress_percentage, text=f"{carrier} 조회 완료 ({progress_percentage}%)")
        
        time.sleep(1) # 서버 과부하 방지를 위한 짧은 딜레이

    # 최종 결과 화면 출력
    my_bar.empty() # 프로그래스바 숨김
    st.success("✅ 조회가 완료되었습니다.")
    
    # 결과를 데이터프레임으로 변환하여 표 형태로 출력
    df_results = pd.DataFrame(results)
    st.dataframe(df_results, use_container_width=True)