#!/usr/bin/env python
#
# RWtests.py
#
# Max Bane <bane@uchicago.edu>
# Kyle Gorman <kgorman@ling.upenn.edu>
# Morgan Sonderegger <morgan@cs.uchicago.edu>
#
# Tests for the read-write functions in textgrid.py (they don't make much
# sense as doctests). not particularly useful for users...

from __future__ import unicode_literals

import textgrid
import unittest

from io import StringIO
from os import remove

tg_with_quotes = '''File type = "ooTextFile"
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
'''

mlf_data = """#!MFL!#
"foo.lab"
0 5000000 sil sil
5000000 7000000 SH SHOW
7000000 11000000 OW
11000000 11000000 sp
11000000 17000000 M ME
17000000 19000000 IY
19000000 20000000 sp
20000000 22000000 DH THE
22000000 29000000 AH
29000000 29000000 sp
29000000 35000000 W ONE
35000000 40000000 AH
40000000 45000000 N
45000000 45000000 sp
45000000 52000000 W WAY
52000000 57000000 EY
57000000 57000000 sp
57000000 63000000 F FLIGHTS
63000000 67000000 L
67000000 69000000 AY
69000000 75000000 T
75000000 80000000 S
80000000 81000000 sp
81000000 87000000 F FROM
87000000 93000000 R
93000000 95000000 AH
95000000 102000000 M
102000000 103000000 sp
103000000 105000000 D DETROIT
105000000 108000000 IH
108000000 113000000 T
113000000 120000000 R
120000000 124000000 OY
124000000 131000000 T
131000000 131000000 sp
131000000 133000000 T TO
133000000 135000000 UW
135000000 136000000 sp
136000000 142000000 W WESTCHESTER
142000000 148000000 EH
148000000 152000000 S
152000000 156000000 T
156000000 161000000 CH
161000000 164000000 EH
164000000 170000000 S
170000000 172000000 T
172000000 177000000 ER
177000000 177000000 sp
177000000 184000000 K COUNTY
184000000 186000000 AW
186000000 190000000 N
190000000 194000000 T
194000000 201000000 IY
201000000 201000000 sp
201000000 230000000 sil sil
.
"bar.lab"
0 5000000 sil sil
5000000 7000000 F FIND
7000000 13000000 AY
13000000 16000000 N
16000000 18000000 D
18000000 18000000 sp
18000000 18100000 M ME
18100000 24000000 IY
24000000 24000000 sp
24000000 30000000 AH A
30000000 32000000 sp
32000000 33000000 F FLIGHT
33000000 40000000 L
40000000 47000000 AY
47000000 50000000 T
50000000 51500000 sp
51500000 52000000 DH THAT
52000000 54000000 AE
54000000 56000000 T
56000000 56100000 sp
56100000 62000000 F FLIES
62000000 69000000 L
69000000 74000000 AY
74000000 77000000 Z
77000000 77000000 sp
77000000 81000000 R FROM
81000000 88000000 AH
88000000 95000000 M
95000000 96000000 sp
96000000 98000000 M MEMPHIS
98000000 100000000 EH
100000000 107000000 M
107000000 109000000 F
109000000 113000000 AH
113000000 118000000 S
118000000 119000000 sp
119000000 120000000 T TO
120000000 121000000 UW
121000000 122000000 sp
122000000 126000000 T TACOMA
126000000 132000000 AH
132000000 134000000 K
134000000 140000000 OW
140000000 142000000 M
142000000 146000000 AH
146000000 146000000 sp
146000000 148000000 sil sil
.
"""


