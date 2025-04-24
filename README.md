# 📦 Olist Payment & Review Analysis

## 📋 Overview

This project explores the relationship between **payment value** and **review scores** in the [Olist E-commerce dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce). The goal is to analyze customer satisfaction and payment trends, especially focusing on the city of **São Paulo in 2018**.

---

## 🔍 Objectives

- Analyze **temporal trends** of payment value and review score.
- Understand the **distribution** of payments and reviews.
- Explore the **correlation** between how much customers pay and how they rate their experience.
- Provide clear and interactive **visualizations** using Altair and Matplotlib.

---

## 📊 Key Analyses

1. **Filtering & Merging**
   - Orders filtered by city (`São Paulo`) and year (`2018`).
   - Merged order data with review and payment information.

2. **Descriptive Statistics**
   - Computed average payment value and average review score for São Paulo in 2018.

3. **Visualizations**
   - **Distributions**:
     - Histograms for `payment_value` and `review_score`.
     - Box plots to identify outliers and variability.
   - **Correlation Analysis**:
     - Scatter plot with regression line between `payment_value` and `review_score`.
     - Pearson and Spearman correlation coefficients.
   - **Temporal Trends**: Line charts showing monthly changes in payment and review score.

---

## 🛠️ Tools & Libraries

- `pandas` for data manipulation
- `matplotlib` & `seaborn` for traditional plots
- `altair` for interactive visualizations
- `streamlit` for dashboard
---

## 📁 Data Source

- [Olist Brazilian E-commerce Public Dataset](https://www.kaggle.com/olistbr/brazilian-ecommerce)


## Setup Environment - uv
```
uv venv
uv pip install -r requirements.txt
```

## Run steamlit app
```
uv run streamlit run dashboard/dashboard.py
```
