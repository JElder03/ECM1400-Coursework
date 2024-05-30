import pandas as pd
import numpy as np
import os
pd.options.display.max_rows = 500

def get_live_data_from_api(endpoint: str, site_code = 'MY1', species_code = 'NO', start_date = None, end_date = None, group_name = 'London', air_quality_index = 1) -> dict:
    """
    Return data from the LondonAir API using its AirQuality API. 

    @param endpoint: An unformatted subdomain to get specific API data
    @param site_code: A code corresponding to a pollution monitoring site
    @param species_code: A code corresponding to a monitored pollutant
    @param start_date: Start of period to recieve data
    @param end_date: End of period to recieve data
    @param group_name: The name of a group of pollution monitoring sites
    @param air_quality_index: A number (1-10) indicating severity of pollution

    @return: Raw requested json data
    """

    import requests
    import datetime

    start_date = datetime.date.today() if start_date is None else start_date
    end_date = start_date + datetime.timedelta(days=1) if end_date is None else end_date
    endpoint = 'https://api.erg.ic.ac.uk/AirQuality' + endpoint
    url = endpoint.format(
        site_code = site_code,
        group_name = group_name,
        species_code = species_code,
        start_date = start_date,
        end_date = end_date,
        air_quality_index = str(air_quality_index),
        )
    
    try:
        response = requests.get(url, timeout = 30)
        if not response.json() is None:
            return response.json()
        else:
            raise Exception
    except TimeoutError:
        print("Connection timeout.\nCheck you are connected to the internet and try again.")
        raise TimeoutError
    except:
        raise Exception

def is_connected() -> bool:
    """
    Checks that user is connected to the internet

    @returns: True if user is connected to internet, else raises ConnectionError
    """

    import socket
    try:
        socket.create_connection(("1.1.1.1", 53))
        return True
    except OSError:
        pass
    raise ConnectionError

def unpack_json(json_data: dict, wrappers: list) -> pd.DataFrame:
    """
    Removes wrappers/keys from json dictionary, and converts it into a DataFrame

    @param json_data: Raw json dictionary data 
    @param wrappers: A list of wappers/superflouse data to be removed from the json

    @returns: The unwrapped json converted into a DataFrame
    @return: None if unwrapping fails 
    """

    try:
        for wrapper in wrappers:
            json_data = json_data[wrapper]
    except:
        return
    #if len(unwapped json) == 1, make it a list like len(unwapped json) > 1
    if type(json_data) == dict:
        json_data = [json_data]

    df = pd.DataFrame(json_data)
    df.columns = [column_name.replace('@','') for column_name in list(df)]
    df.index = np.arange(1, len(df) + 1)
    return df

def site_code_picker(need_live_data = False, need_group_values_only = False) -> str:
    """
    Allows user to select a monitoring site code from a list and get information about that monitoring site.

    @param need_live_data: A bool indicating wether legacy monitoring stations can be picked
    @param need_group_values_only: A bool indicating that the function is being used to gain monitoring site information only.

    @return: The site code of selected monitoring site and data about that site
    @return: None if user quits 
    """

    while True:
        if not need_group_values_only:
            group_name = group_name_picker()
            os.system('cls' if os.name == 'nt' else 'clear')
            if group_name is None:
                return
        if not need_group_values_only:
            group_values = unpack_json(get_live_data_from_api('/Information/MonitoringSites/GroupName={group_name}/Json', group_name = group_name), ['Sites', 'Site'])
        else:
            group_values = unpack_json(get_live_data_from_api('/Information/MonitoringSites/GroupName={group_name}/Json', group_name = 'All'), ['Sites', 'Site'])

        if group_values is None or (group_values[group_values['DateClosed'] == ''].size == 0 and need_live_data):
            print('There are currently no available sites in this monitoring site group')
            while True:
                user_choice = input('Would you like to pick a new monitoring site group? (y/n)\n')
                if user_choice.upper() == 'N': 
                    return
                elif user_choice.upper() == 'Y':
                    break
                else:
                    print('Your input is invalid')
        else:
            group_values['DateClosed'] = group_values['DateClosed'].replace('', 'Still Operating')
            if need_live_data:
                group_values = group_values[group_values['DateClosed'] == 'Still Operating']
            group_values.index = np.arange(1, len(group_values) + 1)
            break

    if not need_group_values_only:   
        print(group_values[['SiteName', 'SiteCode', 'SiteType', 'DateOpened', 'DateClosed']])
    
    while True:
        if not need_group_values_only:
            user_choice = input('Please input a number corresponding to the desired monitoring site code, or input "Q" to quit\n')
            if user_choice.upper() == 'Q':
                return
        try:
            return (group_values['SiteCode'][int(user_choice)] if not need_group_values_only else None), group_values
        except:
            print('The number you have inputed is invalid')
            continue

