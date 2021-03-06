#!/usr/bin/env python
# ----------------------------------------------------------------------
#
# Brad T. Aagaard, U.S. Geological Survey
#
# ----------------------------------------------------------------------
#
# Tabulate performance of preconditioners.
#
# Uses subdirectory 'logs_pctest' with iteration counts in .log files.

import os
import sys
import numpy
import re


style = "latex"
if len(sys.argv) > 2:
    raise ValueError("usage: table_pctest.py [text | latex (default)]")
if len(sys.argv) == 2:
    style = sys.argv[1]

if not style in ["text", 
               "latex", 
               ]:
    raise ValueError("Unknown format (%s) requested." % style)


preconditioners = [('asm', 'ASM'),
                   ('schur_full', 'Schur (full)'),
                   ('schur_upper', 'Schur (upper)'),
                   ('fieldsplit_add', 'FieldSplit (add)'),
                   ('fieldsplit_mult', 'FieldSplit (mult)'),
                   ('fieldsplit_mult_custom', 'FieldSplit (mult,custom)'),
                   ]
cells = ['Tet4',
         'Hex8']
problems = [('np001','S1'),
            ('np002','S2'),
            ('np004','S4'),
            ]
            

# Allocate storage for stats
niters = {}
for pc in preconditioners:
    niters[pc[0]] = {}
    for c in cells:
        niters[pc[0]][c] = numpy.zeros(len(problems), dtype=numpy.int32)

# Get stats
for pc in preconditioners:
    for c in cells:
        ip = 0
        for p in problems:
            filename = "logs_pctest/%s_%s_%s.log" % (c.lower(), pc[0], p[0])
            with open(filename, "r") as fin:
                for line in fin:
                    refields = re.search("Linear solve converged due to \w+ iterations ([0-9]+)", line)
                    if refields:
                        niters[pc[0]][c][ip] = refields.group(1)
                        break
            ip += 1

if style == "text":
    print "PC"+" "*24 + "Cell"+" "*2 + " "*6+"Iterates"
    print "  "+" "*24 + "    "+" "*2 + "   S1    S2    S4"
    for pc in preconditioners:
        line = "%-26s" % pc[1]
        for c in cells:
            if line is None:
                line = " "*26
            line += "%-6s" % c
            ip = 0
            for p in problems:
                line += "%6d" % niters[pc[0]][c][ip]
                ip += 1
            print line
            line = None

else:
    print "\\begin{tabular}{lcrrr}"
    print "  Preconditioner & Cell & \multicolumn{3}{c}{Problem Size} \\\\"
    print "     &      & S1 & S2 & S4 \\\\"
    print "  \hline"
    for pc in preconditioners:
        print "  %s" % pc[1]
        for c in cells:
            line = "    & " + c
            ip = 0
            for p in problems:
                line += " & %d" % niters[pc[0]][c][ip]
                ip += 1
            print line + " \\\\"
            line = None
    print "  \hline"
    print "\\end{tabular}"


