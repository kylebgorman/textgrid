#!/usr/bin/env python -O
#
# Copyright (c) 2011-2016 Kyle Gorman, Max Bane, Morgan Sonderegger
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# textgrid.py: classes for Praat TextGrid and HTK mlf files
#
# Max Bane <bane@uchicago.edu>
# Kyle Gorman <gormanky@ohsu.edu>
# Morgan Sonderegger <morgan.sonderegger@mcgill.ca>

from __future__ import print_function

import re
import codecs
import os.path

from sys import stderr
from bisect import bisect_left

from .exceptions import TextGridError

DEFAULT_TEXTGRID_PRECISION = 5
DEFAULT_MLF_PRECISION = 5


def _getMark(text, short):
    """
    Return the mark or text entry on a line. Praat escapes double-quotes
    by doubling them, so doubled double-quotes are read as single
    double-quotes. Newlines within an entry are allowed.
    """

    line = text.readline()

    # check that the line begins with a valid entry type
    if not short and not re.match(r'^\s*(text|mark) = "', line):
        raise ValueError('Bad entry: ' + line)

    # read until the number of double-quotes is even
    while line.count('"') % 2:
        next_line = text.readline()

        if not next_line:
            raise EOFError('Bad entry: ' + line[:20] + '...')

        line += next_line
    if short:
        pattern = r'^"(.*?)"\s*$'
    else:
        pattern = r'^\s*(text|mark) = "(.*?)"\s*$'
    entry = re.match(pattern, line, re.DOTALL)

    return entry.groups()[-1].replace('""', '"')


def _formatMark(text):
    return text.replace('"', '""')


def detectEncoding(f):
    """
    This helper method returns the file encoding corresponding to path f.
    This handles UTF-8, which is itself an ASCII extension, so also ASCII.
    """
    encoding = 'ascii'
    try:
        with codecs.open(f, 'r', encoding='utf-16') as source:
            source.readline()  # Read one line to ensure correct encoding
    except UnicodeError:
        try:
            with codecs.open(f, 'r', encoding='utf-8-sig') as source: #revised utf-8 to utf-8-sig for utf-8 with byte order mark (BOM)  
                source.readline()  # Read one line to ensure correct encoding
        except UnicodeError:
            with codecs.open(f, 'r', encoding='ascii') as source:
                source.readline()  # Read one line to ensure correct encoding
        else:
            encoding = 'utf-8-sig' #revised utf-8 to utf-8-sig for utf-8 with byte order mark (BOM) 
    else:
        encoding = 'utf-16'

    return encoding


class Point(object):
    """
    Represents a point in time with an associated textual mark, as stored
    in a PointTier.

    """

    def __init__(self, time, mark):
        self.time = time
        self.mark = mark

    def __repr__(self):
        return 'Point({0}, {1})'.format(self.time,
                                        self.mark if self.mark else None)

    def __lt__(self, other):
        if hasattr(other, 'time'):
            return self.time < other.time
        elif hasattr(other, 'minTime'):
            return self.time < other.minTime
        else:
            return self.time < other

    def __gt__(self, other):
        if hasattr(other, 'time'):
            return self.time > other.time
        elif hasattr(other, 'maxTime'):
            return self.time > other.maxTime
        else:
            return self.time > other

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.time == other.time
        elif isinstance(other, Interval):
            return other.minTime < self.time < other.maxTime
        else:
            return self.time == other

    def __gte__(self, other):
        return self > other or self == other

    def __lte__(self, other):
        return self < other or self == other

    def __cmp__(self, other):
        """
        In addition to the obvious semantics, Point/Interval comparison is
        0 iff the point is inside the interval (non-inclusively), if you
        need inclusive membership, use Interval.__contains__
        """
        if hasattr(other, 'time'):
            return cmp(self.time, other.time)
        elif hasattr(other, 'minTime') and hasattr(other, 'maxTime'):
            return cmp(self.time, other.minTime) + \
                   cmp(self.time, other.maxTime)
        else:  # hopefully numerical
            return cmp(self.time, other)

    def __iadd__(self, other):
        self.time += other

    def __isub__(self, other):
        self.time -= other


