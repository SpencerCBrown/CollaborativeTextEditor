from change import *
from char import generatePositionBetween
from char import comparePosition

emptyChar = Char([], 0, 0)

class CRDT:
    def __init__(self):
        self.lines = []
    
    def toString(self):
        pass

    def remoteInsert(self, char):
        pass

    def remoteDelete(self, char):
        pass

    def localInsert(self, lamport, site, change):
        # get char from change, and editor position.
        # use editor position to find the enclosing crdt positions
        # use generatePositionBetween to generate the new position for the change
        # Insert into crdt structure
        # return remotechange with position data
        # Note: change.line is 1-indexed, so subtract 1 to convert to 0-indexed list
        line = self.getLine(change.line - 1)
        l1 = line[:change.column]
        l2 = line[change.column:]

        precedingChar = self.getPrecedingChar(change)
        charAt = self.getCharAt(change)

        # if a non-newline character was inserted, insert these substrings together
        # if a newline was inserted, then add both back into the lines list separately
        # either way, the inserted character goes at the end of l1
        if (len(l1) > 0) and (len(l2) > 0):
            # both sublists have at least one "character" remember these are Char objs
            newPosition = generatePositionBetween(l1[-1].position, l2[0].position, site) # .position field holds identifier list
        elif (len(l1) > 0) and (len(l2) == 0):
            # we are appending to the end of the line
            # I think this also means we are on the last line, as otherwise there would be a newline in l2
            # pass empty list to 
            newPosition = generatePositionBetween(l1[-1].position, charAt.position, site)
        elif (len(l1) == 0) and (len(l2) > 0):
            # we are prepending to the start of a line
            newPosition = generatePositionBetween(precedingChar.position, l2[0].position, site)
            a = 5
        else: # both are empty
            newPosition = generatePositionBetween(precedingChar.position, charAt.position, site)
        
        insertedChar = Char(newPosition, lamport, change.added)
        l1.append(insertedChar)
        if (change.added == "\n"):
            self.lines = self.lines[:change.line - 1] + [l1] + [l2] + self.lines[change.line:]
        else:
            self.lines = self.lines[:change.line - 1] + [(l1 + l2)] + self.lines[change.line:]
        
        #print(self.lines)
        print(str([str(e.digit) for e in insertedChar.position]) + " " + insertedChar.value)
        return insertedChar

    def localDelete(self, change):
        pass

    def getLine(self, lineidx):
        if len(self.lines) > lineidx and lineidx >= 0:
            return self.lines[lineidx]
        else:
            return []

    def getPrecedingChar(self, change):
        if (change.column == 0):
            if (change.line == 1):
                return emptyChar
            else:
                return self.getLine(change.line - 2)[-1]
        else:
            return self.getLine(change.line - 1)[change.column - 1]

    def getCharAt(self, change):
        line = self.getLine(change.line - 1)
        if (change.column >= len(line)):
            if (change.line < len(self.lines)): #if there is a line after
                return self.getLine(change.line)[0]
            else:
                return emptyChar
        else:
            return line[change.column]


def updateLocalToRemote(crdt, lamport, site, change):
    if (change.added != ""): # insert
        insertedChar = crdt.localInsert(lamport, site, change)
        return insertedChar
    elif (change.added != ""): #delete
        pass
    else:
        print("ERROR: change has neither insert nor delete")
