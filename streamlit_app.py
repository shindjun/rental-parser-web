import streamlit as st
import re
import pandas as pd
import os

st.title("렌탈/대여 자동 계산기 (누적 + 삭제)")

CSV_FILE = "result.csv"

# 기존 데이터 로드
if os.path.exists(CSV_FILE):
    df_existing = pd.read_csv(CSV_FILE)
else:
    df_existing = pd.DataFrame(columns=[
        "날짜","업체명","기기타입","랩핑","기기수량",
        "렌탈일수","지역","담당자","업체종류"
    ])

text_input = st.text_area("일정 텍스트 입력", height=250)

if st.button("파싱 & 저장"):
    # 빈 줄 기준으로 여러 건 분리
    lines = [x.strip() for x in text_input.split("\n\n") if x.strip()]
    rows = []
    for line in lines:
        # 날짜: 설치/설치일 뒤의 연도 포함 월일
        date_match = re.search(r"설치(?:일)?\s*[:：]?\s*(\d{4}년\s*\d{1,2}월\d{1,2}일)", line)
        date = date_match.group(1) if date_match else ""

        # 업체명
        company = line.split("/")[0].strip()
        company = re.sub(r"\d{4}년\s*\d{1,2}월\d{1,2}일", "", company).strip()
        company = re.sub(r"^\s*[-~]\s*", "", company)

        # 기기타입
        type_ = "부스" if "부스" in line else ("미니" if "미니" in line else "")

        # 랩핑
        wrapping = "O" if "랩핑" in line else "X"

        # 기기수량
        quantity_match = re.search(r"([0-9]+)대", line)
        quantity = quantity_match.group(1) if quantity_match else ""

        # 렌탈일수
        # 범위 (예: 10~15일)
        range_match = re.search(r"(\d+)~(\d+)일", line)
        if range_match:
            rent_days = int(range_match.group(2)) - int(range_match.group(1))
        else:
            # 단일 숫자+일, 월·일 날짜 제외
            single_matches = re.findall(
                r"(?<!\d{4}년\s*\d{1,2}월)(?:렌탈|대여|렌탈:|대여:)?\s*([1-9][0-9]?)일", line
            )
            rent_days = int(single_matches[0]) if single_matches else ""

        # 지역 (담당자 앞까지만)
        region_match = re.search(r"지역\s*[:：]?\s*(.*?)\s*(?:담당자|$)", line)
        region = region_match.group(1).strip() if region_match else ""

        # 담당자 전화번호
        phone_match = re.search(r"([0-9]{3}-[0-9]{3,4}-[0-9]{4})", line)
        phone = phone_match.group(1) if phone_match else ""

        # 업체종류
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

        rows.append([date, company, type_, wrapping, quantity, rent_days, region, phone, company_type])

    # 기존 데이터와 합치기
    df_new = pd.DataFrame(rows, columns=df_existing.columns)
    df_all = pd.concat([df_existing, df_new], ignore_index=True)
    df_all.to_csv(CSV_FILE, index=False)
    st.success(f"{len(df_new)}건 저장 완료!")

# 저장된 데이터 확인 및 삭제
st.subheader("저장된 데이터 확인 및 삭제")
if not df_existing.empty:
    selected = st.multiselect(
        "삭제할 업체 선택", 
        options=df_existing.index,
        format_func=lambda x: df_existing.loc[x, "업체명"]
    )
    if st.button("선택 삭제"):
        df_existing.drop(selected, inplace=True)
        df_existing.to_csv(CSV_FILE, index=False)
        st.success(f"{len(selected)}건 삭제 완료!")
    st.dataframe(df_existing)
else:
    st.info("저장된 데이터가 없습니다.")