def decode(string):
    """
    Decode HTK's mangling of UTF-8 strings into something useful
    """
    # print(string)
    return string
    return string.decode('string_escape').decode('UTF-8')


class Interval(object):
    """
    Represents an interval of time, with an associated textual mark, as
    stored in an IntervalTier.

    """

    def __init__(self, minTime, maxTime, mark):
        if minTime >= maxTime:
            # Praat does not support intervals with duration <= 0
            raise ValueError(minTime, maxTime)
        self.minTime = minTime
        self.maxTime = maxTime
        self.mark = mark
        self.strict = True

    def __repr__(self):
        return 'Interval({0}, {1}, {2})'.format(self.minTime, self.maxTime,
                                                self.mark if self.mark else None)

    def duration(self):
        """
        Returns the duration of the interval in seconds.
        """
        return self.maxTime - self.minTime

    def __lt__(self, other):
        if hasattr(other, 'minTime'):
            if self.strict and self.overlaps(other):
                raise (ValueError(self, other))
            return self.minTime < other.minTime
        elif hasattr(other, 'time'):
            return self.maxTime < other.time
        else:
            return self.maxTime < other

    def __gt__(self, other):
        if hasattr(other, 'maxTime'):
            if self.strict and self.overlaps(other):
                raise (ValueError(self, other))
            return self.maxTime > other.maxTime
        elif hasattr(other, 'time'):
            return self.minTime > other.time
        else:
            return self.minTime > other

    def __gte__(self, other):
        return self > other or self == other

    def __lte__(self, other):
        return self < other or self == other

    def __cmp__(self, other):
        if hasattr(other, 'minTime') and hasattr(other, 'maxTime'):
            if self.overlaps(other):
                raise ValueError(self, other)
                # this returns the two intervals, so user can patch things
                # up if s/he so chooses
            return cmp(self.minTime, other.minTime)
        elif hasattr(other, 'time'):  # comparing Intervals and Points
            return cmp(self.minTime, other.time) + \
                   cmp(self.maxTime, other.time)
        else:
            return cmp(self.minTime, other) + cmp(self.maxTime, other)

    def __eq__(self, other):
        """
        This might seem superfluous but not that a ValueError will be
        raised if you compare two intervals to each other...not anymore
        """
        if hasattr(other, 'minTime') and hasattr(other, 'maxTime'):
            if self.minTime == other.minTime:
                if self.maxTime == other.maxTime:
                    return True
        elif hasattr(other, 'time'):
            return self.minTime < other.time < self.maxTime
        else:
            return False

    def __iadd__(self, other):
        self.minTime += other
        self.maxTime += other

    def __isub__(self, other):
        self.minTime -= other
        self.maxTime -= other

    def overlaps(self, other):
        """
        Tests whether self overlaps with the given interval. Symmetric.
        See: http://www.rgrjr.com/emacs/overlap.html
        """
        return other.minTime < self.maxTime and \
               self.minTime < other.maxTime

    def __contains__(self, other):
        """
        Tests whether the given time point is contained in this interval,
        either a numeric type or a Point object.
        """
        if hasattr(other, 'minTime') and hasattr(other, 'maxTime'):
            return self.minTime <= other.minTime and \
                   other.maxTime <= self.maxTime
        elif hasattr(other, 'time'):
            return self.minTime <= other.time <= self.maxTime
        else:
            return self.minTime <= other <= self.maxTime

    def bounds(self):
        return (self.minTime, self.maxTime)


