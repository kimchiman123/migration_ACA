from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional

app = FastAPI(title="K-Food Export Analysis Engine")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 데이터 저장소
df = None
COUNTRY_MAPPING = {
    '미국': 'US',
    '중국': 'CN',
    '일본': 'JP',
    '베트남': 'VN',
    '독일': 'DE'
}
REVERSE_MAPPING = {v: k for k, v in COUNTRY_MAPPING.items()}

ISO3_MAPPING = {
    'US': 'USA',
    'CN': 'CHN',
    'JP': 'JPN',
    'VN': 'VNM',
    'DE': 'DEU'
}

@app.on_event("startup")
async def load_data():
    global df
    try:
        # 대용량 데이터 로드 오류 방지를 위해 low_memory=False 사용
        df = pd.read_csv('cleaned_merged_export_trends.csv', low_memory=False)
        
        # 결측치 처리 (Interpolation)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
        
        # 남은 결측치는 평균으로 채움 (지표 급락 방지)
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
        
        print("데이터 로딩 및 정제 완료.")
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        # 폴백용 더미 데이터 생성 (필요 시)
        df = pd.DataFrame()

def calculate_market_health(country_code, recent_data):
    """
    시장 매력도(Market Health): GDP 성장률, 산업 생산지수, 환율을 결합하여 0~10점 산출.
    """
    iso3 = ISO3_MAPPING.get(country_code, 'USA')
    gdp_col = f'Growth_{iso3}'
    ipi_col = f'IPI_{iso3}'
    ex_rate_col = 'exchange_rate' # 기본 환율 컬럼 사용
    
    gdp = recent_data[gdp_col].iloc[-1] if gdp_col in recent_data.columns else 0
    ipi = recent_data[ipi_col].iloc[-1] if ipi_col in recent_data.columns else 0
    ex_rate = recent_data[ex_rate_col].iloc[-1] if ex_rate_col in recent_data.columns else 0
    
    # 정규화 및 가중치 (단순화된 스코어링)
    # GDP (0-5% -> 0-4점), IPI (90-110 -> 0-3점), 환율 (추세 -> 0-3점)
    gdp_score = min(max(gdp * 2, 0), 4)
    ipi_score = min(max((ipi - 90) / 10 * 1.5, 0), 3)
    ex_score = 3.0 # 기본값
    
    score = gdp_score + ipi_score + ex_score
    return round(min(score, 10.0), 1)

def calculate_k_buzz(country_code, recent_data):
    """
    K-푸드 화제성(K-Buzz Index): 선택 국가 코드에 맞는 검색 트렌드 컬럼들을 평균 내어 0~100점 산출.
    """
    # [COUNTRY CODE]_ 접두사로 시작하고 _mean으로 끝나는 컬럼 찾기
    trend_cols = [col for col in recent_data.columns if col.startswith(f"{country_code}_") and col.endswith("_mean")]
    
    if not trend_cols:
        return 50.0 # 데이터 없을 시 중간값
    
    avg_trend = recent_data[trend_cols].iloc[-1].mean()
    return round(min(max(avg_trend, 0), 100.0), 1)

def calculate_price_advantage(recent_data):
    """
    가격 경쟁력(Price Advantage): 수출 단가와 환율 추이를 조합하여 0~10점 산출.
    """
    unit_price = recent_data['unit_price'].iloc[-1] if 'unit_price' in recent_data.columns else 0
    ex_rate = recent_data['exchange_rate'].iloc[-1] if 'exchange_rate' in recent_data.columns else 1
    
    # 단가가 낮고 환율이 높을수록 경쟁력 상승 (수출 기업 입장)
    # 단순화: (환율 / 단가) 비율을 스케일링
    if unit_price > 0:
        ratio = (ex_rate / unit_price) / 100 # 임의의 스케일링 팩터
        score = min(max(ratio, 0), 10)
    else:
        score = 5.0
        
    return round(score, 1)

@app.get("/analyze")
async def analyze(country: str = Query(...), item: str = Query(...)):
    global df
    if df is None or df.empty:
        raise HTTPException(status_code=500, detail="데이터가 로드되지 않았습니다.")
    
    # 국가명 변환 (코드 -> 한국어)
    country_name = REVERSE_MAPPING.get(country)
    if not country_name:
        # 역매핑 시도 (한국어 -> 코드)
        if country in COUNTRY_MAPPING:
            country_name = country
            country = COUNTRY_MAPPING[country]
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 국가입니다: {country}")
            
    # 데이터 필터링
    filtered = df[(df['country_name'] == country_name) & (df['item_name'] == item)].copy()
    
    if filtered.empty:
        # 아이템 이름으로 다시 검색 (유연성)
        filtered = df[(df['country_name'] == country_name) & (df['item_name'].str.contains(item, case=False, na=False))].copy()
        
    if filtered.empty:
        raise HTTPException(status_code=404, detail="해당 조건의 데이터를 찾을 수 없습니다.")
        
    # 날짜 정렬
    filtered['period'] = pd.to_datetime(filtered['period'])
    filtered = filtered.sort_values('period')
    
    recent_data = filtered.tail(12) # 최근 1년치
    
    # 스코어 계산
    market_health = calculate_market_health(country, recent_data)
    k_buzz = calculate_k_buzz(country, recent_data)
    price_advantage = calculate_price_advantage(recent_data)
    
    # 통합 지수 (가중 평균)
    total_score = round((market_health * 10 + k_buzz + price_advantage * 10) / 3, 1)
    
    # 차트 데이터 생성 (Plotly JSON)
    # 1. 수출 추이 차트
    fig_export = px.line(filtered, x='period', y='export_value', title=f"{country_name} {item} 수출 금액 추이")
    fig_export.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    
    # 2. 상관관계 차트 (수출 vs 검색량)
    trend_col = f"{country}_{item}_mean"
    if trend_col not in filtered.columns:
        # Fallback to general KFood trend
        trend_col = f"{country}_KFood_mean"
        
    fig_corr = go.Figure()
    fig_corr.add_trace(go.Scatter(x=filtered['period'], y=filtered['export_value'], name="수출액", yaxis="y1"))
    if trend_col in filtered.columns:
        fig_corr.add_trace(go.Scatter(x=filtered['period'], y=filtered[trend_col], name="검색 트렌드", yaxis="y2"))
        
    fig_corr.update_layout(
        title=f"수출액 및 검색 트렌드 상관관계",
        yaxis=dict(title="수출액", side="left"),
        yaxis2=dict(title="검색량", side="right", overlaying="y", showgrid=False),
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return {
        "country": country,
        "country_name": country_name,
        "item": item,
        "scores": {
            "market_health": market_health,
            "k_buzz": k_buzz,
            "price_advantage": price_advantage,
            "total_score": total_score
        },
        "charts": {
            "export_trend": json.loads(fig_export.to_json()),
            "correlation": json.loads(fig_corr.to_json())
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
