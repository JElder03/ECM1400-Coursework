import os

from intelligence import *
from monitoring import *
from utils import *
from reporting import *


def main_menu() -> None:
    """
    Prints a main menu interface and allows the user to access sub-menus
    """

    submenu_dict = {'R': reporting_menu, 'I': intelligence_menu, 'M': monitoring_menu, 'A': about, 'Q': quit}
    
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print('Please input a letter from the list below to select a submenu:\nR - Access the Pollution Reporting module\nI - Access',
        'the Mobility Intelligence module\nM - Access the Real-Time Monitoring module\nA - Print the About text\nQ - Quit the',
        'application')
        user_choice = input().upper()

        if user_choice not in submenu_dict.keys():
            print('The letter you have inputted is not valid')
        else:
            submenu_dict[user_choice]()


def reporting_menu() -> None:
    """
    Prints the reporting sub-menu interface and allows the user to access functions in reporting.py
    """
    
    import pandas as pd

    def station_pollutant_picker(station_or_pollutant) -> int:
        """
        Allows user to pick a monitoring station or pollutant from a predefined list

        @param station_or_pollutant: int 1 or 0 to differentiate between picking a pollutant and monitoring station by indexing formatting tuple

        @return: Station or pollutant corresponding to the user's choice
        """

        formatting = (('monitoring station', stations), ('pollutant', pollutants))
        while True:
            print('Please input a number from the list below to select a', formatting[station_or_pollutant][0] + ':')
            for i, choice in enumerate(formatting[station_or_pollutant][1]):
                print(i + 1, '-', choice)
            user_station_pollutant = input()

            if user_station_pollutant not in [str(x) for x in range(1, len(formatting[station_or_pollutant][1]) + 1)]:
                print('The number you have entered is not valid')
            else:
                return formatting[station_or_pollutant][1][int(user_station_pollutant) - 1]

    def date_picker() -> str:
        """
        Allows user the pick a date in the year 2021, and checks user's date exists.

        @return: The user's choice of date in the 2021-MM-DD format
        """

        import datetime

        def day_month_picker(day_or_month):
            """
            Allows user to input a day or month of a date

            @param day_or_month: int 1 or 0 to differentiate between picking a day and month by indexing formatting tuple
            
            @return: User's choice of day or month in the two digit DD or MM format
            """

            formatting = (('month', 'MM', 13), ('day', 'DD', 32))
            while True:
                print('Please input a', formatting[day_or_month][0], 'in the two digit', formatting[day_or_month][1], 'format:')
                user_day_month = input()

                try:
                    if int(user_day_month) in range(1, formatting[day_or_month][2]) and len(user_day_month) == 2:
                        return (user_day_month)
                except:
                    pass
                else:
                    print('The', formatting[day_or_month][0], 'you have entered is not in the two digit', formatting[day_or_month][1], 
                    'format, or is not valid')
            
        while True:
            print('Please input a date in the year 2021')
            user_date = '2021-' + day_month_picker(0) + '-' + day_month_picker(1)
            try:
                datetime.datetime.strptime(user_date, '%Y-%m-%d')
                return (user_date)
            except:
                print('The date you have enetered does not exist')

    def new_value_picker() -> any:
        """
        Allows user to pick a value to replace all missing pollution data with

        @return: User's choice of value to replace all missing data with
        """

        print('Please input a value to replace all missing values with:')
        user_new_value = input()
        return (user_new_value)
    
    stations = ('Marylebone Road', 'N. Kensington', 'Harlington')
    pollutants = ('no', 'pm10', 'pm25')
    submenu_dict = {'1': daily_average, '2': daily_median, '3': hourly_average, '4': monthly_average, '5': peak_hour_date, '6': count_missing_data, '7': fill_missing_data, 'Q': None}
    #create a dictionary with stations as keys and corresponding raw data as value 
    data = {k:v for k, v in zip(stations, list(map(lambda station: pd.read_csv(os.path.join(os.path.dirname(__file__), 'data', ('Pollution-London ' + station.replace('.', '') + '.csv')), header = 0, na_values = 'No data'), stations)))}
    
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print('Pollution Reporting Submenu:\nPlease input a number from the list below to select a function, or input Q to return',
          'to the main menu:\n1 - Daily average\n2 - Daily median\n3 - Hourly average\n4 - Monthly average\n5 - Peak hour on a',
          'select date\n6 - Count missing values in a data set\n7 - Fill all missing values')
        user_choice = input().upper()
        if not(user_choice in submenu_dict or user_choice == 'Q'):
            print('Your input is not valid')
        elif user_choice == 'Q':
            return
        elif user_choice == '5':
            print(submenu_dict['5'](data, date_picker(), station_pollutant_picker(0), station_pollutant_picker(1)))
        elif user_choice == '7':
            print(submenu_dict['7'](data, station_pollutant_picker(0), station_pollutant_picker(1), new_value_picker()))
        else:
            print(submenu_dict[user_choice](data, station_pollutant_picker(0), station_pollutant_picker(1)))

