import pandas as pd
import json
from datetime import datetime, timedelta
import numpy as np
from collections import defaultdict

def analyze_sales_data(filepath):
    """
    Analyze sales data from CSV file and return insights
    """
    try:
        # Read CSV file
        df = pd.read_csv(filepath)
        
        # Clean and validate data
        cleaned_data = clean_sales_data(df)
        
        if cleaned_data is None:
            return {
                'status': 'error',
                'message': 'Unable to process the CSV file. Please check the format.'
            }
        
        # Perform analysis
        analysis_results = {
            'status': 'success',
            'summary': generate_sales_summary(cleaned_data),
            'trends': analyze_sales_trends(cleaned_data),
            'products': analyze_product_performance(cleaned_data),
            'customers': analyze_customer_behavior(cleaned_data),
            'time_analysis': analyze_time_patterns(cleaned_data),
            'forecasting': generate_sales_forecast(cleaned_data),
            'recommendations': generate_recommendations(cleaned_data),
            'charts': generate_chart_data(cleaned_data),
            'analyzed_at': datetime.now().isoformat(),
            'data_period': get_data_period(cleaned_data)
        }
        
        return analysis_results
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error processing file: {str(e)}'
        }

def clean_sales_data(df):
    """
    Clean and standardize sales data
    """
    try:
        # Common column name mappings
        column_mappings = {
            'date': ['date', 'order_date', 'sale_date', 'transaction_date'],
            'product': ['product', 'product_name', 'item', 'item_name'],
            'quantity': ['quantity', 'qty', 'amount', 'units'],
            'price': ['price', 'unit_price', 'cost', 'amount'],
            'total': ['total', 'total_amount', 'revenue', 'sales'],
            'customer': ['customer', 'customer_name', 'client', 'buyer']
        }
        
        # Find matching columns
        found_columns = {}
        for standard_name, possible_names in column_mappings.items():
            for col in df.columns:
                if col.lower().strip() in possible_names:
                    found_columns[standard_name] = col
                    break
        
        # Must have at least date and some measure of sales
        if 'date' not in found_columns:
            return None
        
        # Create standardized dataframe
        cleaned_df = pd.DataFrame()
        
        # Date column (required)
        try:
            cleaned_df['date'] = pd.to_datetime(df[found_columns['date']])
        except:
            return None
        
        # Sales amount (try to calculate if not directly available)
        if 'total' in found_columns:
            cleaned_df['sales'] = pd.to_numeric(df[found_columns['total']], errors='coerce')
        elif 'price' in found_columns and 'quantity' in found_columns:
            price = pd.to_numeric(df[found_columns['price']], errors='coerce')
            quantity = pd.to_numeric(df[found_columns['quantity']], errors='coerce')
            cleaned_df['sales'] = price * quantity
        elif 'price' in found_columns:
            cleaned_df['sales'] = pd.to_numeric(df[found_columns['price']], errors='coerce')
        else:
            return None
        
        # Optional columns
        if 'product' in found_columns:
            cleaned_df['product'] = df[found_columns['product']].astype(str)
        else:
            cleaned_df['product'] = 'Unknown Product'
        
        if 'quantity' in found_columns:
            cleaned_df['quantity'] = pd.to_numeric(df[found_columns['quantity']], errors='coerce')
        else:
            cleaned_df['quantity'] = 1
        
        if 'customer' in found_columns:
            cleaned_df['customer'] = df[found_columns['customer']].astype(str)
        else:
            cleaned_df['customer'] = 'Unknown Customer'
        
        # Remove rows with missing critical data
        cleaned_df = cleaned_df.dropna(subset=['date', 'sales'])
        
        # Remove negative sales (likely returns - could be handled separately)
        cleaned_df = cleaned_df[cleaned_df['sales'] >= 0]
        
        # Sort by date
        cleaned_df = cleaned_df.sort_values('date')
        
        return cleaned_df
        
    except Exception as e:
        return None

def generate_sales_summary(df):
    """
    Generate overall sales summary
    """
    total_sales = df['sales'].sum()
    total_transactions = len(df)
    avg_transaction = df['sales'].mean()
    unique_customers = df['customer'].nunique() if 'customer' in df.columns else None
    unique_products = df['product'].nunique() if 'product' in df.columns else None
    
    # Date range
    date_range = df['date'].max() - df['date'].min()
    
    # Growth calculation (if enough data)
    growth_rate = calculate_growth_rate(df)
    
    return {
        'total_sales': round(total_sales, 2),
        'total_transactions': total_transactions,
        'average_transaction': round(avg_transaction, 2),
        'unique_customers': unique_customers,
        'unique_products': unique_products,
        'data_period_days': date_range.days,
        'daily_average': round(total_sales / max(date_range.days, 1), 2),
        'growth_rate': growth_rate
    }