def group_name_picker() -> pd.DataFrame:
    """
    Allows user to select a monitoring site group from a list

    @return: A DataFrame of site code, date opened, etc. on all monitoring sites in selected group
    @return: None if user quits 
    """

    group_names = unpack_json(get_live_data_from_api('/Information/Groups/Json'), ['Groups', 'Group'])
    print(group_names[group_names.columns[0:2]])

    while True:
        user_choice = input('Please input a number corresponding to the group name (region) above which your desired monitoring site is in, or input "Q" to quit\n')
        if user_choice.upper() == 'Q':
            return
        try:
            return group_names['GroupName'][int(user_choice)]
        except:
            print("Your input is invalid")

def get_site_code_input() -> str:
    """
    Gets site code from user. User can enter site code themselve, or select from a list.

    @return user_site_code: Site code from user, and information about chosen site
    @return: None if user quits 
    """

    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print('Please input a number from the list below, or input Q to quit:',
        '\n1 - Find a monitoring site code\n2 - I already have a monitoring site code')
        user_choice = input().upper()
        if user_choice == 'Q':
            return
        elif user_choice == '1':
            response = site_code_picker(need_live_data = True)
            if response is None:
                return
            user_site_code, group_values = response
        elif user_choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            user_site_code = input('Please enter a monitoring site code\n').upper()
            group_values = site_code_picker(need_live_data = True, need_group_values_only = True)
            if group_values is None:
                return
            group_values = group_values[-1]
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Your input is invalid')
            continue  
        try:
            get_live_data_from_api('/Hourly/MonitoringIndex/SiteCode={site_code}/Json', site_code = str(user_site_code))
        except:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('The site code you have entered does not exist')
            continue
        return user_site_code, group_values
        
def get_dashboard_data(site_code:str) -> tuple[str, list, list, list, list, int, str, str, list, list]:
    """
    Retrieves all data displayed on live dashboard

    @param site_code: Code of monitoring site who's data is being displayed on dashboard
    
    @return site_code: Code of monitoring site who's data is being displayed on dashboard
    @return pollutant_codes: List of codes of all pollutants available from monitoring station
    @return pollutant_names: List of names of all pollutants available from monitoring station
    @return live_pollutant_values: Live pollutant values available from monitoring station
    @return latest_pollutant_values: Latest pollutant values available from monitoring station (i.e. not NaN) and date/time collected
    @return max_air_quality_index: The highest air quality index of all pollutants monitored
    @return advice: Advice corresponding to highest air quality index
    @return site_name: The name of the monitoring station
    @return date_and_time: Date/time of live pollutant data
    @return data: Live pollutant values and miscellaneous data (e.g. air quality band of each pollutant) 
    """

    if site_code is None:
        return
    hourly_response = get_live_data_from_api('/Hourly/MonitoringIndex/SiteCode={site_code}/Json', site_code = str(site_code))
    values_response = get_live_data_from_api('/Data/Site/SiteCode={site_code}/StartDate={start_date}/EndDate={end_date}/json', site_code = str(site_code))

    values_response = unpack_json(values_response, ['AirQualityData','Data'])
    data = unpack_json(hourly_response, ['HourlyAirQualityIndex', 'LocalAuthority', 'Site', 'species'])
    pollutant_codes = list(dict.fromkeys(list(data['SpeciesCode'])))
    pollutant_names = list(data['SpeciesName'])
    live_pollutant_values = list(map(lambda pollutant: values_response.loc[values_response['SpeciesCode'] == pollutant].iloc[-1]['Value'], pollutant_codes))
    latest_pollutant_values = list(map(lambda pollutant: get_latest_values(values_response, pollutant), pollutant_codes))

    max_air_quality_index = max(data['AirQualityIndex'])
    if max_air_quality_index == '0':
        advice = 'No Data'
    else:
        advice = unpack_json(get_live_data_from_api('/Information/IndexHealthAdvice/AirQualityIndex={air_quality_index}/Json', air_quality_index = max_air_quality_index), ['AirQualityIndexHealthAdvice','AirQualityBanding','HealthAdvice'])
    site_name = unpack_json(hourly_response, ['HourlyAirQualityIndex', 'LocalAuthority', 'Site'])['SiteName'][1]
    date_and_time = unpack_json(hourly_response, ['HourlyAirQualityIndex', 'LocalAuthority', 'Site'])['BulletinDate'][1]
    return(site_code, pollutant_codes, pollutant_names, live_pollutant_values, latest_pollutant_values, max_air_quality_index, advice, site_name, date_and_time, data)

