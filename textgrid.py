#!/usr/bin/env python
# 
# Copyright (c) 2011 Kyle Gorman, Morgan Sonderegger, Max Bane 
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# 
# textgrid.py
# 
# Max Bane <bane@uchicago.edu>
# Kyle Gorman <kgorman@ling.upenn.edu>
# Morgan Sonderegger <morgan@cs.uchicago.edu>
#
# classes for Praat TextGrid data structures, and HTK .mlf files

"""
Module docs here.
"""

import re
from bisect import bisect_left

class Point(object):
    """ 
    Represents a point in time with an associated textual mark, as stored in a
    PointInterval.

    # Point/Point comparison
    >>> foo = Point(3.0, 'foo')
    >>> bar = Point(4.0, 'bar')
    >>> foo < bar
    True
    >>> foo == Point(3.0, 'baz')
    True
    >>> bar > foo
    True

    # Point/Value comparison
    >>> foo < 4.0
    True
    >>> foo == 3.0
    True
    >>> foo > 5.0
    False

    # Point/Interval comparison
    >>> baz = Interval(3.0, 5.0, 'baz')
    >>> foo < baz
    True
    >>> foo == baz
    False
    >>> bar == baz 
    True
    """

    def __init__(self, time, mark):
        self.time = time
        self.mark = mark
    

    def __repr__(self):
        return 'Point(%r, %r)' % (self.time, self.mark)


    def __cmp__(self, other):
        """
        In addition to the obvious semantics, Point/Interval comparison is 0 
        iff the point is inside the interval (non-inclusively), if you need
        inclusive membership, use Interval.__contains__
        """
        if isinstance(other, Point):
            return cmp(self.time, other.time)
        elif isinstance(other, Interval):
            return cmp(self.time, other.minTime) + \
                   cmp(self.time, other.maxTime)
        else: # hopefully numerical
            return cmp(self.time, other)


class Interval(object):
    """ 
    Represents an interval of time, with an associated textual mark, as stored
    in an IntervalTier.

    >>> foo = Point(3.0, 'foo')
    >>> bar = Point(3.0, 'bar')
    >>> baz = Interval(3.0, 5.0, 'baz')
    >>> foo in baz
    True
    >>> 3.0 in baz
    True
    >>> bar in baz
    True
    >>> 4.0 in baz
    True
    """

    def __init__(self, minTime, maxTime, mark):
        self.minTime = minTime
        self.maxTime = maxTime
        self.mark = mark
    

    def __repr__(self):
        return 'Interval(%r, %r, %r)' % (self.minTime, self.maxTime, self.mark)


    def __min__(self):
        return self.minTime


    def __max__(self):
        return self.maxTime


    def __len__(self):
        """ 
        returns the length of the interval in seconds
        """
        return self.maxTime - self.minTime


    def __cmp__(self, other):
        if isinstance(other, Interval):
            if self.overlaps(other):
                raise ValueError, '%r and %r overlap' % (self, other))
            # given that the two intervals do not overlap:
            return cmp(self.minTime, other.minTime)
        elif isinstance(other, Point):
            return cmp(self.minTime, other.time) + \
                   cmp(self.maxTime, other.time)
        else: 
            return cmp(self.minTime, other) + cmp(self.maxTime, other)


    def overlaps(self, otherInterval):
        """
        Tests whether this interval overlaps with the given interval. Symmetric.
        """
        # how elegant: http://www.rgrjr.com/emacs/overlap.html
        return other.minTime < self.maxTime and self.minTime < other.maxTime


    def __contains__(self, other):
        """
        Tests whether the given time point is contained in this interval, either
        a numeric type or a Point object.
        """
        if isinstance(other, Point):
            return self.minTime <= other.time <= self.maxTime
        else:
            return self.minTime <= other <= self.maxTime


    def bounds(self):
        return (self.minTime, self.maxTime)


