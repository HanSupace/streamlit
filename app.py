import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

@st.cache_data
def load_data():
    df = pd.read_excel("자전거_분포_수정본.xlsx")
    return df

df = load_data()

st.title("서울시 공공자전거 대여소 분포 지도도")
st.caption("거치대수에 따라 막대 높이가 달라지는 3D 지도입니다. 보고싶은 자치구를 선택하십시오")


districts = sorted(df['자치구'].dropna().unique())
all_option = "전체"
options = [all_option] + districts
selected = st.sidebar.multiselect("자치구 선택", options=options, default=[all_option])

if all_option in selected:
    selected_districts = districts
else:
    selected_districts = selected

min_val = int(df['거치대수'].min())
max_val = int(df['거치대수'].max())
min_bike = st.sidebar.slider("거치대수 필터", min_value=min_val, max_value=max_val, value=min_val)

filtered_df = df[df['거치대수'] >= min_bike]
filtered_df = filtered_df[filtered_df['자치구'].isin(selected_districts)]


st.subheader("3D 대여소 분포 지도 (거치대수별 막대 높이)")
if not filtered_df.empty:
    map_data = filtered_df.rename(columns={'위도': 'latitude', '경도': 'longitude'}).copy()


    map_data['color'] = [ [255, 0, 0, 160] ] * len(map_data)


    map_data['elevation'] = map_data['거치대수'] * 10


    layer = pdk.Layer(
        "ColumnLayer",
        data=map_data,
        get_position='[longitude, latitude]',
        get_elevation='elevation',
        elevation_scale=1,
        radius=100,
        get_fill_color='color',
        pickable=True,
        auto_highlight=True
    )

    view_state = pdk.ViewState(
        latitude=map_data['latitude'].mean(),
        longitude=map_data['longitude'].mean(),
        zoom=12,
        pitch=45 
    )

    tooltip = {
        "html": "<b>{대여소명}</b><br>자치구: {자치구}<br>거치대수: {거치대수}대",
        "style": {"backgroundColor": "white", "color": "black"}
    }

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=view_state,
        layers=[layer],
        tooltip=tooltip
    ))
else:
    st.warning("조건에 맞는 대여소가 없습니다.")

st.subheader("자치구별 총 거치대수")
district_sum = (
    df[df['거치대수'] >= min_bike]
    .groupby('자치구')['거치대수']
    .sum()
    .sort_values(ascending=False)
)
st.bar_chart(district_sum)
