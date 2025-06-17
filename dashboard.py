import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from sklearn.ensemble import RandomForestRegressor

# Function to load the processed data
@st.cache_data
def load_data(filepath="casestudy/data/processed_dataset.csv"):
    try:
        data = pd.read_csv(filepath)
        return data
    except FileNotFoundError:
        st.error("Processed dataset not found. Please run the processing script first.")
        return pd.DataFrame()

# Forecasting Function — returns date + forecast dictionary
def get_forecasted_sales(df):
    df['date'] = pd.to_datetime(df['date'])

    if 'total_price' not in df.columns:
        return None

    df = df.groupby('date')['total_price'].sum().reset_index()

    all_days = pd.date_range(start=df['date'].min(), end=df['date'].max())
    df = df.set_index('date').reindex(all_days).rename_axis('date').reset_index()
    df['total_price'] = df['total_price'].interpolate(method='linear')

    df_weekly = df.set_index('date').resample('W-FRI').asfreq().reset_index()

    for i in range(1, 9):
        df_weekly[f'lag_{i}'] = df_weekly['total_price'].shift(i)
    df_model = df_weekly.dropna().reset_index(drop=True)

    features = [f'lag_{i}' for i in range(1, 9)]
    X = df_model[features]
    y = df_model['total_price']

    model = RandomForestRegressor(random_state=42)
    model.fit(X, y)

    last_known = df_model.iloc[-1][features].values.tolist()
    future_dates = pd.date_range(start=df_weekly['date'].max() + pd.Timedelta(weeks=1), periods=4, freq='W-FRI')
    forecast = []

    for _ in range(4):
        input_df = pd.DataFrame([last_known], columns=features)
        pred = model.predict(input_df)[0]
        forecast.append(pred)
        last_known = last_known[1:] + [pred]

    forecast_dict = {str(date.date()): value for date, value in zip(future_dates, forecast)}
    return forecast_dict

# Main function to run the Streamlit app
def main():
    st.title("Balaji Sales Dashboard (April 22' - March 23')")
    st.write("This dashboard displays the processed data and allows stakeholders to filter and search the records.")

    df = load_data()
    if df.empty:
        st.warning("No data to display. Please ensure the dataset is processed and available.")
        return

    df_forecast = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    df = df.rename(columns={"item_type": "Type of Items", "total_price": "Total Sales (₹)"})

    st.sidebar.header("Filter Options")

    st.sidebar.subheader("By Year")
    selected_year = st.sidebar.selectbox("Select Year", options=["All"] + sorted(df['year'].dropna().unique().tolist()))
    if selected_year != "All":
        df = df[df['year'] == selected_year]

    st.sidebar.subheader("By Time of Sale")
    time_options = ["All"] + sorted(df["time_of_sale"].dropna().unique().tolist())
    selected_time = st.sidebar.selectbox("Select Time of Sale", options=time_options)
    if selected_time != "All":
        df = df[df["time_of_sale"] == selected_time]

    # Display summary metrics
    st.subheader("Summary Metrics")
    total_sales = df["Total Sales (₹)"].sum()
    if selected_year == "All":
        st.metric("Total Sales (All Years)", f"₹{total_sales:,.2f}")
    else:
        st.metric(f"Total Sales ({selected_year})", f"₹{total_sales:,.2f}")

    # Get forecasted sales
    forecast_dict = get_forecasted_sales(df_forecast)

    if forecast_dict:
        st.sidebar.subheader("Forecasted Sales Date")
        forecast_keys = list(forecast_dict.keys())
        selected_date = st.sidebar.selectbox("Select Forecast Date", forecast_keys)

        selected_value = forecast_dict[selected_date]
        st.metric(f"Forecasted Sales on {selected_date}", f"₹{selected_value:,.2f}")
    else:
        st.warning("Unable to forecast. Required column 'total_price' missing.")

    # Sales by item type chart
    summary = df.groupby("Type of Items")["Total Sales (₹)"].sum().reset_index()
    fig = px.bar(
        summary,
        x="Type of Items",
        y="Total Sales (₹)",
        title=f"Total Sales by Type of Items ({'All Years' if selected_year == 'All' else selected_year})",
        labels={"Total Sales (₹)": "Total Sales (₹)", "Type of Items": "Item Type"},
        text_auto=".2s",
        color="Type of Items"
    )
    st.plotly_chart(fig, use_container_width=True)

# Entry point
if __name__ == "__main__":
    main()