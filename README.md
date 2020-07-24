textgrid.py
===========

Python classes for Praat TextGrid and TextTier files (and HTK .mlf files)

Kyle Gorman <kylebgorman@gmail.com> and contributors (see commit history).

How to cite:
------------

While you don't have to, if you want to cite textgrid.py in a publication, include a footnote link to the source:

    http://github.com/kylebgorman/textgrid.py/

How to install:
---------------

The code can be placed in your working directory or in your `$PYTHONPATH`,  and then imported in your Python script. You also can install it via `pip`, like so:

    pip install textgrid

(if you're not working in a virtualenv, you may need to do this with `sudo`.)

Synopsis:
---------

See the docstrings in `textgrid.py`

Example:
---------
This is a simple example of reading a TextGrid file. 
```
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
```

The content of the file `test.TextGrid` is as below:
```
File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0
xmax = 1
tiers? <exists>
size = 2
item []:
    item [1]:
        class = "IntervalTier"
        name = "words"
        xmin = 0
        xmax = 1
        intervals: size = 2
        intervals [1]:
            xmin = 0
            xmax = 0.5
            text = """Is anyone home?"""
        intervals [2]:
            xmin = 0.5
            xmax = 1
            text = "asked ""Pat"""
    item [2]:
        class = "TextTier"
        name = "points"
        xmin = 0
        xmax = 1
        points: size = 2
        points [1]:
            number = 0.25
            mark = """event"""
        points [2]:
            number = 0.75
            mark = """event"" with quotes again"
```

By runing the code above, the output is:
```
------- Interval example -------
<IntervalTier words, 2 intervals>
Interval(0.0, 0.5, "Is anyone home?")
0.0
0.5
"Is anyone home?"
------- Point example -------
<PointTier points, 2 points>
Point(0.25, "event")
0.25
"event"
```
