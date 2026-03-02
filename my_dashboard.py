import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="CRM 마스터 대시보드", layout="wide", initial_sidebar_state="expanded")

# ── 글로벌 CSS (라이트 테마 / 선명한 데이터 시각화) ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif !important;
    background-color: #F0F4F9 !important;
    color: #1A202C !important;
}

section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
    box-shadow: 2px 0 12px rgba(0,0,0,0.05) !important;
}
section[data-testid="stSidebar"] * { color: #2D3748 !important; }

.dash-header {
    background: linear-gradient(135deg, #1E40AF 0%, #2563EB 55%, #60A5FA 100%);
    border-radius: 18px;
    padding: 28px 32px 24px;
    margin-bottom: 24px;
    box-shadow: 0 6px 28px rgba(37,99,235,0.22);
}
.dash-header h1 { color: #FFFFFF !important; font-size: 1.65rem; font-weight: 800; margin: 0; letter-spacing: -0.02em; }
.dash-header p  { color: rgba(255,255,255,0.80) !important; font-size: 0.86rem; margin: 6px 0 0; }

.section-title {
    display: flex; align-items: center; gap: 10px;
    font-size: 1.06rem; font-weight: 700; color: #1A202C !important;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 10px; margin: 32px 0 18px;
}
.section-title .badge {
    background: #EBF4FF; color: #2563EB;
    font-size: 0.70rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px; letter-spacing: 0.06em;
}

[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricLabel"]  { color: #718096 !important; font-size: 0.76rem !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; }
[data-testid="stMetricValue"]  { color: #1A202C !important; font-size: 1.55rem !important; font-weight: 800; }
[data-testid="stMetricDelta"]  { font-size: 0.84rem !important; font-weight: 600; }

.stTabs [data-baseweb="tab-list"] {
    background: #E8EDF5 !important; border-radius: 12px !important; padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important; color: #718096 !important;
    font-weight: 600 !important; font-size: 0.83rem !important; padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important; color: #2563EB !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.09) !important;
}

[data-testid="stDataFrame"] {
    border-radius: 12px !important; overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04) !important;
}

hr { border-color: #E2E8F0 !important; margin: 28px 0 !important; }

.streamlit-expanderHeader {
    background: #FFFFFF !important; border-radius: 10px !important;
    border: 1px solid #E2E8F0 !important; font-weight: 600 !important;
}

.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #FFFFFF !important; border-color: #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── 공통 Plotly 레이아웃 ─────────────────────────────────────────────────────
LAYOUT = dict(
    plot_bgcolor="#FFFFFF", paper_bgcolor="#FFFFFF",
    font=dict(family="Noto Sans KR, Apple SD Gothic Neo, sans-serif", color="#374151", size=12),
    margin=dict(t=48, b=28, l=16, r=16),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11), bordercolor="rgba(0,0,0,0)"),
    hoverlabel=dict(bgcolor="#1E293B", font_color="#F8FAFC", font_size=12, bordercolor="#1E293B"),
)
PALETTE = ["#2563EB","#10B981","#F59E0B","#EF4444","#8B5CF6","#06B6D4"]
PALE    = ["#DBEAFE","#D1FAE5","#FEF3C7","#FEE2E2","#EDE9FE","#CFFAFE"]

def apply(fig, title=""):
    fig.update_layout(**LAYOUT, title=dict(text=title, font=dict(size=14, color="#111827"), x=0))
    fig.update_xaxes(showgrid=False, linecolor="#E5E7EB", tickfont=dict(size=11), ticks="outside", ticklen=4)
    fig.update_yaxes(gridcolor="#F3F4F6", linecolor="#E5E7EB", tickfont=dict(size=11))
    return fig

# ── 보안 로그인 ───────────────────────────────────────────────────────────────
def check_password():
    if "password_correct" not in st.session_state:
        _, col, _ = st.columns([1,1.1,1])
        with col:
            st.markdown("""
            <div style='text-align:center; padding:60px 0 24px;'>
                <div style='font-size:3rem; margin-bottom:10px;'>🔐</div>
                <h2 style='font-size:1.45rem; font-weight:800; color:#1A202C; margin:0;'>CRM 마스터 대시보드</h2>
                <p style='color:#718096; font-size:0.88rem; margin:8px 0 24px;'>접속 권한이 있는 사용자만 이용 가능합니다</p>
            </div>
            """, unsafe_allow_html=True)
            pw = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요", label_visibility="collapsed")
            if st.button("접속하기", use_container_width=True, type="primary"):
                if pw == "1234":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True

if not check_password():
    st.stop()

# ════════════════════════════════════════════════════════════════════
#  더미 데이터 세팅
# ════════════════════════════════════════════════════════════════════
MONTHS = ['25년 09월','25년 10월','25년 11월','25년 12월','26년 01월']

df_kpi = pd.DataFrame({
    '비교기간': MONTHS,
    '매출액':   [40437647, 88057694, 135804965, 92780255, 70282509],
    'ROAS':     [797, 2090, 5329, 1744, 1409],
    '클릭률':   [0.8, 4.7, 5.9, 4.3, 3.4],
    '전환율':   [12.9, 13.0, 18.0, 12.6, 11.7],
    '신규비중': [34.5, 43.3, 34.5, 43.3, 31.0],
})

df_signup = pd.DataFrame({
    '월':           MONTHS,
    '신규가입수':   [4820, 6540, 9200, 7310, 5980],
    '당월전환수':   [1900, 2980, 5060, 3200, 2390],
    '당월미전환수': [2920, 3560, 4140, 4110, 3590],
})
df_signup['전환율(%)'] = (df_signup['당월전환수'] / df_signup['신규가입수'] * 100).round(1)

np.random.seed(42)
def make_daily(dates, visit_base, buy_rate):
    n = len(dates)
    v = (visit_base + np.random.randint(-30,50,n) + np.arange(n)*1.5).astype(int)
    b = np.clip((v * buy_rate + np.random.randint(-5,10,n)).astype(int), 0, v)
    return pd.DataFrame({'날짜': dates, '방문수': v, '구매수': b})

df_daily = pd.concat([
    make_daily(pd.date_range('2026-01-01','2026-01-31'), 180, 0.31).assign(월='26년 01월'),
    make_daily(pd.date_range('2026-02-01','2026-02-28'), 210, 0.34).assign(월='26년 02월'),
], ignore_index=True)
df_daily['구매율(%)'] = (df_daily['구매수'] / df_daily['방문수'] * 100).round(1)

campaigns = {
    '신규회원 1일차':  {'발송수':[12000,15500,19800,14200,11300],'클릭수':[1320,1980,3168,1988,1356],
                        '주문건수':[396,693,1267,796,475],'매출':[39600000,76230000,139370000,87560000,52250000],'광고비':[480000,620000,792000,568000,452000]},
    '구매고객 3일차':  {'발송수':[3800,5200,7800,5600,4200],'클릭수':[760,1092,1950,1176,882],
                        '주문건수':[228,382,780,470,309],'매출':[22800000,42020000,85800000,51700000,33990000],'광고비':[190000,260000,390000,280000,210000]},
    '구매고객 7일차':  {'발송수':[2600,3800,5900,4100,3100],'클릭수':[442,722,1298,861,620],
                        '주문건수':[133,253,519,344,217],'매출':[13300000,27830000,57090000,37840000,23870000],'광고비':[130000,190000,295000,205000,155000]},
    '구매고객 14일차': {'발송수':[2100,3100,4800,3300,2500],'클릭수':[315,527,912,594,425],
                        '주문건수':[95,185,365,238,149],'매출':[9500000,20350000,40150000,26180000,16390000],'광고비':[105000,155000,240000,165000,125000]},
}
rows = []
for camp, v in campaigns.items():
    for i, m in enumerate(MONTHS):
        s,c,o,r,cost = v['발송수'][i],v['클릭수'][i],v['주문건수'][i],v['매출'][i],v['광고비'][i]
        rows.append({'캠페인':camp,'월':m,'발송수':s,'클릭수':c,'클릭률(%)':round(c/s*100,1),
                     '주문건수':o,'전환율(%)':round(o/c*100,1),'매출':r,'광고비':cost,'ROAS(%)':round(r/cost*100)})
df_camp = pd.DataFrame(rows)

# Recency 데이터
SEGS = ['전체회원','미구매자','1회 구매자','2~4회 구매자','5회 이상 구매자']
SEG_TOTAL = {'전체회원':50000,'미구매자':12000,'1회 구매자':18000,'2~4회 구매자':13000,'5회 이상 구매자':7000}
PERIODS = ['0~30일','31~60일','61~180일','181~365일','1년 이상']
PERIOD_COLOR = ['#2563EB','#10B981','#F59E0B','#EF4444','#94A3B8']
REC_DIST = {
    '전체회원':          [0.22,0.18,0.25,0.20,0.15],
    '미구매자':          [0.05,0.08,0.20,0.30,0.37],
    '1회 구매자':        [0.18,0.20,0.28,0.22,0.12],
    '2~4회 구매자':      [0.30,0.22,0.26,0.15,0.07],
    '5회 이상 구매자':   [0.45,0.25,0.18,0.08,0.04],
}
rec_rows = []
for seg in SEGS:
    total = SEG_TOTAL[seg]
    for p, ratio in zip(PERIODS, REC_DIST[seg]):
        rec_rows.append({'세그먼트':seg,'기간':p,'회원수':round(total*ratio),'비율(%)':round(ratio*100,1)})
df_rec = pd.DataFrame(rec_rows)

# ════════════════════════════════════════════════════════════════════
#  사이드바
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎛️ 필터 설정")
    st.divider()
    sel_month   = st.selectbox("📅 조회 월", ['전체'] + MONTHS)
    sel_camp    = st.multiselect("📣 캠페인 선택", list(campaigns.keys()), default=list(campaigns.keys()))
    sel_daily_m = st.selectbox("📆 일별 조회 월", ['26년 01월','26년 02월'])
    st.divider()
    if st.button("🚪 로그아웃", use_container_width=True):
        del st.session_state["password_correct"]
        st.rerun()

# ════════════════════════════════════════════════════════════════════
#  헤더
# ════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="dash-header">
    <h1>🚀 CRM 퍼포먼스 분석 대시보드</h1>
    <p>조회 기간: {sel_month} &nbsp;·&nbsp; 마케팅 성과 종합 리포트</p>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
#  [1] 전체 KPI 요약
#  차트: 매출 Bar + ROAS Line 이중축 콤보 | 효율지표 Area Multi-line
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📊 전체 KPI 요약 <span class="badge">OVERVIEW</span></div>', unsafe_allow_html=True)

c1,c2,c3,c4 = st.columns(4)
if sel_month == '전체':
    c1.metric("총 매출",     f"₩{df_kpi['매출액'].sum():,}")
    c2.metric("평균 ROAS",   f"{df_kpi['ROAS'].mean():.0f}%")
    c3.metric("평균 클릭률", f"{df_kpi['클릭률'].mean():.1f}%")
    c4.metric("평균 전환율", f"{df_kpi['전환율'].mean():.1f}%")
else:
    idx  = df_kpi[df_kpi['비교기간']==sel_month].index[0]
    curr = df_kpi.iloc[idx]
    if idx > 0:
        prev = df_kpi.iloc[idx-1]
        md = f"{((curr['매출액']/prev['매출액'])-1)*100:+.1f}%"
        rd = f"{curr['ROAS']-prev['ROAS']:+}%p"
        cd = f"{curr['클릭률']-prev['클릭률']:+.1f}%p"
        vd = f"{curr['전환율']-prev['전환율']:+.1f}%p"
    else:
        md=rd=cd=vd=None
    c1.metric("월 매출액", f"₩{curr['매출액']:,}", delta=md)
    c2.metric("ROAS",      f"{curr['ROAS']}%",     delta=rd)
    c3.metric("클릭률",    f"{curr['클릭률']}%",   delta=cd)
    c4.metric("전환율",    f"{curr['전환율']}%",   delta=vd)

col1, col2 = st.columns([1.1,1])
with col1:
    # 이중축: 매출(Bar) + ROAS(Line) → 규모·효율 동시 파악
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=df_kpi['비교기간'], y=df_kpi['매출액'], name='매출액',
        marker_color=PALE[0], marker_line_color=PALETTE[0], marker_line_width=2,
        text=[f"₩{v/1e6:.0f}M" for v in df_kpi['매출액']],
        textposition='outside', textfont=dict(size=10, color=PALETTE[0])
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df_kpi['비교기간'], y=df_kpi['ROAS'], name='ROAS',
        mode='lines+markers', line=dict(color=PALETTE[3], width=3),
        marker=dict(size=9, color=PALETTE[3], line=dict(color='white',width=2))
    ), secondary_y=True)
    apply(fig, "월별 매출액 & ROAS (이중축)")
    fig.update_yaxes(title_text="매출액 (원)", secondary_y=False, tickformat=',')
    fig.update_yaxes(title_text="ROAS (%)", secondary_y=True, ticksuffix='%')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Area Multi-line: 3개 효율지표 시계열 밀도 변화 강조
    fig2 = go.Figure()
    for label, color in zip(['클릭률','전환율','신규비중'], PALETTE[:3]):
        r,g,b = int(color[1:3],16), int(color[3:5],16), int(color[5:7],16)
        fig2.add_trace(go.Scatter(
            x=df_kpi['비교기간'], y=df_kpi[label], name=label,
            mode='lines+markers',
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color=color, line=dict(color='white',width=2)),
            fill='tozeroy', fillcolor=f"rgba({r},{g},{b},0.07)"
        ))
    apply(fig2, "주요 효율 지표 추이")
    fig2.update_yaxes(ticksuffix='%')
    st.plotly_chart(fig2, use_container_width=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
#  [2] 신규 가입 고객 분석
#  차트: Stacked Bar (전환/미전환 구성) | Line + 평균선 (전환율 트렌드)
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">👤 신규 가입 고객 분석 <span class="badge">ACQUISITION</span></div>', unsafe_allow_html=True)

ds = df_signup if sel_month=='전체' else df_signup[df_signup['월']==sel_month]
sm1,sm2,sm3,sm4 = st.columns(4)
total_sig = ds['신규가입수'].sum()
total_con = ds['당월전환수'].sum()
sm1.metric("총 신규 가입",  f"{total_sig:,}명")
sm2.metric("당월 전환",     f"{total_con:,}명")
sm3.metric("당월 미전환",   f"{ds['당월미전환수'].sum():,}명")
sm4.metric("평균 전환율",   f"{total_con/total_sig*100:.1f}%")

col_a, col_b = st.columns([1.3,1])
with col_a:
    # Stacked Bar: 전환/미전환 구성 비율 + 총 가입수 볼륨 동시 파악
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=df_signup['월'], y=df_signup['당월전환수'], name='당월 전환',
        marker_color=PALETTE[1],
        text=df_signup['당월전환수'].apply(lambda x:f"{x:,}"),
        textposition='inside', textfont=dict(color='white', size=11)
    ))
    fig3.add_trace(go.Bar(
        x=df_signup['월'], y=df_signup['당월미전환수'], name='당월 미전환',
        marker_color=PALE[3],
        text=df_signup['당월미전환수'].apply(lambda x:f"{x:,}"),
        textposition='inside', textfont=dict(color=PALETTE[3], size=11)
    ))
    apply(fig3, "신규 가입 고객 당월 전환 현황")
    fig3.update_layout(barmode='stack')
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    # Line + 평균 기준선: 전환율 추세 + 목표 달성 여부 시각화
    avg_c = df_signup['전환율(%)'].mean()
    fig4 = go.Figure()
    fig4.add_hline(y=avg_c, line_dash='dot', line_color='#CBD5E0', line_width=1.5,
                   annotation_text=f"평균 {avg_c:.1f}%",
                   annotation_position='bottom right',
                   annotation_font=dict(color='#9CA3AF', size=11))
    fig4.add_trace(go.Scatter(
        x=df_signup['월'], y=df_signup['전환율(%)'],
        mode='lines+markers+text',
        line=dict(color=PALETTE[0], width=3),
        marker=dict(size=11, color=PALETTE[0], line=dict(color='white',width=2.5)),
        text=[f"{v}%" for v in df_signup['전환율(%)']],
        textposition='top center', textfont=dict(size=11, color=PALETTE[0], weight=700)
    ))
    apply(fig4, "월별 신규 고객 전환율")
    fig4.update_yaxes(ticksuffix='%', range=[0, df_signup['전환율(%)'].max()*1.35])
    st.plotly_chart(fig4, use_container_width=True)

