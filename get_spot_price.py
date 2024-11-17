from entsoe import EntsoePandasClient
import pandas as pd
from pandas.core.groupby.generic import DataFrameGroupBy, SeriesGroupBy
import os
import matplotlib.pyplot as plt

def __hourly_based(df: pd.DataFrame):
    ax = df.plot(x="DateTime", y="Price", kind="line", figsize=(30,10))
    ax.set_ylabel('DateTime')
    ax.set_ylabel('Spot price (c€)')
    ax.set_title('Spot price, hourly based (ALV24)')
    xticks = list(range(0, len(df["DateTime"]), int(df.shape[0] / 20)))
    ax.set_xticks(xticks)
    plt.xticks(rotation=75)
    ax.set_xticklabels(df['year_month'][xticks])
    plt.subplots_adjust(bottom=0.2)
    plt.savefig('hourly_based.png')
    plt.close()

def __monthly_based(df_group_by_month: SeriesGroupBy):
    ax = df_group_by_month.mean().plot(kind="line", figsize=(30,10))
    ax.set_xlabel('DateTime')
    ax.set_ylabel('Spot price (c€)')
    ax.set_title('Spot price, monthly average (ALV24)')
    plt.xticks(rotation=75)
    plt.subplots_adjust(bottom=0.2)
    plt.axhline(y=10, color='y', linestyle='-')
    plt.savefig('monthly_based.png')
    plt.close()

def __create_graph(path_spot_price_alv0: str):
    df:pd.DataFrame = pd.read_csv(path_spot_price_alv0)
    df.columns = ["DateTime", "Price"]
    df["Price"] = df["Price"] * 1.24 / 10
    df:pd.DataFrame = df[df[
        "DateTime"] >= "2017-01-01 00:02:00+02:00"].reset_index(drop=True)
    df['iso8601_date'] = pd.to_datetime(df['DateTime'], utc=True)
    df['year_month'] = df['iso8601_date'].dt.to_period("M")
    df_group_by_month: SeriesGroupBy = df.groupby(["year_month"])["Price"]
    __hourly_based(df)
    __monthly_based(df_group_by_month)
    print(df)

def __get_and_save_spot_price(path_spot_price_alv0: str):
    client = EntsoePandasClient(api_key="{:s}".format(os.environ["ENTSOE_API_KEY"]))
    start = pd.Timestamp('20220101', tz='Europe/Helsinki')
    end = pd.Timestamp('20241231', tz='Europe/Helsinki')
    country_code = 'FI'
    df: pd.DataFrame = client.query_day_ahead_prices(country_code, start=start, end=end)
    print(df.dtypes)
    df.to_csv(path_spot_price_alv0)

def main():
    script_folder: str = os.path.dirname(os.path.realpath(__file__))
    path_spot_price_alv0: str = "{:s}/{:s}".format(script_folder, "PreprocessedData/Spot_Price_Alv0_Table.csv")
    __get_and_save_spot_price(path_spot_price_alv0)
    __create_graph(path_spot_price_alv0)

if __name__ == "__main__":
    main()
