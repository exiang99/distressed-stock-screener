'''
This file uses yfinance to pull data from Yahoo Finance
screens for leverage ratios
should return a database of companies that fit our reqs
'''

import yfinance as yf
import csv
import requests
import pandas as pd


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
    Returns: Altman Zscore (int)
        ** A score below 1.8 means it's likely the company is headed for bankruptcy,
        while companies with scores above 3 are not likely to go bankrupt **
    '''
    balance_sheet = yf.Ticker(ticker).balance_sheet
    cash_flow = yf.Ticker(ticker).cashflow
    income_statement = yf.Ticker(ticker).earnings

    total_assets = balance_sheet.iloc[4, 0]
    total_liabilities = balance_sheet.iloc[1, 0]
    working_capital = balance_sheet.iloc[18, 0] - balance_sheet.iloc[13, 0]
    retained_earnings = balance_sheet.iloc[7, 0]
    sales = income_statement.iloc[-1, 0] #technically getting revenue but whatever
    mv_equity = yf.Ticker(ticker).info['marketCap']
    ebit = yf.Ticker(ticker).info['operatingMargins'] * sales

    A = working_capital / total_assets
    B = retained_earnings / total_assets
    C = ebit / total_assets
    D = mv_equity / total_liabilities
    E = sales / total_assets

    z_score = 1.2*A + 1.4*B + 3.3*C + 0.6*D + 1.0*E
    return z_score


def run_database(threshold):
    '''
    This function finds the Altman score for all stock tickers
    If stock is not found on yfinance, then 
    Inputs:
        lst of tickers (lst)
        threshold value (float)
    Returns: all the company tickers that match the threshold (lst)
    '''
    ticker_lst = get_ticker_lst()
    
    pass
    # ticker_lst = get_ticker_lst()
    # for ticker in ticker_lst:
    #     stock = yf.Ticker(str(ticker))
    #     print(stock.info)