# -*- coding: utf-8 -*-

import pyedna
import pandas as pd

# With the exception of GetHistRaw, all data pull functions are called the
# same way, by supplying a tag, start time, end time, and period.

# The following code will pull snap data from ADE1CA01 over a 30-second interval:
import pyedna.ezdna as dna
tag = "MDSSCSC1.ANVCALC.ADE1CA01"           # format site.service.tag
start = "12/01/16 01:01:01"                 # format mm/dd/yy hh:mm:ss
end = "01/03/17 01:01:01"                   # format mm/dd/yy hh:mm:ss
period = "00:00:30"                         # format hh:mm:ss
df = dna.GetHistSnap(tag, start, end, period)

#Substitute 'GetHistSnap' for any of the other data pull functions, as required.

# Raw data may be obtained from ADE1CA01 using:
df = dna.GetHistRaw(tag, start, end)

# Multiple tags can be pulled at the same time using:

df = dna.GetMultipleTags(['MDSSCSC1.ANVCALC.ADE1CA02',
                          'MDSSCSC1.ANVCALC.ADE1CA03',
                          'MDSSCSC1.ANVCALC.ADE1CA04'],
                          '12/26/16 01:01:01',
                          '01/04/17 01:01:01',
                          sampling_rate=10,
                          fill_limit=600)

# Be careful, the data will be merged and filled only up until the selected
# fill_limit. After that point, the data will be empty, because it will be
# assumed that the data connection has dropped.
