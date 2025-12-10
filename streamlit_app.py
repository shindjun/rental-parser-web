import streamlit as st
import re
import pandas as pd

st.title("렌탈/대여 자동 계산기")

# 텍스트 입력
text_input = st.text_area("일정 텍스트 입력", height=200)

if st.button("파싱 실행"):
    # 전체 텍스트를 한 줄로 합치되, 줄바꿈은 공백으로
    line = text_input.replace("\n", " ").strip()

    # 1. 날짜 (설치일)
    date_match = re.search(r"설치일\s*[:：]?\s*(\d{4}년\s*\d{1,2}월\d{1,2}일)", line)
    date = date_match.group(1) if date_match else ""

    # 2. 업체명 (슬래시 전, 날짜 제외)
    company = line.split("/")[0].strip()
    company = re.sub(r"\d{4}년\s*\d{1,2}월\d{1,2}일", "", company).strip()

    # 3. 기기타입
    type_ = "부스" if "부스" in line else ("미니" if "미니" in line else "")

    # 4. 랩핑
    wrapping = "O" if "랩핑" in line else "X"

    # 5. 기기수량
    quantity_match = re.search(r"([0-9]+)대", line)
    quantity = quantity_match.group(1) if quantity_match else ""

    # 6. 렌탈일수
    # 범위형: 10~15일 -> 5일
    range_match = re.search(r"([1-9][0-9]*)~([1-9][0-9]*)일", line)
    if range_match:
        rent_days = int(range_match.group(2)) - int(range_match.group(1))
    else:
        # 단일형: 렌탈 6일, 대여: 3일 등
        single_match = re.search(r"(?:렌탈|대여|렌탈:|대여:)\s*([0-9]+)일", line)
        rent_days = int(single_match.group(1)) if single_match else ""

    # 7. 지역 (담당자 앞까지만)
    region_match = re.search(r"지역\s*[:：]?\s*(.*?)\s*(?:담당자|$)", line)
    region = region_match.group(1).strip() if region_match else ""

    # 8. 담당자 전화번호
    phone_match = re.search(r"([0-9]{3}-[0-9]{3,4}-[0-9]{4})", line)
    phone = phone_match.group(1) if phone_match else ""

    # 9. 업체종류
    company_type = "기업"
    if re.search(r"교회|성당|기독교|천주교", company):
        company_type = "교회"
    elif re.search(r"시청|구청|도청|군청|읍면동|주민센터|청사", company):
        company_type = "지자체"
    elif re.search(r"대학|대학교|고등학교|중학교|초등학교|유치원|학원|학교|학생회|포스텍|대$|대 |대\(|대\.", company):
        company_type = "학교"
    elif re.search(r"경찰서|소방서|보건소|교육청|한국전력|도로공사|LH|공사|공단|검찰청|법원|세무서", company):
        company_type = "공공기관"
    elif re.search(r"군인회|향군|전우회|보훈", company):
        company_type = "군인"

    # 데이터프레임 한 행 생성
    df = pd.DataFrame([[date, company, type_, wrapping, quantity, rent_days, region, phone, company_type]],
                      columns=["날짜","업체명","기기타입","랩핑","기기수량","렌탈일수","지역","담당자","업체종류"])

    st.dataframe(df)