class PointTier(object):
    """
    Represents Praat PointTiers (also called TextTiers) as list of Points
    (e.g., for point in pointtier). A PointTier is used much like a Python
    set in that it has add/remove methods, not append/extend methods.

    """

    def __init__(self, name=None, minTime=0., maxTime=None):
        self.name = name
        self.minTime = minTime
        self.maxTime = maxTime
        self.points = []

    def __str__(self):
        return '<PointTier {0}, {1} points>'.format(self.name, len(self))

    def __repr__(self):
        return 'PointTier({0}, {1})'.format(self.name, self.points)

    def __iter__(self):
        return iter(self.points)

    def __len__(self):
        return len(self.points)

    def __getitem__(self, i):
        return self.points[i]

    def add(self, time, mark):
        """
        constructs a Point and adds it to the PointTier, maintaining order
        """
        self.addPoint(Point(time, mark))

    def addPoint(self, point):
        if point < self.minTime:
            raise ValueError(self.minTime)  # too early
        if self.maxTime and point > self.maxTime:
            raise ValueError(self.maxTime)  # too late
        i = bisect_left(self.points, point)
        if i < len(self.points) and self.points[i].time == point.time:
            raise ValueError(point)  # we already got one right there
        self.points.insert(i, point)

    def remove(self, time, mark):
        """
        removes a constructed Point i from the PointTier
        """
        self.removePoint(Point(time, mark))

    def removePoint(self, point):
        self.points.remove(point)

    def read(self, f, round_digits=DEFAULT_TEXTGRID_PRECISION):
        """
        Read the Points contained in the Praat-formated PointTier/TextTier
        file indicated by string f
        """
        encoding = detectEncoding(f)
        with codecs.open(f, 'r', encoding=encoding) as source:
            file_type, short = parse_header(source)
            if file_type != 'TextTier':
                raise TextGridError('The file could not be parsed as a PointTier as it is lacking a proper header.')

            self.minTime = parse_line(source.readline(), short, round_digits)
            self.maxTime = parse_line(source.readline(), short, round_digits)
            n = int(parse_line(source.readline(), short, round_digits))
            for i in range(n):
                source.readline().rstrip()  # header
                itim = parse_line(source.readline(), short, round_digits)
                imrk = _getMark(source, short)
                self.points.append(Point(itim, imrk))

    def write(self, f):
        """
        Write the current state into a Praat-format PointTier/TextTier
        file. f may be a file object to write to, or a string naming a
        path for writing
       """
        sink = f if hasattr(f, 'write') else codecs.open(f, 'w', 'UTF-8')
        print('File type = "ooTextFile"', file=sink)
        print('Object class = "TextTier"\n', file=sink)

        print('xmin = {0}'.format(self.minTime), file=sink)
        print('xmax = {0}'.format(self.maxTime if self.maxTime \
                                      else self.points[-1].time), file=sink)
        print('points: size = {0}'.format(len(self)), file=sink)
        for (i, point) in enumerate(self.points, 1):
            print('points [{0}]:'.format(i), file=sink)
            print('\ttime = {0}'.format(point.time), file=sink)
            mark = _formatMark(point.mark)
            print('\tmark = "{0}"'.format(mark), file=sink)
        sink.close()

    def bounds(self):
        return (self.minTime, self.maxTime or self.points[-1].time)

    # alternative constructor

    @classmethod
    def fromFile(cls, f, name=None):
        pt = cls(name=name)
        pt.read(f)
        return pt