def get_latest_values(values_response: pd.DataFrame, pollutant_code):
    """Your documentation goes here"""
    for i in range(len(values_response.loc[values_response['SpeciesCode'] == pollutant_code])):
        value = values_response.loc[values_response['SpeciesCode'] == pollutant_code].iloc[-(i+1)]['Value']
        date_collected = values_response.loc[values_response['SpeciesCode'] == pollutant_code].iloc[-(i+1)]['MeasurementDateGMT']
        if value != '':
            return (value, date_collected)
    return 'No Data'

def render_dashboard() -> None:
    """
    Prints data from get_dashboard_data(). Allows user to refresh data and choose to graph live values against historic data.

    @return: None if user quits
    """

    from datetime import datetime
    while True:
        response = get_dashboard_data(get_site_code_input()[0])
        if response is None:
            return 
        else:  
            site_code, pollutant_codes, pollutant_names, live_pollutant_values, latest_pollutant_values, max_air_quality_index, advice, site_name, date_and_time, data = response
            air_quality_bands = {0:'No Data', 1: 'Low', 2: 'Low', 3: 'Low', 4: 'Moderate', 5: 'Moderate', 6: 'Moderate', 7: 'High', 8: 'High', 9: 'High', 10:'Very Low'}
        os.system('cls' if os.name == 'nt' else 'clear')
        
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print('\nWELCOME TO THE REAL-TIME MONITORING DASHBOARD\n')
            print('DATA COLLECTED: ' + str(date_and_time) + ' ' * 10 + 'LAST UPDATED: ' + str(datetime.now())[11:19],
            ' ' * 10 + 'SITE NAME: '+ site_name + ' ' * 10 + 'SITE CODE: '+ site_code)
            print('\nCURRENT POLLUTANT LEVELS:')
            for i in range(len(pollutant_codes)):
                if live_pollutant_values[i] != '':
                    pollutant_value = (str(live_pollutant_values[i]) + ' ('+  str(date_and_time) + ')') 
                elif all([value == 'No Data' for value in latest_pollutant_values]):
                    pollutant_value = 'No Data'
                else:
                    pollutant_value = str(latest_pollutant_values[i][0]) + ' (' + str(latest_pollutant_values[i][1]) +')'
                print(str(pollutant_names[i]) + ' (' + str(list(pollutant_codes)[i]) + ') - ' + pollutant_value + ' (' + str(data['AirQualityBand'][i+1]) + ')')
            print('\nMAXIMUM AIR QUALITY INDEX: ' + str(max_air_quality_index) + ' (' + air_quality_bands[int(max_air_quality_index)] + ')')
            print('CORRESPONDING ADVICE:')
            if advice is None or (type(advice) is str and advice == 'No Data'):
                print('No advice available')
            else:
                for i in range(len(advice)):
                    print(advice['Population'][i+1] + ': ' + advice['Advice'][i+1])
            user_choice = input('\nInput "N" to select a new monitoring site, "G" to access site graph, "Q" to quit, or any other key to refresh the dashboard\n')
            if user_choice.upper() == 'Q':
                return
            elif user_choice.upper() == 'N':
                break   
            elif user_choice.upper() == 'G':
                dashboard_to_graph(site_code, pollutant_codes, live_pollutant_values, latest_pollutant_values, pollutant_names, date_and_time)
                continue 
            response = get_dashboard_data(site_code)[1:]
            if response is None:
                return
            pollutant_codes, pollutant_names, live_pollutant_values, latest_pollutant_values, max_air_quality_index, advice, site_name, date_and_time, data = response
            continue

