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

if __name__ == '__main__':
    import sys
    import os
    base = os.path.dirname(os.path.realpath(__file__))
    print(base)
    sys.path.append(base)
    import textgrid
    from os import remove

    ## print
    print('TEST: if this works, you will see "True" twice below...')

    ## MLF
    # write MLF file
    open('baz.mlf', 'w').write("""#!MFL!#
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
""")
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
    print(repr(foo) == repr(foo_copy))

    ## IntervalTier
    phones = foo[0]
    # write it out
    phones.write('phones.IntervalTier')
    # read it back in
    phones_copy = textgrid.IntervalTier.fromFile('phones.IntervalTier', 'phones')
    print(repr(phones) == repr(phones_copy))

    ## clean up the mess we've made
    remove('baz.mlf')
    remove('foo.TextGrid')
    remove('foo_copy.TextGrid')
    remove('bar.TextGrid')
    remove('phones.IntervalTier')

    ## check multiline text field handling
    class FakeFile(object):
        def __init__(self, string):
            self.lines = string.splitlines(True)
            # this preserves final newline char
        def readline(self):
            return self.lines.pop(0)

    print('TEST: if this works, you will see a three-line sentence below...')
    some_text = """            text = "This is an annoying, but
not technically ill-formed
line."
This latter line shouldn't be pulled in at all.
"""
    ff = FakeFile(some_text)
    print(textgrid.TextGrid._getMark(ff))
