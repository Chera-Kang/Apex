# Apex Info
> 에이펙스 레전드(Apex Legends) 공식 위키 데이터를 크롤링하여 무기 스펙을 검증하고 조회하는 개인 토이 프로젝트입니다.

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-ETL-150458?style=flat-square)](https://pandas.pydata.org/)

---

## 📌 소개
공식 위키에 등록된 29종 무기 수치 데이터를 직접 크롤링하여 정제하고, 인게임 데미지 규칙과 공식에 결함(오타, 비정상 수치)이 없는지 자동으로 검증해본 실험용 데이터 샌드박스입니다.

- **위키 데이터 크롤링 (`apex_crawler.py`)**: 무기별 데미지, RPM, 탄약 유형 등 최신 스펙 추출 및 JSON 정제
- **수치 정합성 자동 검증 (`verify_weapons.py`)**: 헤드/바디 데미지 비율 및 DPS 공식 무결성 검증 (Assertion)
- **미니 웹 도감 (`index.html`)**: 검증된 JSON 데이터를 가볍게 조회할 수 있는 초경량 웹 뷰

---

## 🚀 실행 방법

```bash
# 1. 패키지 설치
pip install -r requirements.txt

# 2. 크롤링 및 수치 검증 실행
python scripts/apex_crawler.py
python scripts/verify_weapons.py

# 3. 웹 도감 확인: 브라우저에서 index.html 바로 열기
```