class IntervalTier(object):
    """
    Represents Praat IntervalTiers as list of sequence types of Intervals
    (e.g., for interval in intervaltier). An IntervalTier is used much like a
    Python set in that it has add/remove methods, not append/extend methods.

    """

    def __init__(self, name=None, minTime=0., maxTime=None):
        self.name = name
        self.minTime = minTime
        self.maxTime = maxTime
        self.intervals = []
        self.strict = True

    def __str__(self):
        return '<IntervalTier {0}, {1} intervals>'.format(self.name,
                                                          len(self))

    def __repr__(self):
        return 'IntervalTier({0}, {1})'.format(self.name, self.intervals)

    def __iter__(self):
        return iter(self.intervals)

    def __len__(self):
        return len(self.intervals)

    def __getitem__(self, i):
        return self.intervals[i]

    def add(self, minTime, maxTime, mark):
        interval = Interval(minTime, maxTime, mark)
        interval.strict = self.strict
        self.addInterval(interval)

    def addInterval(self, interval):
        if interval.minTime < self.minTime:  # too early
            raise ValueError(self.minTime)
        if self.maxTime and interval.maxTime > self.maxTime:  # too late
            # raise ValueError, self.maxTime
            raise ValueError(self.maxTime)
        i = bisect_left(self.intervals, interval)
        if i != len(self.intervals) and self.intervals[i] == interval:
            raise ValueError(self.intervals[i])
        interval.strict = self.strict
        self.intervals.insert(i, interval)

    def remove(self, minTime, maxTime, mark):
        self.removeInterval(Interval(minTime, maxTime, mark))

    def removeInterval(self, interval):
        self.intervals.remove(interval)

    def indexContaining(self, time):
        """
        Returns the index of the interval containing the given time point,
        or None if the time point is outside the bounds of this tier. The
        argument can be a numeric type, or a Point object.
        """
        i = bisect_left(self.intervals, time)
        if i != len(self.intervals):
            if self.intervals[i].minTime <= time <= \
                    self.intervals[i].maxTime:
                return i

    def intervalContaining(self, time):
        """
        Returns the interval containing the given time point, or None if
        the time point is outside the bounds of this tier. The argument
        can be a numeric type, or a Point object.
        """
        i = self.indexContaining(time)
        if i:
            return self.intervals[i]

    def read(self, f, round_digits=DEFAULT_TEXTGRID_PRECISION):
        """
        Read the Intervals contained in the Praat-formated IntervalTier
        file indicated by string f
        """
        encoding = detectEncoding(f)
        with codecs.open(f, 'r', encoding=encoding) as source:
            file_type, short = parse_header(source)
            if file_type != 'IntervalTier':
                raise TextGridError('The file could not be parsed as a IntervalTier as it is lacking a proper header.')

            self.minTime = parse_line(source.readline(), short, round_digits)
            self.maxTime = parse_line(source.readline(), short, round_digits)
            n = int(parse_line(source.readline(), short, round_digits))
            for i in range(n):
                source.readline().rstrip()  # header
                imin = parse_line(source.readline(), short, round_digits)
                imax = parse_line(source.readline(), short, round_digits)
                imrk = _getMark(source, short)
                self.intervals.append(Interval(imin, imax, imrk))

    def _fillInTheGaps(self, null):
        """
        Returns a pseudo-IntervalTier with the temporal gaps filled in
        """
        prev_t = self.minTime
        output = []
        for interval in self.intervals:
            if prev_t < interval.minTime:
                output.append(Interval(prev_t, interval.minTime, null))
            output.append(interval)
            prev_t = interval.maxTime
        # last interval
        if self.maxTime is not None and prev_t < self.maxTime:  # also false if maxTime isn't defined
            output.append(Interval(prev_t, self.maxTime, null))
        return output

    def write(self, f, null=''):
        """
        Write the current state into a Praat-format IntervalTier file. f
        may be a file object to write to, or a string naming a path for
        writing
        """
        sink = f if hasattr(f, 'write') else open(f, 'w')
        print('File type = "ooTextFile"', file=sink)
        print('Object class = "IntervalTier"\n', file=sink)
        print('xmin = {0}'.format(self.minTime), file=sink)
        print('xmax = {0}'.format(self.maxTime if self.maxTime \
                                      else self.intervals[-1].maxTime), file=sink)
        # compute the number of intervals and make the empty ones
        output = self._fillInTheGaps(null)
        # write it all out
        print('intervals: size = {0}'.format(len(output)), file=sink)
        for (i, interval) in enumerate(output, 1):
            print('intervals [{0}]'.format(i), file=sink)
            print('\txmin = {0}'.format(interval.minTime), file=sink)
            print('\txmax = {0}'.format(interval.maxTime), file=sink)
            mark = _formatMark(interval.mark)
            print('\ttext = "{0}"'.format(mark), file=sink)
        sink.close()

    def bounds(self):
        return self.minTime, self.maxTime or self.intervals[-1].maxTime

    # alternative constructor

    @classmethod
    def fromFile(cls, f, name=None):
        it = cls(name=name)
        it.intervals = []
        it.read(f)
        return it


