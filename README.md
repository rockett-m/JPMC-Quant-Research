## Introduction
This repo is for the [JPMorgan Quant Research program
](https://www.theforage.com/simulations/jpmorgan/quantitative-research-11oc)


### Setup

#### Virtual Environment
```console
brew install virtualenv
```

```console
virtualenv -p python3.12 .venv_jpmc_quant
```

```console
source .venv_jpmc_quant/bin/activate
```

```console
pip install -r requirements.txt
```

## Task One
After asking around for the source of the existing data, you learn that the current process is to take a monthly snapshot of prices from a market data provider, which represents the market price of natural gas delivered at the end of each calendar month. This data is available for roughly the next 18 months and is combined with historical prices in a time series database. After gaining access, you are able to download the data in a CSV file. "Nat_Gas.csv"
You should use this monthly snapshot to produce a varying picture of the existing price data, as well as an extrapolation for an extra year, in case the client needs an indicative price for a longer-term storage contract.

Download the monthly natural gas price data. "Nat_Gas.csv"
    
- Each point in the data set corresponds to the purchase price of natural gas at the end of a month, from 31st October 2020 to 30th September 2024.
    
- Analyze the data to estimate the purchase price of gas at any date in the past and extrapolate it for one year into the future. 
    
- Your code should take a date as input and return a price estimate.
    
Try to visualize the data to find patterns and consider what factors might cause the price of natural gas to vary. This can include looking at months of the year for seasonal trends that affect the prices, but market holidays, weekends, and bank holidays need not be accounted for.

## Task Two

## Task Three

## Task Four

