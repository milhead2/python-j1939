from __future__ import print_function

import j1939.utils

val = j1939.utils.request_pgn(0xfeda, src=0xff)
fieldCount = val[0]
print ("%d elements in list" % fieldCount)

res=""
for c in val[1:]:
    res += chr(c)

res2=res.split('*')
print (res2)

print("Destination Address:     %d (0x%x)" % (23, 23))
print("Number of ID items:      %d (0x%x)" % (fieldCount, fieldCount))
print("Model Number:            %s " % (res2[0]))
print("Vendor Part Number:      %s" % (res2[1]))
print("Hardware Serial Number:  %s" % (res2[2]))
print("VIN:                     %s" % (res2[3]))
print("Hardware Part Number:    %s" % (res2[4]))
print("ECU Part Number:         %s" % (res2[5]))
print("Program Version:         %s" % (res2[6]))
print("Software Version Number: %s" % (res2[7]))
print("Software Part Number:    %s" % (res2[8]))
print("Checksum:                0x%s" % (res2[9]))