class PointTier(object):
    """ 
    Represents Praat PointTiers (also called TextTiers) as list of Points
    (e.g., for point in pointtier)

    >>> foo = PointTier('foo')
    >>> foo.add(4.0, 'bar')
    >>> foo.add(2.0, 'baz')
    >>> foo
    PointTier('foo', [Point(2.0, 'baz'), Point(4.0, 'bar')])
    >>> foo.remove(4.0, 'bar')
    >>> foo.add(6.0, 'bar')
    >>> foo
    PointTier('foo', [Point(2.0, 'baz'), Point(6.0, 'bar')])
    """ 

    def __init__(self, name=None, file=None):
        self.points = []
        if file:
            self.read(file)
            # name is ignored
        else:
            self.name = name


    def __str__(self):
        return '<PointTier %r with %d points>' % (self.name, len(self))


    def __repr__(self):
        return 'PointTier(%r, %r)' % (self.name, self.points)


    def __iter__(self):
        return iter(self.points)
    

    def __len__(self):
        return len(self.points)
    

    def __getitem__(self, i):
        return self.points[i]


    def getfirst(self, tierName):
        for t in self.tiers:
            if t.name == tierName:
                return t
        return None


    def getlist(self, tierName):
        tiers = []
        for t in self.tiers:
            if t.name == tierName:
                tiers.append(t)
        return tiers


    def tierNames(self):
        """
        Returns a list of the names (strings) of the intervals contained in this
        TextGrid, in order.
        """
        return [tier.name for tier in self.tiers]


    def __min__(self):
        return self.points[0].time


    def __max__(self):
        return self.points[-1].time 


    def add(self, time, mark):
        """ 
        constructs a Point and adds it to the PointTier, maintaining order
        """
        self.addPoint(Point(time, mark))


    def addPoint(self, point):
        i = bisect_left(self.points, point)
        if i != len(self.points) and self.points[i] == point:
            raise ValueError, '%r already exists at this time'
        self.points.insert(i, point)


    def remove(self, time, mark):
        """
        removes a constructed Point i from the PointTier
        """
        self.removePoint(Point(time, mark))


    def removePoint(self, point):
        self.points.remove(point)


    def read(self, file):
        """
        Read the Intervals contained in the Praat-formated IntervalTier file 
        and append those tiers. f may be a file object to read from, or a 
        string naming a path for reading
        """
        source = f if isinstance(f, file) else open(f, 'r')
        source.readline() # header junk 
        source.readline()
        source.readline()
        for i in xrange(int(source.readline().rstrip().split()[3])):
            source.readline().rstrip() # header
            itim = float(source.readline().rstrip().split()[2])
            imrk = source.readline().rstrip().split()[2].replace('"', '') 
            self.points.append(Point(imrk, itim))


    def write(self, f):
        """
        Write the current state into a Praat-format PointTier/TextTier file. f
        may be a file object to write to, or a string naming a path for writing
        """
        sink = f if isinstance(f, file) else open(f, 'w')
        sink.write('File type = "ooTextFile"\n')
        sink.write('Object class = "TextTier"\n\n')
        sink.write('xmin = %f\n' % min(self))
        sink.write('xmax = %f\n' % max(self))
        sink.write('points: size = %d\n' % len(self))
        for (i, point) in enumerate(self.points):
            sink.write('points [%d]:\n' % i + 1)
            sink.write('\ttime = %f\n' % point.time)
            sink.write('\tmark = "%s"\n' % point.mark)
        sink.close()


