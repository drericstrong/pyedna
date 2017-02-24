# -*- coding: utf-8 -*-

import pandas as pd
import pyedna.ezdna as dna

# The following code will pull snap data from TESTPNT1 over a 30-second interval:

tag = "TESTSITE.TESTSERVICE.TESTPNT1"      # format site.service.tag
start = "12/01/16 01:01:01"                 # format mm/dd/yy hh:mm:ss
end = "01/03/17 01:01:01"                   # format mm/dd/yy hh:mm:ss
period = "00:00:30"                         # format hh:mm:ss
df = dna.GetHist(tag, start, end, period=period, mode="snap")

# Raw data may be obtained from TESTPNT1 using:

df2 = dna.GetHist(tag, start, end)

# Other supported pull types include Average, Interpolated, Max, and Min. Please
# refer to eDNA documentation for more description about these pull types.

# Multiple tags can be pulled (in Raw mode) at the same time using:

tags = ["TESTSITE.TESTSERVICE.TESTPNT1", "TESTSITE.TESTSERVICE.TESTPNT2",
        "TESTSITE.TESTSERVICE.TESTPNT3", "TESTSITE.TESTSERVICE.TESTPNT4"]
df3 = dna.GetMultipleTags(tags, start, end)

# A list of connected services may be obtained using GetServices:

services = dna.GetServices()

# A list of point information for a given service can be found using GetPoints:

points = dna.GetPoints("TESTSITE.TESTSERVICE")