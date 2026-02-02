프로젝트 프롬프트: K-Food 수출 인사이트 시각화 시스템 구축
1. 프로젝트 개요
본 프로젝트의 목적은 기존 Spring Boot(Back) + React/Next.js(Front) 환경에 Python(FastAPI) 분석 엔진을 추가하여, 수출 트렌드 데이터를 직관적인 비즈니스 인사이트로 변환해 보여주는 대시보드를 구축하는 것이다.

2. 시스템 아키텍처
Frontend: React/Next.js (기존 UI 스타일 가이드 준수)

Backend: Spring Boot (API Gateway 및 인증 관리)

Analysis Engine: Python FastAPI (Pandas를 활용한 데이터 처리 및 시각화)

Data: cleaned_merged_export_trends.csv (서버 기동 시 메모리 로드)

3. 핵심 기능 요구사항 (Core Logic)
A. 데이터 전처리 및 지표 통합 (Pre-calculation)
성능 최적화를 위해 Python 서버 기동 시 다음 지표를 미리 계산하여 메모리에 상주시킨다.

시장 매력도 (Market Health Score): gdp_growth, industrial_prod_monthly, KRW_USD를 결합하여 0~10점 척도로 정규화.

K-푸드 화제성 (K-Buzz Index): 국가별(US, JP, VN, DE) 검색 트렌드 컬럼(예: US_KFood_mean, US_Kimchi_mean 등)을 평균 내어 0~100점 척도로 변환.

가격 경쟁력 (Price Advantage): 환율 변동 추이와 수출 단가를 결합하여 계산.

B. 사용자 인터페이스 (UI/UX)
메인 화면: 국가(Country)와 물품(Item)을 선택할 수 있는 셀렉트 박스/버튼 배치.

인사이트 카드: 복잡한 지표를 요약한 스코어 카드 3종(시장 매력도, 화제성, 경쟁력)을 최상단에 배치.

상세 시각화: * 수출액/중량 추이 그래프 (Dual Axis)

화제성 지수와 실제 수출액의 상관관계 차트

(선택 시 노출) CPI, GDP 등 상세 경제 지표 그래프

4. 상세 구현 지시 사항
[Backend - Python FastAPI]
@app.on_event("startup")을 사용하여 서버 시작 시 CSV를 로드하고 통합 지표 컬럼을 생성할 것.

/analyze?country={country}&item={item} 엔드포인트를 생성하여 다음을 반환할 것:

통합 스코어 데이터 (JSON)

Matplotlib/Seaborn으로 생성한 시각화 이미지 (Base64 인코딩 문자열) 또는 Plotly JSON 데이터.

[Backend - Spring Boot]
Python 서버(포트 8000 예정)와 통신하는 AnalysisServiceClient를 작성할 것.

Frontend의 요청을 받아 Python 서버로 전달하고 결과를 반환하는 프록시 API를 구축할 것.

[Frontend - React/Next.js]
기존 시스템의 디자인 시스템(색상, 폰트, 컴포넌트 스타일)을 계승할 것.

사용자가 국가/물품을 선택하면 즉시 대시보드가 업데이트되는 반응형 UI를 구현할 것.

차트 라이브러리는 Recharts 또는 Python에서 생성한 Base64 이미지를 렌더링할 것.

5. 비기능적 요구사항
성능: 모든 데이터는 전처리되어 있어야 하며, 사용자 선택 시 응답 시간은 0.5초 이내여야 함.

확장성: 향후 새로운 국가나 품목이 추가되어도 코드 수정 없이 CSV 업데이트만으로 대응 가능해야 함.