class IntervalTier(object):
    """ 
    Represents Praat IntervalTiers as list of sequence types of Intervals 
    (e.g., for interval in intervaltier)
    """

    def __init__(self, name=None, file=None):
        self.intervals = []
        if file:
            self.read(file)
            # name is ignored
        else:
            self.name = name


    def __str__(self):
        return '<IntervalTier %r with %d points>' % (self.name, len(self))


    def __repr__(self):
        return 'IntervalTier(%r, %r)', (self.name, self.intervals)


    def __iter__(self):
        return iter(self.intervals)


    def __len__(self):
        return len(self.intervals)


    def __getitem__(self, i):
        return self.intervals[i]


    def __min__(self):
        raise NotImplementedError


    def __max__(self):
        raise NotImplementedError


    def add(self, minTime, maxTime, mark):
        self.addInterval(Interval(minTime, maxTime, mark))


    def addInterval(self, Interval):
        raise NotImplementedError
        

    def remove(self, minTime, maxTime, mark):
        self.removeInterval(Interval(minTime, maxTime, mark))


    def removeInterval(self, Interval):
        raise NotImplementedError


    def intervalContaining(self, point):
        """
        Returns the interval containing the given time point, or None if the
        time point is outside the bounds of this tier. point may either be a
        numeric type, or a Point object.
        """
        raise NotImplementedError


    def read(self, file):
        """
        Read the tiers contained in the Praat-format IntervalTier file named by
        the given string, and append those tiers to self. f may be a file
        object to read from, or a string naming the path to open for reading
        """
        source = f if isinstance(f, file) else open(f, 'r')
        source.readline() # header junk 
        source.readline()
        source.readline()
        n = int(source.readline().rstrip().split()[3])
        for i in xrange(n):
            source.readline().rstrip() # header
            imin = float(source.readline().rstrip().split()[2]) 
            imax = float(source.readline().rstrip().split()[2])
            imrk = source.readline().rstrip().split()[2].replace('"', '') # txt
            self.intervals.append(Interval(imin, imax, imrk))
        source.close()


    def write(self, file):
        """
        Write the current state into a Praat-format IntervalTier file. f may be
        a file object to write to, or a string naming a path for writing
        """
        sink = f if isinstance(f, file) else open(f, 'w')
        sink.write('File type = "ooTextFile"\n')
        sink.write('Object class = "IntervalTier"\n\n')
        sink.write('xmin = %f\n' % min(self))
        sink.write('xmax = %f\n' % max(self))
        sink.write('intervals: size = %d\n' % len(self))
        for (i, interval) in enumerate(self.intervals):
            sink.write('intervals [%d]:\n' % i + 1)
            sink.write('\txmin = %f\n' % min(interval))
            sink.write('\txmax = %f\n' % max(interval))
            sink.write('\tsink = "%s"\n' % interval.mark)
        sink.close()


class TextGrid(object):
    """ 
    Represents Praat TextGrids as list of sequence types of tiers (e.g., for
    tier in textgrid), and as map from names to tiers (e.g.,
    textgrid['tierName']). 
    """

    def __init__(self, name=None, file=None): 
        """
        Construct a TextGrid instance with the given (optional) name (which is
        only relevant for MLF stuff). If file is given, it is a string naming
        the location of a Praat-format TextGrid file from which to populate this
        instance.
        """
        self.tiers = []
        if file:
            self.read(file)
        else:
            self.name = name


    def __str__(self):
        return '<TextGrid %r with %d Tiers>' % (self.name, len(self))


    def __repr__(self):
        return "TextGrid(%r, %r)" % (self.name, self.tiers)


    def __iter__(self):
        return iter(self.tiers)


    def __len__(self):
        return len(self.tiers)


    def __getitem__(self, i):
        """ 
        Return the ith tier
        """
        return self.tiers[i]


    def getfirst(self, string):
        """
        returns the first tier with a name matching string
        """
        raise NotImplementedError        


    def getlist(self, string):
        """
        returns all tiers with a name matching string (Praat allows tiers with
        the same name in a TextGrid)
        """
        raise NotImplementedError

    
    def getnames(self):
        """
        return a list of the names of the intervals contained in this TextGrid
        """
        return [tier.name for tier in self.tiers]


    def __min__(self):
        return min(min(tier) for tier in self.tiers)


    def __max__(self):
        return max(max(tier) for tier in self.tiers)


    def append(self, tier):
        self.tier.append(tier)


    def extend(self, tiers):
        for tier in tiers:
            self.tier.append(tier)


    @staticmethod
    def _getMark(text):
        a = re.search('(\S+) (=) (".*")', text.readline().rstrip())
        assert(a)
        assert(len(a.groups()) == 3)
        return a.groups()[2][1:-1]


    def read(self, f):
        """ 
        Read the tiers contained in a Praat-format TextGrid file. f may be a
        file object to read from, or a string naming the path for reading
        """
        source = f if isinstance(f, file) else open(f, 'r')
        for i in xrange(6):
            source.readline() # header crap
        m = int(source.readline().rstrip().split()[2]) # will be self.n soon
        source.readline()
        for i in xrange(m): # loop over grids
            source.readline()
            if source.readline().rstrip().split()[2] == '"IntervalTier"': 
                inam = source.readline().rstrip().split(' = ')[1].strip('"')
                imin = float(source.readline().rstrip().split()[2])
                imax = float(source.readline().rstrip().split()[2])
                itie = IntervalTier(inam)
                for j in xrange(int(source.readline().rstrip().split()[3])):
                    source.readline().rstrip().split() # header junk
                    jmin = float(source.readline().rstrip().split()[2])
                    jmax = float(source.readline().rstrip().split()[2])
                    jmrk = self._getMark(source)
                    itie.add(Interval(jmin, jmax, jmrk))
                self.append(itie) 
            else: # pointTier
                inam = source.readline().rstrip().split(' = ')[1].strip('"')
                imin = float(source.readline().rstrip().split()[2])
                imax = float(source.readline().rstrip().split()[2])
                #itie = PointTier(inam, imin, imax) 
                itie = PointTier(inam)
                n = int(source.readline().rstrip().split()[3])
                for j in range(n):
                    source.readline().rstrip() # header junk
                    jtim = float( source.readline().rstrip().split()[2])
                    jmrk = source.readline().rstrip().split()[2][1:-1]
                    itie.add(Point(jtim, jmrk))
                self.append(itie)
        source.close()


    def write(self, f):
        """
        Write the current state into a Praat-format TextGrid file. f may be a
        file object to write to, or a string naming a path to open for writing.
        """
        sink = f if isinstance(f, file) else open(f, 'w')
        sink.write('File type = "ooTextFile"\n')
        sink.write('Object class = "TextGrid"\n\n')
        sink.write('xmin = %f\n' % min(self))
        sink.write('xmax = %f\n' % max(self))
        sink.write('tiers? <exists>\n')
        sink.write('size = %d\n' % len(self))
        sink.write('item []:\n')
        for (i, tier) in enumerate(self.tiers):
            sink.write('\titem [%d]:\n' % i + 1)
            if tier.__class__ == IntervalTier: 
                sink.write('\t\tclass = "IntervalTier"\n')
                sink.write('\t\tname = "%s"\n' % tier.name)
                sink.write('\t\txmin = %f\n' % min(tier))
                sink.write('\t\txmax = %f\n' % min(tier))
                sink.write('\t\tintervals: size = %d\n' % len(tier))
                for (j, interval) in enumerate(tier):
                    sink.write('\t\t\tintervals [%d]:\n' % j + 1)
                    sink.write('\t\t\t\txmin = %f\n' % interval.xmin)
                    sink.write('\t\t\t\txmax = %f\n' % interval.xmax)
                    sink.write('\t\t\t\tsink = "%s"\n' % interval.mark)
            else: # PointTier
                sink.write('\t\tclass = "TextTier"\n')
                sink.write('\t\tname = "%s"\n' % tier.name)
                sink.write('\t\txmin = %f\n' % min(tier))
                sink.write('\t\txmax = %f\n' % max(tier))
                sink.write('\t\tpoints: size = %d\n' % len(tier))
                for (k, point) in enumerate(tier):
                    sink.write('\t\t\tpoints [%d]:\n' % k + 1)
                    sink.write('\t\t\t\ttime = %f\n' % point.time)
                    sink.write('\t\t\t\tmark = "%s"\n' % point.mark)
        sink.close()


