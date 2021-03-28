'''
This file uses yfinance to pull data from Yahoo Finance
screens for leverage ratios
should return a database of companies that fit our reqs
'''

import yfinance as yf
import csv
import requests
import pandas as pd
import numpy as np


def get_ticker_lst():
    '''
    This function reads an excel file and creates a list from all the tickers
    from US stock exchanges, ie. NYSE, Nasdaq, AMEX (totalling ~19k tickers)
    Inputs: nothing
    Returns: lst of str
    '''
    ticker_lst = []
    ticker_data = pd.read_excel('all-tickers.xlsx', header=None)
    ticker_lst = ticker_data[0].values.tolist()
    return ticker_lst


def calculate_altman_score(ticker):
    '''
    Given a ticker, find its Altman Z score
    Input: ticker (str)
    Returns: Altman Zscore (int) or None
        ** A score below 1.8 means it's likely the company is headed for bankruptcy,
        while companies with scores above 3 are not likely to go bankrupt **
    '''
    try:
        balance_sheet = yf.Ticker(ticker).balance_sheet
        income_statement = yf.Ticker(ticker).earnings
        if balance_sheet.empty:
            print(ticker + "'s balance sheet is empty!")
            return None
        if income_statement.empty:
            print(ticker + "'s income statement is empty!")
            return None
        first_column = balance_sheet.columns[0]
        total_assets = int(balance_sheet.loc["Total Assets", str(first_column)])
        total_liabilities = int(balance_sheet.loc["Total Liab", str(first_column)])
        working_capital = int(balance_sheet.loc["Total Current Assets", str(
                                    first_column)]) - int(balance_sheet.loc[
                                    "Total Current Liabilities", str(first_column)])
        retained_earnings = int(balance_sheet.loc["Retained Earnings", str(first_column)])
        sales = income_statement.iloc[-1, 0] #technically getting revenue lel
        mv_equity = yf.Ticker(ticker).info['marketCap']
        ebit = yf.Ticker(ticker).info['operatingMargins'] * sales
    except (KeyError, ValueError):
        print ("There is not enough data on " + ticker)
        return None

    A = working_capital / total_assets
    B = retained_earnings / total_assets
    C = ebit / total_assets
    D = mv_equity / total_liabilities
    E = sales / total_assets

    z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
    return z_score


def determine_market_cap_size(ticker):
    '''
    Given ticker, determiner what market size the company is
    '''
    market_cap = yf.Ticker(ticker).info['marketCap']
    if market_cap <= 500000000:
        market_cap_size = "nano-cap"
    elif 50000000 < market_cap <= 300000000:
        market_cap_size = "micro-cap"
    elif 300000000 < market_cap <= 2000000000:
        market_cap_size = "small-cap"
    elif 2000000000 < market_cap <= 10000000000:
        market_cap_size = "mid-cap"
    elif 10000000000 < market_cap:    
        market_cap_size = "large-cap"
    market_cap_adj = "{:,}".format(market_cap)
    return market_cap_adj, market_cap_size
    

def run_database(threshold):
    '''
    This function finds the Altman score for all stock tickers
    If stock is not found on yfinance, then it is skipped over
    we also keep track of market cap
    Inputs:
        threshold value (float)
    Returns: all the companies that fit the threshold (dict) {stock ticker : Altman Z score}
            along with market cap size
    '''
    ticker_lst = get_ticker_lst()
    final_lst = {}
    missing_lst = []
    print(ticker_lst[1000:1005])
    for ticker in ticker_lst[1000:1005]:
        z_score = calculate_altman_score(ticker)
        if z_score == None:
            missing_lst.append(ticker)
            market_cap = "N/A"
            market_cap_size = "N/A"
            print ("Lack of data means " + ticker + "'s score cannot be determined")
        elif z_score <= threshold:
            z_score = round(z_score, 5)
            market_cap, market_cap_size = determine_market_cap_size(ticker)
            final_lst[ticker] = z_score, market_cap, market_cap_size
        print(ticker, z_score, market_cap, market_cap_size)
    return final_lst, missing_lst