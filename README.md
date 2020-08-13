textgrid.py
===========

Python classes for Praat TextGrid and TextTier files (and HTK .mlf files)

Kyle Gorman <kylebgorman@gmail.com> and contributors (see commit history).

How to cite:
------------

While you don't have to, if you want to cite textgrid.py in a publication, include a footnote link to the source:

    http://github.com/kylebgorman/textgrid/

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

```python
import textgrid

# Read a TextGrid object from a file.
tg = textgrid.TextGrid.fromFile('test.TextGrid')

# Read a IntervalTier object.
print("------- IntervalTier Example -------")
print(tg[0])
print(tg[0][0])
print(tg[0][0].minTime)
print(tg[0][0].maxTime)
print(tg[0][0].mark)

# Read a PointTier object.
print("------- PointTier Example -------")
print(tg[1])
print(tg[1][0])
print(tg[1][0].time)
print(tg[1][0].mark)
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

The following is the output of the above snippet:
```
------- IntervalTier Example -------
<IntervalTier words, 2 intervals>
Interval(0.0, 0.5, "Is anyone home?")
0.0
0.5
"Is anyone home?"
------- PointTier Example -------
<PointTier points, 2 points>
Point(0.25, "event")
0.25
"event"
```
