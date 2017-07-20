# Simple examples for read TextGrid file

import textgrid

# Read TextGrid object from file
tg = textgrid.TextGrid.fromFile('test.TextGrid')

# Interval example
print ("------- Interval example -------")
print (tg[0]) # item[1]
print (tg[0][0]) # interval[1]
print (tg[0][0].minTime) # interval[1].xmin
print (tg[0][0].maxTime) # interval[1].xmax
print (tg[0][0].mark) # interval[1].mark

# Point example
print ("------- Point example -------")
print (tg[1]) # item[2]
print (tg[1][0]) # points[1]
print (tg[1][0].time) # points[1].number
print (tg[1][0].mark) # points[1].mark
