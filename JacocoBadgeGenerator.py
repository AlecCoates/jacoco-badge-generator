#!/usr/bin/env python3
#
# jacoco-badge-generator: Github action for generating a jacoco coverage
# percentage badge.
# 
# Copyright (c) 2020-2021 Vincent A Cicirello
# https://www.cicirello.org/
#
# MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

import csv
import sys
import math
import pathlib
import os

badgeTemplate = '<svg xmlns="http://www.w3.org/2000/svg" width="104" \
height="20" role="img" aria-label="coverage: {0}">\
<linearGradient id="s" x2="0" y2="100%">\
<stop offset="0" stop-color="#bbb" stop-opacity=".1"/>\
<stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r">\
<rect width="104" height="20" rx="3" fill="#fff"/></clipPath>\
<g clip-path="url(#r)"><rect width="61" height="20" fill="#555"/>\
<rect x="61" width="43" height="20" fill="{1}"/>\
<rect width="104" height="20" fill="url(#s)"/></g>\
<g fill="#fff" text-anchor="middle" \
font-family="Verdana,Geneva,DejaVu Sans,sans-serif" \
text-rendering="geometricPrecision" font-size="110">\
<text aria-hidden="true" x="315" y="150" fill="#010101" \
fill-opacity=".3" transform="scale(.1)" textLength="510">{3}</text>\
<text x="315" y="140" transform="scale(.1)" fill="#fff" \
textLength="510">{3}</text>\
<text aria-hidden="true" x="815" y="150" \
fill="#010101" fill-opacity=".3" transform="scale(.1)" \
textLength="{2}">{0}</text><text x="815" y="140" \
transform="scale(.1)" fill="#fff" textLength="{2}">{0}</text>\
</g></svg>'

colors = [ "#4c1", "#97ca00", "#a4a61d", "#dfb317", "#fe7d37", "#e05d44" ]

def generateBadge(covStr, color, badgeType="coverage") :
    """Generates the badge as a string.

    Keyword arguments:
    covStr - The coverage as a string.
    color - The color for the badge.
    badgeType - The text string for a label on the badge.
    """
    if len(covStr) >= 4 :
        textLength = "330"
    elif len(covStr) >= 3 :
        textLength = "250" 
    else :
        textLength = "170"
    return badgeTemplate.format(covStr, color, textLength, badgeType)

def computeCoverage(filename) :
    """Parses a jacoco.csv file and computes code coverage
    percentages. Returns: coverage, branchCoverage.  The coverage
    is instruction coverage.

    Keyword arguments:
    filename - The name, including path, of the jacoco.csv
    """
    missed_tested = 0
    missed_untested = 0
    covered_tested = 0
    covered_untested = 0
    missedBranches_tested = 0
    missedBranches_untested = 0
    coveredBranches_tested = 0
    coveredBranches_untested = 0
    missedLines_tested = 0
    missedLines_untested = 0
    coveredLines_tested = 0
    coveredLines_untested = 0
    with open(filename, newline='') as csvfile :
        jacocoReader = csv.reader(csvfile)
        for i, row in enumerate(jacocoReader) :
            if i > 0 :
                if int(row[4]) > 0:
                    missed_tested += int(row[3])
                else:
                    missed_untested += int(row[3])
                if int(row[4]) > 0:
                    covered_tested += int(row[4])
                else:
                    covered_untested += int(row[4])
                if int(row[6]) > 0:
                    missedBranches_tested += int(row[5])
                else:
                    missedBranches_untested += int(row[5])
                if int(row[6]) > 0:
                    coveredBranches_tested += int(row[6])
                else:
                    coveredBranches_untested += int(row[6])
                if int(row[8]) > 0:
                    missedLines_tested += int(row[7])
                else:
                    missedLines_untested += int(row[7])
                if int(row[8]) > 0:
                    coveredLines_tested += int(row[8])
                else:
                    coveredLines_untested += int(row[8])
    return (covered_tested + covered_untested) / ((covered_tested + covered_untested) + (missed_tested + missed_untested)), \
           (coveredBranches_tested + coveredBranches_untested) / ((coveredBranches_tested + coveredBranches_untested) + (missedBranches_tested + missedBranches_untested)), \
           (coveredLines_tested + coveredLines_untested) / ((coveredLines_tested + coveredLines_untested) + (missedLines_tested + missedLines_untested)), \
           covered_tested / (covered_tested + missed_tested), \
           coveredBranches_tested / (coveredBranches_tested + missedBranches_tested), \
           coveredLines_tested / (coveredLines_tested + missedLines_tested)

