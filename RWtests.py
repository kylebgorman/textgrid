#!/usr/bin/env python
#
# RWtests.py
# 
# Max Bane <bane@uchicago.edu>
# Kyle Gorman <kgorman@ling.upenn.edu>
# Morgan Sonderegger <morgan@cs.uchicago.edu>
#
# tests for the read-write functions in textgrid.py (they don't make much 
# sense as doctests). not particularly useful for users...

if __name__ == '__main__':
    import textgrid
    from os import remove
    
    ## print
    print 'if this works, you should see "True" twice below...'

    ## MLF
    # write MLF file
    open('baz.mlf', 'w').write("""#!MFL!#
"foo.lab"
0 7000000 SH SHOW
7000000 11000000 OW
11000000 17000000 M ME
17000000 19000000 IY
19000000 22000000 DH THE
22000000 29000000 AH
29000000 35000000 W ONE
35000000 40000000 AH
40000000 45000000 N
45000000 52000000 W WAY
52000000 57000000 EY
57000000 63000000 F FLIGHTS
63000000 67000000 L
67000000 69000000 AY
69000000 75000000 T
75000000 80000000 S
80000000 87000000 F FROM
87000000 93000000 R
93000000 95000000 AH
95000000 102000000 M
102000000 105000000 D DETROIT
105000000 108000000 IH
108000000 113000000 T
113000000 120000000 R
120000000 124000000 OY
124000000 131000000 T
131000000 133000000 T TO
133000000 135000000 UW
135000000 142000000 W WESTCHESTER
142000000 148000000 EH
148000000 152000000 S
152000000 156000000 T
156000000 161000000 CH
161000000 164000000 EH
164000000 170000000 S
170000000 172000000 T
172000000 177000000 ER
177000000 184000000 K COUNTY
184000000 186000000 AW
186000000 190000000 N
190000000 194000000 T
194000000 201000000 IY
.
"bar.lab"
0 7000000 F FIND
7000000 13000000 AY 13000000 16000000 N 16000000 18000000 D
18000000 24000000 IY ME
24000000 30000000 AH A
30000000 33000000 F FLIGHT
33000000 40000000 L
40000000 47000000 AY
47000000 50000000 T
50000000 52000000 DH THAT
52000000 54000000 AE
54000000 56000000 T
56000000 62000000 F FLIES
62000000 69000000 L
69000000 74000000 AY
74000000 77000000 Z
77000000 81000000 R FROM
81000000 88000000 AH
88000000 95000000 M
95000000 98000000 M MEMPHIS
98000000 100000000 EH
100000000 107000000 M
107000000 109000000 F
109000000 113000000 AH
113000000 118000000 S
118000000 121000000 UW TO
121000000 126000000 T TACOMA
126000000 132000000 AH
132000000 134000000 K
134000000 140000000 OW
140000000 142000000 M
142000000 146000000 AH
.
""")
    # read it in, writing over mlf
    mlf = textgrid.MLF('baz.mlf')
    # write them to foo.TextGrid and bar.TextGrid
    mlf.write()

    ## TextGrid
    # read foo.TextGrid
    foo = textgrid.TextGridFromFile('foo.TextGrid')
    # write it out
    foo.write('foo_copy.TextGrid')
    # read it back in
    foo_copy = textgrid.TextGridFromFile('foo_copy.TextGrid')
    print repr(foo) == repr(foo_copy)
    
    ## IntervalTier
    phones = foo[0]
    # write it out
    phones.write('phones.IntervalTier')
    # read it back in
    phones_copy = textgrid.IntervalTierFromFile('phones.IntervalTier', 'phones')
    print repr(phones) == repr(phones_copy)

    ## clean up the mess we've made
    remove('baz.mlf')
    remove('foo.TextGrid')
    remove('foo_copy.TextGrid')
    remove('bar.TextGrid')
    remove('phones.IntervalTier')
