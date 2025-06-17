import pandas as pd
import os

def load_and_process_data(filepath="data/dataset.csv", output_path="data/processed_dataset.csv"):
    """
    Loads the dataset, removes duplicates, fills missing values, adds total_price column,
    sorts by date, and saves the processed dataset.

    Args:
        filepath (str): Path to the input dataset.
        output_path (str): Path to save the processed dataset.

    Returns:
        pd.DataFrame: Processed DataFrame.
    """
    # Load the dataset
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Input file not found: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Original dataset shape: {df.shape}")

    # Remove duplicate rows
    df = df.drop_duplicates()
    print(f"Dataset shape after removing duplicates: {df.shape}")

    # Convert the date column to datetime format 
    df['date'] = pd.to_datetime(df['date'], format='mixed', dayfirst=False)

    # Sort by date from oldest to newest
    df = df.sort_values(by='date', ascending=True)

    # Reset index after sorting (optional but recommended)
    df = df.reset_index(drop=True)

    # Fill blank or missing values in 'transaction_type' column with 'Credit card'
    if 'transaction_type' in df.columns:
        df['transaction_type'] = df['transaction_type'].fillna('Credit card')
        df['transaction_type'] = df['transaction_type'].replace('', 'Credit card')
        print("Missing values in 'transaction_type' filled with 'Credit card'.")
    else:
        print("Column 'transaction_type' not found in dataset.")

    # Create a new column 'total_price' = item_price * quantity
    if 'item_price' in df.columns and 'quantity' in df.columns:
        df['total_price'] = df['item_price'] * df['quantity']
        print("'total_price' column created successfully.")
    else:
        print("Columns 'item_price' or 'quantity' not found in dataset.")

    # Save the processed dataset
    output_path = os.path.abspath(output_path)
    try:
        print(f"Attempting to save to: {output_path}")
        df.to_csv(output_path, index=False)
        print("Processed dataset saved successfully!")
    except Exception as e:
        print(f"Failed to save file. Error: {e}")

    return df

if __name__ == "__main__":
    load_and_process_data()