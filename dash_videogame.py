
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Set Streamlit page config
st.set_page_config(page_title="🎮 Video Game Sales Dashboard", layout="wide")
st.title("🎮 Video Game Sales Dashboard")
st.markdown("Explore trends in global video game sales by genre, platform, region, and more.")

# Load cleaned dataset
df = pd.read_csv("cleaned_vgsales.csv")

# Sidebar filters
st.sidebar.header("🎛️ Filters")
st.sidebar.markdown("### 🧮 Advanced Feature: Cascading Filters")
years = sorted(df["Year"].dropna().unique())
year_range = st.sidebar.slider("Select Year Range", int(min(years)), int(max(years)), (1980, 2020))

platforms = sorted(df["Platform"].unique())
selected_platform = st.sidebar.selectbox("Platform", platforms)

genres = df[df["Platform"] == selected_platform]["Genre"].unique()
selected_genre = st.sidebar.selectbox("Genre", sorted(genres))

# Filtered data
filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1]) &
    (df["Platform"] == selected_platform) &
    (df["Genre"] == selected_genre)
]

# --- Summary Metrics ---
st.markdown("## 📊 Summary Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Global Sales (M)", f"{filtered_df['Global_Sales'].sum():.2f}")
col2.metric("Total Games", filtered_df.shape[0])
col3.metric("Top Publisher", filtered_df.groupby("Publisher")["Global_Sales"].sum().idxmax())

# --- Row 1: Top Games + Games Released ---
col4, col5 = st.columns(2)

with col4:
    st.markdown("### 🏆 Top 10 Games by Global Sales")
    top_games = filtered_df.sort_values(by="Global_Sales", ascending=False).head(10)
    fig1, ax1 = plt.subplots(figsize=(8, 4))
    sns.barplot(data=top_games, x="Global_Sales", y="Name", ax=ax1, palette="mako")
    ax1.set_xlabel("Sales (M)")
    st.pyplot(fig1)

with col5:
    st.markdown("### 📅 Games Released Per Year")
    games_year = filtered_df["Year"].value_counts().sort_index().reset_index()
    games_year.columns = ["Year", "Count"]
    fig2 = px.line(games_year, x="Year", y="Count", markers=True, title="Games Released Over Time")
    st.plotly_chart(fig2, use_container_width=True)

# --- Row 2: Genre Pie + Boxplot ---
col6, col7 = st.columns(2)

with col6:
    st.markdown("### 🍕 Genre Share (All Games)")
    pie_df = df[df["Platform"] == selected_platform]
    fig3 = px.pie(pie_df, names='Genre', values='Global_Sales', hole=0.4,
                  title=f"Genre Share on {selected_platform}")
    st.plotly_chart(fig3)

with col7:
    st.markdown("### 📦 Box Plot: Global Sales by Genre")
    fig4, ax4 = plt.subplots(figsize=(8, 4))
    sns.boxplot(data=pie_df, x="Genre", y="Global_Sales", palette="Set2")
    ax4.set_xticklabels(ax4.get_xticklabels(), rotation=45)
    st.pyplot(fig4)

# --- Row 3: Correlation + Top NA Publishers ---
col8, col9 = st.columns(2)

with col8:
    st.markdown("### 🧊 Regional Sales Correlation")
    corr = filtered_df[["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]].corr()
    fig5, ax5 = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax5)
    st.pyplot(fig5)

with col9:
    st.markdown("### 🇺🇸 Top Publishers in North America")
    top_na = filtered_df.groupby("Publisher")["NA_Sales"].sum().sort_values(ascending=False).head(5).reset_index()
    fig6 = px.bar(top_na, x="NA_Sales", y="Publisher", orientation="h", color="NA_Sales",
                  color_continuous_scale="Viridis", title="Top 5 NA Publishers")
    st.plotly_chart(fig6)

# Regional Sales Map
st.markdown("### 🗺️ Interactive Regional Sales Map (Based on Filters)")

# Dictionary of region info: coordinates and column names
region_data = [
    {"Region": "North America", "lat": 40.0, "lon": -100.0, "column": "NA_Sales"},
    {"Region": "Europe", "lat": 54.5, "lon": 15.3, "column": "EU_Sales"},
    {"Region": "Japan", "lat": 36.2, "lon": 138.2, "column": "JP_Sales"},
    {"Region": "Other", "lat": -8.8, "lon": 115.2, "column": "Other_Sales"},
]

# Build data for the map
map_data = []
for item in region_data:
    region = item["Region"]
    col = item["column"]
    if col in filtered_df.columns:
        map_data.append({
            "Region": region,
            "Sales (M)": filtered_df[col].sum(),
            "lat": item["lat"],
            "lon": item["lon"]
        })

map_df = pd.DataFrame(map_data)

# Plot interactive map
fig = px.scatter_mapbox(
    map_df,
    lat="lat",
    lon="lon",
    size="Sales (M)",
    color="Region",
    size_max=60,
    zoom=1,
    mapbox_style="carto-positron",
    title="Regional Sales Distribution",
    hover_name="Region",
    hover_data={"Sales (M)": True, "lat": False, "lon": False}
)

st.plotly_chart(fig, use_container_width=True)

# --- Filtered Data View ---
with st.expander("📋 Show Filtered Data Table"):
    st.dataframe(filtered_df.sort_values(by="Global_Sales", ascending=False))