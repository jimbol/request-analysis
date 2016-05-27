import csv
import urllib
from collections import defaultdict
from urlparse import parse_qs
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
import numpy
import operator
from tabulate import tabulate

# Partial requests  1,690
# Total requests    3,140

# b_cookie 0
# country 1
# heapAfter 2
# heapBefore 3
# heap_after_steno 4
# heap_before_steno 5
# logType 6
# memoryRSS 7
# method 8
# pageId 9
# platform 10
# remoteAddress 11
# requestId 12
# responseTime 13
# rss_steno 14
# s_cookie 15
# status 16
# url 17
# userAgent 18
# timestamp 19

def run():
  fileReader = openFile()
  presentedData = bucketByTime(fileReader)

  # timeCategories = presentedData[0]['2016-04-25T03']['category']
  allCategories = presentedData[1]['category']
  # aC = sorted(allCategories, key=operator.itemgetter(1))
  # print aC

  # print alignCategories(presentedData)['2016-04-25T03']
  categories = alignCategories(presentedData)
  categories = sortTimeCategories(categories)
  pltSortedCategories(categories, len(allCategories), 200)
  # print categories['2016-04-25T03']

def sortTimeCategories (categories):
  for time in categories:
    cat = categories[time]
    categories[time] = sorted(cat, key=operator.itemgetter(0))

  return categories

def pltSortedCategories (categories, count, threshold):
  fig = plt.figure()
  ax = fig.add_subplot(111)
  plt.title('Categories')
  plt.xlabel("Category values")
  plt.ylabel("Frequency")

  width = 0.8

  ind = numpy.arange(len(categories))

  colorMap = getColorMap(count)

  tableData = []

  while count > 0:
    count -= 1

    barValues = []

    for time in categories:
      barValues.append(categories[time][count][1])

    if len([val for val in barValues if val > threshold]) > 0:
      tableData.append([categories[time][count][0]] + barValues)
      ax.bar(ind, barValues, width, color=colorMap(count), label=categories[time][count][0])

  # Look into `matplotlib pcolormesh` to show table
  # print tabulate(tableData)
  # plt.legend()

  # plt.show()

def getColorMap(N):
    '''Returns a function that maps each index in 0, 1, ... N-1 to a distinct
    RGB color.'''
    color_norm  = colors.Normalize(vmin=0, vmax=N-1)
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv')
    def map_index_to_rgb_color(index):
        return scalar_map.to_rgba(index)
    return map_index_to_rgb_color

def align(presentedData):
  # Not all categories will have the same values
  # accross time slots.  For charting, each will
  # need to contain the same values and be in the
  # same order.

  allKeys = presentedData[1]
  keysByTime = presentedData[0]

  output = defaultdict(list)


  for key in allKeys:
    for time in keysByTime:
      timeCategory = keysByTime[time]['category'][key]

      if timeCategory == None:
        tpl = (key, 0)
      else:
        tpl = (key, timeCategory)

      output[time].append(tpl)

  return output


def alignCategories(presentedData):
  # Not all categories will have the same values
  # accross time slots.  For charting, each will
  # need to contain the same values and be in the
  # same order.

  allCategories = presentedData[1]['category']
  times = presentedData[0]

  output = defaultdict(list)

  for key in allCategories:
    for time in times:
      timeCategory = times[time]['category'][key]

      if timeCategory == None:
        tpl = (key, 0)
      else:
        tpl = (key, timeCategory)

      output[time].append(tpl)

  return output

def openFile():
  botFile = open('googlebot-requests.csv', 'rb')
  return csv.reader(botFile)

def bucketByTime(fileReader):
  # Bucket rows by time.  Also, count the occurances
  # of each value for each property.

  output = defaultdict(lambda : defaultdict(lambda : defaultdict(int)))
  allKeys = defaultdict(lambda : defaultdict(int))

  # Skip labels
  next(fileReader)

  for row in fileReader:

    bucketKey = findTimeBucket(row[12], 'hour')
    urlHash = getQueryHash(row[10])

    # for each property in urlHash
    for prop in urlHash:
      propValue = urlHash[prop][0]

      allKeys[prop][propValue] += 1
      output[bucketKey][prop][propValue] += 1

  return (output, allKeys)

def getQueryHash (requestUrl):
  q = requestUrl.split('?')

  if len(q) < 2:
    return {}

  return parse_qs(q[1])

def findTimeBucket (timestamp, bucketSize):
  if bucketSize == 'day':
    return timestamp.split('T')[0]
  if bucketSize == 'hour':
    return timestamp.split(':')[0]




def runGet():
  with open('googlebot-requests.csv', 'rb') as botFile:
    botFileReader = csv.reader(botFile)
    output = defaultdict(defaultdict)

    for row in botFileReader:
      requestUrl = urllib.unquote(row[10])

      queryHash = getQueryHash(requestUrl)

      for key in queryHash:
        for value in queryHash[key]:
          if not value in output[key]:
            output[key][value] = 0

          output[key][value] += 1

    # The parameters Google tests
    print output.keys()

    # bucketedOutput = bucket(output, 'hour')
    # pltParam(output, 'category')

def pltParam (output, key):
  param = output[key]
  param = param.items()

  param.sort(key=operator.itemgetter(1))

  keys = [item[0] for item in param]
  values = [item[1] for item in param]

  plt.title(key)


  plt.xlabel(key+" values")
  plt.ylabel("Frequency")

  width = 0.8
  print values
  ind = numpy.arange(len(keys))

  p1 = plt.bar(ind, values, width, color='r')

  plt.show()

def countUrlProperties (urlHash):
  output = defaultdict(defaultdict)
  for key in urlHash:
    for value in urlHash[key]:
      if not value in output[key]:
        output[key][value] = 0

      output[key][value] += 1

  return output


run()
