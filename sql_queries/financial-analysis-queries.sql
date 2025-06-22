-- Circle Internet Group (CRCL) Financial Analysis SQL Queries
-- ============================================================
-- 
-- This file contains SQL queries for analyzing CRCL's financial data
-- Compatible with PostgreSQL, MySQL, and SQL Server
--
-- Author: Your Name
-- Date: June 2025

-- 1. CREATE TABLES FOR FINANCIAL DATA
-- ===================================

CREATE TABLE IF NOT EXISTS crcl_financials (
    id SERIAL PRIMARY KEY,
    reporting_period VARCHAR(20) NOT NULL,
    fiscal_year INTEGER,
    quarter INTEGER,
    total_revenue DECIMAL(15,2),
    reserve_income DECIMAL(15,2),
    operating_income DECIMAL(15,2),
    net_income DECIMAL(15,2),
    ebitda DECIMAL(15,2),
    total_assets DECIMAL(15,2),
    shareholders_equity DECIMAL(15,2),
    usdc_circulation DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    open_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    volume BIGINT,
    market_cap DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interest_rates (
    id SERIAL PRIMARY KEY,
    rate_date DATE NOT NULL,
    fed_funds_rate DECIMAL(6,4),
    treasury_10y DECIMAL(6,4),
    treasury_2y DECIMAL(6,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. INSERT SAMPLE DATA
-- ====================

INSERT INTO crcl_financials (reporting_period, fiscal_year, total_revenue, reserve_income, operating_income, net_income, usdc_circulation) VALUES
('2019', 2019, 15.44, 12.50, -10.20, -8.50, NULL),
('2020', 2020, 56.12, 45.20, -25.60, -85.55, 1.2),
('2021', 2021, 539.54, 420.30, 45.80, -768.85, 42.7),
('2022', 2022, 735.89, 700.50, 6.08, 267.56, 44.0),
('2023', 2023, 1430.00, 1400.00, 247.89, 18.11, 24.4),
('2024', 2024, 1890.00, 1660.00, 167.16, 155.67, 33.6),
('Q1 2025', 2025, 578.57, 557.91, 92.94, 64.79, 61.4);

-- 3. FINANCIAL ANALYSIS QUERIES
-- =============================

-- Revenue Growth Analysis
SELECT 
    reporting_period,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY fiscal_year) as prev_revenue,
    ROUND(
        ((total_revenue - LAG(total_revenue) OVER (ORDER BY fiscal_year)) / 
         LAG(total_revenue) OVER (ORDER BY fiscal_year)) * 100, 2
    ) as revenue_growth_pct
FROM crcl_financials
WHERE total_revenue IS NOT NULL
ORDER BY fiscal_year;

-- Profitability Trend Analysis
SELECT 
    reporting_period,
    total_revenue,
    operating_income,
    net_income,
    ROUND((operating_income / total_revenue) * 100, 2) as operating_margin_pct,
    ROUND((net_income / total_revenue) * 100, 2) as net_margin_pct
FROM crcl_financials
WHERE total_revenue > 0
ORDER BY fiscal_year;

-- Reserve Income Analysis
SELECT 
    reporting_period,
    reserve_income,
    total_revenue,
    ROUND((reserve_income / total_revenue) * 100, 2) as reserve_income_pct,
    usdc_circulation,
    CASE 
        WHEN usdc_circulation IS NOT NULL 
        THEN ROUND((reserve_income / usdc_circulation) * 100, 4)
        ELSE NULL 
    END as implied_yield_pct
FROM crcl_financials
WHERE reserve_income IS NOT NULL
ORDER BY fiscal_year;

-- 4. ADVANCED ANALYTICS QUERIES
-- =============================

-- Moving Averages for Revenue
SELECT 
    reporting_period,
    total_revenue,
    AVG(total_revenue) OVER (
        ORDER BY fiscal_year 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as revenue_3period_ma,
    AVG(total_revenue) OVER (
        ORDER BY fiscal_year 
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) as revenue_5period_ma
FROM crcl_financials
WHERE total_revenue IS NOT NULL
ORDER BY fiscal_year;

-- Year-over-Year Comparison
WITH yoy_comparison AS (
    SELECT 
        reporting_period,
        fiscal_year,
        total_revenue,
        operating_income,
        net_income,
        LAG(total_revenue, 1) OVER (ORDER BY fiscal_year) as prev_revenue,
        LAG(operating_income, 1) OVER (ORDER BY fiscal_year) as prev_operating_income,
        LAG(net_income, 1) OVER (ORDER BY fiscal_year) as prev_net_income
    FROM crcl_financials
    WHERE fiscal_year >= 2020
)
SELECT 
    reporting_period,
    total_revenue,
    prev_revenue,
    ROUND(((total_revenue - prev_revenue) / prev_revenue) * 100, 2) as revenue_yoy_growth,
    operating_income,
    prev_operating_income,
    CASE 
        WHEN prev_operating_income != 0 
        THEN ROUND(((operating_income - prev_operating_income) / ABS(prev_operating_income)) * 100, 2)
        ELSE NULL 
    END as operating_income_yoy_change
FROM yoy_comparison
ORDER BY fiscal_year;

-- 5. VALUATION METRICS
-- ====================

-- Calculate Price-to-Sales and other multiples
SELECT 
    m.trade_date,
    m.close_price,
    m.market_cap,
    f.total_revenue as ttm_revenue,
    ROUND(m.market_cap / f.total_revenue, 2) as price_to_sales,
    f.net_income as ttm_net_income,
    CASE 
        WHEN f.net_income > 0 
        THEN ROUND(m.market_cap / f.net_income, 2)
        ELSE NULL 
    END as price_to_earnings
FROM market_data m
CROSS JOIN (
    SELECT total_revenue, net_income 
    FROM crcl_financials 
    WHERE reporting_period = '2024'
) f
WHERE m.trade_date >= '2025-06-01'
ORDER BY m.trade_date DESC
LIMIT 10;

-- 6. SENSITIVITY ANALYSIS
-- =======================

-- Interest Rate Sensitivity Model
WITH rate_scenarios AS (
    SELECT 
        scenario_name,
        fed_funds_rate,
        usdc_reserves
    FROM (
        VALUES 
            ('Bull Case', 0.0725, 61.4),
            ('Base Case', 0.0525, 61.4),
            ('Bear Case', 0.0325, 61.4),
            ('Worst Case', 0.0225, 61.4)
    ) AS scenarios(scenario_name, fed_funds_rate, usdc_reserves)
)
SELECT 
    scenario_name,
    ROUND(fed_funds_rate * 100, 2) as fed_funds_rate_pct,
    usdc_reserves as usdc_reserves_billion,
    ROUND(usdc_reserves * fed_funds_rate, 2) as projected_reserve_income_billion,
    ROUND((usdc_reserves * fed_funds_rate) * 1000, 0) as projected_reserve_income_million
FROM rate_scenarios
ORDER BY fed_funds_rate DESC;

-- 7. PERFORMANCE BENCHMARKING
-- ===========================

-- Compare CRCL performance metrics
SELECT 
    'CRCL 2024' as company,
    1890.00 as revenue_millions,
    167.16 as operating_income_millions,
    ROUND((167.16 / 1890.00) * 100, 2) as operating_margin_pct,
    155.67 as net_income_millions,
    ROUND((155.67 / 1890.00) * 100, 2) as net_margin_pct,
    52600 as market_cap_millions,
    ROUND(52600 / 1890.00, 2) as price_to_sales

UNION ALL

SELECT 
    'FinTech Average' as company,
    NULL as revenue_millions,
    NULL as operating_income_millions,
    15.5 as operating_margin_pct,
    NULL as net_income_millions,
    12.8 as net_margin_pct,
    NULL as market_cap_millions,
    13.5 as price_to_sales;

-- 8. RISK ANALYSIS QUERIES
-- ========================

-- Revenue Volatility Analysis
WITH revenue_stats AS (
    SELECT 
        AVG(total_revenue) as avg_revenue,
        STDDEV(total_revenue) as revenue_stddev,
        COUNT(*) as periods
    FROM crcl_financials
    WHERE total_revenue IS NOT NULL
)
SELECT 
    f.reporting_period,
    f.total_revenue,
    r.avg_revenue,
    ROUND(r.revenue_stddev, 2) as revenue_stddev,
    ROUND((f.total_revenue - r.avg_revenue) / r.revenue_stddev, 2) as revenue_z_score,
    CASE 
        WHEN ABS((f.total_revenue - r.avg_revenue) / r.revenue_stddev) > 2 
        THEN 'High Volatility'
        WHEN ABS((f.total_revenue - r.avg_revenue) / r.revenue_stddev) > 1 
        THEN 'Medium Volatility'
        ELSE 'Low Volatility'
    END as volatility_level
FROM crcl_financials f
CROSS JOIN revenue_stats r
WHERE f.total_revenue IS NOT NULL
ORDER BY f.fiscal_year;

-- 9. FORECASTING QUERIES
-- ======================

-- Simple Linear Trend for Revenue Forecasting
WITH revenue_trend AS (
    SELECT 
        fiscal_year,
        total_revenue,
        ROW_NUMBER() OVER (ORDER BY fiscal_year) as period_number
    FROM crcl_financials
    WHERE fiscal_year BETWEEN 2020 AND 2024
    AND total_revenue IS NOT NULL
),
trend_stats AS (
    SELECT 
        COUNT(*) as n,
        AVG(period_number) as avg_x,
        AVG(total_revenue) as avg_y,
        SUM((period_number - AVG(period_number) OVER()) * (total_revenue - AVG(total_revenue) OVER())) as sum_xy,
        SUM(POWER(period_number - AVG(period_number) OVER(), 2)) as sum_x2
    FROM revenue_trend
)
SELECT 
    'Revenue Trend Analysis' as analysis_type,
    ROUND(avg_y, 2) as avg_revenue,
    ROUND(sum_xy / sum_x2, 2) as slope_revenue_per_year,
    ROUND(avg_y - (sum_xy / sum_x2) * avg_x, 2) as intercept
FROM trend_stats;

-- 10. EXPORT VIEWS FOR DASHBOARD
-- ==============================

-- Create view for dashboard consumption
CREATE OR REPLACE VIEW dashboard_summary AS
SELECT 
    reporting_period,
    fiscal_year,
    total_revenue,
    reserve_income,
    operating_income,
    net_income,
    usdc_circulation,
    ROUND((operating_income / total_revenue) * 100, 2) as operating_margin_pct,
    ROUND((net_income / total_revenue) * 100, 2) as net_margin_pct,
    ROUND((reserve_income / total_revenue) * 100, 2) as reserve_income_pct
FROM crcl_financials
WHERE total_revenue IS NOT NULL
ORDER BY fiscal_year;

-- Financial metrics summary
CREATE OR REPLACE VIEW financial_metrics_summary AS
SELECT 
    COUNT(*) as total_periods,
    MIN(fiscal_year) as first_year,
    MAX(fiscal_year) as last_year,
    ROUND(AVG(total_revenue), 2) as avg_revenue,
    ROUND(MAX(total_revenue), 2) as max_revenue,
    ROUND(MIN(total_revenue), 2) as min_revenue,
    ROUND(AVG(CASE WHEN operating_income IS NOT NULL THEN (operating_income / total_revenue) * 100 END), 2) as avg_operating_margin,
    ROUND(AVG(CASE WHEN net_income IS NOT NULL THEN (net_income / total_revenue) * 100 END), 2) as avg_net_margin
FROM crcl_financials
WHERE total_revenue IS NOT NULL;

-- End of SQL queries
-- ==================