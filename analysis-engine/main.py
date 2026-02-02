from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import json
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional
from contextlib import asynccontextmanager
import os
from scipy.stats import linregress

# 국가 매핑
COUNTRY_MAPPING = {
    '미국': 'US',
    '중국': 'CN',
    '일본': 'JP',
    '베트남': 'VN',
    '독일': 'DE'
}

REVERSE_MAPPING = {v: k for k, v in COUNTRY_MAPPING.items()} # {'US': '미국', ...}

# UI 표시 이름 -> CSV 저장 이름 매핑
UI_TO_CSV_ITEM_MAPPING = {
    "간장": "간장", "감": "감", "건고사리": "고사리", "고추장": "고추장", "국수": "국수",
    "참치 통조림": "기름에 담근 것", "김치": "김치", "깐마늘": "껍질을 깐 것", "김밥류": "냉동김밥",
    "냉면": "냉면", "당면": "당면", "건더덕": "더덕", "된장": "된장", "두부": "두부",
    "들기름": "들기름과 그 분획물", "라면": "라면", "쌀": "멥쌀", "피클 및 절임채소": "밀폐용기에 넣은 것",
    "냉동 밤": "밤", "쿠키 및 크래커": "비스킷, 쿠키와 크래커", "삼계탕": "삼계탕", "소시지": "소시지",
    "소주": "소주", "만두": "속을 채운 파스타(조리한 것인지 또는 그 밖의 방법으로 조제한 것인지에 상관없다)",
    "초코파이류": "스위트 비스킷", "떡볶이 떡": "쌀가루의 것", "전통 한과/약과": "쌀과자", "유자": "유자",
    "인스턴트 커피": "인스턴트 커피의 조제품", "즉석밥": "찌거나 삶은 쌀", "참기름": "참기름과 그 분획물",
    "춘장": "춘장", "막걸리": "탁주", "쌀 튀밥": "튀긴 쌀", "팽이버섯": "팽이버섯", 
    "표고버섯": "표고버섯", "쌈장 및 양념장": "혼합조미료", "홍삼 엑기스": "홍삼 추출물(extract)"
}

CSV_TO_UI_ITEM_MAPPING = {v: k for k, v in UI_TO_CSV_ITEM_MAPPING.items()}

# 아이템별 검색어(Trend Keyword) 매핑
# 트렌드 데이터 컬럼명 예시: {COUNTRY}_{KEYWORD}_mean
ITEM_TO_TREND_MAPPING = {
    "간장": "Gochujang",
    "고추장": "Gochujang",
    "된장": "Doenjang",
    "춘장": "Gochujang",
    "쌈장 및 양념장": "Ssamjang",
    "김치": "Kimchi",
    "라면": "Ramyun",
    "국수": "Ramyun",
    "냉면": "Ramyun",
    "당면": "Ramyun",
    "소주": "Soju",
    "막걸리": "Makgeolli",
    "김밥류": "Gimbap",
    "떡볶이 떡": "Tteokbokki",
    "유자": "Yuja",
    "만두": "KFood",
    "삼계탕": "KFood",
    "참치 통조림": "KFood",
    "초코파이류": "KFood",
    "쿠키 및 크래커": "KFood",
    "전통 한과/약과": "KFood",
    "인스턴트 커피": "KFood",
    "즉석밥": "KFood",
    "쌀": "KFood",
    "두부": "KFood",
    "들기름": "KFood",
    "참기름": "KFood",
    "팽이버섯": "KFood",
    "표고버섯": "KFood",
    "홍삼 엑기스": "KFood"
}