class mlf(object):
    """
    Read in a HTK .mlf file. iterating over it gives you a list of 
    TextGrids
    """

    def __init__(self, file, samplerate=10e6):
        """ doctest """
        self.files = []
        source = open(file, 'r')
        source.readline() # get rid of header
        while 1: # loop over text
            name = source.readline()[1:-1]
            if name:
                grid = TextGrid()
                phon = IntervalTier('phones')
                word = IntervalTier('words')
                wmrk = ''
                wsrt = 0.
                wend = 0.
                while 1: # loop over the lines in each grid
                    line = source.readline().rstrip().split()
                    if len(line) == 4: # word on this baby
                        pmin = float(line[0]) / samplerate
                        pmax = float(line[1]) / samplerate
                        phon.append(Interval(pmin, pmax, line[2]))
                        if wmrk:
                            word.append(Interval(wsrt, wend, wmrk))
                        wmrk = line[3]
                        wsrt = pmin
                        wend = pmax
                    elif len(line) == 3: # just phone
                        pmin = float(line[0]) / samplerate
                        pmax = float(line[1]) / samplerate
                        phon.append(Interval(pmin, pmax, line[2]))
                        wend = pmax 
                    else: # it's a period
                        word.append(Interval(wsrt, wend, wmrk))
                        self.files.append(grid)
                        break
                grid.append(phon)
                grid.append(word)
            else:
                source.close()
                break


    def write(self, prefix=''):
        """ 
        """
        raise NotImplementedError


if __name__ == '__main__':
    import doctest
    doctest.testmod()
