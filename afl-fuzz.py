#!/usr/bin/env python

"""A tiny attempt at building a fuzzer that uses American Fuzzy Lop's
instrumentation, but in Python. Currently it doesn't do much."""

import sys
from StringIO import StringIO
import random
import os
import string
from shm_instrumentation import SHMInstrumentation, MAP_SIZE


class AFLFuzz(object):

    def __init__(self, target):
        self.target = target
        self.devnull = open(os.path.devnull)
        self.instr = SHMInstrumentation()

    def case_score(self, case):
        # print("Trying %s" % repr(case))
        n = self.instr.go(self.target, self.devnull, StringIO(case),
                          stderr=self.devnull, timeout=0.1)
        return MAP_SIZE - n.count('\x00')

    def gen_random_case(self):
        return ''.join(chr(random.randint(0, 255)) for i in range(10))

    def run(self):
        cases = {str(self.gen_random_case()): None for i in range(10)}
        max_score = 0
        while True:
            for case in cases:
                cases[case] = self.case_score(case)
            cases_sorted = sorted(cases.items(), key=lambda x: x[1])

            if cases_sorted[-1][1] > max_score:
                max_score = cases_sorted[-1][1]
                print("New max score: %d" % max_score)

            # print("max=%d,%s" % (cases_sorted[-1][1],
            #                      repr(cases_sorted[-1][0])))

            # Replace worst cases with new ones
            del cases_sorted[0]
            del cases_sorted[0]
            cases_sorted = [(self.gen_random_case(), None)] + cases_sorted
            cases_sorted = [(self.gen_random_case(), None)] + cases_sorted

            # Randomly mutate the best case
            s = bytearray(cases_sorted[-1][0])
            i = random.randint(0, 9)
            s[i] = chr(random.randint(0, 255))
            cases_sorted[-1] = (str(s), None)
            cases = dict(cases_sorted)

if __name__ == '__main__':
    AFLFuzz(sys.argv[1:]).run()
