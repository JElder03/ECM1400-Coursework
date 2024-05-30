# better variable names for month averages and day average (all round?)
# fix global stations?
import numpy as np
import pandas as pd
import typing as t

from utils import *

def daily_average(data: list[pd.DataFrame], monitoring_station: str, pollutant: str) -> list[float]:

    averages = []
    for day in [data[monitoring_station][pollutant][x:x+24] for x in range(0, len(data[monitoring_station][pollutant]), 24)]:
        day = day[~np.isnan(day)]
        if len(day) == 0:
            averages.append(np.NAN)
        else:
            averages.append(meannvalue(list(day)))
    return averages


def daily_median(data: list[np.ndarray[np.void]], monitoring_station: str, pollutant: str) -> list[float]:

    medians = []
    
    for day in [data[monitoring_station][pollutant][x:x+24] for x in range(0, len(data[monitoring_station][pollutant]), 24)]:
        day = day[~np.isnan(day)]
        if len(day) == 0:
            medians.append(np.NAN)
        else:
            medians.append(np.median(list(day)))
    return medians

def hourly_average(data: list[np.ndarray[np.void]], monitoring_station: str, pollutant: str) -> list[float]:
    
    averages = []
    
    for hour in [data[monitoring_station][pollutant][x::24] for x in range(24)]:
        hour = hour[~np.isnan(hour)]
        if len(hour) == 0:
            averages.append(np.NAN)
        else:
            averages.append(meannvalue(list(hour)))
    return averages

def monthly_average(data: list[np.ndarray[np.void]], monitoring_station: str, pollutant: str) -> list[float]:

    averages = []
    
    #create a DataFrame of months only by slicing the dates in data
    months_start = data[monitoring_station]['date'].str[5:7]
    #create a DataFrame from the previous with True at an index if that inex matches the previous, False otherwise
    months_start = months_start.eq(months_start.shift())
    #create a list from the previous DataFrame of the indexes of all False values.
    #this is a list of indexes of the begining of each month in the "date" column of the data DataFrame
    months_start = [index for index, value in enumerate(months_start) if not value] + [None]

    for month in [data[monitoring_station][pollutant][start:end] for start, end in zip(months_start, months_start[1:])]:
        month = month[~np.isnan(month)]
        if len(month) == 0:
            averages.append(np.NAN)
        else:
            averages.append(meannvalue(list(month)))
    return averages


def peak_hour_date(data: list[np.ndarray[np.void]], date: str, monitoring_station: str, pollutant: str) -> float|int:

    day_indexes = list(data[monitoring_station][data[monitoring_station]['date'] == date].index)
    day = data[monitoring_station][pollutant][day_indexes[0]:day_indexes[-1]+1]
    day = day[~np.isnan(day)]
    
    if len(day) == 0:
        return(np.NAN)
    else:
        return(maxvalue(list(day)))

    
def count_missing_data(data: list[np.ndarray[np.void]], monitoring_station: str, pollutant: str) -> int:
    
    return(sum(data[monitoring_station][pollutant].isnull()))


def fill_missing_data(data: list[np.ndarray[np.void]], monitoring_station: str, pollutant: str, new_value: t.Any) -> list:

    data[monitoring_station][pollutant] = data[monitoring_station][pollutant].replace(np.NAN, new_value)
    return (data)
