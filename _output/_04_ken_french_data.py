#!/usr/bin/env python
# coding: utf-8

# # 04. Ken French Data and Pandas DataReader
# 
# Pandas DataReader is a powerful tool that provides easy access to various financial data sources through a consistent API.
# The [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html), accessible through pandas_datareader, offers a comprehensive collection of:
# 
#  - Historical stock returns organized into various portfolios
#  - Risk factors (like market, size, value, momentum)
#  - Pre-calculated research datasets commonly used in empirical asset pricing
# 
# In this notebook, we'll explore how to access and use these datasets using pandas_datareader.
# 
# ## Browsing the Data
# 
# First, let's see what datasets are available:
# 

# In[ ]:


import warnings

import pandas as pd
from pandas_datareader.famafrench import get_available_datasets
import pandas_datareader.data as web


# In[ ]:


len(get_available_datasets())


# In[ ]:


get_available_datasets()


# For this short demo, let's focus on `25_Portfolios_OP_INV_5x5_daily`, which is a dataset of 25 portfolios of stocks 25 sorted based on Operating Profitability and Investment
# 
# Note that there are 3 that are very similar:
# 
#  - `25_Portfolios_OP_INV_5x5`
#  - `25_Portfolios_OP_INV_5x5_Wout_Div`
#  - `25_Portfolios_OP_INV_5x5_daily`
# 
# You can find more information these portfolios [here:](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/tw_5_ports_op_inv.html)
# 
# 
# 
# > **Univariate Sort Portfolios Formed on Investment**
# >
# > **Daily Returns**:	 	July 1, 1963 - November 30, 2024
# >
# > **Monthly Returns**:	 	July 1963 - November 2024
# >
# > **Annual Returns**:	 	1964 - 2023
# >
# > **Construction**:	 	The portfolios, which are constructed at the end of each June, are the intersections of 5 portfolios formed on profitability (OP) and 5 portfolios formed on investment (Inv). OP for June of year t is annual revenues minus cost of goods sold, interest expense, and selling, general, and administrative expenses divided by book equity for the last fiscal year end in t-1. The OP breakpoints are NYSE quintiles. Investment is the change in total assets from the fiscal year ending in year t-2 to the fiscal year ending in t-1, divided by t-2 total assets. The Inv breakpoints are NYSE quintiles.
# > 	 	 
# > Please be aware that some of the value-weight averages of operating profitability for deciles 1 and 10 are extreme. These are driven by extraordinary values of OP for individual firms. We have spot checked the accounting data that produce the extraordinary values and all the numbers we examined accurately reflect the data in the firm's accounting statements.
# > 	 	 
# >**Stocks**:	 	The portfolios for July of year t to June of t+1 include all NYSE, AMEX, and NASDAQ stocks for which we have (positive) BE for t-1, total assets data for t-2 and t-1, non-missing revenues data for t-1, and non-missing data for at least one of the following: cost of goods sold, selling, general and administrative expenses, or interest expense for t-1.
# 

# ## DISCUSSION: Why characteristic-based portfolios?
# 
# Suppose I thought that stocks with, say, high operating profitability and low investment are more likely to be undervalued. Why would I be interested in forming _portfolios_ based off of this characteristic rather just choose 1 or two stocks of companies that have high operating profitability and low investment?
# 
#  - Testing theories?
#  - Diversification?

# ## Accessing the Data
# 
# ### Portfolio Sorts, Characteristic-Based Portfolios

# In[ ]:


with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message="The argument 'date_parser' is deprecated",
    )
    ds = web.DataReader('25_Portfolios_OP_INV_5x5_daily', 'famafrench')


# In[ ]:


ds.keys()


# In[ ]:


ds


# In[ ]:


print(ds["DESCR"])


# In[ ]:


ds[0].tail()


# In[ ]:


ds[0].info()


# ### Benchmark Data
# 
# Let's also download some benchmark data.

# In[ ]:


with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=FutureWarning,
        message="The argument 'date_parser' is deprecated",
    )
    dbs = web.DataReader('F-F_Research_Data_Factors_daily', 'famafrench')

dbs.keys()


# In[ ]:


print(dbs["DESCR"])


# In[ ]:


dbs[0].tail()


# Note, based on the description provided, Ken French's 5x5 portfolios are formed using independent sorts, but with an important nuance:
# 
# 1. The breakpoints (quintiles) for both Operating Profitability and Investment are determined using **NYSE stocks only**
# 
# 2. However, the portfolios themselves include **all stocks** (NYSE, AMEX, and NASDAQ) that meet the data requirements
# 
# This methodology means:
# - The breakpoints are not influenced by the typically smaller AMEX and NASDAQ stocks
# - When all stocks are sorted into the portfolios using these NYSE-based breakpoints, the resulting portfolios will likely NOT have equal value weights
# - This is intentional - it helps address issues with microcaps while still including the broader universe of stocks
# 
# This is different from what you described with median cuts where you might expect equal weights. The use of NYSE breakpoints but all-stock portfolios means some portfolios (especially those containing small NASDAQ stocks) might end up with more firms but smaller total market cap than others.
# 
# This methodology has become standard in the empirical asset pricing literature precisely because it handles the size-based peculiarities of the US stock market in a systematic way.
# 

# ## Performance Analysis
# 
# Now, let's analyze the performance of one of these portfolios. Let's create a tear sheet for the portfolio.
# A "tear sheet" is a comprehensive summary of portfolio performance that includes key metrics and visualizations. Common components include:
# * Risk metrics (Sharpe ratio, maximum drawdown, Value at Risk)
# * Return statistics (CAGR, monthly/annual returns, win rates)
# * Risk-adjusted performance measures (Sortino ratio, Calmar ratio)
# * Visual analytics (drawdown plots, return distributions, rolling statistics)
# 
# The [QuantStats package](https://github.com/ranaroussi/quantstats) is just a small, demo package that provides some quick analytics for use to work with. It combines statistical analysis with visualization capabilities, making it easy to create portfolio reports. The package can also generate HTML tear sheets that include a nice array of metrics and plots. In the future, you'll want to create your own customized code to create tear sheets. But, for now, let's use theirs.
# 
# 
# Here's a simple example. 
# 
# First, let's create a dataframe with the portfolio returns and the benchmark returns.
# 

# In[ ]:


portfolio_returns = ds[0][["HiOP LoINV"]]


# In[ ]:


portfolio_returns.tail()


# In[ ]:


df = pd.concat([portfolio_returns, dbs[0]], axis=1)
df["Mkt"] = df["Mkt-RF"] + df["RF"]

# df.index = df.index.to_timestamp()

df = df/100
df.tail()



# In[ ]:


import quantstats as qs

qs.extend_pandas()

# Generate HTML tear sheet comparing the portfolio to the S&P 500
# qs.reports.basic(df["HiOP LoINV"], benchmark=df["Mkt"], rf=df["RF"].mean(), periods_per_year=12)
qs.reports.basic(df["HiOP LoINV"], benchmark=df["Mkt"], rf=df["RF"].mean())


# In[ ]:


# qs.reports.full(df["HiOP LoINV"], benchmark=df["Mkt"], rf=df["RF"].mean(), periods_per_year=12)
# qs.reports.full(df["HiOP LoINV"], benchmark=df["Mkt"], rf=df["RF"].mean())


# In[ ]:




