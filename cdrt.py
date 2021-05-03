from math import floor

BASE = 256

class Identifier:
    def __init__(self, digit, site):
        self.digit = digit
        self.site = site

class Char:
    def __init__(self, position, lamport, value):
        self.position = position # position is list [] of Identifier
        self.lamport = lamport
        self.value = value

def comparePosition(ids1, ids2):
    for i in range(0, min(len(ids1), len(ids2))):
        compare = compareIdentifier(ids1[i], ids2[i])
        if compare != 0:
            return compare
    if len(ids1) < len(ids2):
        return -1
    elif len(ids1) > len(ids2):
        return 1
    else:
        return 0

def compareIdentifier(id1, id2):
    if (id1.digit < id2.digit):
        return -1
    elif (id1.digit > id2.digit):
        return 1
    else:
        if (id1.site < id2.site):
            return -1
        elif (id1.site > id2.site):
            return 1
        else:
            return 0

def fromIdentifierList(ids):
    return [id.digit for id in ids]

def subtractGreaterThan(n1, n2):
    carry = 0
    diff = [None] * max(len(n1), len(n2))
    for i in range(len(diff) - 1, -1, -1):
        d1 = (n1[i] or 0) - carry
        d2 = (n2[i] or 0)
        if (d1 < d2):
            carry = 1
            diff[i] = d1 + BASE - d2
        else:
            carry = 0
            diff[i] = d1 - d2
    return diff

def add(n1, n2):
    carry = 0
    diff = [None] * max(len(n1), len(n2))
    for i in range(len(diff) - 1, -1, -1):
        sum = (n1[i] or 0) + (n2[i] or 0) + carry
        carry = floor(sum / BASE)
        diff[i] = (sum % BASE)
    if (carry != 0):
        print("ERROR. Sum too large.")
    return diff

def increment(n1, delta):
    firstNonzeroDigit = next(i for i,v in enumerate(delta) if v != 0)
    inc = delta[0:firstNonzeroDigit] + [0,1]
    v1 = add(n1, inc)
    v2 = add(v1, inc) if v1[len(v1) - 1] == 0 else v1
    return v2

def constructPosition(digit, index, before, after, creationSite, n):
    if (index == (len(n) - 1)):
        return Identifier(digit, creationSite)
    elif (index < len(before) and digit == before[index].digit):
        return Identifier(digit, before[index].site)
    elif (index < len(after) and digit == after[index].digit):
        return Identifier(digit, after[index].site)
    else
        return Identifier(digit, creationSite)

def toIdentifierList(n, before, after, creationSite):
    return [constructPosition(x, idx, before, after, creationSite, n) for idx, x in enumerate(n)]

# p1 and p2 are lists of identifier
def generatePositionBetween(p1, p2, site):
    head1 = p1[0] if len(p1) > 0 else Identifier(0, site)
    head2 = p2[0] if len(p2) > 0 else Identifier(0, site)
    if (head1.digit != head2.digit):
        n1 = fromIdentifierList(p1)
        n2 = fromIdentifierList(p2)
        delta = subtractGreaterThan(n2, n1)
        nxt = increment(n1, delta)
        return toIdentifierList(nxt, p1, p2, site)
    else:
        if (head1.site < head2.site):
            return generatePositionBetween(p1[1:], [], site).append(0, head1)
        elif (head1.site == head2.site):
            return generatePositionBetween(p1[1:], p2[1:], site).append(0, head1)
        else:
            print("ERROR, site ordering shouldn't be possible.")


