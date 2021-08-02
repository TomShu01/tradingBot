# make sure that you've installed python before you start coding in python

# Pandas is an open source Python package that is most widely used for data
#  science/data analysis and machine learning tasks. It is built on top of
#  another package named Numpy, which provides support for multi-dimensional arrays.
#  pandas provides the dataFrame which is super useful in data science

# tutorial for how to perform analysis on stock data in python: https://blog.quantinsti.com/stock-market-data-analysis-python/

# from scipy import interpolate # imports scipy so we can interpolate discrete stock data to polynomials
import numpy as np # imports numpy so we can use numpy arrays
import yfinance as yf # imports yahoo finance's module for getting stock data
import matplotlib.pyplot as plt # imports plt for visualizing data
from datetime import datetime, timedelta # imports datetime to deal with dates

# yfinance testing code:
start_date = input('enter the start date for your stock data, e.x. 2021-07-09: ') # there's no ";" in python
end_date = input('enter the end date for your stock data, e.x. 2021-08-01: ')

ticker = input('enter the stock quote you want to look into, e.x. GOOGL: ')

data = yf.download(ticker, start_date, end_date, progress=False) # data is a pandas dataFrame
# progress=False disables yfinance from outputing useless output

# i think python evaluates and shows the value of expressions like racket,
# however, to see those values in output, you have to print them

# plot adjusted close price data using matplotlib
# data['Adj Close'].plot(figsize=(10,7))
# plt.title("adjusted clsoe price of %s" % ticker, fontsize=16)
# plt.ylabel('price', fontsize=14)
# plt.xlabel('year', fontsize=14)
# plt.grid(which='major', color='k', linestyle='-.', linewidth=0.5)
# plt.show()

# i originally planned to interpolate the data to a function
#  then take the derivative and find extrema and use the extrema
#  to determine the intervals of increase and decrease in the data
#  but then i realized that there's a way simpler solution

# # extract x (dates) and y (close price on that date) from our data
# data = data.filter(['Close']) # cleans data to only the close prices
# y = data.to_numpy().squeeze() # converts data to numpy array, then from 2d array to 1d
# x = np.arange(0, len(y)) # we don't really need the dates for x so we just construct a list of points for x
# # np.arange is non-inclusive for end value

# print(len(y))
# print(y) # testing code for extracting time and stock price as arrays
# print(x)

# # construct function from discrete stock data using interpolation
# stockFunction = interpolate.interp1d(x, y)

# print(stockFunction)

data = data.filter(['Close'])
data = data.to_numpy().squeeze() # converts numpy array to 1d array

dataExtrema = [-2] * len(data) # initializes a list with length len(data) full of -2

# determines whether the close price on a date is a local max (1) or local min (-1) or neither (0)
# this method cannot detect cases where there is a flat portion above or below neighboring points
# does not loop through first and last point since they can't be local extrema
i = 1 # python does not have for loop syntax like for(i=0; i<n; i++), so i have to make a work around
while i < (len(data) - 1):
    # print(data[i])
    if (data[i - 1] < data[i] and data[i] > data[i + 1]):
        dataExtrema[i] = 1
    elif (data[i - 1] > data[i] and data[i] < data[i + 1]):
        dataExtrema[i] = -1
    else:
        dataExtrema[i] = 0
    i += 1 # for some reason, python doesn't have i++ either

# print(dataExtrema)

# removes all 0s from dataExtrema
dataExtremaWithoutZero = [x for x in dataExtrema if x != 0]

# initializes the extrema type for endpoints of data
if dataExtremaWithoutZero[1] == 1:
    dataExtremaWithoutZero[0] = -1
else:
    dataExtremaWithoutZero[0] = 1

if dataExtremaWithoutZero[len(dataExtremaWithoutZero) - 2] == 1:
    dataExtremaWithoutZero[len(dataExtremaWithoutZero) - 1] = -1
else:
    dataExtremaWithoutZero[len(dataExtremaWithoutZero) - 1] = 1

# print(dataExtremaWithoutZero)

intervalType = [0] * (len(dataExtremaWithoutZero) - 1)

# determine whether an interval is increasing (1) or decreasing (-1)
# because of the way I find extrema, the extrema has to be alternating
# between min and max, there's no consecutive min or max
for i in range(len(intervalType)):
    # remember that in python for loops, i returns the element at index i not the index
    # this is why i loop through range of length of itnervalType instead of using "for i in intervalType"
    if (dataExtremaWithoutZero[i] == 1):
        intervalType[i] = -1
    else:
        intervalType[i] = 1

# print (intervalType)

# determine how long each interval is (inclusive)
intervalLength = [] # the interval lengths are calculated inclusively

counter = 0
for i in dataExtrema:
    if (i == 0):
        counter += 1
    elif (counter == 0):
        counter += 1
    else:
        counter += 1
        intervalLength.append(counter)
        counter = 1 # not 0 because you count the first extrema into the interval length

# print(intervalLength)

# makes a 2d array of intervals, each with a interval type and length
intervals = np.column_stack((intervalType, intervalLength))

# print(intervals)

# identifies intervals that are increasing and ones that are decreasing
increasingIntervals = intervals[intervals[:,0] == 1]
increasingIntervals = np.delete(increasingIntervals, 0, axis=1).squeeze()
decreasingIntervals = intervals[intervals[:,0] == -1]
decreasingIntervals = np.delete(decreasingIntervals, 0, axis=1).squeeze()

# print(increasingIntervals)
# print(decreasingIntervals)

# calculate the average length of increasing and decreasing intervals
avgIncreasingInterval = np.average(increasingIntervals)
avgDecreasingInterval = np.average(decreasingIntervals)

# print(avgIncreasingInterval)
# print(avgDecreasingInterval)

def evalStock(date):
    startDate = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=30)
    data = yf.download(ticker, startDate.strftime('%Y-%m-%d'), date, progress=False)
    data = data.filter(['Close'])
    data = data.to_numpy().squeeze()

    length = 1 # starts with 1 because intervals are inclusive
    intervType = 0
    i = len(data) - 2 # python does not have for loop syntax like for(i=0; i<n; i++), so i have to make a work around
    while i >= 0:
        length += 1
        if (data[i - 1] < data[i] and data[i] > data[i + 1]):
            intervType= -1
            break
        elif (data[i - 1] > data[i] and data[i] < data[i + 1]):
            intervType = 1
            break
        i -= 1 # for some reason, python doesn't have i++ either

    if intervType == 1:
        if length >= avgIncreasingInterval:
            return("sell, don't buy")
        else:
            return("don't sell, don't buy")
    elif intervType == -1:
        if length >= avgDecreasingInterval:
            return("buy, don't sell")
        else:
            return("don't buy")

print(evalStock(input("enter the date of the stock price you want to evaluate, e.x. 2021-08-01: ")))