def dashboard_to_graph(site_code: str, pollutant_codes: list, live_pollutant_values: list, latest_pollutant_values: list, pollutant_names: list, date_and_time: str) -> None:
    '''
    Converts data from the live dashboard for use in the render_graph() function

    @param site_code: Code of monitoring site who's data is being displayed on dashboard
    @param pollutant_codes: List of codes of all pollutants available from monitoring station
    @param live_pollutant_values: Live pollutant values available from monitoring station
    @param latest_pollutant_values: Latest pollutant values available from monitoring station (i.e. not NaN) and date/time collected
    @param pollutant_names: List of names of all pollutants available from monitoring station
    @param date_and_time: Date/time of live pollutant data

    @return: None if user quits
    '''
    
    import datetime

    pollutant_values = []
    for i in range(len(pollutant_codes)):
        if live_pollutant_values[i] != '':
            pollutant_values.append([str(pollutant_names[i]), str(list(pollutant_codes)[i]), str(live_pollutant_values[i]), datetime.datetime.strptime(date_and_time, '%Y-%m-%d %H:%M:%S')])
        elif all([value == 'No Data' for value in latest_pollutant_values]):
            os.system('cls' if os.name == 'nt' else 'clear')
            print('There is no data to plot for this monitoring site. Press any key to acknowledge.')
            input()
            return
        else:
            pollutant_values.append([str(pollutant_names[i]), str(list(pollutant_codes)[i]), latest_pollutant_values[i][0], datetime.datetime.strptime(latest_pollutant_values[i][1], '%Y-%m-%d %H:%M:%S')])
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Please input a number to select a pollutant from the following list:")
        for i in range(len(pollutant_values)):
            print(str(i+1) + ' - ' + pollutant_values[i][0])
        user_choice = input()
        try:
            if int(user_choice) - 1 in list(range(len(pollutant_values))):
                user_pollutant_values = pollutant_values[int(user_choice) - 1]
                break
        except:
            pass
        os.system('cls' if os.name == 'nt' else 'clear')
        print('Your input is invalid')
    render_graph((user_pollutant_values[2], site_code + " live data"), user_pollutant_values[1])
    return

def get_graph_parameters(used_site_codes:list, pollutant_code:str, start_date, end_date):

    '''
    Gets the parameters needed to retrieve data for graphing

    @param used_site_codes: A list of site codes of sites currently being displayed on the graph
    @param pollutant_code: The code of the pollutant being displayed on the graph
    @param start_date: The start date of data being displayed on the graph
    @param end_date: The end date of data being displayed on the graph

    @return: starting parameters, name of pollutant, and updated used site codes list
    '''

    import datetime
    while True:
        response = get_site_code_input()
        if response is None:
            return
        site_code, group_values = response
        if site_code in used_site_codes:
            print('Data from the site you selected is already displayed on the graph. Would you like to continue? (y/n)')
            user_choice = input()
            if user_choice.upper() == 'N':
                return
            elif user_choice.upper() != 'Y':
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Your input is invalid')
            continue
        max_date = group_values.loc[group_values['SiteCode'] == site_code].reset_index()['DateClosed'][0]
        max_date = datetime.date.today() + datetime.timedelta(days=1) if max_date == 'Still Operating' else datetime.datetime.strptime(max_date, '%Y-%m-%d %H:%M:%S').date()
        min_date = datetime.datetime.strptime(group_values.loc[group_values['SiteCode'] == site_code].reset_index()['DateOpened'][0], '%Y-%m-%d %H:%M:%S').date()
        if (not start_date is None and start_date < min_date) or (not end_date is None and end_date > max_date):
            while True:
                print('The station you have selected does not have data covering your chosen timespan. Would you like to continue? (y/n)')
                user_choice = input()
                if user_choice.upper() == 'N':
                    return
                elif user_choice.upper() != 'Y':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print('Your input is invalid')
                    continue
        response = graph_date_range_picker(max_date, min_date, start_date, end_date)
        if response is None:
            print('trigger2')
            return
        start_date, end_date = response

        response = unpack_json(get_live_data_from_api('/Hourly/MonitoringIndex/SiteCode={site_code}/Json', site_code = str(site_code)), ['HourlyAirQualityIndex', 'LocalAuthority', 'Site', 'species'])
        available_pollutants = list(set(response['SpeciesCode']))
        pollutant_code = graph_pollutant_picker(pollutant_code, available_pollutants)
        if pollutant_code is None:
            return
        pollutant_name = response.loc[response['SpeciesCode'] == pollutant_code]['SpeciesName']
        
        return(site_code, used_site_codes.append(site_code), pollutant_name, pollutant_code, start_date, end_date)