df = None
growth_summary_df = None # (item, country, weight_growth, price_growth, value_size)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global df, growth_summary_df
    csv_path = 'cleaned_merged_export_trends.csv'
    
    if not os.path.exists(csv_path):
        parent_path = os.path.join('..', csv_path)
        if os.path.exists(parent_path):
            csv_path = parent_path
            
    try:
        if os.path.exists(csv_path):
            print(f"데이터 로드 중: {csv_path}")
            # 1-1. 'period' 컬럼을 문자열로 읽기 위해 dtype 지정
            df = pd.read_csv(csv_path, low_memory=False, dtype={'period': str})
            
            # 1-2. period 변환 및 정렬
            if 'period' in df.columns:
                def convert_period(val):
                    try:
                        if pd.isna(val) or val == '': return ''
                        s = str(val).strip()
                        
                        # Case 1: "2022.10" (7글자) -> 2022-10
                        # Case 2: "2022.1"  (6글자) -> 2022-01
                        # Case 3: "2022.01" (7글자) -> 2022-01
                        
                        parts = s.split('.')
                        year = parts[0]
                        if len(parts) > 1:
                            month_part = parts[1]
                        # "10", "11", "12"는 그대로
                            if len(month_part) == 2:
                                month = month_part
                            # 한 글자인 경우:
                            # 데이터셋 분석 결과 1월은 '01'로, 10월은 '1'로(0이 탈락) 저장된 패턴 확인됨
                            elif len(month_part) == 1:
                                if month_part == '1':
                                    month = '10' # 1 -> 10월
                                else:
                                    month = '0' + month_part # 2~9 -> 02~09월
                            else:
                                month = str(month_part)[:2].zfill(2)
                        else:
                            month = '01' # 월 정보 없으면 default
                            
                        return f"{year}-{month}"
                    except: return ''
                
                df['period_str'] = df['period'].apply(convert_period)
                # 잘못된 변환으로 중복된 period가 생길 수 있으므로 이를 방지하기 위한 추가 정렬
                df = df.sort_values(by=['country_name', 'item_name', 'period_str'])

            # 2. 결측치 처리 (Interpolation 제거 -> 0 채움)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(0)
            
            if 'export_value' in df.columns:
                df['export_value'] = pd.to_numeric(df['export_value'], errors='coerce').fillna(0)
            
            # 3. Growth Matrix(산점도)용 요약 데이터 미리 계산
            # 각 (국가, 아이템) 별로 최근 1년 vs 직전 1년 성장률 계산
            print("성장 매트릭스 계산 중...")
            summaries = []
            
            # 그룹핑하여 계산
            group_cols = ['country_code', 'item_name']
            if 'country_code' not in df.columns:
                 group_cols = ['country_name', 'item_name']
                 
            grouped = df.groupby(group_cols)
            
            for name, group in grouped:
                if len(group) < 24: continue # 최소 2년치 데이터 필요
                
                # 정렬 보장
                group = group.sort_values('period_str')
                
                recent_12 = group.tail(12)
                prev_12 = group.iloc[-24:-12]
                
                # 양적 성장 (수출 중량)
                weight_col = 'export_weight' if 'export_weight' in group.columns else None
                if weight_col:
                    w_curr = recent_12[weight_col].sum()
                    w_prev = prev_12[weight_col].sum()
                else: 
                     w_curr = recent_12['export_value'].sum()
                     w_prev = prev_12['export_value'].sum()

                # 단, 분모가 0이면 성장률 계산 불가 -> 0 또는 예외처리
                weight_growth = ((w_curr - w_prev) / w_prev * 100) if w_prev > 0 else 0
                
                # 질적 성장 (수출 단가)
                # 단가는 합계가 아니라 평균으로 비교
                p_curr = recent_12['unit_price'].mean()
                p_prev = prev_12['unit_price'].mean()
                price_growth = ((p_curr - p_prev) / p_prev * 100) if p_prev > 0 else 0
                
                # 버블 크기 (수출 규모)
                total_value = recent_12['export_value'].sum()
                
                summaries.append({
                    'country': name[0] if 'country_code' in df.columns else COUNTRY_MAPPING.get(name[0], name[0]),
                    'item_csv_name': name[1],
                    'weight_growth': round(weight_growth, 1),
                    'price_growth': round(price_growth, 1),
                    'total_value': total_value
                })
            
            growth_summary_df = pd.DataFrame(summaries)
            print("데이터 로딩 및 요약 완료.")
            
        else:
            print(f"경고: {csv_path} 파일을 찾을 수 없습니다.")
            df = pd.DataFrame()
            growth_summary_df = pd.DataFrame()
            
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        df = pd.DataFrame()
        growth_summary_df = pd.DataFrame()
    yield
    print("서버를 종료합니다.")

