import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(page_title="CRM 마스터 보안 대시보드", layout="wide")

# --- 보안 로그인 로직 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.title("🔒 보안 인증")
        password = st.text_input("대시보드 접속 비밀번호를 입력하세요", type="password")
        if st.button("접속하기"):
            if password == "1234":  # <--- 여기서 비밀번호를 수정하세요!
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("비밀번호가 틀렸습니다.")
        return False
    return True

if check_password():
    # --- 여기서부터 기존 대시보드 코드 ---
    
    # 2. 데이터 세팅
    df = pd.DataFrame({
        '비교기간': ['25년 09월', '25년 10월', '25년 11월', '25년 12월', '26년 01월'],
        '매출액': [40437647, 88057694, 135804965, 92780255, 70282509],
        'ROAS': [797, 2090, 5329, 1744, 1409],
        '클릭률': [0.8, 4.7, 5.9, 4.3, 3.4],
        '전환율': [12.9, 13.0, 18.0, 12.6, 11.7],
        '신규비중': [34.5, 43.3, 34.5, 43.3, 31.0]
    })

    # 3. 사이드바 필터
    st.sidebar.header("📅 기간 선택")
    sel = st.sidebar.selectbox("조회 월", ['전체'] + list(df['비교기간']))
    
    st.title(f"🚀 CRM 퍼포먼스 분석 ({sel})")

    # 4. KPI 지표 및 전월 대비 계산
    c1, c2, c3, c4 = st.columns(4)

    if sel == '전체':
        c1.metric("총 매출", f"₩{df['매출액'].sum():,}")
        c2.metric("평균 ROAS", f"{df['ROAS'].mean():.0f}%")
        c3.metric("평균 클릭률", f"{df['클릭률'].mean():.1f}%")
        c4.metric("평균 전환율", f"{df['전환율'].mean():.1f}%")
    else:
        idx = df[df['비교기간'] == sel].index[0]
        curr = df.iloc[idx]
        
        if idx > 0:
            prev = df.iloc[idx-1]
            m_delta = f"{((curr['매출액']/prev['매출액'])-1)*100:.1f}%"
            r_delta = f"{curr['ROAS'] - prev['ROAS']}%p"
            c_delta = f"{curr['클릭률'] - prev['클릭률']:.1f}%p"
            v_delta = f"{curr['전환율'] - prev['전환율']:.1f}%p"
        else:
            m_delta = r_delta = c_delta = v_delta = None

        c1.metric("월 매출액", f"₩{curr['매출액']:,}", delta=m_delta)
        c2.metric("ROAS", f"{curr['ROAS']}%", delta=r_delta)
        c3.metric("클릭률", f"{curr['클릭률']}%", delta=c_delta)
        c4.metric("전환율", f"{curr['전환율']}%", delta=v_delta)

    st.divider()

    # 5. 차트 시각화
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 월별 매출 추이")
        f1 = px.bar(df, x='비교기간', y='매출액', text_auto=',.0f')
        st.plotly_chart(f1, use_container_width=True)
    with col2:
        st.subheader("🎯 주요 효율 지표 (%)")
        f2 = px.line(df, x='비교기간', y=['클릭률', '전환율', '신규비중'], markers=True)
        f2.update_layout(yaxis_ticksuffix="%")
        st.plotly_chart(f2, use_container_width=True)

    # 6. 데이터 상세 테이블
    st.subheader("📋 전체 성과 데이터 시트")
    t_df = df.copy()
    t_df['매출액'] = t_df['매출액'].apply(lambda x: f"₩{x:,}")
    for c in ['ROAS', '클릭률', '전환율', '신규비중']:
        t_df[c] = t_df[c].apply(lambda x: f"{x}%")
    st.table(t_df)

    # 로그아웃 버튼 (사이드바 하단)
    if st.sidebar.button("로그아웃"):
        del st.session_state["password_correct"]
        st.rerun()