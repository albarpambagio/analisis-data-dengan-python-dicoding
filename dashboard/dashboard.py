import streamlit as st
import altair as alt
import pandas as pd
from pathlib import Path

# Define base path (one level above the script's location)
base_path = Path(__file__).parents[1]
 
# Path to the csv files
csv_path_ct = base_path / 'data' / 'olist_customers_dataset.csv'
csv_path_od = base_path / 'data' / 'olist_orders_dataset.csv'
csv_path_pm = base_path / 'data' / 'olist_order_payments_dataset.csv'


# Load each sheet
df_ct = pd.read_csv(csv_path_ct)
df_od = pd.read_csv(csv_path_od)
df_pm = pd.read_csv(csv_path_pm)


# Merge orders with customer info to get city
merged_df = df_od.merge(df_ct[['customer_id', 'customer_city']], on='customer_id', how='left')

# --- Plot 1: Top 5 Cities by Order Count ---
order_count = merged_df.groupby('customer_city')['order_delivered_customer_date'].count().reset_index()
order_count.rename(columns={'order_delivered_customer_date': 'order_count'}, inplace=True)
top_5_order_count = order_count.nlargest(5, 'order_count')


fig1 = alt.Chart(top_5_order_count).mark_bar().encode(
    x=alt.X('customer_city:N', title='Customer City', sort='-y'),
    y=alt.Y('order_count:Q', title='Order Count'),
    color=alt.Color('customer_city:N', legend=None)
).properties(
    title='Top 5 Cities by Order Count'
)

# --- Plot 2: Top 5 Cities by Payment Value ---
merged_with_payment = merged_df.merge(df_pm[['order_id', 'payment_value']], on='order_id', how='left')
payment_by_city = merged_with_payment.groupby('customer_city')['payment_value'].sum().reset_index()
top_5_payment_by_city = payment_by_city.nlargest(5, 'payment_value')

fig2 = alt.Chart(top_5_payment_by_city).mark_bar().encode(
    x=alt.X('customer_city:N', title='Customer City', sort='-y'),
    y=alt.Y('payment_value:Q', title='Payment Value'),
    color=alt.Color('customer_city:N', legend=None)
).properties(
    title='Top 5 Cities by Payment Value'
)


# --- Streamlit Layout ---
st.set_page_config(layout="wide")
st.title("Dashboard: Orders & Payments by City")

col1, col2 = st.columns(2)

with col1:
    st.altair_chart(fig1, use_container_width=True)

with col2:
    st.altair_chart(fig2, use_container_width=True)