app = FastAPI(title="K-Food Export Analysis Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.get("/")
async def root():
    return {"message": "K-Food Analysis Engine (Visual Analytics Mode)", "status": "Ready"}

@app.get("/items")
async def get_items():
    global df
    if df is None or df.empty: return {"items": []}
    try:
        csv_items = df['item_name'].dropna().unique().tolist()
        ui_items = sorted(list(set([CSV_TO_UI_ITEM_MAPPING.get(i, i) for i in csv_items])))
        return {"items": ui_items}
    except: return {"items": []}

@app.get("/analyze")
async def analyze(country: str = Query(...), item: str = Query(...)):
    global df, growth_summary_df
    
    # 1. 매핑 및 유효성 검사
    country_name = REVERSE_MAPPING.get(country, country) # 코드(US) -> 이름(미국)
    if country in COUNTRY_MAPPING: # 입력이 한글(미국)이면 코드로 변환
         country_code = COUNTRY_MAPPING[country]
         country_name = country
    else:
         country_code = country # 입력이 코드(US)면 그대로
         
    csv_item_name = UI_TO_CSV_ITEM_MAPPING.get(item, item)
    
    # 데이터 필터링
    filtered = df[
        (df['country_name'] == country_name) & 
        (df['item_name'] == csv_item_name)
    ].copy()
    
    if filtered.empty or (filtered['export_value'].sum() == 0):
        return {"has_data": False}

    # 날짜순 정렬
    filtered = filtered.sort_values('period_str')

    # ---------------------------------------------------------
    # Chart 1: Trend Stack (수출액 + 환율 + GDP/Econ)
    # ---------------------------------------------------------
    rows = 2
    titles = ["수출액 Trend", f"{country_name} 현지 환율"]
    if 'gdp_level' in filtered.columns:
        rows = 3
        titles.append(f"{country_name} GDP 지표")
        
    fig_stack = make_subplots(rows=rows, cols=1, shared_xaxes=True, 
                              vertical_spacing=0.1, subplot_titles=titles)
                              
    # Row 1: Export Value (Bar + Color Gradient)
    fig_stack.add_trace(go.Bar(
        x=filtered['period_str'], y=filtered['export_value'], name="수출액 ($)",
        marker=dict(color=filtered['export_value'], colorscale='Purples')
    ), row=1, col=1)
    
    # Row 2: Exchange Rate (Line with Fill)
    fig_stack.add_trace(go.Scatter(
        x=filtered['period_str'], y=filtered['exchange_rate'], name="환율",
        line=dict(color='#f59e0b', width=2), fill='tozeroy', fillcolor='rgba(245, 158, 11, 0.1)'
    ), row=2, col=1)
    
    # Row 3: GDP (if exists)
    if rows == 3:
        fig_stack.add_trace(go.Scatter(
            x=filtered['period_str'], y=filtered['gdp_level'], name="GDP",
            line=dict(color='#10b981', width=2, dash='dot')
        ), row=3, col=1)

    fig_stack.update_layout(
        height=600 if rows == 3 else 450, 
        template="plotly_white", 
        showlegend=False,
        margin=dict(l=40, r=20, t=60, b=40)
    )

    # ---------------------------------------------------------
    # Chart 2: Signal Map (Leading-Lagging)
    # ---------------------------------------------------------
    fig_signal = make_subplots(specs=[[{"secondary_y": True}]])
    
    # 1. 공통 선행 지표: 전체 K-Food 관심도 (Baseline)
    common_trend_col = f"{country_code}_KFood_mean"
    has_common = common_trend_col in filtered.columns
    if has_common:
        fig_signal.add_trace(go.Scatter(
            x=filtered['period_str'], y=filtered[common_trend_col], 
            name="K-Food 전체 관심도",
            line=dict(color='#fda4af', width=2, dash='dot'), # 연한 핑크 점선
            opacity=0.6
        ), secondary_y=True)

    # 2. 개별 선행 지표: 1:1 매핑된 품목 관심도
    trend_kw = ITEM_TO_TREND_MAPPING.get(item)
    # KFood와 중복되지 않는 경우에만 추가로 그림
    if trend_kw and trend_kw != "KFood":
        specific_trend_col = f"{country_code}_{trend_kw}_mean"
        if specific_trend_col in filtered.columns:
            fig_signal.add_trace(go.Scatter(
                x=filtered['period_str'], y=filtered[specific_trend_col], 
                name=f"품목 관심도 ({trend_kw})",
                line=dict(color='#f43f5e', width=4), # 진한 장미색 실선
                mode='lines+markers'
            ), secondary_y=True)
    elif not has_common:
        # KFood도 없고 매핑도 없을 때만 아무 트렌드나 하나 찾아서 표시 (폴백)
        fallback_col = next((c for c in filtered.columns if c.startswith(f"{country_code}_") and c.endswith("_mean")), None)
        if fallback_col:
            fig_signal.add_trace(go.Scatter(
                x=filtered['period_str'], y=filtered[fallback_col], 
                name="관심도 (관련 데이터)",
                line=dict(color='#f43f5e', width=3)
            ), secondary_y=True)

    # 3. 후행 지표: 실적(수출액) - Area
    fig_signal.add_trace(go.Scatter(
        x=filtered['period_str'], y=filtered['export_value'], name="수출 실적 ($)",
        fill='tozeroy', line=dict(color='#6366f1', width=0), opacity=0.3
    ), secondary_y=False)
        
    fig_signal.update_layout(
        title="Signal Map (관심도 vs 실적 시차 분석)",
        template="plotly_white",
        height=400,
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor='center'),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    fig_signal.update_yaxes(title_text="수출액 ($)", secondary_y=False, showgrid=False)
    fig_signal.update_yaxes(title_text="관심도 Index", secondary_y=True, showgrid=False)

    # ---------------------------------------------------------
    # Chart 3: Growth Matrix (Scatter Plot)
    # ---------------------------------------------------------
    country_matrix = growth_summary_df[growth_summary_df['country'] == country_code].copy()
    fig_scatter = go.Figure()
    
    if not country_matrix.empty and not country_matrix[country_matrix['item_csv_name'] == csv_item_name].empty:
        country_matrix['ui_name'] = country_matrix['item_csv_name'].apply(lambda x: CSV_TO_UI_ITEM_MAPPING.get(x, x))
        
        curr = country_matrix[country_matrix['item_csv_name'] == csv_item_name]
        others = country_matrix[country_matrix['item_csv_name'] != csv_item_name]
        
        # Others
        fig_scatter.add_trace(go.Scatter(
            x=others['weight_growth'], y=others['price_growth'],
            mode='markers',
            marker=dict(size=10, color='#94a3b8', opacity=0.4),
            text=others['ui_name'], name="타 품목",
            hovertemplate="<b>%{text}</b><br>양적: %{x}%<br>질적: %{y}%"
        ))
        
        # Current
        fig_scatter.add_trace(go.Scatter(
            x=curr['weight_growth'], y=curr['price_growth'],
            mode='markers+text',
            marker=dict(size=25, color='#f43f5e', line=dict(width=2, color='white')),
            text=curr['ui_name'], textposition="top center",
            textfont=dict(size=15, color='#f43f5e', family="Arial Black"),
            name=item,
            hovertemplate="<b>%{text}</b> (현재)<br>양적: %{x}%<br>질적: %{y}%"
        ))
        
        # Quadrant Lines
        fig_scatter.add_hline(y=0, line_dash="solid", line_color="#e2e8f0")
        fig_scatter.add_vline(x=0, line_dash="solid", line_color="#e2e8f0")
        
        # Annotations (1~4사분면)
        # 1사분면 (우상향): Premium Expansion
        fig_scatter.add_annotation(x=10, y=10, text="Premium (고부가가치 성장)", showarrow=False, font=dict(color="#10b981", size=12), xanchor="left")
        # 4사분면 (우하향): Volume Driven
        fig_scatter.add_annotation(x=10, y=-10, text="Volume (박리다매)", showarrow=False, font=dict(color="#3b82f6", size=12), xanchor="left")
        
        fig_scatter.update_layout(
            title="성장의 질 (Growth Matrix)",
            xaxis_title="양적 성장 (물량 증가율 %)",
            yaxis_title="질적 성장 (단가 증가율 %)",
            template="plotly_white",
            height=500,
            showlegend=False,
            margin=dict(l=40, r=20, t=60, b=40)
        )
    else:
        # 데이터가 부족해서 매트릭스를 그릴 수 없을 때 빈 차트
        fig_scatter.update_layout(
            title="성장의 질 (데이터 부족)",
            template="plotly_white", height=500
        )

    return {
        "country": country,
        "country_name": country_name,
        "item": item,
        "has_data": True,
        "charts": {
            "trend_stack": json.loads(fig_stack.to_json()),
            "signal_map": json.loads(fig_signal.to_json()),
            "growth_matrix": json.loads(fig_scatter.to_json())
        }
    }

@app.get("/dashboard")
async def dashboard():
    global df
    if df is None or df.empty:
        return {"has_data": False}
        
    try:
        # 1. Top 5 국가 수출 추세 (Line)
        # 국가별, 월별 합산
        country_trend = df.groupby(['period_str', 'country_name'])['export_value'].sum().reset_index()
        # 총 수출액 기준 Top 5 국가 선정
        top_countries = df.groupby('country_name')['export_value'].sum().nlargest(5).index.tolist()
        country_trend_top = country_trend[country_trend['country_name'].isin(top_countries)]
        
        fig1 = px.line(country_trend_top, x='period_str', y='export_value', color='country_name',
                       title="1. Top 5 국가 수출 추세 (Market Trend)")
        fig1.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), xaxis_title="기간", yaxis_title="수출액 ($)")

        # 2. Top 5 품목 수출 추세 (Line)
        item_trend = df.groupby(['period_str', 'item_name'])['export_value'].sum().reset_index()
        top_items = df.groupby('item_name')['export_value'].sum().nlargest(5).index.tolist()
        item_trend_top = item_trend[item_trend['item_name'].isin(top_items)]
        
        # UI 이름으로 매핑
        item_trend_top['ui_name'] = item_trend_top['item_name'].apply(lambda x: CSV_TO_UI_ITEM_MAPPING.get(x, x))
        
        fig2 = px.line(item_trend_top, x='period_str', y='export_value', color='ui_name',
                       title="2. Top 5 품목 수출 추세 (Product Lifecycle)")
        fig2.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), xaxis_title="기간", yaxis_title="수출액 ($)")

        # 3. 국가별 평균 단가 비교 (Bar - Profitability)
        # 단가 = 총 수출액 / 총 중량 (중량 없으면 unit_price 평균 대용)
        # 여기서는 간단히 unit_price의 평균을 국가별로 비교
        profitability = df.groupby('country_name')['unit_price'].mean().sort_values(ascending=False).reset_index()
        
        fig3 = px.bar(profitability, x='country_name', y='unit_price', color='unit_price',
                      title="3. 국가별 평균 단가 (Profitability Check)", color_continuous_scale='Viridis')
        fig3.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), xaxis_title="국가", yaxis_title="평균 단가 ($/kg)")

        # 4. 시장 포지셔닝 맵 (Scatter - Volume vs Value)
        # 국가별 총 수출액(Value) vs 총 중량(Volume)
        positioning = df.groupby('country_name').agg({
            'export_value': 'sum',
            'export_weight': 'sum'
        }).reset_index()
        
        fig4 = px.scatter(positioning, x='export_weight', y='export_value', text='country_name',
                          size='export_value', color='country_name',
                          title="4. 시장 포지셔닝 (Volume vs Value)")
        fig4.update_traces(textposition='top center')
        fig4.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20), 
                           xaxis_title="총 물량 (Volume)", yaxis_title="총 금액 (Value)")

        # 5. 품목별 월별 계절성 (Heatmap)
        # 월(Month) 추출
        df['month'] = df['period_str'].apply(lambda x: x.split('-')[1] if '-' in str(x) else '00')
        seasonality = df[df['item_name'].isin(top_items)].groupby(['item_name', 'month'])['export_value'].sum().reset_index()
        
        # UI 이름 매핑
        seasonality['ui_name'] = seasonality['item_name'].apply(lambda x: CSV_TO_UI_ITEM_MAPPING.get(x, x))
        
        # Pivot for Heatmap: Index=Item, Columns=Month, Values=ExportValue
        heatmap_data = seasonality.pivot(index='ui_name', columns='month', values='export_value').fillna(0)
        # 월 순서 정렬
        sorted_months = sorted(heatmap_data.columns)
        heatmap_data = heatmap_data[sorted_months]
        
        fig5 = px.imshow(heatmap_data, labels=dict(x="월 (Month)", y="품목", color="수출액"),
                         title="5. 계절성 분석 (Seasonality Heatmap)", aspect="auto", color_continuous_scale='OrRd')
        fig5.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=40, b=20))

        return {
            "has_data": True,
            "charts": {
                "top_countries": json.loads(fig1.to_json()),
                "top_items": json.loads(fig2.to_json()),
                "profitability": json.loads(fig3.to_json()),
                "positioning": json.loads(fig4.to_json()),
                "seasonality": json.loads(fig5.to_json())
            }
        }
    except Exception as e:
        print(f"Dashboard Error: {e}")
        return {"has_data": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
