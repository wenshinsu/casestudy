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

# Filter by year
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year

    # Sidebar filter
    st.sidebar.header("Filter Options")
    selected_year = st.sidebar.selectbox("Select Year", options=["All"] + sorted(df['year'].dropna().unique().tolist()))

    # Filter by selected year
    if selected_year != "All":
        df = df[df['year'] == selected_year]

    # Rename columns for display
    df = df.rename(columns={"item_type": "Type of Items", "total_price": "Total Sales (₹)"})

    # Group and sum sales by item type
    summary = df.groupby("Type of Items")["Total Sales (₹)"].sum().reset_index()

# Summary metrics of Total Sales by year
    st.subheader("Summary Metrics")
    total_sales = df["Total Sales (₹)"].sum()
    if selected_year == "All":
        st.metric("Total Sales (All Years)", f"₹{total_sales:,.2f}")
    else:
        st.metric(f"Total Sales ({selected_year})", f"₹{total_sales:,.2f}")

# Create bar chart using Plotly
    fig = px.bar(
        summary,
        x="Type of Items",
        y="Total Sales (₹)",
        title=f"Total Sales by Type of Items ({'All Years' if selected_year == 'All' else selected_year})",
        labels={"Total Sales (₹)": "Total Sales (in ₹)", "Type of Items": "Item Type"},
        text_auto=".2s",
        color="Type of Items"
    )

    # Show the chart
    st.plotly_chart(fig, use_container_width=True)

# Entry point for the Streamlit app
if __name__ == "__main__":
    main()