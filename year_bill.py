import os
import pytz
import pandas as pd
import numpy as np
import argparse
import warnings
pd.set_option('display.max_rows', None)

class YearBill():
    TIME_ZONE = pytz.timezone("Europe/Helsinki")
    PREPROCESSED_FOLDER: str = 'PreprocessedData'
    DEFA_RECORDS_FILE: str = 'Defa_Table.gzip'
    INPUT_FOLDER: str = "InputData"
    PARKING_PLACE_NAMES_FILE: str = "Chargeing_point_name.json"
    CHARGEING_POINT_OWNER_FILE_NAME: str = "Chargeing_point_owner_changes.json"
    ELECTRICITY_PRICES: str = "Electricity_Prices_V1.jsonl"


    def __init__(self, year: str) -> None:
        self.year: str = year
        self.startDate: str = f"{self.year}-01-01"
        self.endDate: str = f"{self.year}-12-31"
        print(f"Start date: {self.startDate}")
        print(f"End date: {self.endDate}")
        self.localStartTime, self.localEndTime = self.__setStartEndTime()
        print(f"Local start time: {self.localStartTime}")
        print(f"Local end time: {self.localEndTime}")
        self.chargeingRecords: pd.DataFrame = self.__readChargingRecords()
        self.chargeingRecords: pd.DataFrame = self.__addParkingPlaceName(self.chargeingRecords)
        self.chargeingRecords: pd.DataFrame = self.__addParkingPlaceOwner(self.chargeingRecords)
        self.__addYearMonthColumns(self.chargeingRecords)
        self.theFirstAndTheLastRecords: pd.DataFrame = self.__selectTheFirstAndTheLastRecordFromEveryParkingPlace(self.chargeingRecords)
        print(f"theFirstAndTheLastRecords:\n{self.theFirstAndTheLastRecords}")
        df_pivot:pd.DataFrame = self.theFirstAndTheLastRecords.pivot(index=['parkingPlaceId','Autopaikka', 'Owner_changed'], columns='year_month_start', values='UsedEnergy')
        df_pivot.fillna(0, inplace=True)
        df_pivot["Yhteensä"] = df_pivot.sum(axis=1)
        self.__read_electricity_prices(self.theFirstAndTheLastRecords)
        df_lasku_yhteenveto:pd.DataFrame = self.theFirstAndTheLastRecords.pivot(index=['parkingPlaceId','Autopaikka', 'Owner_changed'], columns='year_month_start', values='Kokonaishinta (€)')
        df_lasku_yhteenveto.fillna(0, inplace=True)
        df_lasku_yhteenveto["Yhteensä"] = df_lasku_yhteenveto.sum(axis=1)
        print(f"Pivot table:\n{df_pivot}")
        print(f"Lasku yhteenveto:\n{df_lasku_yhteenveto}")

    def __selectTheFirstAndTheLastRecordFromEveryParkingPlace(self, df: pd.DataFrame):
        grouped: pd.DataFrame = df.groupby(["Autopaikka", "year_month_start", "Owner_changed"])
        firstRecords: pd.DataFrame = grouped.first().reset_index()
        print(firstRecords[firstRecords["start_time"] < self.localStartTime].to_string(index=False))
        lastRecords = grouped.last().reset_index()
        print(lastRecords[lastRecords["end_time"] > self.localEndTime].to_string(index=False))
        merged = pd.merge(
            firstRecords[["Autopaikka", "Owner_changed", "year_month_start", "meterStartKwh", "parkingPlaceId"]],
            lastRecords[["Autopaikka", "Owner_changed", "year_month_start", "meterStopKwh"]],
            on=["Autopaikka", "year_month_start", "Owner_changed"],
            how="inner"
        )
        merged["UsedEnergy"] = (merged["meterStopKwh"] - merged["meterStartKwh"]).round(1)
        merged.reset_index(drop=True, inplace=True)
        merged = merged.sort_values(by=["parkingPlaceId", "year_month_start"]).reset_index(drop=True)
        return merged

    def __readChargingRecords(self):
        filePath: str = os.path.join(self.PREPROCESSED_FOLDER, self.DEFA_RECORDS_FILE)
        chargeingRecords: pd.DataFrame = pd.read_parquet(filePath)
        print(chargeingRecords.dtypes)
        filteredRecords = chargeingRecords[
            (chargeingRecords['end_time'] >= self.localStartTime) &
            (chargeingRecords['start_time'] <= self.localEndTime)
        ]
        return filteredRecords

    def __addParkingPlaceName(self, df: pd.DataFrame):
        parkingPlaceRecords: pd.DataFrame = self.__readParkingPlaceRecords()
        df = df.merge(
            parkingPlaceRecords[['Autopaikka', 'id', 'connectorId']],
            on=['id', 'connectorId'],
            how='left'
        )
        df["parkingPlaceId"] = df["Autopaikka"].str.extract(r'(\d+)$').astype(int)
        return df

    def __addParkingPlaceOwner(self, df: pd.DataFrame):
        filePath: str = os.path.join(self.INPUT_FOLDER, self.CHARGEING_POINT_OWNER_FILE_NAME)
        with open(filePath, "r") as file:
            parkingPlaceOwner: pd.DataFrame = pd.read_json(file, lines=True)
        parkingPlaceOwner: pd.DataFrame = parkingPlaceOwner[parkingPlaceOwner["start_date"] >= self.startDate]
        parking_places = set(parkingPlaceOwner["Autopaikka"])
        df["Owner_changed"] = df["Autopaikka"].map(lambda x: x in parking_places)
        df["Owner_changed"] = ""
        merged_df = df.merge(parkingPlaceOwner, on="Autopaikka", how="left", suffixes=("", "_owner"))
        merged_df.loc[
            (merged_df["start_time"] >= merged_df["start_date"]),
            "Owner_changed"
        ] = "New owner"
        return merged_df

    def __readParkingPlaceRecords(self):
        filePath: str = os.path.join(self.INPUT_FOLDER, self.PARKING_PLACE_NAMES_FILE)
        with open(filePath, "r") as file:
            parkingPlaceRecords: pd.DataFrame = pd.read_json(file, lines=True)
        return parkingPlaceRecords

    def __read_electricity_prices(self, theFirstAndTheLastRecords: pd.DataFrame):
        file_path: str = os.path.join(self.INPUT_FOLDER, self.ELECTRICITY_PRICES)
        file = open(file_path, "r")
        df: pd.DataFrame = pd.read_json(file, lines=True)
        df['startDate'] = pd.to_datetime(df['start_date']).dt.tz_localize(self.TIME_ZONE)
        df['endDate'] = pd.to_datetime(df['end_date']).dt.tz_localize(self.TIME_ZONE)
        df['year_month_start'] = df['startDate'].dt.to_period('M')
        df['year_month_end'] = df['endDate'].dt.to_period('M')
        siirto:pd.DataFrame = df[["Siirto", "year_month_start", "year_month_end", "alv"]][~df["Siirto"].isna()]
        energia:pd.DataFrame = df[["Energia", "year_month_start", "year_month_end", "alv"]][~df["Energia"].isna()]
        marginaali:pd.DataFrame = df[["Marginaali", "year_month_start", "year_month_end", "alv"]][~df["Marginaali"].isna()]
        vero:pd.DataFrame = df[["Vero", "year_month_start", "year_month_end", "alv"]][~df["Vero"].isna()]
        print(df)
        print(siirto)
        print(energia)
        print(marginaali)
        print(vero)
        def find_value(df, row, column_name):
            match = df[(df['year_month_start'] <= row['year_month_start']) &
                        ((df['year_month_end'].isna()) | (df['year_month_end'] >= row['year_month_start']))]
            return match[column_name].iloc[0] if not match.empty else np.nan

        theFirstAndTheLastRecords['SiirtoHinta'] = theFirstAndTheLastRecords.apply(lambda row: find_value(siirto, row, "Siirto"), axis=1)
        theFirstAndTheLastRecords['SiirtoALV'] = theFirstAndTheLastRecords.apply(lambda row: find_value(siirto, row, "alv"), axis=1)
        theFirstAndTheLastRecords['EnergiaHinta'] = theFirstAndTheLastRecords.apply(lambda row: find_value(energia, row, "Energia"), axis=1)
        theFirstAndTheLastRecords['EnergiaALV'] = theFirstAndTheLastRecords.apply(lambda row: find_value(energia, row, "alv"), axis=1)
        theFirstAndTheLastRecords['MarginaaliHinta'] = theFirstAndTheLastRecords.apply(lambda row: find_value(marginaali, row, "Marginaali"), axis=1)
        theFirstAndTheLastRecords['MarginaaliALV'] = theFirstAndTheLastRecords.apply(lambda row: find_value(marginaali, row, "alv"), axis=1)
        theFirstAndTheLastRecords['VeroHinta'] = theFirstAndTheLastRecords.apply(lambda row: find_value(vero, row, "Vero"), axis=1)
        theFirstAndTheLastRecords['VeroALV'] = theFirstAndTheLastRecords.apply(lambda row: find_value(vero, row, "alv"), axis=1)
        self.__calculateTotalPricePerKwh(theFirstAndTheLastRecords)
        theFirstAndTheLastRecords["Kokonaishinta (€)"] = (theFirstAndTheLastRecords["UsedEnergy"] * theFirstAndTheLastRecords["Hinta_per_kwh (c€)"] / 100).round(2)
        print(theFirstAndTheLastRecords)
        return df

    def __addYearMonthColumns(self, df: pd.DataFrame):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df['year_month_start'] = df['start_time'].dt.to_period('M')
            df['year_month_end'] = df['end_time'].dt.to_period('M')

    def __calculateTotalPricePerKwh(self, df:pd.DataFrame):
        df["Hinta_per_kwh (c€)"] = (df["SiirtoHinta"] * (1 + df["SiirtoALV"] / 100) +
                            df["EnergiaHinta"] * (1 + df["EnergiaALV"] / 100) +
                            df["MarginaaliHinta"] * (1 + df["MarginaaliALV"] / 100) +
                            df["VeroHinta"] * (1 + df["VeroALV"] / 100))

    def createBill(self):
        print(self.theFirstAndTheLastRecords.head().to_string())
        print(self.theFirstAndTheLastRecords.tail().to_string())
        print(self.theFirstAndTheLastRecords[["Autopaikka", "year_month_start", "meterStartKwh", "meterStopKwh", "UsedEnergy"]].to_string(index=False))

    def __setStartEndTime(self):
        localStartTime = pd.to_datetime(self.startDate).tz_localize(self.TIME_ZONE)
        localEndTime = pd.to_datetime(self.endDate).tz_localize(self.TIME_ZONE) + pd.Timedelta(hours=24, minutes=00, seconds=00)
        return localStartTime, localEndTime

def __parse_cmd_args():
    parser = argparse.ArgumentParser(
        description="Compare images with logging and optional name output"
    )
    parser.add_argument("year", type=str, help="A billing year")
    cmdLineArgs = vars(parser.parse_args())
    return cmdLineArgs


def __main():
    cmdLineArgs = __parse_cmd_args()
    yearBill: YearBill = YearBill(cmdLineArgs["year"])
    # yearBill.createBill()

if __name__ == "__main__":
    __main()