def parse_line(line, short, to_round):
    line = line.strip()
    if short:
        if '"' in line:
            return line[1:-1]
        return round(float(line), to_round)
    if '"' in line:
        m = re.match(r'.+? = "(.*)"', line)
        return m.groups()[0]
    m = re.match(r'.+? = (.*)', line)
    return round(float(m.groups()[0]), to_round)


def parse_header(source):
    header = source.readline()  # header junk
    m = re.match('File type = "([\w ]+)"', header)
    if m is None or not m.groups()[0].startswith('ooTextFile'):
        raise TextGridError('The file could not be parsed as a Praat text file as it is lacking a proper header.')

    short = 'short' in m.groups()[0]
    file_type = parse_line(source.readline(), short, '')  # header junk
    t = source.readline()  # header junk
    return file_type, short


class TextGrid(object):
    """
    Represents Praat TextGrids as list of sequence types of tiers (e.g.,
    for tier in textgrid), and as map from names to tiers (e.g.,
    textgrid['tierName']). Whereas the *Tier classes that make up a
    TextGrid impose a strict ordering on Points/Intervals, a TextGrid
    instance is given order by the user. Like a true Python list, there
    are append/extend methods for a TextGrid.

    """

    def __init__(self, name=None, minTime=0., maxTime=None, strict=True):
        """
        Construct a TextGrid instance with the given (optional) name
        (which is only relevant for MLF stuff). If file is given, it is a
        string naming the location of a Praat-format TextGrid file from
        which to populate this instance.
        """
        self.name = name
        self.minTime = minTime
        self.maxTime = maxTime
        self.tiers = []
        self.strict = strict

    def __str__(self):
        return '<TextGrid {0}, {1} Tiers>'.format(self.name, len(self))

    def __repr__(self):
        return 'TextGrid({0}, {1})'.format(self.name, self.tiers)

    def __iter__(self):
        return iter(self.tiers)

    def __len__(self):
        return len(self.tiers)

    def __getitem__(self, i):
        """
        Return the ith tier
        """
        return self.tiers[i]

    def getFirst(self, tierName):
        """
        Return the first tier with the given name.
        """
        for t in self.tiers:
            if t.name == tierName:
                return t

    def getList(self, tierName):
        """
        Return a list of all tiers with the given name.
        """
        tiers = []
        for t in self.tiers:
            if t.name == tierName:
                tiers.append(t)
        return tiers

    def getNames(self):
        """
        return a list of the names of the intervals contained in this
        TextGrid
        """
        return [tier.name for tier in self.tiers]

    def append(self, tier):
        if self.maxTime is not None and tier.maxTime is not None and tier.maxTime > self.maxTime:
            raise ValueError(self.maxTime)  # too late
        tier.strict = self.strict
        for i in tier:
            i.strict = self.strict
        self.tiers.append(tier)

    def extend(self, tiers):
        if min([t.minTime for t in tiers]) < self.minTime:
            raise ValueError(self.minTime)  # too early
        if self.maxTime and max([t.minTime for t in tiers]) > self.maxTime:
            raise ValueError(self.maxTime)  # too late
        self.tiers.extend(tiers)

    def pop(self, i=None):
        """
        Remove and return tier at index i (default last). Will raise
        IndexError if TextGrid is empty or index is out of range.
        """
        return (self.tiers.pop(i) if i else self.tiers.pop())

    def read(self, f, round_digits=DEFAULT_TEXTGRID_PRECISION, encoding=None):
        """
        Read the tiers contained in the Praat-formatted TextGrid file
        indicated by string f. Times are rounded to the specified precision.
        """
        if encoding is None:
            encoding = detectEncoding(f)
        with codecs.open(f, 'r', encoding=encoding) as source:
            file_type, short = parse_header(source)
            if file_type != 'TextGrid':
                raise TextGridError('The file could not be parsed as a TextGrid as it is lacking a proper header.')
            self.minTime = parse_line(source.readline(), short, round_digits)
            self.maxTime = parse_line(source.readline(), short, round_digits)
            source.readline()  # more header junk
            if short:
                m = int(source.readline().strip())  # will be self.n
            else:
                m = int(source.readline().strip().split()[2])  # will be self.n
            if not short:
                source.readline()
            for i in range(m):  # loop over grids
                if not short:
                    source.readline()
                if parse_line(source.readline(), short, round_digits) == 'IntervalTier':
                    inam = parse_line(source.readline(), short, round_digits)
                    imin = parse_line(source.readline(), short, round_digits)
                    imax = parse_line(source.readline(), short, round_digits)
                    itie = IntervalTier(inam, imin, imax)
                    itie.strict = self.strict
                    n = int(parse_line(source.readline(), short, round_digits))
                    for j in range(n):
                        if not short:
                            source.readline().rstrip().split()  # header junk
                        jmin = parse_line(source.readline(), short, round_digits)
                        jmax = parse_line(source.readline(), short, round_digits)
                        jmrk = _getMark(source, short)
                        if jmin < jmax:  # non-null
                            itie.addInterval(Interval(jmin, jmax, jmrk))
                    self.append(itie)
                else:  # pointTier
                    inam = parse_line(source.readline(), short, round_digits)
                    imin = parse_line(source.readline(), short, round_digits)
                    imax = parse_line(source.readline(), short, round_digits)
                    itie = PointTier(inam)
                    n = int(parse_line(source.readline(), short, round_digits))
                    for j in range(n):
                        source.readline().rstrip()  # header junk
                        jtim = parse_line(source.readline(), short, round_digits)
                        jmrk = _getMark(source, short)
                        itie.addPoint(Point(jtim, jmrk))
                    self.append(itie)

    def write(self, f, null=''):
        """
        Write the current state into a Praat-format TextGrid file. f may
        be a file object to write to, or a string naming a path to open
        for writing.
        """
        sink = f if hasattr(f, 'write') else codecs.open(f, 'w', 'UTF-8')
        print('File type = "ooTextFile"', file=sink)
        print('Object class = "TextGrid"\n', file=sink)
        print('xmin = {0}'.format(self.minTime), file=sink)
        # compute max time
        maxT = self.maxTime
        if not maxT:
            maxT = max([t.maxTime if t.maxTime else t[-1].maxTime \
                        for t in self.tiers])
        print('xmax = {0}'.format(maxT), file=sink)
        print('tiers? <exists>', file=sink)
        print('size = {0}'.format(len(self)), file=sink)
        print('item []:', file=sink)
        for (i, tier) in enumerate(self.tiers, 1):
            print('\titem [{0}]:'.format(i), file=sink)
            if tier.__class__ == IntervalTier:
                print('\t\tclass = "IntervalTier"', file=sink)
                print('\t\tname = "{0}"'.format(tier.name), file=sink)
                print('\t\txmin = {0}'.format(tier.minTime), file=sink)
                print('\t\txmax = {0}'.format(maxT), file=sink)
                # compute the number of intervals and make the empty ones
                output = tier._fillInTheGaps(null)
                print('\t\tintervals: size = {0}'.format(
                    len(output)), file=sink)
                for (j, interval) in enumerate(output, 1):
                    print('\t\t\tintervals [{0}]:'.format(j), file=sink)
                    print('\t\t\t\txmin = {0}'.format(
                        interval.minTime), file=sink)
                    print('\t\t\t\txmax = {0}'.format(
                        interval.maxTime), file=sink)
                    mark = _formatMark(interval.mark)
                    print('\t\t\t\ttext = "{0}"'.format(mark), file=sink)
            elif tier.__class__ == PointTier:  # PointTier
                print('\t\tclass = "TextTier"', file=sink)
                print('\t\tname = "{0}"'.format(tier.name), file=sink)
                print('\t\txmin = {0}'.format(tier.minTime), file=sink)
                print('\t\txmax = {0}'.format(maxT), file=sink)
                print('\t\tpoints: size = {0}'.format(len(tier)), file=sink)
                for (k, point) in enumerate(tier, 1):
                    print('\t\t\tpoints [{0}]:'.format(k), file=sink)
                    print('\t\t\t\ttime = {0}'.format(point.time), file=sink)
                    mark = _formatMark(point.mark)
                    print('\t\t\t\tmark = "{0}"'.format(mark), file=sink)
        sink.close()

    # alternative constructor

    @classmethod
    def fromFile(cls, f, name=None):
        tg = cls(name=name)
        tg.read(f)
        return tg


