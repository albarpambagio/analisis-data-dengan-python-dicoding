import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

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

def filter_sao_paulo_data(orders, customers, payments, reviews, selected_year):
    """Filter data for São Paulo customers and selected year"""
    # Get São Paulo customers
    sao_paulo_customers = customers[customers['customer_state'] == 'SP']['customer_id'].unique()
    
    # Filter orders by São Paulo customers and selected year
    sao_paulo_orders = orders[orders['customer_id'].isin(sao_paulo_customers)]
    sao_paulo_orders_year = sao_paulo_orders[sao_paulo_orders['year'] == selected_year]
    
    # Get order_ids for filtered orders
    sp_order_ids = sao_paulo_orders_year['order_id'].unique()
    
    # Filter payments and reviews
    sp_payments = payments[payments['order_id'].isin(sp_order_ids)]
    sp_reviews = reviews[reviews['order_id'].isin(sp_order_ids)]
    sp_reviews_year = sp_reviews[sp_reviews['year'] == selected_year]
    
    return sao_paulo_orders_year, sp_payments, sp_reviews_year

def process_monthly_data(orders_filtered, payments_filtered, reviews_filtered):
    """Process data to get monthly statistics"""
    # Prepare monthly payment data
    monthly_payments = payments_filtered.merge(
        orders_filtered[['order_id', 'month']], 
        on='order_id', 
        how='left'
    )
    
    # Calculate monthly payment statistics - focus only on avg_payment
    monthly_payment_stats = monthly_payments.groupby('month').agg(
        avg_payment=('payment_value', 'mean')
    ).reset_index()
    
    # Prepare monthly review data - focus only on avg_score
    monthly_review_stats = reviews_filtered.groupby('month').agg(
        avg_score=('review_score', 'mean')
    ).reset_index()
    
    # Ensure all months are included (even if no data)
    all_months = pd.DataFrame({'month': range(1, 13)})
    
    monthly_payment_stats = all_months.merge(monthly_payment_stats, on='month', how='left').fillna(0)
    monthly_review_stats = all_months.merge(monthly_review_stats, on='month', how='left').fillna(0)
    
    return monthly_payment_stats, monthly_review_stats

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
    
    st.sidebar.header("Filters")
    
    # Load data
    with st.spinner("Loading data..."):
        try:
            orders, customers, payments, reviews = load_data()
            
            # Get available years for selection
            available_years = sorted(orders['order_purchase_timestamp'].dt.year.unique())
            
            if not available_years:
                st.error("No order data available.")
                return
            
            # Year selection
            selected_year = st.sidebar.selectbox(
                "Select Year", 
                available_years
            )
            
            # Filter data based on selections
            orders_filtered, payments_filtered, reviews_filtered = filter_sao_paulo_data(
                orders, customers, payments, reviews, selected_year
            )
            
            # Process data
            monthly_payment_stats, monthly_review_stats = process_monthly_data(
                orders_filtered, payments_filtered, reviews_filtered
            )
            
            # Create charts
            payment_chart = create_payment_chart(monthly_payment_stats)
            review_chart = create_review_chart(monthly_review_stats)
            
            # Display charts
            st.subheader(f"Monthly Trends - São Paulo {selected_year}")
            st.altair_chart(payment_chart, use_container_width=True)
            st.altair_chart(review_chart, use_container_width=True)
            
        except FileNotFoundError:
            st.error("Dataset files not found. Please ensure all Olist dataset files are in the working directory.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

if __name__ == "__main__":
    main()