def graph_pollutant_picker(pollutant:str|None, available_pollutants:list) -> str:
    '''
    Allows the user to pick a pollutant from all pollutants monitored by a station, if a pollutant has not already been picked.

    @param pollutant: If None, a new pollutant is chosen
    @param available_pollutants: All pollutants monitored by the chosen station

    @return: chosen pollutant
    '''

    if pollutant is None:
        while True:
            print('Please input a number to pick a pollutant from the following list, or input "Q" to quit')
            for i in range(len(available_pollutants)):
                print(str(i + 1) + ' - ' + available_pollutants[i])
            user_choice = input()
            if user_choice.upper() == 'Q':
                return
            try:
                if int(user_choice) - 1 in list(range(len(available_pollutants))):
                    return list(available_pollutants)[int(user_choice) - 1]
            except:
                pass
            os.system('cls' if os.name == 'nt' else 'clear')
            print('Your input is invalid')
    elif not pollutant in available_pollutants:
        os.system('cls' if os.name == 'nt' else 'clear')
        print('The required pollutant data is not available from this monitoring site. Press any key to acknowledge.')
        input()
        return
    return pollutant

def date_picker():
    '''
    Allows the user to pick a date in the YYYY-MM-DD format

    @return: chosen date in the datetime.datetime() type
    '''

    import datetime
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        user_date = input('Please input a desired date in the YYYY-MM-DD format, or input "Q" to quit\n')
        if user_date.upper() == 'Q':
            return
        try:
            import re
            date_format = re.compile('\d\d\d\d-\d\d-\d\d')
            if bool(date_format.match(user_date)):
                return datetime.date.fromisoformat(user_date)
        except:
            pass
        os.system('cls' if os.name == 'nt' else 'clear')
        print('The date you have entered is invalid')
            
def graph_date_range_picker(max_date, min_date, start_date, end_date):
    '''
    Allows user to pick a range covered by two dates. Ensures that all monitoring sites have data covering the chosen period.

    @param max_data: Upper bound of the date available to display in DataTime.DateTime() type.
    @param min_data: Lower bound of the date available to display in DataTime.DateTime() type.
    @param start_date: Upper bound date of the data being displayed. If None, a new start_date is chosen.
    @param end_date: Lower bound date of the data being displayed. If None, a new end_date is chosen.

    @return: new start and end dates if both were None, else initial start and end dates.
    '''

    if end_date is None:
        os.system('cls' if os.name == 'nt' else 'clear')
        while True:
            print('Please input a number from the list below, or input Q to quit:',
        '\n1 - Select a custom end date\n2 - Use the maximum end date for this station (' + str(max_date) + ')')
            user_choice = input()
            if user_choice == '1':
                end_date = date_picker()
                if end_date is None:
                    return
                elif min_date > end_date or end_date > max_date:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print('The date you have entered is not within the allowed period (' + str(min_date) + ' to ' + str(max_date) + ')')
                    continue
            elif user_choice == '2':
                end_date = max_date
            elif user_choice.upper() == 'Q':
                return
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Your input is invalid')
                continue
            break
        
    if start_date is None:
        os.system('cls' if os.name == 'nt' else 'clear')
        while True:
            print('Please input a number from the list below, or input Q to quit:',
        '\n1 - Select a custom start date\n2 - Use the minimum start date for this station (' + str(min_date) + ')')
            user_choice = input()
            if user_choice == '1':
                start_date = date_picker()
                if start_date is None:
                    return
                elif start_date < min_date or start_date > end_date:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print('The date you have entered is not within the allowed period (' + str(min_date) + ' to ' + str(end_date) + ')')
                    continue
            elif user_choice == '2':
                start_date = min_date
            elif user_choice.upper() == 'Q':
                print('trigger')
                return
            else:
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Your input is invalid')
                continue
            break
    return (start_date, end_date)

