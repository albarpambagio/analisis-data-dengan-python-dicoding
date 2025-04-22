import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date


def load_data():
    """Load and prepare all required datasets"""
    orders = pd.read_csv('data/olist_orders_dataset.csv')
    customers = pd.read_csv('data/olist_customers_dataset.csv')
    payments = pd.read_csv('data/olist_order_payments_dataset.csv')
    reviews = pd.read_csv('data/olist_order_reviews_dataset.csv')
    
    # Convert date columns to datetime
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    reviews['review_creation_date'] = pd.to_datetime(reviews['review_creation_date'])
    
    # Add year and month columns
    orders['year'] = orders['order_purchase_timestamp'].dt.year
    orders['month'] = orders['order_purchase_timestamp'].dt.month
    reviews['year'] = reviews['review_creation_date'].dt.year
    reviews['month'] = reviews['review_creation_date'].dt.month
    
    return orders, customers, payments, reviews

def filter_sao_paulo_data(orders, customers, payments, reviews, start_date, end_date):
    """Filter data for São Paulo customers and date range"""
    # Get São Paulo customers
    sao_paulo_customers = customers[customers['customer_state'] == 'SP']['customer_id'].unique()
    
    # Filter orders by São Paulo customers and date range
    sao_paulo_orders = orders[orders['customer_id'].isin(sao_paulo_customers)]
    sao_paulo_orders_date_range = sao_paulo_orders[
        (sao_paulo_orders['order_purchase_timestamp'] >= pd.Timestamp(start_date)) & 
        (sao_paulo_orders['order_purchase_timestamp'] <= pd.Timestamp(end_date))
    ]
    
    # Get order_ids for filtered orders
    sp_order_ids = sao_paulo_orders_date_range['order_id'].unique()
    
    # Filter payments and reviews
    sp_payments = payments[payments['order_id'].isin(sp_order_ids)]
    sp_reviews = reviews[reviews['order_id'].isin(sp_order_ids)]
    sp_reviews_date_range = sp_reviews[
        (sp_reviews['review_creation_date'] >= pd.Timestamp(start_date)) & 
        (sp_reviews['review_creation_date'] <= pd.Timestamp(end_date))
    ]
    
    return sao_paulo_orders_date_range, sp_payments, sp_reviews_date_range

def process_monthly_data(orders_filtered):
    """Process data to get monthly statistics"""
    # Extract month from order timestamp
    monthly_data = orders_filtered.copy()
    monthly_data['year_month'] = monthly_data['order_purchase_timestamp'].dt.to_period('M')
    monthly_data['month'] = monthly_data['order_purchase_timestamp'].dt.month
    
    return monthly_data

def calculate_payment_stats(monthly_data, payments_filtered):
    """Calculate payment statistics by month"""
    # Merge payment data with orders data
    payment_data = payments_filtered.merge(
        monthly_data[['order_id', 'month']], 
        on='order_id', 
        how='left'
    )
    
    # Calculate average payment by month
    monthly_payment_stats = payment_data.groupby('month').agg(
        avg_payment=('payment_value', 'mean')
    ).reset_index()
    
    # Ensure all months are included
    all_months = pd.DataFrame({'month': range(1, 13)})
    monthly_payment_stats = all_months.merge(monthly_payment_stats, on='month', how='left').fillna(0)
    
    return monthly_payment_stats

def calculate_review_stats(monthly_data, reviews_filtered):
    """Calculate review statistics by month"""
    # Extract month from review creation date
    reviews_data = reviews_filtered.copy()
    reviews_data['month'] = reviews_data['review_creation_date'].dt.month
    
    # Calculate average review score by month
    monthly_review_stats = reviews_data.groupby('month').agg(
        avg_score=('review_score', 'mean')
    ).reset_index()
    
    # Ensure all months are included
    all_months = pd.DataFrame({'month': range(1, 13)})
    monthly_review_stats = all_months.merge(monthly_review_stats, on='month', how='left').fillna(0)
    
    return monthly_review_stats

def create_payment_chart(data):
    """Create payment visualization"""
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('month:O', title='Month'),
        y=alt.Y('avg_payment:Q', title='Average Payment Value (R$)'),
        tooltip=['month', 'avg_payment']
    ).properties(
        title='Average Payment Value by Month - São Paulo',
        width=600,
        height=400
    )
    
    # Add text labels
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text=alt.Text('avg_payment:Q', format=',.2f')
    )
    
    return chart + text

def create_review_chart(data):
    """Create review visualization"""
    chart = alt.Chart(data).mark_bar(color='orange').encode(
        x=alt.X('month:O', title='Month'),
        y=alt.Y('avg_score:Q', title='Average Review Score (1-5)', scale=alt.Scale(domain=[0, 5])),
        tooltip=['month', 'avg_score']
    ).properties(
        title='Average Review Score by Month - São Paulo',
        width=600,
        height=400
    )
    
    # Add text labels
    text = chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5
    ).encode(
        text=alt.Text('avg_score:Q', format='.2f')
    )
    
    return chart + text

def main():
    st.set_page_config(
        page_title="Olist São Paulo Analysis",
        layout="wide"
    )
    
    st.title("Olist São Paulo Temporal Analysis Dashboard")
    
    st.sidebar.header("Date Filters")
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            orders, customers, payments, reviews = load_data()
            
            # Get min and max dates from orders
            min_date = orders['order_purchase_timestamp'].min().date()
            max_date = orders['order_purchase_timestamp'].max().date()
            
            # Date picker for start date
            start_date = st.sidebar.date_input(
                "Start Date",
                min_date,
                min_value=min_date,
                max_value=max_date
            )
            
            # Date picker for end date
            end_date = st.sidebar.date_input(
                "End Date",
                max_date,
                min_value=start_date,
                max_value=max_date
            )
            
            if start_date > end_date:
                st.error("Error: End date must be after start date.")
                return
            
            # Filter data based on date range
            orders_filtered, payments_filtered, reviews_filtered = filter_sao_paulo_data(
                orders, customers, payments, reviews, start_date, end_date
            )
            
            # Check if we have data
            if len(orders_filtered) == 0:
                st.warning("No data available for the selected date range.")
                return
            
            # Process data
            monthly_data = process_monthly_data(orders_filtered)
            monthly_payment_stats = calculate_payment_stats(monthly_data, payments_filtered)
            monthly_review_stats = calculate_review_stats(monthly_data, reviews_filtered)
            
            # Create charts
            payment_chart = create_payment_chart(monthly_payment_stats)
            review_chart = create_review_chart(monthly_review_stats)
            
            # Display date range info
            st.subheader(f"Monthly Trends - São Paulo ({start_date.strftime('%d/%m/%Y')} to {end_date.strftime('%d/%m/%Y')})")
            
            # Display order count
            st.info(f"Total orders in period: {len(orders_filtered)}")
            
            # Display charts
            st.altair_chart(payment_chart, use_container_width=True)
            st.altair_chart(review_chart, use_container_width=True)
            
        except FileNotFoundError:
            st.error("Dataset files not found. Please ensure all Olist dataset files are in the data directory.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()