class MLF(object):
    """
    Read in a HTK .mlf file generated with HVite -o SM and turn it into a
    list of TextGrids. The resulting class can be iterated over to give
    one TextGrid at a time, or the write(prefix='') class method can be
    used to write all the resulting TextGrids into separate files.

    Unlike other classes, this is always initialized from a text file.
    """

    def __init__(self, f, samplerate=10e6):
        self.grids = []
        self.read(f, samplerate)

    def __iter__(self):
        return iter(self.grids)

    def __str__(self):
        return '<MLF, {0} TextGrids>'.format(len(self))

    def __repr__(self):
        return 'MLF({0})'.format(self.grids)

    def __len__(self):
        return len(self.grids)

    def __getitem__(self, i):
        """
        Return the ith TextGrid
        """
        return self.grids[i]

    def read(self, f, samplerate, round_digits=DEFAULT_MLF_PRECISION):
        source = open(f, 'r')  # HTK returns ostensible ASCII

        source.readline()  # header
        while True:  # loop over text
            name = re.match('\"(.*)\"', source.readline().rstrip())
            if name:
                name = name.groups()[0]
                grid = TextGrid(name)
                phon = IntervalTier(name='phones')
                word = IntervalTier(name='words')
                wmrk = ''
                wsrt = 0.
                wend = 0.
                while 1:  # loop over the lines in each grid
                    line = source.readline().rstrip().split()
                    if len(line) == 4:  # word on this baby
                        pmin = round(float(line[0]) / samplerate, round_digits)
                        pmax = round(float(line[1]) / samplerate, round_digits)
                        if pmin == pmax:
                            raise ValueError('null duration interval')
                        phon.add(pmin, pmax, line[2])
                        if wmrk:
                            word.add(wsrt, wend, wmrk)
                        wmrk = decode(line[3])
                        wsrt = pmin
                        wend = pmax
                    elif len(line) == 3:  # just phone
                        pmin = round(float(line[0]) / samplerate, round_digits)
                        pmax = round(float(line[1]) / samplerate, round_digits)
                        if line[2] == 'sp' and pmin != pmax:
                            if wmrk:
                                word.add(wsrt, wend, wmrk)
                            wmrk = decode(line[2])
                            wsrt = pmin
                            wend = pmax
                        elif pmin != pmax:
                            phon.add(pmin, pmax, line[2])
                        wend = pmax
                    else:  # it's a period
                        word.add(wsrt, wend, wmrk)
                        self.grids.append(grid)
                        break
                grid.append(phon)
                grid.append(word)
            else:
                source.close()
                break

    def write(self, prefix=''):
        """
        Write the current state into Praat-formatted TextGrids. The
        filenames that the output is stored in are taken from the HTK
        label files. If a string argument is given, then the any prefix in
        the name of the label file (e.g., "mfc/myLabFile.lab"), it is
        truncated and files are written to the directory given by the
        prefix. An IOError will result if the folder does not exist.

        The number of TextGrids is returned.
        """
        for grid in self.grids:
            (junk, tail) = os.path.split(grid.name)
            (root, junk) = os.path.splitext(tail)
            my_path = os.path.join(prefix, root + '.TextGrid')
            grid.write(codecs.open(my_path, 'w', 'UTF-8'))
        return len(self.grids)