def get_graph_data(used_site_codes = [], pollutant_code = None, start_date = None, end_date = None) -> tuple[str,str,any,any,list[list, list, str]]:
    '''
    @param used_site_codes: A list of site codes of sites currently being displayed on the graph
    @param pollutant_code: The code of the pollutant being displayed on the graph
    @param start_date: The start date of data being displayed on the graph
    @param end_date: The end date of data being displayed on the graph

    @return: Name and code of pollutant to display, date range of data, and x and y values to plot
    '''

    from datetime import datetime
    response = get_graph_parameters(used_site_codes, pollutant_code, start_date, end_date)
    if response is None:
        return
    site_code, used_site_codes, pollutant_name, pollutant_code, start_date, end_date = response
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Fetching data. This may take some time.')
    data = get_live_data_from_api('/Data/SiteSpecies/SiteCode={site_code}/SpeciesCode={species_code}/StartDate={start_date}/EndDate={end_date}/Json',
    site_code = site_code, species_code = pollutant_code, start_date = start_date, end_date = end_date)
    data = unpack_json(data, ['RawAQData', 'Data'])
    x_values = list(map(lambda value: datetime.strptime(value, '%Y-%m-%d %H:%M:%S'), data['MeasurementDateGMT']))
    y_values = data['Value'].replace('', np.nan).to_numpy(dtype = float)
    y_values[y_values < 0] = np.nan
    return(pollutant_name, pollutant_code, start_date, end_date, [x_values, y_values, site_code])

def render_graph(line = None, pollutant_code = None) -> None:
    """
    Displays a graph from data recieved

    @param line: The x and y values of a line retrieved from live dashboard. Optional if no dashboard data to display
    @param pollutant_code: The pollutant code retrieved from dashboard. Optional if no dashboard data to display
    """

    import matplotlib.pyplot as plt
    import matplotlib.dates

    response = get_graph_data(pollutant_code = pollutant_code)
    if response is None:
        return
    pollutant_name, pollutant_code, start_date, end_date = response[:4]
    data = [response[-1]]
    used_site_codes = [response[-1][-1]]
    if not line is None:
        plt.plot_date(matplotlib.dates.date2num([data[0][0][-0], data[0][0][-1]]), (line[0], line[0]), color='r', linestyle='--', label = line[1])
    while True:
        for i in range(len(data)):
            plt.plot_date(matplotlib.dates.date2num(data[i][0]), data[i][1], label = data[i][2])
        plt.xlabel('Time')
        plt.ylabel(str(pollutant_name.iloc[0]) + ' Level')
        plt.title(str(pollutant_name.iloc[0]) + ' Levels Over Time')
        plt.legend()
        plt.show()
        while True:
            print('Input "N" to add new monitoring site data, or input "Q" to quit')
            user_choice = input()
            print(user_choice.upper == 'Q')
            if user_choice.upper() == 'N':
                response = get_graph_data(used_site_codes = used_site_codes, pollutant_code = pollutant_code, start_date = start_date, end_date = end_date)
                if response is None:
                    return
                data.append(response[-1])
                used_site_codes = [response[-1][2]]
                continue
            elif user_choice.upper() != 'Q':
                os.system('cls' if os.name == 'nt' else 'clear')
                print('Your input is invalid')
            return