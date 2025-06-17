import pandas as pd
import streamlit as st
import plotly.express as px

# Function to load the processed data
@st.cache_data
def load_data(filepath="data/processed_dataset.csv"):
    """
    Loads the processed dataset.

    Args:
        filepath (str): Path to the processed dataset.

    Returns:
        pd.DataFrame: Loaded data.
    """
    try:
        data = pd.read_csv(filepath)
        return data
    except FileNotFoundError:
        st.error("Processed dataset not found. Please run the processing script first.")
        return pd.DataFrame()

# Main function to run the Streamlit app
def main():
    st.title("Balaji Sales Dashboard (April 22' - March 23')")
    st.write("This dashboard displays the processed data and allows stakeholders to filter and search the records.")

    # Load the processed data
    df = load_data()
    if df.empty:
        st.warning("No data to display. Please ensure the dataset is processed and available.")
        return

    # Ensure date column is datetime and extract year
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Rename columns for display
    df = df.rename(columns={"item_type": "Type of Items", "total_price": "Total Sales (₹)"})

    # Sidebar filters
    st.sidebar.header("Filter Options")

    # Filter by year
    st.sidebar.subheader("By Year")
    selected_year = st.sidebar.selectbox("Select Year", options=["All"] + sorted(df['year'].dropna().unique().tolist()))
    if selected_year != "All":
        df = df[df['year'] == selected_year]

    # Filter by time of sale
    st.sidebar.subheader("By Time of Sale")
    time_options = ["All"] + sorted(df["time_of_sale"].dropna().unique().tolist())
    selected_time = st.sidebar.selectbox("Select Time of Sale", options=time_options)
    if selected_time != "All":
        df = df[df["time_of_sale"] == selected_time]

    # Display summary metrics of Total Sales
    st.subheader("Summary Metrics")
    total_sales = df["Total Sales (₹)"].sum()
    if selected_year == "All":
        st.metric("Total Sales (All Years)", f"₹{total_sales:,.2f}")
    else:
        st.metric(f"Total Sales ({selected_year})", f"₹{total_sales:,.2f}")

    # Group and sum sales by item type
    summary = df.groupby("Type of Items")["Total Sales (₹)"].sum().reset_index()

    # Create bar chart using Plotly
    fig = px.bar(
        summary,
        x="Type of Items",
        y="Total Sales (₹)",
        title=f"Total Sales by Type of Items ({'All Years' if selected_year == 'All' else selected_year})",
        labels={"Total Sales (₹)": "Total Sales (₹)", "Type of Items": "Item Type"},
        text_auto=".2s",
        color="Type of Items"
    )

    # Show the chart
    st.plotly_chart(fig, use_container_width=True)

# Entry point for the Streamlit app
if __name__ == "__main__":
    main()