def monitoring_menu() -> None:
    """
    Prints the real-time monitoring sub-menu interface and allows the user to access functions in monitoring.py
    """

    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        submenu_dict ={'1': render_dashboard, '2': render_graph, 'Q': None}
        print('Real-Time Monitoring Reporting Submenu:\nPlease input a number from the list below to select a function, or input Q to return',
          'to the main menu:\n1 - Live dashboard\n2 - Plot live graphs')
        user_choice = input().upper()
        if not(user_choice in submenu_dict.keys()):
            print('Your input is not valid')
        elif user_choice == 'Q':
            return
        else:
            try:
                submenu_dict[user_choice]
            except (ConnectionError):
                print("Connection to the London Air API failed.\nCheck you are connected to the internet and try again.")
            except (TimeoutError):
                print("Connection timeout to the London Air API")
                continue


def intelligence_menu() -> None:
    """
    Prints a mobility intelligence sub-menu interface and allows the user to access functions in intelligence.py
    """

    def get_threshold_input(upper:bool) -> int:
        """
        Gets an integer input from user between 0 and 255

        @param upper: A boolean to format text interface and ask user for an upper or lower threashold
        """

        while True:
            user_threshold = input('Please input an ' + ('upper' if upper else 'lower') + ' threshold between 0 and 255')
            try:
                if 0 <= int(user_threshold) <= 255:
                    return int(user_threshold)
            except:
                pass
            print('\nYour input is invalid')

    submenu_dict = {'1': find_red_pixels, '2': find_cyan_pixels, '3': detect_connected_components, '4': detect_connected_components_sorted, 'Q': None}

    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print('Pollution Reporting Submenu:\nPlease input a number from the list below to select a function, or input Q to return',
          'to the main menu:\n1 - Find red pixels\n2 - Find cyan pixels\n3 - Find all connected components\n4 - Order all connected components by size')
        user_choice = input().upper()
        if not(user_choice in submenu_dict.keys()):
            print('Your input is not valid')
        elif user_choice == 'Q':
            return
        elif user_choice == '1' or user_choice == '2':
            try:
                submenu_dict[user_choice](input('Please enter the filename of a city map\n'), get_threshold_input(True), get_threshold_input(False))
                break
            except FileNotFoundError:
                    print('The filename you have entered could not be found')
                    continue
        elif user_choice == '3':
            while True:
                user_choice = input("Input 1 to find connected cyan components, or 2 to find connected red components\n")
                if user_choice in ['1', '2']:
                    submenu_dict['3'](submenu_dict[user_choice]())
                    break
                else:
                    print('\nYour input is invalid')
        elif user_choice == '4':
            while True:
                user_choice = input("Input 1 to find sorted connected cyan components, or 2 to find sorted connected red components\n")
                if user_choice in ['1', '2']:
                    submenu_dict['4'](submenu_dict['3'](submenu_dict[user_choice]()))
                    break
                else:
                    print('\nYour input is invalid')
        print('Please check the current working directory to find results')
        break

def about() -> None:
    """
    Prints module code and candidate number
    """
    
    print('ECM1400')
    print('258077')
    return


def quit() -> None:
    """
    Terminates the program
    """
    
    exit()


if __name__ == '__main__':
    print('Welcome to the Air Quality Analytics platform')
    main_menu()