def analyze_sales_trends(df):
    """
    Analyze sales trends over time
    """
    # Daily sales
    daily_sales = df.groupby(df['date'].dt.date)['sales'].sum()
    
    # Monthly sales
    monthly_sales = df.groupby(df['date'].dt.to_period('M'))['sales'].sum()
    
    # Weekly sales
    weekly_sales = df.groupby(df['date'].dt.to_period('W'))['sales'].sum()
    
    # Trend analysis
    trend_direction = 'stable'
    if len(daily_sales) >= 7:
        recent_avg = daily_sales.tail(7).mean()
        earlier_avg = daily_sales.head(7).mean()
        
        if recent_avg > earlier_avg * 1.1:
            trend_direction = 'increasing'
        elif recent_avg < earlier_avg * 0.9:
            trend_direction = 'decreasing'
    
    # Best and worst performing days
    best_day = daily_sales.idxmax()
    worst_day = daily_sales.idxmin()
    best_sales = daily_sales.max()
    worst_sales = daily_sales.min()
    
    return {
        'trend_direction': trend_direction,
        'daily_average': round(daily_sales.mean(), 2),
        'daily_std': round(daily_sales.std(), 2),
        'best_day': {
            'date': str(best_day),
            'sales': round(best_sales, 2)
        },
        'worst_day': {
            'date': str(worst_day),
            'sales': round(worst_sales, 2)
        },
        'monthly_trend': monthly_sales.to_dict() if len(monthly_sales) > 0 else {},
        'volatility': round(daily_sales.std() / daily_sales.mean() * 100, 2) if daily_sales.mean() > 0 else 0
    }

def analyze_product_performance(df):
    """
    Analyze individual product performance
    """
    if 'product' not in df.columns:
        return {'message': 'Product information not available'}
    
    # Product sales totals
    product_sales = df.groupby('product')['sales'].agg(['sum', 'count', 'mean']).round(2)
    product_sales.columns = ['total_sales', 'transactions', 'avg_per_transaction']
    
    # Sort by total sales
    product_sales = product_sales.sort_values('total_sales', ascending=False)
    
    # Top and bottom performers
    top_products = product_sales.head(10).to_dict('index')
    bottom_products = product_sales.tail(5).to_dict('index')
    
    # Product diversity
    total_products = len(product_sales)
    top_10_percent = max(1, total_products // 10)
    revenue_concentration = (product_sales.head(top_10_percent)['total_sales'].sum() / 
                           product_sales['total_sales'].sum() * 100)
    
    return {
        'total_products': total_products,
        'top_performers': top_products,
        'bottom_performers': bottom_products,
        'revenue_concentration': round(revenue_concentration, 2),
        'product_diversity_score': calculate_diversity_score(product_sales['total_sales'])
    }

def analyze_customer_behavior(df):
    """
    Analyze customer purchasing behavior
    """
    if 'customer' not in df.columns:
        return {'message': 'Customer information not available'}
    
    # Customer analysis
    customer_stats = df.groupby('customer')['sales'].agg(['sum', 'count', 'mean']).round(2)
    customer_stats.columns = ['total_spent', 'transactions', 'avg_per_transaction']
    
    # Sort by total spent
    customer_stats = customer_stats.sort_values('total_spent', ascending=False)
    
    # Customer segments
    total_customers = len(customer_stats)
    
    # Top 20% of customers (VIP)
    vip_count = max(1, total_customers // 5)
    vip_customers = customer_stats.head(vip_count)
    vip_revenue_share = (vip_customers['total_spent'].sum() / 
                        customer_stats['total_spent'].sum() * 100)
    
    # Customer lifetime value
    avg_customer_value = customer_stats['total_spent'].mean()
    
    # Repeat customer rate
    repeat_customers = (customer_stats['transactions'] > 1).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0
    
    return {
        'total_customers': total_customers,
        'avg_customer_value': round(avg_customer_value, 2),
        'repeat_customer_rate': round(repeat_rate, 2),
        'vip_customers': vip_count,
        'vip_revenue_share': round(vip_revenue_share, 2),
        'top_customers': customer_stats.head(10).to_dict('index'),
        'customer_distribution': {
            'high_value': (customer_stats['total_spent'] > avg_customer_value * 2).sum(),
            'medium_value': ((customer_stats['total_spent'] >= avg_customer_value * 0.5) & 
                           (customer_stats['total_spent'] <= avg_customer_value * 2)).sum(),
            'low_value': (customer_stats['total_spent'] < avg_customer_value * 0.5).sum()
        }
    }

def analyze_time_patterns(df):
    """
    Analyze sales patterns by time periods
    """
    # Day of week analysis
    df['day_of_week'] = df['date'].dt.day_name()
    daily_patterns = df.groupby('day_of_week')['sales'].agg(['sum', 'mean', 'count']).round(2)
    
    # Month analysis
    df['month'] = df['date'].dt.month_name()
    monthly_patterns = df.groupby('month')['sales'].agg(['sum', 'mean', 'count']).round(2)
    
    # Hour analysis (if time data available)
    hour_patterns = {}
    if df['date'].dt.hour.nunique() > 1:  # Has time component
        hour_patterns = df.groupby(df['date'].dt.hour)['sales'].agg(['sum', 'mean', 'count']).round(2).to_dict('index')
    
    # Best performing periods
    best_day = daily_patterns['sum'].idxmax()
    best_month = monthly_patterns['sum'].idxmax()
    
    return {
        'daily_patterns': daily_patterns.to_dict('index'),
        'monthly_patterns': monthly_patterns.to_dict('index'),
        'hour_patterns': hour_patterns,
        'best_day_of_week': best_day,
        'best_month': best_month,
        'seasonality_detected': detect_seasonality(df)
    }

def generate_sales_forecast(df):
    """
    Generate simple sales forecast
    """
    try:
        # Simple moving average forecast
        daily_sales = df.groupby(df['date'].dt.date)['sales'].sum()
        
        if len(daily_sales) < 7:
            return {'message': 'Insufficient data for forecasting'}
        
        # Calculate trend
        recent_avg = daily_sales.tail(7).mean()
        overall_avg = daily_sales.mean()
        
        # Simple forecast for next 7 days
        trend_factor = recent_avg / overall_avg if overall_avg > 0 else 1
        
        forecast_days = []
        last_date = df['date'].max()
        
        for i in range(1, 8):
            forecast_date = last_date + timedelta(days=i)
            forecast_value = overall_avg * trend_factor
            forecast_days.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_sales': round(forecast_value, 2)
            })
        
        # Forecast confidence
        volatility = daily_sales.std() / daily_sales.mean() if daily_sales.mean() > 0 else 1
        confidence = max(0, min(100, 100 - (volatility * 100)))
        
        return {
            'next_7_days': forecast_days,
            'confidence_score': round(confidence, 2),
            'trend_factor': round(trend_factor, 3),
            'methodology': 'Moving Average with Trend Adjustment'
        }
        
    except Exception as e:
        return {'message': f'Forecasting error: {str(e)}'}

def generate_recommendations(df):
    """
    Generate actionable business recommendations
    """
    recommendations = []
    
    # Analyze trends
    daily_sales = df.groupby(df['date'].dt.date)['sales'].sum()
    
    if len(daily_sales) >= 14:
        recent_avg = daily_sales.tail(7).mean()
        previous_avg = daily_sales.iloc[-14:-7].mean()
        
        if recent_avg > previous_avg * 1.1:
            recommendations.append({
                'type': 'positive',
                'category': 'trend',
                'title': 'Sales Growth Detected',
                'description': 'Your sales are trending upward! Consider scaling marketing efforts.',
                'priority': 'medium'
            })
        elif recent_avg < previous_avg * 0.9:
            recommendations.append({
                'type': 'warning',
                'category': 'trend',
                'title': 'Sales Decline Detected',
                'description': 'Recent sales are below average. Review marketing strategy and customer feedback.',
                'priority': 'high'
            })
    
    # Product recommendations
    if 'product' in df.columns:
        product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=False)
        
        if len(product_sales) >= 5:
            top_product_share = product_sales.iloc[0] / product_sales.sum() * 100
            
            if top_product_share > 50:
                recommendations.append({
                    'type': 'warning',
                    'category': 'product',
                    'title': 'High Product Concentration Risk',
                    'description': f'Over 50% of revenue comes from one product. Consider diversifying offerings.',
                    'priority': 'medium'
                })
            
            # Low performers
            bottom_products = product_sales.tail(3)
            avg_sales = product_sales.mean()
            
            underperformers = bottom_products[bottom_products < avg_sales * 0.1]
            if len(underperformers) > 0:
                recommendations.append({
                    'type': 'info',
                    'category': 'product',
                    'title': 'Underperforming Products Identified',
                    'description': f'Consider discontinuing or improving marketing for {len(underperformers)} low-performing products.',
                    'priority': 'low'
                })
    
    # Customer recommendations
    if 'customer' in df.columns:
        customer_stats = df.groupby('customer')['sales'].agg(['sum', 'count'])
        repeat_rate = (customer_stats['count'] > 1).mean() * 100
        
        if repeat_rate < 30:
            recommendations.append({
                'type': 'improvement',
                'category': 'customer',
                'title': 'Low Customer Retention',
                'description': f'Only {repeat_rate:.1f}% of customers make repeat purchases. Focus on retention strategies.',
                'priority': 'high'
            })
        elif repeat_rate > 70:
            recommendations.append({
                'type': 'positive',
                'category': 'customer',
                'title': 'Excellent Customer Retention',
                'description': f'{repeat_rate:.1f}% repeat customer rate is excellent! Consider referral programs.',
                'priority': 'low'
            })
    
    # Time-based recommendations
    day_patterns = df.groupby(df['date'].dt.day_name())['sales'].mean()
    best_day = day_patterns.idxmax()
    worst_day = day_patterns.idxmin()
    
    if day_patterns[best_day] > day_patterns[worst_day] * 2:
        recommendations.append({
            'type': 'info',
            'category': 'timing',
            'title': 'Strong Day-of-Week Patterns',
            'description': f'{best_day} is your best day. Consider special promotions on {worst_day} to boost sales.',
            'priority': 'medium'
        })
    
    return recommendations