class TestDoubleQuotes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open('test_double_quotes.TextGrid', 'w') as tg_file:
            tg_file.write(tg_with_quotes)

        cls.tg = textgrid.TextGrid.fromFile('test_double_quotes.TextGrid')

        cls.tg.write('test_double_quotes_tg.TextGrid')
        cls.tg[0].write('test_double_quotes_it.IntervalTier')
        cls.tg[1].write('test_double_quotes_pt.PointTier')

        cls.interval_marks = ['"Is anyone home?"', 'asked "Pat"']
        cls.point_marks = ['"event"', '"event" with quotes again']

        cls.interval_marks_txt = [' """Is anyone home?"""\n', ' "asked ""Pat"""\n']
        cls.point_marks_txt = [' """event"""\n', ' """event"" with quotes again"\n']

    @classmethod
    def tearDownClass(cls):
        remove('test_double_quotes.TextGrid')
        remove('test_double_quotes_tg.TextGrid')
        remove('test_double_quotes_it.IntervalTier')
        remove('test_double_quotes_pt.PointTier')

    def test_read_tg_double_quotes(self):
        for n, mark in enumerate(self.interval_marks):
            self.assertEqual(self.tg[0][n].mark, mark)

        for n, mark in enumerate(self.point_marks):
            self.assertEqual(self.tg[1][n].mark, mark)

    def test_write_tg_double_quotes(self):
        with open('test_double_quotes_tg.TextGrid') as tg_file:
            tg_string = tg_file.read()

        for mark in self.interval_marks_txt:
            self.assertIn(mark, tg_string)

        for mark in self.point_marks_txt:
            self.assertIn(mark, tg_string)

    def test_read_it_double_quotes(self):
        it = textgrid.IntervalTier.fromFile('test_double_quotes_it.IntervalTier')

        for n, mark in enumerate(self.interval_marks):
            self.assertEqual(it[n].mark, mark)

    def test_write_it_double_quotes(self):
        with open('test_double_quotes_it.IntervalTier') as it_file:
            it_string = it_file.read()

        for mark in self.interval_marks_txt:
            self.assertIn(mark, it_string)

    def test_read_pt_double_quotes(self):
        pt = textgrid.PointTier.fromFile('test_double_quotes_pt.PointTier')

        for n, mark in enumerate(self.point_marks):
            self.assertEqual(pt[n].mark, mark)

    def test_write_pt_double_quotes(self):
        with open('test_double_quotes_pt.PointTier') as pt_file:
            pt_string = pt_file.read()

        for mark in self.point_marks_txt:
            self.assertIn(mark, pt_string)


class TestRoundTrip(unittest.TestCase):

    def setUp(self):
        with open('baz.mlf', 'w') as mlf_file:
            mlf_file.write(mlf_data)

    def tearDown(self):
        remove('baz.mlf')
        remove('foo.TextGrid')
        remove('foo_copy.TextGrid')
        remove('bar.TextGrid')
        remove('phones.IntervalTier')

    def test_roundtrip(self):
        ## MLF
        # read it in, writing over mlf
        mlf = textgrid.MLF('baz.mlf')
        # write them to foo.TextGrid and bar.TextGrid
        mlf.write()

        ## TextGrid
        # read foo.TextGrid
        foo = textgrid.TextGrid.fromFile('foo.TextGrid')
        # write it out
        foo.write('foo_copy.TextGrid')
        # read it back in
        foo_copy = textgrid.TextGrid.fromFile('foo_copy.TextGrid')

        self.assertEqual(repr(foo), repr(foo_copy))

        ## IntervalTier
        phones = foo[0]
        # write it out
        phones.write('phones.IntervalTier')
        # read it back in
        phones_copy = textgrid.IntervalTier.fromFile('phones.IntervalTier', 'phones')

        self.assertEqual(repr(phones), repr(phones_copy))


class TestMultilineTextField(unittest.TestCase):

    def test_multiline(self):
        some_text = """            text = "This is an annoying, but
not technically ill-formed
line."
This latter line shouldn't be pulled in at all.
"""

        source = StringIO(some_text)

        self.assertEqual(textgrid.textgrid._getMark(source, False), """This is an annoying, but
not technically ill-formed
line.""")

    def test_multiline_with_double_quotes(self):
        multiline_text_with_quotes = '''            text = "This is an ""annoying"", ""but""
not ""technically"" ill-formed
line."
This latter line shouldn't be pulled in at all.
'''
        source = StringIO(multiline_text_with_quotes)
    
        self.assertEqual(textgrid.textgrid._getMark(source, False), """This is an "annoying", "but"
not "technically" ill-formed
line.""")


class TestPointComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.foo = textgrid.textgrid.Point(3.0, 'foo')
        cls.bar = textgrid.textgrid.Point(4.0, 'bar')
        cls.baz = textgrid.textgrid.Interval(3.0, 5.0, 'baz')

    def test_point_point(self):
        self.assertLess(self.foo, self.bar)
        self.assertEqual(self.foo, textgrid.textgrid.Point(3.0, 'baz'))
        self.assertGreater(self.bar, self.foo)

    def test_point_value(self):
        self.assertLess(self.foo, 4.0)
        self.assertEqual(self.foo, 3.0)
        self.assertFalse(self.foo > 5.0)
    
    def test_point_interval(self):
        self.assertFalse(self.foo < self.baz)
        self.assertFalse(self.foo == self.baz)
        self.assertEqual(self.bar, self.baz)


class TestIntervalComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.foo = textgrid.textgrid.Point(3.0, 'foo')
        cls.bar = textgrid.textgrid.Point(4.0, 'bar')
        cls.baz = textgrid.textgrid.Interval(3.0, 5.0, 'baz')

    def test_point_in_interval(self):
        self.assertIn(self.foo, self.baz)
        self.assertIn(self.bar, self.baz)
    
    def test_value_in_interval(self):
        self.assertIn(3.0, self.baz)
        self.assertIn(4.0, self.baz)


class TestPointTierComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        foo_point = textgrid.textgrid.Point(3.0, 'foo')
        bar_point = textgrid.textgrid.Point(4.0, 'bar')
        baz_interval = textgrid.textgrid.Interval(3.0, 5.0, 'baz')

        cls.foo = textgrid.textgrid.PointTier()
        cls.bar = textgrid.textgrid.PointTier()
        cls.bam = textgrid.textgrid.PointTier()
        cls.baz = textgrid.textgrid.IntervalTier()

        cls.foo.addPoint(foo_point)
        cls.bar.addPoint(bar_point)
        cls.bam.addPoint(bar_point)
        cls.baz.addInterval(baz_interval)

    def test_point_equal(self):
        self.assertEqual(self.bar, self.bam)

    def test_point_unequal(self):
        self.assertNotEqual(self.foo, self.bar)

    def test_type_unequal(self):
        self.assertNotEqual(self.foo, self.baz)


class TestIntervalTierComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        foo_point = textgrid.textgrid.Point(3.0, 'foo')
        baz_interval = textgrid.textgrid.Interval(3.0, 5.0, 'baz')
        bat_interval = textgrid.textgrid.Interval(5.0, 6.0, 'bar')

        cls.foo = textgrid.textgrid.PointTier()
        cls.bar = textgrid.textgrid.IntervalTier()
        cls.baz = textgrid.textgrid.IntervalTier()
        cls.bat = textgrid.textgrid.IntervalTier()

        cls.foo.addPoint(foo_point)
        cls.bar.addInterval(baz_interval)
        cls.baz.addInterval(baz_interval)
        cls.bat.addInterval(bat_interval)

    def test_interval_equal(self):
        self.assertEqual(self.bar, self.baz)

    def test_interval_unequal(self):
        self.assertNotEqual(self.baz, self.bat)

    def test_type_unequal(self):
        self.assertNotEqual(self.foo, self.baz)