def badgeCoverageStringColorPair(coverage) :
    """Converts the coverage percentage to a formatted string,
    and determines the badge color.
    Returns: coveragePercentageAsString, colorAsString

    Keyword arguments:
    coverage - The coverage percentage.
    """
    # Truncate the 2nd decimal place, rather than rounding
    # to avoid considering a non-passing percentage as
    # passing (e.g., if user considers 70% as passing threshold,
    # then 69.99999...% is technically not passing).
    coverage = int(1000 * coverage) / 10
    c = math.ceil((100 - coverage) / 10)
    if c >= len(colors) :
        c = len(colors) - 1
    if coverage - int(coverage) == 0 :
        cov = "{0:d}%".format(int(coverage))
    else :
        cov = "{0:.1f}%".format(coverage)
    return cov, colors[c]

def createOutputDirectories(jacocoBadgeFile) :
    """Creates the output directory if it doesn't already exist.

    Keyword arguments:
    jacocoBadgeFile - The path, including filename, to the output badge file.
    """
    if not os.path.exists(jacocoBadgeFile) :
        p = pathlib.Path(os.path.dirname(jacocoBadgeFile))
        p.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__" :
    jacocoCsvFile = sys.argv[1]
    jacocoBadgeFile = sys.argv[2]

    cov, branches, lines, cov_tested, branches_tested, lines_tested = computeCoverage(jacocoCsvFile)
    
    covStr, covColor = badgeCoverageStringColorPair(cov)
    createOutputDirectories(jacocoBadgeFile + "jacoco.svg")
    with open(jacocoBadgeFile + "jacoco.svg", "w") as badge :
        badge.write(generateBadge(covStr, covColor))
        
    branchesStr, branchesColor = badgeCoverageStringColorPair(branches)
    createOutputDirectories(jacocoBadgeFile + "jacocoBranches.svg")
    with open(jacocoBadgeFile + "jacocoBranches.svg", "w") as badge :
        badge.write(generateBadge(branchesStr, branchesColor))
        
    linesStr, linesColor = badgeCoverageStringColorPair(lines)
    createOutputDirectories(jacocoBadgeFile + "jacocoLines.svg")
    with open(jacocoBadgeFile + "jacocoLines.svg", "w") as badge :
        badge.write(generateBadge(linesStr, linesColor))
        
    cov_testedStr, cov_testedColor = badgeCoverageStringColorPair(cov_tested)
    createOutputDirectories(jacocoBadgeFile + "jacocoTested.svg")
    with open(jacocoBadgeFile + "jacocoTested.svg", "w") as badge :
        badge.write(generateBadge(cov_testedStr, cov_testedColor))
        
    branches_testedStr, branches_testedColor = badgeCoverageStringColorPair(branches_tested)
    createOutputDirectories(jacocoBadgeFile + "jacocoBranchesTested.svg")
    with open(jacocoBadgeFile + "jacocoBranchesTested.svg", "w") as badge :
        badge.write(generateBadge(branches_testedStr, branches_testedColor))
        
    lines_testedStr, lines_testedColor = badgeCoverageStringColorPair(lines_tested)
    createOutputDirectories(jacocoBadgeFile + "jacocoLinesTested.svg")
    with open(jacocoBadgeFile + "jacocoLinesTested.svg", "w") as badge :
        badge.write(generateBadge(lines_testedStr, lines_testedColor))

    print("::set-output name=coverage::" + str(cov))
    print("::set-output name=branches::" + str(branches))
    print("::set-output name=lines::" + str(lines))
    print("::set-output name=coverage_tested::" + str(cov_tested))
    print("::set-output name=branches_tested::" + str(branches_tested))
    print("::set-output name=lines_tested::" + str(lines_tested))
    
    
