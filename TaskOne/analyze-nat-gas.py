#!/usr/bin/env python3

import os
import sys
import argparse
# import csv
import logging
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import seaborn as sns

# Run example:
# python analyze-nat-gas.py -f "data/Nat_Gas.csv" -l DEBUG

def parse_args():
    parser = argparse.ArgumentParser(description="Analyze natural gas prices.")
    parser.add_argument("-f", "--filename", type=str, help="Filename", required=True, dest="filename")
    parser.add_argument("-l", "--log_severity", type=str, help="Logging severity",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default="INFO", dest="log_sev")
    return parser.parse_args()

args = parse_args()

# Set up logging
log_sev = args.log_sev
log_dir = os.path.join(os.getcwd(), "logs")
os.makedirs("logs", exist_ok=True)
log_format = "[%(levelname)s] %(asctime)s (%(filename)s:%(lineno)d) %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

log_name = os.path.join(log_dir, "analyze-nat-gas.log")
# preserve old logs
if os.path.exists(log_name):
    old_log_name = os.path.join(log_dir, "analyze-nat-gas.{}.log".format(time.strftime("%Y-%m-%d-%H:%M:%S")))
    os.rename(log_name, os.path.join(log_dir, old_log_name))

logging.basicConfig(level=getattr(logging, log_sev),
                    format=log_format,
                    datefmt=date_format,
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(log_name),
                    ])

# hide matplotlib font messages
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
logging.Formatter.converter = time.gmtime


def load_data(filename: str):
    if not os.path.exists(filename):
        logging.error("File %s does not exist", filename)
        sys.exit(1)

    df = None
    with open(filename, "r") as fin:
        try:
            df = pd.read_csv(fin, parse_dates=["Dates"], date_parser=lambda x: pd.to_datetime(x, format="%m/%d/%y"))
        except Exception as e:
            logging.error("Failed to read %s: %s", filename, e)
            sys.exit(1)

    if df is None:
        logging.error("Failed to read %s", filename)
        sys.exit(1)

    # Drop rows with missing values
    df.dropna(inplace=True)

    logging.debug("Loaded nat gas file %s into dataframe: \n%s\n", filename, df.describe())
    logging.debug("df:\n%s\n", df)

    return df


def analyze_df(df: pd.DataFrame):

    logging.info("Analyzing dataframe...\n")

    logging.info("df.shape:\n%s\n", df.shape)

    logging.info("df.dtypes:\n%s\n", df.dtypes)

    logging.info("df.info:\n%s\n", df.info)

    logging.info("df.describe:\n%s\n", df.describe())

    logging.info("df.head:\n%s\n", df.head())

    logging.info("\nCalculating statistics...\n")

    logging.info("\ndf['Prices'].mean:\n%s\n", df['Prices'].mean())

    logging.info("\ndf['Prices'].std:\n%s\n", df['Prices'].std())

    logging.info("\ndf['Prices'].median:\n%s\n", df['Prices'].median())

    logging.info("\ndf['Prices'].mode:\n%s\n", df['Prices'].mode())

    logging.info("\ndf['Prices'].skew:\n%s\n", df['Prices'].skew())

    logging.info("\ndf['Prices'].kurt:\n%s\n", df['Prices'].kurt())

    logging.info("\ndf['Prices'].var:\n%s\n", df['Prices'].var())

    logging.info("\ndf['Prices'].quantile:\n%s\n", df['Prices'].quantile())

    logging.info("\ndf['Prices'].min:\n%s\n", df['Prices'].min())

    logging.info("\ndf['Prices'].max:\n%s\n", df['Prices'].max())

    logging.info("\ndf['Prices'].sum:\n%s\n", df['Prices'].sum())


def plot_df(df: pd.DataFrame):

    logging.info("Plotting dataframe...")

    # print(plt.style.available)
    plt.style.use('seaborn-v0_8-pastel')
    sns.set_theme(style="darkgrid")
    plt.figure(figsize=(10, 6))
    plt.title("National Gas Prices", fontsize=14, fontweight='bold')
    plt.xlabel("Dates (Last Day of the Month)", fontsize=12, fontweight='bold')
    plt.ylabel("Prices (USD)", fontsize=12, fontweight='bold')

    plt.scatter(df["Dates"], df["Prices"])

    # show every 3rd month on x-axis to not be too cluttered
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))  # Full date format
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Set major ticks to be every 3 days

    # money with two places past the decimal
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'$ {x:.2f}'))

    plt.gcf().autofmt_xdate()  # Rotate date labels to fit
    plt.grid(True)
    plt.gca().tick_params(axis='x', pad=0)  # Adjust padding to bring labels closer

    # Annotate highest and lowest points
    min_price = df["Prices"].min()
    max_price = df["Prices"].max()

    ylim_buffer = (max_price - min_price) * 0.15
    plt.ylim(min_price - ylim_buffer, max_price + ylim_buffer)

    # save plot
    visuals_dir = os.path.join(os.getcwd(), "visuals")
    os.makedirs(visuals_dir, exist_ok=True)
    # preserve old plots
    if os.path.exists(os.path.join(visuals_dir, 'scatter_nat_gas.png')):
        old_plot_name = os.path.join(visuals_dir, 'scatter_nat_gas.{}.png'.format(time.strftime("%Y-%m-%d-%H:%M:%S")))
        os.rename(os.path.join(visuals_dir, 'scatter_nat_gas.png'), old_plot_name)

    plot_name = os.path.join(visuals_dir, 'scatter_nat_gas.png')
    plt.savefig(plot_name)

    logging.info("Saved plot to %s", os.path.join(visuals_dir, 'scatter_nat_gas.png'))

    plt.show()

    return plot_name


def main():

    load_data(args.filename)

    df = load_data(args.filename)

    if log_sev == "DEBUG":
        analyze_df(df)

    plot_name = plot_df(df)

    print(f'\n{log_name = }\n')

    print(f'{plot_name = }\n')


if __name__ == "__main__":
    main()
