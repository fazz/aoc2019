
from random import randrange
from copy import deepcopy

def getmem(memory, position):
    if position > len(memory)-1:
        memory.extend([0] * (1 + position - len(memory)))

    if position < 0:
        raise "Subzero address on read"

    return memory[position]

def setmem(memory, position, value):
    getmem(memory, position)

    if position < 0:
        raise "Subzero address on write"

    memory[position] = value
    return memory

def arraygen(input):
    while len(input) > 0:
        yield input.pop(0)

def arrayplusgen(input, othergen):
    while len(input) > 0:
        yield input.pop(0)
    while True:
        yield next(othergen)

# 0 - position mode
# 1 - immediate mode
# 2 - relative mode
def value(memory, position, mode, rel):
    if mode == 0:
        return getmem(memory, getmem(memory, position))
    if mode == 1:
        return memory[position]
    if mode == 2:
        return getmem(memory, getmem(memory, position) + rel)

def position(memory, position, mode, rel):
    if mode == 0:
        return getmem(memory, position)
    if mode == 1:
        raise "Unspecified?"
    if mode == 2:
        return getmem(memory, position) + rel

def execute(image, inputgenerator):
    memory = image.copy()
    pc = 0
    lastoutput = None
    rel = 0

    while memory[pc] != 99:
        opcode = memory[pc] % 100
        p1mode = (memory[pc] // 100 ) % 10
        p2mode = (memory[pc] // 1000 ) % 10
        p3mode = (memory[pc] // 10000 ) % 10

        if opcode == 1:
            pcinc = 4
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            resultpos = position(memory, pc+3, p3mode, rel)
            setmem(memory, resultpos, op1+op2)
            
        elif opcode == 2:
            pcinc = 4
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            resultpos = position(memory, pc+3, p3mode, rel)
            setmem(memory, resultpos, op1*op2)

        elif opcode == 3:
            pcinc = 2
            resultpos = position(memory, pc+1, p1mode, rel)
            try:
                ivalue = next(inputgenerator)
            except StopIteration:
                raise RuntimeError("Input not available")
            setmem(memory, resultpos, ivalue)
            if ivalue == -1:
                yield ('NOINP', -1)

        elif opcode == 4:
            pcinc = 2
            op1 = value(memory, pc+1, p1mode, rel)
            lastoutput = op1
            yield ('OUT', op1)

        elif opcode == 5:
            pcinc = 3
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            if op1 != 0:
                pc = op2
                pcinc = 0

        elif opcode == 6:
            pcinc = 3
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            if op1 == 0:
                pc = op2
                pcinc = 0

        elif opcode == 7:
            pcinc = 4
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            resultpos = position(memory, pc+3, p3mode, rel)
            setmem(memory, resultpos, 1 if op1 < op2 else 0)


        elif opcode == 8:
            pcinc = 4
            op1 = value(memory, pc+1, p1mode, rel)
            op2 = value(memory, pc+2, p2mode, rel)
            resultpos = position(memory, pc+3, p3mode, rel)
            setmem(memory, resultpos, 1 if op1 == op2 else 0)

        elif opcode == 9:
            pcinc = 2
            op1 = value(memory, pc+1, p1mode, rel)
            rel += op1

        else:
            raise "Unknown opcode"
        
        pc = pc+pcinc

    return (memory, lastoutput)


inputprogram='3,62,1001,62,11,10,109,2249,105,1,0,1503,1097,1666,767,2152,1740,1874,1270,703,1775,1606,1029,2043,1971,1169,1637,1470,2119,2181,600,1134,2080,1841,1303,1806,1379,1439,635,1410,1940,827,924,1206,1332,571,1544,860,2006,969,893,1573,1909,1237,796,1707,2218,672,1062,1000,736,0,0,0,0,0,0,0,0,0,0,0,0,3,64,1008,64,-1,62,1006,62,88,1006,61,170,1105,1,73,3,65,21001,64,0,1,20101,0,66,2,21101,0,105,0,1105,1,436,1201,1,-1,64,1007,64,0,62,1005,62,73,7,64,67,62,1006,62,73,1002,64,2,132,1,132,68,132,1001,0,0,62,1001,132,1,140,8,0,65,63,2,63,62,62,1005,62,73,1002,64,2,161,1,161,68,161,1101,1,0,0,1001,161,1,169,101,0,65,0,1101,0,1,61,1101,0,0,63,7,63,67,62,1006,62,203,1002,63,2,194,1,68,194,194,1006,0,73,1001,63,1,63,1106,0,178,21101,0,210,0,105,1,69,2102,1,1,70,1102,0,1,63,7,63,71,62,1006,62,250,1002,63,2,234,1,72,234,234,4,0,101,1,234,240,4,0,4,70,1001,63,1,63,1105,1,218,1105,1,73,109,4,21101,0,0,-3,21101,0,0,-2,20207,-2,67,-1,1206,-1,293,1202,-2,2,283,101,1,283,283,1,68,283,283,22001,0,-3,-3,21201,-2,1,-2,1105,1,263,21202,-3,1,-3,109,-4,2105,1,0,109,4,21102,1,1,-3,21101,0,0,-2,20207,-2,67,-1,1206,-1,342,1202,-2,2,332,101,1,332,332,1,68,332,332,22002,0,-3,-3,21201,-2,1,-2,1106,0,312,22101,0,-3,-3,109,-4,2106,0,0,109,1,101,1,68,359,20101,0,0,1,101,3,68,366,21001,0,0,2,21102,376,1,0,1106,0,436,21201,1,0,0,109,-1,2106,0,0,1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536,131072,262144,524288,1048576,2097152,4194304,8388608,16777216,33554432,67108864,134217728,268435456,536870912,1073741824,2147483648,4294967296,8589934592,17179869184,34359738368,68719476736,137438953472,274877906944,549755813888,1099511627776,2199023255552,4398046511104,8796093022208,17592186044416,35184372088832,70368744177664,140737488355328,281474976710656,562949953421312,1125899906842624,109,8,21202,-6,10,-5,22207,-7,-5,-5,1205,-5,521,21102,1,0,-4,21102,1,0,-3,21102,1,51,-2,21201,-2,-1,-2,1201,-2,385,470,21002,0,1,-1,21202,-3,2,-3,22207,-7,-1,-5,1205,-5,496,21201,-3,1,-3,22102,-1,-1,-5,22201,-7,-5,-7,22207,-3,-6,-5,1205,-5,515,22102,-1,-6,-5,22201,-3,-5,-3,22201,-1,-4,-4,1205,-2,461,1106,0,547,21101,0,-1,-4,21202,-6,-1,-6,21207,-7,0,-5,1205,-5,547,22201,-7,-6,-7,21201,-4,1,-4,1105,1,529,22101,0,-4,-7,109,-8,2106,0,0,109,1,101,1,68,564,20101,0,0,0,109,-1,2105,1,0,1101,0,37489,66,1102,1,1,67,1102,598,1,68,1102,1,556,69,1102,1,0,71,1102,600,1,72,1105,1,73,1,1734,1101,0,101681,66,1102,1,1,67,1102,1,627,68,1102,556,1,69,1102,3,1,71,1101,629,0,72,1106,0,73,1,5,14,9293,14,18586,2,53857,1102,72493,1,66,1102,1,4,67,1102,662,1,68,1101,0,302,69,1102,1,1,71,1101,670,0,72,1106,0,73,0,0,0,0,0,0,0,0,18,159519,1101,49597,0,66,1102,1,1,67,1101,699,0,68,1102,556,1,69,1101,1,0,71,1102,1,701,72,1106,0,73,1,23,47,93567,1102,1,42577,66,1101,2,0,67,1101,730,0,68,1102,1,302,69,1101,1,0,71,1101,0,734,72,1105,1,73,0,0,0,0,42,96982,1101,53593,0,66,1102,1,1,67,1101,763,0,68,1102,556,1,69,1101,1,0,71,1101,765,0,72,1106,0,73,1,179,21,151738,1102,52387,1,66,1102,1,1,67,1102,794,1,68,1101,556,0,69,1101,0,0,71,1102,1,796,72,1105,1,73,1,1467,1102,88079,1,66,1101,1,0,67,1102,1,823,68,1101,0,556,69,1102,1,1,71,1102,825,1,72,1106,0,73,1,-523,37,62313,1102,1,19457,66,1102,1,1,67,1102,1,854,68,1102,1,556,69,1101,2,0,71,1102,1,856,72,1105,1,73,1,2293,27,289972,24,25589,1101,0,54499,66,1101,0,1,67,1101,887,0,68,1102,1,556,69,1102,1,2,71,1102,1,889,72,1105,1,73,1,3,13,10306,27,217479,1101,91997,0,66,1101,1,0,67,1102,920,1,68,1102,556,1,69,1102,1,1,71,1102,922,1,72,1105,1,73,1,2632,12,41061,1102,1,90289,66,1102,1,1,67,1102,951,1,68,1102,556,1,69,1102,8,1,71,1102,953,1,72,1105,1,73,1,2,12,13687,11,103991,13,15459,27,72493,21,227607,21,379345,2,269285,2,323142,1101,0,52457,66,1101,1,0,67,1102,1,996,68,1102,556,1,69,1101,1,0,71,1101,0,998,72,1105,1,73,1,1153,6,228867,1101,0,25673,66,1101,1,0,67,1101,1027,0,68,1102,1,556,69,1101,0,0,71,1101,1029,0,72,1106,0,73,1,1333,1102,1,103991,66,1101,2,0,67,1102,1056,1,68,1101,302,0,69,1102,1,1,71,1101,0,1060,72,1106,0,73,0,0,0,0,13,5153,1102,1,31189,66,1102,3,1,67,1101,0,1089,68,1101,302,0,69,1102,1,1,71,1102,1095,1,72,1106,0,73,0,0,0,0,0,0,1,142322,1102,1,71161,66,1102,1,4,67,1101,0,1124,68,1101,253,0,69,1101,1,0,71,1101,1132,0,72,1105,1,73,0,0,0,0,0,0,0,0,11,207982,1101,0,70979,66,1102,1,3,67,1102,1161,1,68,1102,302,1,69,1101,1,0,71,1102,1167,1,72,1105,1,73,0,0,0,0,0,0,18,53173,1101,9293,0,66,1101,0,4,67,1101,1196,0,68,1101,302,0,69,1101,1,0,71,1102,1204,1,72,1105,1,73,0,0,0,0,0,0,0,0,2,161571,1102,53051,1,66,1102,1,1,67,1102,1,1233,68,1101,0,556,69,1102,1,1,71,1101,1235,0,72,1106,0,73,1,85909,47,62378,1102,1,48491,66,1101,0,2,67,1101,0,1264,68,1102,302,1,69,1102,1,1,71,1101,0,1268,72,1105,1,73,0,0,0,0,16,9661,1102,1,65371,66,1102,2,1,67,1102,1297,1,68,1101,0,302,69,1101,1,0,71,1101,0,1301,72,1105,1,73,0,0,0,0,18,212692,1101,0,33073,66,1102,1,1,67,1101,1330,0,68,1102,1,556,69,1102,1,0,71,1102,1,1332,72,1106,0,73,1,1175,1101,72497,0,66,1101,0,1,67,1101,0,1359,68,1101,556,0,69,1102,9,1,71,1101,0,1361,72,1106,0,73,1,1,47,31189,37,83084,6,76289,12,54748,40,78889,8,85154,42,48491,16,19322,24,76767,1101,20399,0,66,1102,1,1,67,1101,0,1406,68,1101,0,556,69,1102,1,1,71,1101,0,1408,72,1105,1,73,1,160,2,107714,1102,1,13763,66,1102,1,1,67,1101,0,1437,68,1102,1,556,69,1101,0,0,71,1102,1,1439,72,1106,0,73,1,1734,1101,24179,0,66,1102,1,1,67,1102,1,1466,68,1101,0,556,69,1101,0,1,71,1101,0,1468,72,1106,0,73,1,-683,6,152578,1101,0,9661,66,1101,2,0,67,1101,1497,0,68,1101,302,0,69,1102,1,1,71,1102,1,1501,72,1105,1,73,0,0,0,0,21,303476,1102,1,32887,66,1102,1,1,67,1102,1530,1,68,1101,556,0,69,1101,0,6,71,1101,0,1532,72,1106,0,73,1,21834,7,130742,20,70979,20,212937,5,36877,5,73754,5,110631,1101,93967,0,66,1102,1,1,67,1102,1571,1,68,1102,1,556,69,1101,0,0,71,1101,1573,0,72,1105,1,73,1,1995,1102,1,78889,66,1102,1,2,67,1101,0,1600,68,1101,0,302,69,1102,1,1,71,1102,1604,1,72,1106,0,73,0,0,0,0,8,42577,1101,0,62869,66,1101,0,1,67,1102,1633,1,68,1102,1,556,69,1101,0,1,71,1102,1635,1,72,1105,1,73,1,125,14,37172,1102,29671,1,66,1102,1,1,67,1101,0,1664,68,1101,556,0,69,1101,0,0,71,1102,1666,1,72,1106,0,73,1,1425,1102,53857,1,66,1102,1,6,67,1101,1693,0,68,1101,302,0,69,1101,1,0,71,1101,0,1705,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,0,0,22,128966,1101,104651,0,66,1101,1,0,67,1102,1734,1,68,1102,556,1,69,1102,1,2,71,1101,0,1736,72,1106,0,73,1,10,14,27879,2,215428,1102,36877,1,66,1102,1,3,67,1102,1767,1,68,1101,302,0,69,1102,1,1,71,1101,0,1773,72,1105,1,73,0,0,0,0,0,0,18,106346,1101,0,42491,66,1102,1,1,67,1102,1,1802,68,1101,0,556,69,1101,0,1,71,1101,0,1804,72,1105,1,73,1,17,21,75869,1102,1,25589,66,1102,1,3,67,1101,1833,0,68,1101,302,0,69,1101,1,0,71,1101,1839,0,72,1106,0,73,0,0,0,0,0,0,20,141958,1102,64483,1,66,1101,2,0,67,1101,1868,0,68,1102,1,351,69,1101,0,1,71,1102,1872,1,72,1105,1,73,0,0,0,0,255,32887,1101,76289,0,66,1102,1,3,67,1102,1901,1,68,1102,1,302,69,1102,1,1,71,1102,1907,1,72,1106,0,73,0,0,0,0,0,0,1,213483,1102,1,63773,66,1102,1,1,67,1101,1936,0,68,1102,1,556,69,1101,0,1,71,1101,1938,0,72,1105,1,73,1,104161,40,157778,1101,0,10657,66,1101,1,0,67,1102,1,1967,68,1102,1,556,69,1102,1,1,71,1102,1969,1,72,1106,0,73,1,-18,24,51178,1102,5153,1,66,1101,3,0,67,1102,1998,1,68,1102,302,1,69,1102,1,1,71,1102,2004,1,72,1105,1,73,0,0,0,0,0,0,27,144986,1102,1,20771,66,1101,4,0,67,1101,0,2033,68,1101,0,302,69,1101,0,1,71,1102,1,2041,72,1106,0,73,0,0,0,0,0,0,0,0,1,71161,1102,13687,1,66,1101,4,0,67,1101,0,2070,68,1102,1,302,69,1102,1,1,71,1102,2078,1,72,1105,1,73,0,0,0,0,0,0,0,0,1,284644,1101,0,75869,66,1101,5,0,67,1102,2107,1,68,1101,302,0,69,1101,1,0,71,1102,1,2117,72,1106,0,73,0,0,0,0,0,0,0,0,0,0,7,65371,1101,0,24697,66,1101,1,0,67,1102,2146,1,68,1102,1,556,69,1101,0,2,71,1102,1,2148,72,1106,0,73,1,37,37,20771,37,41542,1101,58393,0,66,1102,1,1,67,1101,2179,0,68,1101,0,556,69,1102,0,1,71,1102,1,2181,72,1106,0,73,1,1476,1101,53173,0,66,1101,4,0,67,1102,1,2208,68,1102,253,1,69,1102,1,1,71,1102,2216,1,72,1106,0,73,0,0,0,0,0,0,0,0,22,64483,1102,1,91463,66,1102,1,1,67,1102,1,2245,68,1102,1,556,69,1102,1,1,71,1101,0,2247,72,1106,0,73,1,1663,12,27374'

origmemory = [int(x) for x in inputprogram.split(',')]

count = 50

machines = []


def arraygennb(input):
    while True:
        if len(input) > 0:
            yield input.pop(0)
        else:
            yield -1

for i in range(count):
    inp = [i]
    g = execute(origmemory, arraygennb(inp))
    machines.append((g, inp))

active = 0
result = -1
while True:
    print("Active:", active)
    (k, a) = next(machines[active][0])
    if k == 'OUT':
        (k, x) = next(machines[active][0])
        (k, y) = next(machines[active][0])

        if a == 255:
            result = y
            break
        d = machines[a][1]
        d.append(x)
        d.append(y)
    active = (active + 1) % count

print("Result 1", result)