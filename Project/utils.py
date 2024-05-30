import numpy as np
import typing as t

def sumvalues(values: list[int|float]|np.ndarray[int|float]) -> int|float:
    """
    Sums a list of values

    @param values: values to sum
    """

    if (not isinstance(values, (list, np.ndarray))) and all(isinstance(n, (int, float)) for n in values):
        raise TypeError('sumvalues() expects a list or array of int and float values only')
    summation = 0
    for n in values:
        summation = summation + n 
    return summation


def maxvalue(values: list[int|float]|np.ndarray[int|float]) -> int|float:
    """
    Finds the maximum of a list of values
    
    @param values: values to find the maximum of
    """

    if len(values) == 0:
        raise IndexError('maxvalue() expects a list or array with at least one value')
    elif (not isinstance(values, (list, np.ndarray))) and all(isinstance(n, (int, float)) for n in values):
        raise TypeError('maxvalue() expects a list or array of int and float values only')
    else:
        maximum = values[0]
        for n in values:
            if n > maximum:
                maximum = n 
    return maximum


def minvalue(values: list[int|float]|np.ndarray[int|float]) -> int|float:
    """
    Finds the minimum of a list of values
    
    @param values: values to find the minimum of
    """

    if len(values) == 0:
        raise IndexError('minvalue() expects a list or array with at least one value')
    elif (not isinstance(values, (list, np.ndarray))) and all(isinstance(n, (int, float)) for n in values):
        raise TypeError('minvalue() expects a list or array of int and float values only')
    else:
        minimum = values[0]
        for n in values:
            if n < minimum:
                minimum = n 
    return minimum


def meannvalue(values: list[int|float]|np.ndarray[int|float]) -> float:
    """
    Finds the mnean of a list of values
    
    @param values: values to find the mean of
    """

    if len(values) == 0:
        raise IndexError('meanvalue() expects a list or array with at least one value')
    elif (not (isinstance(values, (list, np.ndarray))) and all(isinstance(n, (int, float)) for n in values)):
        raise TypeError('meanvalue() expects a list or array of int and float values only')
    else:
        sumn = 0
        for n in values:
            sumn = sumn + n 
    return sumn/len(values)


def countvalue(values: list|np.ndarray, x: t.Any) -> int:
    """
    counts the values in a list
    
    @param values: values to count the number of
    """

    if not isinstance(values, (list, np.ndarray)):
        raise TypeError('countvalue() expects a list or array of values only')
    else:
        count = 0
        for n in values:
            if n == x:
                count = count + 1
    return count