class TestTextGridComparison(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        foo_point = textgrid.textgrid.Point(3.0, 'foo')
        bar_interval = textgrid.textgrid.Interval(3.0, 5.0, 'bar')
        baz_interval = textgrid.textgrid.Interval(5.0, 6.0, 'baz')

        cls.foo_tier = textgrid.textgrid.PointTier()
        bar_tier = textgrid.textgrid.IntervalTier()
        baz_tier = textgrid.textgrid.IntervalTier()
        bat_tier = textgrid.textgrid.IntervalTier()

        cls.foo_tier.addPoint(foo_point)
        bar_tier.addInterval(bar_interval)
        baz_tier.addInterval(baz_interval)
        bat_tier.addInterval(baz_interval)

        cls.foo_grid = textgrid.textgrid.TextGrid()
        cls.bar_grid = textgrid.textgrid.TextGrid()
        cls.baz_grid = textgrid.textgrid.TextGrid()
        cls.bat_grid = textgrid.textgrid.TextGrid()

        cls.foo_grid.append(cls.foo_tier)
        cls.bar_grid.append(bar_tier)
        cls.baz_grid.append(baz_tier)
        cls.bat_grid.append(bat_tier)

    def test_textgrid_equal(self):
        self.assertEqual(self.baz_grid, self.bat_grid)

    def test_textgrid_unequal_different_intervals(self):
        self.assertNotEqual(self.bar_grid, self.baz_grid)

    def test_textgrid_unequal_different_tier_types(self):
        self.assertNotEqual(self.foo_grid, self.bar_grid)

    def test_type_unequal(self):
        self.assertNotEqual(self.foo_tier, self.foo_grid)


class TestPointTier(unittest.TestCase):

    def setUp(self):
        self.foo = textgrid.textgrid.PointTier('foo')
    
    def test_add(self):
        self.foo.add(4.0, 'bar')
        self.foo.add(2.0, 'baz')
        
        self.assertEqual(repr(self.foo), 'PointTier(foo, [Point(2.0, baz), Point(4.0, bar)])')
        
    def test_remove(self):
        self.foo.add(4.0, 'bar')
        self.foo.add(2.0, 'baz')
        self.foo.remove(4.0, 'bar')
        self.foo.add(6.0, 'bar')
        
        self.assertEqual(repr(self.foo), 'PointTier(foo, [Point(2.0, baz), Point(6.0, bar)])')


class TestIntervalTier(unittest.TestCase):

    def setUp(self):
        self.foo = textgrid.textgrid.IntervalTier('foo')
        
    def test_add(self):
        self.foo.add(0.0, 2.0, 'bar')
        self.foo.add(2.0, 2.5, 'baz')
        
        self.assertEqual(repr(self.foo), 'IntervalTier(foo, [Interval(0.0, 2.0, bar), Interval(2.0, 2.5, baz)])')

        self.assertRaises(ValueError, self.foo.add, 2.5, 2.5, 'bar')
        
    def test_remove(self):
        self.foo.add(0.0, 2.0, 'bar')
        self.foo.add(2.0, 2.5, 'baz')
        self.foo.remove(0.0, 2.0, 'bar')
        
        self.assertEqual(repr(self.foo), 'IntervalTier(foo, [Interval(2.0, 2.5, baz)])')

    def test_add_before(self):
        self.foo.add(2.0, 2.5, 'baz')
        self.foo.add(0.0, 1.0, 'bar')
        
        self.assertEqual(repr(self.foo), 'IntervalTier(foo, [Interval(0.0, 1.0, bar), Interval(2.0, 2.5, baz)])')

    def test_add_fail(self):
        self.foo.add(0.0, 1.0, 'bar')
        self.foo.add(2.0, 2.5, 'baz')
        
        with self.assertRaisesRegex(ValueError, r'\(Interval\(2.0, 2.5, baz\), Interval\(1.0, 3.0, baz\)\)'):
            self.foo.add(1.0, 3.0, 'baz')
            
    def test_interval_containing(self):
        self.foo.add(0.0, 1.0, 'bar')
        self.foo.add(2.0, 2.5, 'baz')
        
        self.assertEqual(repr(self.foo.intervalContaining(2.25)), 'Interval(2.0, 2.5, baz)')
        self.assertEqual(repr(self.foo.intervalContaining(0.5)), 'Interval(0.0, 1.0, bar)')

    def test_add_too_late(self):
        foo = textgrid.textgrid.IntervalTier('foo', maxTime=3.5)
        
        with self.assertRaisesRegex(ValueError, '3.5'):
            foo.add(2.7, 3.7, 'bar')
    
    def test_fill_in_the_gaps(self):
        foo = textgrid.textgrid.IntervalTier('foo', maxTime=3.5)
        foo.add(1.3, 2.4, 'bar')
        foo.add(2.7, 3.3, 'baz')
        
        temp = foo._fillInTheGaps('')
        
        self.assertEqual(repr(temp[0]), 'Interval(0.0, 1.3, None)')
        self.assertEqual(repr(temp[-1]), 'Interval(3.3, 3.5, None)')
        self.assertEqual(repr(temp[2]), 'Interval(2.4, 2.7, None)')


class TestTextGrid(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.foo = textgrid.textgrid.TextGrid('foo')

        cls.bar = textgrid.textgrid.PointTier('bar')
        cls.bar.add(1.0, 'spam')
        cls.bar.add(2.75, 'eggs')

        cls.baz = textgrid.textgrid.IntervalTier('baz')
        cls.baz.add(0.0, 2.5, 'spam')
        cls.baz.add(2.5, 3.5, 'eggs')

        cls.foo.extend([cls.bar, cls.baz])
        cls.foo.append(cls.bar)

    def test_mintime_maxtime(self):
        self.assertEqual(self.foo.minTime, 0.0)
        self.assertIsNone(self.foo.maxTime)

    def test_get_first(self):
        self.assertEqual(repr(self.foo.getFirst('bar')), 'PointTier(bar, [Point(1.0, spam), Point(2.75, eggs)])')

    def test_get_list(self):
        self.assertEqual(repr(self.foo.getList('bar')[1]), 'PointTier(bar, [Point(1.0, spam), Point(2.75, eggs)])')

    def test_get_names(self):
        self.assertListEqual(self.foo.getNames(), ['bar', 'baz', 'bar'])


class TestReadTextGrid(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import os
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cls.short_textgrid_path = os.path.join(base_dir, 'tests', 'data', 'short_format.TextGrid')
        cls.long_textgrid_path = os.path.join(base_dir, 'tests', 'data', 'long_format.TextGrid')

    def test_read_short(self):
        tg = textgrid.TextGrid()
        tg.read(self.short_textgrid_path)
        assert tg.tiers[0].name == 'phone'
        assert tg.tiers[1].name == 'word'
        assert tg.tiers[0][0].mark == 'sil'
        assert abs(tg.tiers[0][0].minTime - 1358.8925) < 0.01
        assert abs(tg.tiers[0][0].maxTime - 1361.8925) < 0.01

    def test_read_long(self):
        tg = textgrid.TextGrid()
        tg.read(self.long_textgrid_path)
        assert tg.tiers[0].name == 'phone'
        assert tg.tiers[1].name == 'word'
        assert tg.tiers[0][0].mark == 'sil'
        assert abs(tg.tiers[0][0].minTime - 1358.8925) < 0.01
        assert abs(tg.tiers[0][0].maxTime - 1361.8925) < 0.01




if __name__ == '__main__':
    unittest.main()