with st.expander("📋 신규 고객 상세 데이터"):
    t = df_signup.copy()
    for c in ['신규가입수','당월전환수','당월미전환수']:
        t[c] = t[c].apply(lambda x: f"{x:,}명")
    t['전환율(%)'] = t['전환율(%)'].apply(lambda x: f"{x}%")
    st.dataframe(t, use_container_width=True, hide_index=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
#  [3] 일별 방문·구매 현황
#  차트: Bar(방문수, 볼륨) + Line(구매수, 트렌드) 이중축 콤보
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📅 일별 방문 & 구매 현황 <span class="badge">DAILY TRAFFIC</span></div>', unsafe_allow_html=True)

df_d = df_daily[df_daily['월']==sel_daily_m]
dm1,dm2,dm3,dm4 = st.columns(4)
dm1.metric("총 방문수",    f"{df_d['방문수'].sum():,}명")
dm2.metric("총 구매수",    f"{df_d['구매수'].sum():,}명")
dm3.metric("일평균 방문",  f"{df_d['방문수'].mean():.0f}명")
dm4.metric("평균 구매율",  f"{df_d['구매율(%)'].mean():.1f}%")

# Bar(방문볼륨) + Line(구매추이): 트래픽 규모와 전환 흐름 동시 파악 최적
fig5 = make_subplots(specs=[[{"secondary_y": True}]])
fig5.add_trace(go.Bar(
    x=df_d['날짜'], y=df_d['방문수'], name='방문수',
    marker_color=PALE[0], marker_line_color=PALETTE[0], marker_line_width=0.8,
), secondary_y=False)
fig5.add_trace(go.Scatter(
    x=df_d['날짜'], y=df_d['구매수'], name='구매수',
    mode='lines+markers', line=dict(color=PALETTE[1], width=2.5),
    marker=dict(size=5, color=PALETTE[1])
), secondary_y=True)
apply(fig5, f"{sel_daily_m} 일별 방문수 & 구매수 (이중축)")
fig5.update_yaxes(title_text="방문수", secondary_y=False, tickformat=',')
fig5.update_yaxes(title_text="구매수", secondary_y=True, tickformat=',')
fig5.update_layout(hovermode='x unified')
st.plotly_chart(fig5, use_container_width=True)

with st.expander("📋 일별 상세 데이터"):
    td = df_d[['날짜','방문수','구매수','구매율(%)']].copy()
    td['날짜'] = td['날짜'].dt.strftime('%m월 %d일')
    td['방문수'] = td['방문수'].apply(lambda x: f"{x:,}")
    td['구매수'] = td['구매수'].apply(lambda x: f"{x:,}")
    td['구매율(%)'] = td['구매율(%)'].apply(lambda x: f"{x}%")
    st.dataframe(td, use_container_width=True, hide_index=True)

st.divider()


# ════════════════════════════════════════════════════════════════════
#  [4] 캠페인별 성과
#  차트: Line(ROAS 시계열) | Grouped Bar(매출·광고비) | Grouped Bar(클릭·전환율) | Bubble(효율 포지셔닝)
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📣 캠페인별 성과 분석 <span class="badge">CAMPAIGN</span></div>', unsafe_allow_html=True)

df_c = df_camp[df_camp['캠페인'].isin(sel_camp)]
if sel_month != '전체':
    df_c = df_c[df_c['월']==sel_month]

tabs = st.tabs(["📈 ROAS 추이","💰 매출·광고비","📊 클릭·전환율","⚡ 효율 버블","📋 상세"])

with tabs[0]:
    # Multi-line: 캠페인간 ROAS 흐름 비교, 시계열 추세 명확
    fig_r = go.Figure()
    for i, camp in enumerate(sel_camp):
        d = df_camp[df_camp['캠페인']==camp]
        fig_r.add_trace(go.Scatter(
            x=d['월'], y=d['ROAS(%)'], name=camp,
            mode='lines+markers+text',
            line=dict(color=PALETTE[i%len(PALETTE)], width=2.5),
            marker=dict(size=9, color=PALETTE[i%len(PALETTE)], line=dict(color='white',width=2)),
            text=[f"{v:,}%" for v in d['ROAS(%)']],
            textposition='top center', textfont=dict(size=10)
        ))
    apply(fig_r, "캠페인별 월별 ROAS 추이")
    fig_r.add_hline(y=1000, line_dash='dash', line_color='#D1D5DB',
                    annotation_text='기준선 1,000%', annotation_position='bottom right',
                    annotation_font=dict(color='#9CA3AF', size=11))
    fig_r.update_yaxes(ticksuffix='%')
    st.plotly_chart(fig_r, use_container_width=True)

with tabs[1]:
    col_rev, col_cost = st.columns(2)
    with col_rev:
        # Grouped Bar: 캠페인간 절대 매출 규모 직접 비교
        fig_rev = px.bar(df_c, x='월', y='매출', color='캠페인', barmode='group',
                         color_discrete_sequence=PALETTE)
        apply(fig_rev, "캠페인별 월별 매출")
        fig_rev.update_yaxes(tickformat=',')
        st.plotly_chart(fig_rev, use_container_width=True)
    with col_cost:
        fig_cost = px.bar(df_c, x='월', y='광고비', color='캠페인', barmode='group',
                          color_discrete_sequence=PALETTE)
        apply(fig_cost, "캠페인별 월별 광고비")
        fig_cost.update_yaxes(tickformat=',')
        fig_cost.update_layout(showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)

with tabs[2]:
    col_clk, col_cvr = st.columns(2)
    with col_clk:
        fig_clk = px.bar(df_c, x='월', y='클릭률(%)', color='캠페인', barmode='group',
                         color_discrete_sequence=PALETTE)
        apply(fig_clk, "캠페인별 클릭률")
        fig_clk.update_yaxes(ticksuffix='%')
        st.plotly_chart(fig_clk, use_container_width=True)
    with col_cvr:
        fig_cvr = px.bar(df_c, x='월', y='전환율(%)', color='캠페인', barmode='group',
                         color_discrete_sequence=PALETTE)
        apply(fig_cvr, "캠페인별 전환율")
        fig_cvr.update_yaxes(ticksuffix='%')
        fig_cvr.update_layout(showlegend=False)
        st.plotly_chart(fig_cvr, use_container_width=True)

with tabs[3]:
    # Bubble: X=클릭률, Y=전환율, 크기=매출 → 캠페인 효율 포지셔닝 한눈에 파악
    fig_b = px.scatter(
        df_c, x='클릭률(%)', y='전환율(%)', size='매출', color='캠페인',
        hover_data={'월':True,'발송수':True,'주문건수':True,'ROAS(%)':True,'매출':':,'},
        color_discrete_sequence=PALETTE, size_max=55, opacity=0.82,
        text='캠페인'
    )
    fig_b.update_traces(textposition='top center', textfont=dict(size=10))
    apply(fig_b, "캠페인 효율 포지셔닝 버블 (버블 크기 = 매출)")
    fig_b.update_xaxes(ticksuffix='%')
    fig_b.update_yaxes(ticksuffix='%')
    st.plotly_chart(fig_b, use_container_width=True)

with tabs[4]:
    disp_c = df_c.copy()
    disp_c['매출']     = disp_c['매출'].apply(lambda x: f"₩{x:,}")
    disp_c['광고비']   = disp_c['광고비'].apply(lambda x: f"₩{x:,}")
    disp_c['발송수']   = disp_c['발송수'].apply(lambda x: f"{x:,}")
    disp_c['클릭수']   = disp_c['클릭수'].apply(lambda x: f"{x:,}")
    disp_c['주문건수'] = disp_c['주문건수'].apply(lambda x: f"{x:,}")
    disp_c['클릭률(%)']  = disp_c['클릭률(%)'].apply(lambda x: f"{x}%")
    disp_c['전환율(%)']  = disp_c['전환율(%)'].apply(lambda x: f"{x}%")
    disp_c['ROAS(%)']    = disp_c['ROAS(%)'].apply(lambda x: f"{x:,}%")
    st.dataframe(disp_c, use_container_width=True, hide_index=True)

if not df_c.empty:
    st.markdown("#### 📌 선택 기간·캠페인 합계")
    k1,k2,k3,k4,k5 = st.columns(5)
    k1.metric("총 발송",   f"{df_c['발송수'].sum():,}건")
    k2.metric("총 클릭",   f"{df_c['클릭수'].sum():,}건")
    k3.metric("총 주문",   f"{df_c['주문건수'].sum():,}건")
    k4.metric("총 매출",   f"₩{df_c['매출'].sum():,}")
    k5.metric("평균 ROAS", f"{df_c['ROAS(%)'].mean():.0f}%")

st.divider()


# ════════════════════════════════════════════════════════════════════
#  [5] 회원 구매빈도 × 최근 방문 Recency 분석
#  차트: 100% Stacked Bar (구성 비율) | Grouped Bar (절대 인원) | Heatmap (교차 분석)
# ════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 회원 구매빈도 × 최근 방문 분석 <span class="badge">RECENCY</span></div>', unsafe_allow_html=True)

active_30   = df_rec[(df_rec['세그먼트']=='전체회원')&(df_rec['기간']=='0~30일')]['회원수'].values[0]
inactive_1y = df_rec[(df_rec['세그먼트']=='전체회원')&(df_rec['기간']=='1년 이상')]['회원수'].values[0]
total_mem   = SEG_TOTAL['전체회원']

rm1,rm2,rm3,rm4 = st.columns(4)
rm1.metric("전체 회원",        f"{total_mem:,}명")
rm2.metric("30일 내 활성",     f"{active_30:,}명",  delta=f"{active_30/total_mem*100:.1f}%")
rm3.metric("1년+ 장기 미접속", f"{inactive_1y:,}명", delta=f"-{inactive_1y/total_mem*100:.1f}%", delta_color="inverse")
rm4.metric("분석 세그먼트",    "5개 그룹")

tab_r1, tab_r2, tab_r3 = st.tabs(["📊 구성 비율 비교 (100% 누적 Bar)","📦 절대 인원 비교 (Grouped Bar)","🗺️ 교차 분석 히트맵"])

with tab_r1:
    # 100% Stacked Bar: 각 세그먼트 내 Recency 구성 비율 비교 → 위험군 비중 즉각 파악
    pivot = df_rec.pivot(index='세그먼트', columns='기간', values='비율(%)').reindex(SEGS)[PERIODS]
    fig_r1 = go.Figure()
    for i, period in enumerate(PERIODS):
        fig_r1.add_trace(go.Bar(
            name=period, x=pivot.index, y=pivot[period],
            marker_color=PERIOD_COLOR[i],
            text=[f"{v:.0f}%" for v in pivot[period]],
            textposition='inside',
            textfont=dict(size=11, color='white' if i < 3 else '#374151'),
        ))
    apply(fig_r1, "세그먼트별 최근 방문 기간 구성 비율")
    fig_r1.update_layout(
        barmode='relative', yaxis_ticksuffix='%',
        legend=dict(traceorder='normal', orientation='h', y=-0.14, x=0.5, xanchor='center')
    )
    st.plotly_chart(fig_r1, use_container_width=True)
    st.caption("💡 파란색(0~30일)이 짧고 회색(1년+)이 길수록 이탈 위험이 높은 세그먼트입니다. 재활성화 캠페인 우선순위 판단에 활용하세요.")

with tab_r2:
    # Grouped Bar: 세그먼트별 기간별 실제 인원 규모 비교
    fig_r2 = go.Figure()
    for i, period in enumerate(PERIODS):
        dd = df_rec[df_rec['기간']==period].set_index('세그먼트').reindex(SEGS)
        fig_r2.add_trace(go.Bar(
            name=period, x=SEGS, y=dd['회원수'],
            marker_color=PERIOD_COLOR[i],
            text=dd['회원수'].apply(lambda x: f"{int(x):,}" if pd.notna(x) else ""),
            textposition='outside', textfont=dict(size=9),
        ))
    apply(fig_r2, "세그먼트별 최근 방문 기간별 절대 인원")
    fig_r2.update_layout(
        barmode='group', yaxis_tickformat=',',
        legend=dict(orientation='h', y=-0.14, x=0.5, xanchor='center')
    )
    st.plotly_chart(fig_r2, use_container_width=True)

with tab_r3:
    # Heatmap: 구매빈도 × 방문기간 교차 → 고위험/고가치 셀 즉시 식별
    pivot_h = df_rec.pivot(index='세그먼트', columns='기간', values='회원수').reindex(SEGS)[PERIODS]
    text_vals = [
        [f"{int(pivot_h.iloc[r,c]):,}명\n({pivot_h.iloc[r,c]/SEG_TOTAL[SEGS[r]]*100:.0f}%)"
         for c in range(len(PERIODS))]
        for r in range(len(SEGS))
    ]
    fig_hm = go.Figure(go.Heatmap(
        z=pivot_h.values,
        x=PERIODS, y=SEGS,
        colorscale=[[0,'#EFF6FF'],[0.3,'#93C5FD'],[0.65,'#2563EB'],[1,'#1E3A8A']],
        text=text_vals,
        texttemplate="%{text}",
        textfont=dict(size=11),
        showscale=True,
        colorbar=dict(title='회원수', tickformat=',')
    ))
    apply(fig_hm, "구매빈도 × 최근 방문 기간 히트맵 (숫자 = 인원 / 세그먼트 내 비율)")
    fig_hm.update_layout(margin=dict(t=50, b=60, l=160, r=20))
    fig_hm.update_xaxes(side='bottom', title='최근 방문 기간', showgrid=False)
    fig_hm.update_yaxes(title='구매 빈도 세그먼트', showgrid=False)
    st.plotly_chart(fig_hm, use_container_width=True)
    st.caption("💡 색이 진할수록 인원이 많습니다. 우하단(5회+/1년+) 진한 셀은 고가치 이탈 위험군으로 재활성화 우선 타깃입니다.")

with st.expander("📋 세그먼트별 Recency 상세 데이터"):
    disp_r = df_rec.copy()
    disp_r['회원수']   = disp_r['회원수'].apply(lambda x: f"{x:,}명")
    disp_r['비율(%)'] = disp_r['비율(%)'].apply(lambda x: f"{x}%")
    st.dataframe(disp_r, use_container_width=True, hide_index=True)