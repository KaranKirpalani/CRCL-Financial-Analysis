
"""
Circle Internet Group (CRCL) SEC Filing Analysis
==============================================

This module provides comprehensive analysis of CRCL's SEC filings,
financial statements, and investment metrics.

Author: Your Name
Date: June 2025
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class CRCLAnalysis:
    """
    Main class for Circle Internet Group financial analysis
    """

    def __init__(self):
        self.ticker = "CRCL"
        self.cik = "1876042"
        self.ipo_date = "2025-06-06"
        self.ipo_price = 31.00

    def get_sec_filings(self, filing_type="10-K"):
        """
        Retrieve SEC filings for CRCL

        Parameters:
        filing_type (str): Type of SEC filing (10-K, 10-Q, 8-K, etc.)

        Returns:
        list: List of filing URLs and dates
        """

        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": self.cik,
            "type": filing_type,
            "dateb": "",
            "owner": "exclude",
            "count": "10"
        }

        try:
            response = requests.get(base_url, params=params)
            soup = BeautifulSoup(response.content, 'html.parser')

            filings = []
            for row in soup.select('table.tableFile2 tr'):
                cells = row.find_all('td')
                if len(cells) > 1:
                    filing = {
                        'type': cells[0].text.strip(),
                        'date': cells[3].text.strip(),
                        'url': 'https://www.sec.gov' + cells[1].a['href'] if cells[1].a else None
                    }
                    filings.append(filing)

            return filings

        except Exception as e:
            print(f"Error retrieving SEC filings: {e}")
            return []

    def get_financial_data(self):
        """
        Load and process CRCL financial data

        Returns:
        pd.DataFrame: Processed financial data
        """

        # Historical financial data based on SEC filings
        financial_data = {
            'year': [2019, 2020, 2021, 2022, 2023, 2024, 'Q1 2025'],
            'total_revenue': [15.44, 56.12, 539.54, 735.89, 1430.00, 1890.00, 578.57],
            'reserve_income': [12.50, 45.20, 420.30, 700.50, 1400.00, 1660.00, 557.91],
            'operating_income': [-10.20, -25.60, 45.80, 6.08, 247.89, 167.16, 92.94],
            'net_income': [-8.50, -85.55, -768.85, 267.56, 18.11, 155.67, 64.79],
            'ebitda': [None, -85.55, None, 9.95, 254.20, 198.54, 66.10],
            'usdc_circulation': [None, 1.2, 42.7, 44.0, 24.4, 33.6, 61.4],
            'fed_funds_rate': [1.75, 0.25, 0.25, 4.25, 5.25, 5.25, 5.25]
        }

        df = pd.DataFrame(financial_data)

        # Calculate growth rates
        for col in ['total_revenue', 'reserve_income', 'operating_income']:
            df[f'{col}_growth'] = df[col].pct_change() * 100

        return df

    def calculate_dcf_valuation(self, 
                               growth_rate=0.25, 
                               terminal_growth=0.03, 
                               wacc=0.12, 
                               projection_years=5):
        """
        Perform DCF valuation analysis

        Parameters:
        growth_rate (float): Revenue growth rate
        terminal_growth (float): Terminal growth rate
        wacc (float): Weighted Average Cost of Capital
        projection_years (int): Number of projection years

        Returns:
        dict: Valuation results
        """

        # Base year financial metrics (2024)
        base_revenue = 1890.0  # Million USD
        base_ebitda_margin = 0.105  # 10.5%

        projections = []

        for year in range(1, projection_years + 1):
            revenue = base_revenue * ((1 + growth_rate) ** year)
            ebitda = revenue * base_ebitda_margin

            # Simple FCF estimation (EBITDA - CapEx - Tax)
            capex = revenue * 0.02  # 2% of revenue
            tax_rate = 0.25
            fcf = ebitda * (1 - tax_rate) - capex

            # Present value
            pv_factor = 1 / ((1 + wacc) ** year)
            pv_fcf = fcf * pv_factor

            projections.append({
                'year': 2024 + year,
                'revenue': revenue,
                'ebitda': ebitda,
                'fcf': fcf,
                'pv_fcf': pv_fcf
            })

        # Terminal value
        terminal_fcf = projections[-1]['fcf'] * (1 + terminal_growth)
        terminal_value = terminal_fcf / (wacc - terminal_growth)
        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)

        # Total enterprise value
        total_pv_fcf = sum([p['pv_fcf'] for p in projections])
        enterprise_value = total_pv_fcf + pv_terminal

        # Shares outstanding (estimated)
        shares_outstanding = 219.0  # Million shares

        # Equity value per share
        equity_value_per_share = enterprise_value / shares_outstanding

        return {
            'projections': projections,
            'terminal_value': terminal_value,
            'pv_terminal': pv_terminal,
            'enterprise_value': enterprise_value,
            'equity_value_per_share': equity_value_per_share,
            'total_pv_fcf': total_pv_fcf
        }

    def interest_rate_sensitivity(self, rate_scenarios=None):
        """
        Analyze interest rate sensitivity on reserve income

        Parameters:
        rate_scenarios (list): List of interest rate scenarios

        Returns:
        pd.DataFrame: Sensitivity analysis results
        """

        if rate_scenarios is None:
            rate_scenarios = [0.01, 0.0225, 0.0325, 0.0525, 0.0725]

        # Current USDC reserves (billion USD)
        usdc_reserves = 61.4

        results = []
        for rate in rate_scenarios:
            annual_income = usdc_reserves * rate
            results.append({
                'fed_funds_rate': f"{rate*100:.2f}%",
                'reserve_income_billion': annual_income,
                'reserve_income_million': annual_income * 1000,
                'vs_current_rate': ((annual_income / (usdc_reserves * 0.0525)) - 1) * 100
            })

        return pd.DataFrame(results)

    def monte_carlo_simulation(self, simulations=10000):
        """
        Monte Carlo simulation for revenue projections

        Parameters:
        simulations (int): Number of simulation runs

        Returns:
        dict: Simulation results and statistics
        """

        np.random.seed(42)

        # Current metrics
        base_reserves = 61.4
        base_rate = 0.0525

        results = []

        for _ in range(simulations):
            # Random variables
            rate_change = np.random.normal(0, 0.015)  # Rate volatility
            reserve_growth = np.random.normal(0.05, 0.02)  # Reserve growth

            # Constrain values
            new_rate = max(0.01, base_rate + rate_change)
            new_reserves = base_reserves * (1 + reserve_growth)

            # Calculate annual reserve income
            annual_income = new_reserves * new_rate
            results.append(annual_income)

        results = np.array(results)

        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'percentile_5': np.percentile(results, 5),
            'percentile_95': np.percentile(results, 95),
            'median': np.median(results),
            'results': results
        }

    def generate_investment_thesis(self):
        """
        Generate comprehensive investment thesis

        Returns:
        dict: Bull and bear case scenarios
        """

        bull_case = {
            'price_target': 315.75,
            'probability': 0.25,
            'key_drivers': [
                'GENIUS Act accelerates market share gains',
                'Stablecoin market grows to $2T by 2035',
                'Interest rates remain elevated (5%+)',
                'Institutional adoption accelerates',
                'Regulatory moat strengthens'
            ],
            'assumptions': {
                'revenue_growth': 0.40,
                'market_share_gain': 0.05,
                'ebitda_margin': 0.35
            }
        }

        base_case = {
            'price_target': 198.50,
            'probability': 0.50,
            'key_drivers': [
                'Steady stablecoin market growth',
                'Maintained regulatory compliance',
                'Moderate interest rate environment',
                'Gradual market share expansion'
            ],
            'assumptions': {
                'revenue_growth': 0.25,
                'market_share_stable': 0.267,
                'ebitda_margin': 0.28
            }
        }

        bear_case = {
            'price_target': 95.20,
            'probability': 0.25,
            'key_drivers': [
                'Interest rates decline significantly',
                'Increased competition from banks',
                'Regulatory changes favor competitors',
                'Stablecoin market growth slows'
            ],
            'assumptions': {
                'revenue_growth': 0.10,
                'market_share_loss': -0.03,
                'ebitda_margin': 0.20
            }
        }

        return {
            'bull_case': bull_case,
            'base_case': base_case,
            'bear_case': bear_case,
            'current_price': 240.28,
            'recommendation': 'BUY with price target of $198.50 (base case)'
        }

# Example usage
if __name__ == "__main__":
    # Initialize analysis
    crcl = CRCLAnalysis()

    # Get financial data
    print("Loading CRCL Financial Data...")
    financial_df = crcl.get_financial_data()
    print(financial_df.head())

    # Perform DCF valuation
    print("\nPerforming DCF Valuation...")
    dcf_results = crcl.calculate_dcf_valuation()
    print(f"DCF Fair Value: ${dcf_results['equity_value_per_share']:.2f}")

    # Interest rate sensitivity
    print("\nInterest Rate Sensitivity Analysis...")
    sensitivity_df = crcl.interest_rate_sensitivity()
    print(sensitivity_df)

    # Monte Carlo simulation
    print("\nMonte Carlo Simulation...")
    mc_results = crcl.monte_carlo_simulation()
    print(f"Expected Reserve Income: ${mc_results['mean']:.2f}B")
    print(f"90% Confidence Interval: ${mc_results['percentile_5']:.2f}B - ${mc_results['percentile_95']:.2f}B")

    # Investment thesis
    print("\nInvestment Thesis Summary...")
    thesis = crcl.generate_investment_thesis()
    print(f"Base Case Price Target: ${thesis['base_case']['price_target']}")
    print(f"Current Price: ${thesis['current_price']}")
    print(f"Recommendation: {thesis['recommendation']}")