def generate_chart_data(df):
    """
    Generate data for various charts
    """
    charts = {}
    
    # Daily sales line chart
    daily_sales = df.groupby(df['date'].dt.date)['sales'].sum().reset_index()
    charts['daily_sales'] = {
        'type': 'line',
        'data': [{'date': str(row['date']), 'sales': round(row['sales'], 2)} 
                for _, row in daily_sales.iterrows()],
        'title': 'Daily Sales Trend'
    }
    
    # Product performance bar chart
    if 'product' in df.columns:
        product_sales = df.groupby('product')['sales'].sum().nlargest(10).reset_index()
        charts['top_products'] = {
            'type': 'bar',
            'data': [{'product': row['product'], 'sales': round(row['sales'], 2)} 
                    for _, row in product_sales.iterrows()],
            'title': 'Top 10 Products by Sales'
        }
    
    # Day of week pattern
    day_sales = df.groupby(df['date'].dt.day_name())['sales'].mean().reindex([
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
    ]).reset_index()
    charts['day_pattern'] = {
        'type': 'bar',
        'data': [{'day': row['day_of_week'], 'avg_sales': round(row['sales'], 2)} 
                for _, row in day_sales.iterrows() if not pd.isna(row['sales'])],
        'title': 'Average Sales by Day of Week'
    }
    
    # Monthly trend
    monthly_sales = df.groupby(df['date'].dt.to_period('M'))['sales'].sum().reset_index()
    monthly_sales['date'] = monthly_sales['date'].astype(str)
    charts['monthly_trend'] = {
        'type': 'line',
        'data': [{'month': row['date'], 'sales': round(row['sales'], 2)} 
                for _, row in monthly_sales.iterrows()],
        'title': 'Monthly Sales Trend'
    }
    
    return charts

def calculate_growth_rate(df):
    """
    Calculate growth rate between periods
    """
    try:
        daily_sales = df.groupby(df['date'].dt.date)['sales'].sum()
        
        if len(daily_sales) < 14:
            return None
        
        # Compare recent 7 days to previous 7 days
        recent_total = daily_sales.tail(7).sum()
        previous_total = daily_sales.iloc[-14:-7].sum()
        
        if previous_total > 0:
            growth_rate = ((recent_total - previous_total) / previous_total) * 100
            return round(growth_rate, 2)
        
        return None
    except:
        return None

def calculate_diversity_score(sales_series):
    """
    Calculate product diversity score (higher = more diverse)
    """
    try:
        # Calculate Gini coefficient (0 = perfect equality, 1 = perfect inequality)
        sorted_sales = np.sort(sales_series.values)
        n = len(sorted_sales)
        gini = (2 * np.sum(np.arange(1, n + 1) * sorted_sales)) / (n * np.sum(sorted_sales)) - (n + 1) / n
        
        # Convert to diversity score (inverse of Gini)
        diversity_score = (1 - gini) * 100
        return round(diversity_score, 2)
    except:
        return 50  # Default neutral score

def detect_seasonality(df):
    """
    Detect if there's seasonality in the data
    """
    try:
        if len(df) < 30:  # Need at least a month of data
            return False
        
        # Check for weekly patterns
        daily_avg = df.groupby(df['date'].dt.dayofweek)['sales'].mean()
        weekly_variation = daily_avg.std() / daily_avg.mean()
        
        # Check for monthly patterns (if enough data)
        monthly_avg = df.groupby(df['date'].dt.month)['sales'].mean()
        monthly_variation = monthly_avg.std() / monthly_avg.mean() if len(monthly_avg) > 3 else 0
        
        # Consider seasonal if variation is significant
        return weekly_variation > 0.2 or monthly_variation > 0.3
        
    except:
        return False

def get_data_period(df):
    """
    Get the period covered by the data
    """
    start_date = df['date'].min()
    end_date = df['date'].max()
    
    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'total_days': (end_date - start_date).days + 1
    }