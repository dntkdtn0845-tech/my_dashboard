import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 1. 페이지 설정
st.set_page_config(page_title="CRM 마스터 보안 대시보드", layout="wide")

# 커스텀 CSS
st.markdown("""
<style>
    .main { background-color: #0f1117; }
    .stMetric { background: linear-gradient(135deg, #1a1d2e, #252840); border-radius: 12px; padding: 16px; border: 1px solid #2e3250; }
    .stMetric label { color: #8b9ecb !important; font-size: 0.8rem !important; letter-spacing: 0.08em; text-transform: uppercase; }
    .stMetric [data-testid="stMetricValue"] { color: #e2e8f0 !important; font-size: 1.6rem !important; font-weight: 700; }
    .stMetric [data-testid="stMetricDelta"] { font-size: 0.85rem !important; }
    div[data-testid="stSidebar"] { background: #0d1018; border-right: 1px solid #1e2235; }
    .section-header { 
        background: linear-gradient(90deg, #1e2235, transparent);
        border-left: 3px solid #4f7cff;
        padding: 12px 20px;
        margin: 20px 0 16px 0;
        border-radius: 0 8px 8px 0;
        color: #c8d4f0;
        font-weight: 600;
        font-size: 1.05rem;
        letter-spacing: 0.04em;
    }
    .kpi-badge {
        display: inline-block;
        background: #1a2740;
        border: 1px solid #2a4070;
        color: #60a5fa;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        margin: 4px 4px;
        letter-spacing: 0.05em;
    }
    h1, h2, h3 { color: #e2e8f0 !important; }
    .stDataFrame { background: #1a1d2e; }
    .stTabs [data-baseweb="tab-list"] { background: #1a1d2e; border-radius: 10px; padding: 4px; }
    .stTabs [data-baseweb="tab"] { color: #8b9ecb; }
    .stTabs [aria-selected="true"] { background: #252840 !important; color: #e2e8f0 !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ─── 보안 로그인 ───────────────────────────────────────────────────────────────
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("""
        <div style='text-align:center; padding: 80px 0 30px 0;'>
            <div style='font-size:3rem; margin-bottom:10px;'>🔒</div>
            <h2 style='color:#c8d4f0; font-weight:700; letter-spacing:0.05em;'>CRM 마스터 대시보드</h2>
            <p style='color:#6b7ba0; font-size:0.9rem;'>접속 권한이 있는 사용자만 이용 가능합니다</p>
        </div>
        """, unsafe_allow_html=True)
        col_l, col_m, col_r = st.columns([1, 1.2, 1])
        with col_m:
            password = st.text_input("비밀번호", type="password", placeholder="비밀번호를 입력하세요")
            if st.button("접속하기", use_container_width=True, type="primary"):
                if password == "1234":
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        return False
    return True

if not check_password():
    st.stop()

# ─── 더미 데이터 ───────────────────────────────────────────────────────────────

# (A) 기존 월별 KPI
df_kpi = pd.DataFrame({
    '비교기간': ['25년 09월', '25년 10월', '25년 11월', '25년 12월', '26년 01월'],
    '매출액':   [40437647, 88057694, 135804965, 92780255, 70282509],
    'ROAS':     [797, 2090, 5329, 1744, 1409],
    '클릭률':   [0.8, 4.7, 5.9, 4.3, 3.4],
    '전환율':   [12.9, 13.0, 18.0, 12.6, 11.7],
    '신규비중': [34.5, 43.3, 34.5, 43.3, 31.0],
})

# (B) 신규 가입 고객 데이터
df_signup = pd.DataFrame({
    '월':           ['25년 09월', '25년 10월', '25년 11월', '25년 12월', '26년 01월'],
    '신규가입수':   [4820, 6540, 9200, 7310, 5980],
    '당월전환수':   [1900, 2980, 5060, 3200, 2390],
    '당월미전환수': [2920, 3560, 4140, 4110, 3590],
})
df_signup['전환율(%)'] = (df_signup['당월전환수'] / df_signup['신규가입수'] * 100).round(1)

# (C) 일별 방문수 / 구매수 (26년 01월 & 02월)
np.random.seed(42)
dates_jan = pd.date_range('2026-01-01', '2026-01-31')
dates_feb = pd.date_range('2026-02-01', '2026-02-28')

def make_daily(dates, visit_base, buy_rate):
    n = len(dates)
    visits = (visit_base + np.random.randint(-30, 50, n) + np.arange(n) * 1.5).astype(int)
    buys   = (visits * buy_rate + np.random.randint(-5, 10, n)).astype(int)
    return pd.DataFrame({'날짜': dates, '방문수': visits, '구매수': buys})

df_daily = pd.concat([
    make_daily(dates_jan, 180, 0.31).assign(월='26년 01월'),
    make_daily(dates_feb, 210, 0.34).assign(월='26년 02월'),
], ignore_index=True)
df_daily['구매율(%)'] = (df_daily['구매수'] / df_daily['방문수'] * 100).round(1)

# (D) 캠페인별 성과
campaigns = {
    '신규회원 1일차': {
        '발송수': [12000,15500,19800,14200,11300],
        '클릭수': [1320, 1980, 3168, 1988, 1356],
        '주문건수':[396,  693, 1267,  796,  475],
        '매출':   [39600000,76230000,139370000,87560000,52250000],
        '광고비': [480000,  620000,  792000,  568000,  452000],
    },
    '구매고객 3일차': {
        '발송수': [3800, 5200, 7800, 5600, 4200],
        '클릭수': [760, 1092, 1950, 1176, 882],
        '주문건수':[228,  382,  780,  470,  309],
        '매출':   [22800000,42020000,85800000,51700000,33990000],
        '광고비': [190000,  260000,  390000,  280000,  210000],
    },
    '구매고객 7일차': {
        '발송수': [2600, 3800, 5900, 4100, 3100],
        '클릭수': [442,  722, 1298,  861,  620],
        '주문건수':[133,  253,  519,  344,  217],
        '매출':   [13300000,27830000,57090000,37840000,23870000],
        '광고비': [130000,  190000,  295000,  205000,  155000],
    },
    '구매고객 14일차': {
        '발송수': [2100, 3100, 4800, 3300, 2500],
        '클릭수': [315,  527,  912,  594,  425],
        '주문건수':[95,   185,  365,  238,  149],
        '매출':   [9500000,20350000,40150000,26180000,16390000],
        '광고비': [105000,  155000,  240000,  165000,  125000],
    },
}

months = ['25년 09월', '25년 10월', '25년 11월', '25년 12월', '26년 01월']
rows = []
for camp, vals in campaigns.items():
    for i, m in enumerate(months):
        send = vals['발송수'][i]; click = vals['클릭수'][i]
        order = vals['주문건수'][i]; rev = vals['매출'][i]; cost = vals['광고비'][i]
        rows.append({
            '캠페인': camp, '월': m,
            '발송수': send, '클릭수': click,
            '클릭률(%)': round(click/send*100, 1),
            '주문건수': order,
            '전환율(%)': round(order/click*100, 1),
            '매출': rev, '광고비': cost,
            'ROAS(%)': round(rev/cost*100),
        })
df_camp = pd.DataFrame(rows)

# ─── 사이드바 ──────────────────────────────────────────────────────────────────
st.sidebar.markdown("## 🎛️ 필터 설정")
st.sidebar.markdown("---")
sel_month = st.sidebar.selectbox("📅 조회 월", ['전체'] + months)
sel_camp  = st.sidebar.multiselect("📣 캠페인 선택", list(campaigns.keys()), default=list(campaigns.keys()))
st.sidebar.markdown("---")
if st.sidebar.button("🚪 로그아웃", use_container_width=True):
    del st.session_state["password_correct"]
    st.rerun()

# ─── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='display:flex; align-items:center; gap:14px; padding: 10px 0 20px 0;'>
    <span style='font-size:2.2rem;'>🚀</span>
    <div>
        <h1 style='margin:0; font-size:1.7rem; color:#e2e8f0; font-weight:800; letter-spacing:0.03em;'>
            CRM 퍼포먼스 분석 대시보드
        </h1>
        <p style='margin:0; color:#6b7ba0; font-size:0.85rem;'>조회 기간: {sel_month} &nbsp;|&nbsp; 실시간 마케팅 성과 종합</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── [1] 기존 KPI 지표 ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 전체 KPI 요약</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

if sel_month == '전체':
    c1.metric("총 매출", f"₩{df_kpi['매출액'].sum():,}")
    c2.metric("평균 ROAS", f"{df_kpi['ROAS'].mean():.0f}%")
    c3.metric("평균 클릭률", f"{df_kpi['클릭률'].mean():.1f}%")
    c4.metric("평균 전환율", f"{df_kpi['전환율'].mean():.1f}%")
else:
    idx  = df_kpi[df_kpi['비교기간'] == sel_month].index[0]
    curr = df_kpi.iloc[idx]
    if idx > 0:
        prev = df_kpi.iloc[idx-1]
        m_d = f"{((curr['매출액']/prev['매출액'])-1)*100:.1f}%"
        r_d = f"{curr['ROAS']-prev['ROAS']}%p"
        c_d = f"{curr['클릭률']-prev['클릭률']:.1f}%p"
        v_d = f"{curr['전환율']-prev['전환율']:.1f}%p"
    else:
        m_d = r_d = c_d = v_d = None
    c1.metric("월 매출액",  f"₩{curr['매출액']:,}", delta=m_d)
    c2.metric("ROAS",       f"{curr['ROAS']}%",     delta=r_d)
    c3.metric("클릭률",     f"{curr['클릭률']}%",   delta=c_d)
    c4.metric("전환율",     f"{curr['전환율']}%",   delta=v_d)

col1, col2 = st.columns(2)
with col1:
    fig = px.bar(df_kpi, x='비교기간', y='매출액', text_auto=',.0f',
                 color_discrete_sequence=['#4f7cff'],
                 template='plotly_dark')
    fig.update_traces(textfont_size=11, marker_line_color='#6e99ff', marker_line_width=1)
    fig.update_layout(title='월별 매출 추이', plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                      font_color='#c8d4f0', title_font_size=14, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig2 = px.line(df_kpi, x='비교기간', y=['클릭률','전환율','신규비중'], markers=True,
                   color_discrete_sequence=['#4f7cff','#34d399','#f59e0b'],
                   template='plotly_dark')
    fig2.update_layout(title='주요 효율 지표 (%)', plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                       font_color='#c8d4f0', title_font_size=14, yaxis_ticksuffix='%',
                       legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ─── [2] 신규 가입 고객 분석 ──────────────────────────────────────────────────
st.markdown('<div class="section-header">👤 신규 가입 고객 분석</div>', unsafe_allow_html=True)

disp_signup = df_signup if sel_month == '전체' else df_signup[df_signup['월'] == sel_month]

m1, m2, m3, m4 = st.columns(4)
m1.metric("총 신규 가입",   f"{disp_signup['신규가입수'].sum():,}명")
m2.metric("당월 전환 고객", f"{disp_signup['당월전환수'].sum():,}명",
          delta=f"전환율 {disp_signup['당월전환수'].sum()/disp_signup['신규가입수'].sum()*100:.1f}%")
m3.metric("당월 미전환",    f"{disp_signup['당월미전환수'].sum():,}명")
m4.metric("평균 전환율",    f"{disp_signup['전환율(%)'].mean():.1f}%")

col_a, col_b = st.columns([1.4, 1])
with col_a:
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(name='당월 전환', x=df_signup['월'], y=df_signup['당월전환수'],
                          marker_color='#34d399', text=df_signup['당월전환수'], textposition='inside'))
    fig3.add_trace(go.Bar(name='당월 미전환', x=df_signup['월'], y=df_signup['당월미전환수'],
                          marker_color='#f87171', text=df_signup['당월미전환수'], textposition='inside'))
    fig3.update_layout(barmode='stack', title='신규 가입 고객 전환 현황',
                       plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                       font_color='#c8d4f0', title_font_size=14,
                       legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig3, use_container_width=True)

with col_b:
    fig4 = px.line(df_signup, x='월', y='전환율(%)', markers=True,
                   color_discrete_sequence=['#a78bfa'], template='plotly_dark')
    fig4.add_hline(y=df_signup['전환율(%)'].mean(), line_dash='dot', line_color='#fbbf24',
                   annotation_text=f"평균 {df_signup['전환율(%)'].mean():.1f}%", annotation_position='top left')
    fig4.update_layout(title='월별 신규 고객 전환율 추이',
                       plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                       font_color='#c8d4f0', title_font_size=14, yaxis_ticksuffix='%')
    st.plotly_chart(fig4, use_container_width=True)

# 테이블
t_su = df_signup.copy()
t_su['신규가입수']   = t_su['신규가입수'].apply(lambda x: f"{x:,}명")
t_su['당월전환수']   = t_su['당월전환수'].apply(lambda x: f"{x:,}명")
t_su['당월미전환수'] = t_su['당월미전환수'].apply(lambda x: f"{x:,}명")
t_su['전환율(%)']    = t_su['전환율(%)'].apply(lambda x: f"{x}%")
t_su.columns = ['월', '신규가입', '당월전환', '당월미전환', '전환율']
st.dataframe(t_su, use_container_width=True, hide_index=True)

st.divider()

# ─── [3] 일별 방문·구매 현황 ──────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 일별 방문수 & 구매수</div>', unsafe_allow_html=True)

sel_daily_month = st.selectbox("조회 월 선택", df_daily['월'].unique().tolist(), key="daily_month")
df_d = df_daily[df_daily['월'] == sel_daily_month]

md1, md2, md3, md4 = st.columns(4)
md1.metric("총 방문수",  f"{df_d['방문수'].sum():,}명")
md2.metric("총 구매수",  f"{df_d['구매수'].sum():,}명")
md3.metric("일평균 방문", f"{df_d['방문수'].mean():.0f}명")
md4.metric("평균 구매율", f"{df_d['구매율(%)'].mean():.1f}%")

fig5 = make_subplots(specs=[[{"secondary_y": True}]])
fig5.add_trace(go.Bar(x=df_d['날짜'], y=df_d['방문수'], name='방문수',
                      marker_color='rgba(79,124,255,0.5)', marker_line_color='#4f7cff', marker_line_width=0.5),
               secondary_y=False)
fig5.add_trace(go.Scatter(x=df_d['날짜'], y=df_d['구매수'], name='구매수',
                           mode='lines+markers', line=dict(color='#34d399', width=2.5),
                           marker=dict(size=5)),
               secondary_y=True)
fig5.update_layout(title=f'{sel_daily_month} 일별 방문수 & 구매수',
                   plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                   font_color='#c8d4f0', title_font_size=14,
                   legend=dict(bgcolor='rgba(0,0,0,0)'), hovermode='x unified')
fig5.update_yaxes(title_text='방문수', secondary_y=False, gridcolor='#252840')
fig5.update_yaxes(title_text='구매수', secondary_y=True)
st.plotly_chart(fig5, use_container_width=True)

with st.expander("📋 일별 상세 데이터 보기"):
    disp_d = df_d[['날짜','방문수','구매수','구매율(%)']].copy()
    disp_d['날짜'] = disp_d['날짜'].dt.strftime('%Y-%m-%d')
    disp_d['방문수'] = disp_d['방문수'].apply(lambda x: f"{x:,}")
    disp_d['구매수'] = disp_d['구매수'].apply(lambda x: f"{x:,}")
    disp_d['구매율(%)'] = disp_d['구매율(%)'].apply(lambda x: f"{x}%")
    st.dataframe(disp_d, use_container_width=True, hide_index=True)

st.divider()

# ─── [4] 캠페인별 성과 ────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📣 캠페인별 월별 성과</div>', unsafe_allow_html=True)

df_c = df_camp[df_camp['캠페인'].isin(sel_camp)]
if sel_month != '전체':
    df_c = df_c[df_c['월'] == sel_month]

tabs = st.tabs(["📈 ROAS 비교", "💰 매출·광고비", "📊 클릭·전환율", "📋 상세 테이블"])

with tabs[0]:
    fig_r = px.line(df_c, x='월', y='ROAS(%)', color='캠페인', markers=True,
                    color_discrete_sequence=['#4f7cff','#34d399','#f59e0b','#f87171'],
                    template='plotly_dark')
    fig_r.add_hline(y=1000, line_dash='dot', line_color='#6b7ba0',
                    annotation_text='ROAS 1000%', annotation_position='top left')
    fig_r.update_layout(title='캠페인별 월별 ROAS 추이',
                        plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                        font_color='#c8d4f0', yaxis_ticksuffix='%',
                        legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_r, use_container_width=True)

with tabs[1]:
    col_rev, col_cost = st.columns(2)
    with col_rev:
        fig_rev = px.bar(df_c, x='월', y='매출', color='캠페인', barmode='group',
                         color_discrete_sequence=['#4f7cff','#34d399','#f59e0b','#f87171'],
                         template='plotly_dark', text_auto=',.0f')
        fig_rev.update_layout(title='캠페인별 월별 매출',
                               plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                               font_color='#c8d4f0', showlegend=True,
                               legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_rev, use_container_width=True)
    with col_cost:
        fig_cost = px.bar(df_c, x='월', y='광고비', color='캠페인', barmode='group',
                          color_discrete_sequence=['#4f7cff','#34d399','#f59e0b','#f87171'],
                          template='plotly_dark', text_auto=',.0f')
        fig_cost.update_layout(title='캠페인별 월별 광고비',
                                plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                                font_color='#c8d4f0', showlegend=False)
        st.plotly_chart(fig_cost, use_container_width=True)

with tabs[2]:
    col_clk, col_cvr = st.columns(2)
    with col_clk:
        fig_clk = px.bar(df_c, x='월', y='클릭률(%)', color='캠페인', barmode='group',
                         color_discrete_sequence=['#4f7cff','#34d399','#f59e0b','#f87171'],
                         template='plotly_dark')
        fig_clk.update_layout(title='캠페인별 클릭률',
                               plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                               font_color='#c8d4f0', yaxis_ticksuffix='%',
                               legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_clk, use_container_width=True)
    with col_cvr:
        fig_cvr = px.bar(df_c, x='월', y='전환율(%)', color='캠페인', barmode='group',
                         color_discrete_sequence=['#4f7cff','#34d399','#f59e0b','#f87171'],
                         template='plotly_dark')
        fig_cvr.update_layout(title='캠페인별 전환율',
                               plot_bgcolor='#1a1d2e', paper_bgcolor='#1a1d2e',
                               font_color='#c8d4f0', yaxis_ticksuffix='%',
                               legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_cvr, use_container_width=True)

with tabs[3]:
    disp_c = df_c.copy()
    disp_c['매출']  = disp_c['매출'].apply(lambda x: f"₩{x:,}")
    disp_c['광고비'] = disp_c['광고비'].apply(lambda x: f"₩{x:,}")
    disp_c['발송수'] = disp_c['발송수'].apply(lambda x: f"{x:,}")
    disp_c['클릭수'] = disp_c['클릭수'].apply(lambda x: f"{x:,}")
    disp_c['주문건수'] = disp_c['주문건수'].apply(lambda x: f"{x:,}")
    disp_c['클릭률(%)']  = disp_c['클릭률(%)'].apply(lambda x: f"{x}%")
    disp_c['전환율(%)']  = disp_c['전환율(%)'].apply(lambda x: f"{x}%")
    disp_c['ROAS(%)']    = disp_c['ROAS(%)'].apply(lambda x: f"{x:,}%")
    st.dataframe(disp_c, use_container_width=True, hide_index=True)

# 캠페인 KPI 요약 카드
if not df_c.empty:
    st.markdown("#### 선택 기간 캠페인 합계")
    kc1, kc2, kc3, kc4, kc5 = st.columns(5)
    kc1.metric("총 발송",     f"{df_c['발송수'].sum():,}건")
    kc2.metric("총 클릭",     f"{df_c['클릭수'].sum():,}건")
    kc3.metric("총 주문",     f"{df_c['주문건수'].sum():,}건")
    kc4.metric("총 매출",     f"₩{df_c['매출'].sum():,}")
    kc5.metric("평균 ROAS",   f"{df_c['ROAS(%)'].mean():.0f}%")