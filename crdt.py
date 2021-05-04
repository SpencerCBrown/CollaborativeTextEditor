from change import *
from char import generatePositionBetween
from char import comparePosition

emptyChar = Char([], 0, 0)

class CRDT:
    def __init__(self):
        self.lines = []
    
    def toString(self):
        string = ""
        for line in self.lines:
            for char in line:
                # concat each char.value
                string = string + char.value
        return string

    def findPosition(self, char):
        if len(self.lines) == 0:
            return (1,0,False) # location should be first line, first column. Existing character not found here.
        for i,l in enumerate(self.lines):
            if isInLine(l, char):
                # search for the position within line
                if comparePosition(l[0].position, char.position) == 0:
                    # it *is* first char of line
                    return (i + 1, 0, True)
                elif comparePosition(l[-1].position, char.position) == 0:
                    # it *is* last char of line
                    return (i + 1, len(l) - 1, True)
                else:
                    # it's somewhere in between
                    # len(l) >= 3 at this point
                    for cidx,c in enumerate(l):
                        # we're guaranteed to find the slot before we hit the end (we checked the endpoint)
                        between = isBetween(c, l[cidx+1], char)
                        if between:
                            # check if it's one of the endpoints first:
                            if char == c:
                                return (l + 1, cidx, True)
                            elif char == l[cidx+1]:
                                return (l + 1, cidx + 1, True)
                            # insert before l[i+1]
                            return (l + 1, cidx + 1, False)
            else:
                # Since we're doing linear search, if it's not in this line it implies it follows this line.

                # if not in line, check if less than first char of next line. If so, prepend to that line.
                # if this is last line, append to this line.
                # Unless there's a newline here. In that case, make a new line and prepend/append there.
                nextLine = self.getLine(i + 1)
                if nextLine != []:
                    # there is a next line
                    # is it empty ? If it is, it's the last line, otherwise it would have a newline.
                    if len(nextLine) == 0:
                        # Since there is a next line, that means there's a newline at the end of this line.
                        # So we need to prepend char to next line.
                        return (i + 1 + 1, 0, False)
                    elif comparePosition(char.position, nextLine[0].position) == -1:
                        # less than first char of nextLine
                        # so prepend to nextLine
                        return (i + 1, 0, False)
                    else:
                        # if it isn't before the first char of nextLine, we'll let the next iteration handle it.
                        continue
                else:
                    # this is apparently the last line
                    # so append to this line, or if there is a newline in this line, create a nextLine and put there
                    if l[-1].value == "\n":
                        # create new line, insert char, then append line
                        pass
                    else:
                        return (i + 1, len(l), False)

    def remoteInsert(self, char):
        (lineidx, charidx, found) = self.findPosition(char)
        if (not found):
            # have to be careful here. indices could not exist.
            # lineidx is one indexed, becuase TKinter is.
            # I'm starting to hate the fact that I didn't convert to 0-indexing at the boundary between GUI and abstract
            # editor data structure. Too late now...
            if (lineidx - 1) < len(self.lines): 
                # line exists
                line = self.lines[lineidx - 1]
                # shift all characters starting at charidx over to the right 1
                # this works if line is empty too
                before = line[:charidx]
                after = line[charidx:]
                before = before + char

                # replace line(s) in lines list
                # TODO: might need to circle back here. The [after] makes me nervous. What if it's empty?
                # TODO:     will there be an extraneous empty line screwing up things?
                # TODO:     or is this handled correctly? There can be empty lines if they are empty and last?
                if (char.value == "\n"):
                    self.lines = self.lines[:lineidx - 1] + [before] + [after] + self.lines[lineidx:]
                else:
                    self.lines = self.lines[:lineidx - 1] + [(before + after)] + self.lines[lineidx:]

            else:
                newline = [char]
                self.lines.append(newline)
        else:
            # had to have gotten a duplicate message somehow. Log and discard.
            print("Remote Change request inserts character already in local CRDT. Duplicate message?")

    def remoteDelete(self, char):
        (lineidx, charidx, found) = self.findPosition(char)
        if (found):
            # this is simpler than remoteInsert, because we know for a fact that the line and column exist
            line = self.lines[lineidx - 1]
            before = line[:charidx]
            after = line[charidx+1:]
            if (char.value == "\n"):
                self.lines = self.lines[:lineidx - 1] + [before + self.getLine(lineidx)] + self.lines[lineidx + 1:]
            else:
                self.lines = self.lines[:lineidx - 1] + [(before + after)] + self.lines[lineidx]
        else:
            # had to have gotten a duplicate message somehow. Log and discard.
            print("Remote Change request deletes character nonexistent in local CRDT. Duplicate message?")

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
        #print(str([str(e.digit) for e in insertedChar.position]) + " " + insertedChar.value)
        return insertedChar

    def localDelete(self, change):
        line = self.getLine(change.line - 1)
        l1 = line[:change.column]
        l2 = line[change.column+1:]
        deletedChar = line[change.column]

        if (change.removed == "\n"):
            nextline = self.getLine(change.line) # following line
            self.lines = self.lines[:change.line - 1] + [(l1 + l2 + nextline)] + self.lines[change.line + 1:]
        else:
            self.lines = self.lines[:change.line - 1] + [(l1 + l2)] + self.lines[change.line:]
        
        #print(str([str(e.digit) for e in deletedChar.position]) + " " + deletedChar.value)
        return deletedChar

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
            if (change.line < len(self.lines)): #if there is a line following
                return self.getLine(change.line)[0]
            else:
                return emptyChar
        else:
            return line[change.column]


def updateLocalToRemote(crdt, lamport, site, change):
    if (change.added != ""): # insert
        insertedChar = crdt.localInsert(lamport, site, change)
        change = RemoteChange("add", insertedChar)
        return change
    elif (change.removed != ""): #delete
        removedChar = crdt.localDelete(change)
        change = RemoteChange("remove", removedChar)
        return change
    else:
        print("ERROR: change has neither insert nor delete")

def updateRemoteToLocal(crdt, change):
    char = change.char
    if change.command == "add":
        crdt.remoteInsert(char)
        return crdt.toString()
    elif change.command == "remove":
        crdt.remoteDelete(char)
        return crdt.toString()
    else:
        print("ERROR: attempted to apply remote change with invalid command type. Must be \"add\" or \"remove\"")

def isBetween(c1, c2, target):
    if comparePosition(c1.position, target.position) == 0:
        # left endpoint
        return True
    elif comparePosition(c2.position, target.position) == 0:
        # right endpoint
        return True
    else:
        # (directly) between
        return (comparePosition(c1.position, target.position) == -1) and (comparePosition(target.position, c2.position) == -1)

    # Note: unless it's the last line, it has at least one char: newline.
def isInLine(line, char):
    if len(line) == 0:
        return False
    else:
        if comparePosition(line[0].position, char.position) == 0:
            # this first char in line is the char we're looking for.
            return True
        elif comparePosition(line[-1].position, char.position) == 0:
            # last char in line is the char we're looking for
            return True
        elif comparePosition(line[0].position, char.position) == 1:
            # target char is before start of line
            return False
        elif comparePosition(line[-1].position, char.position) == -1:
            # target char is after end of line
            return False
        else:
            # It's either:
            # 1. One of the interval endpoints
            # 2. To the left of the interval
            # 3. To the right of the interval
            # 4. Or inside the interval
            # These are the only possibilities, right? So I don't have to check anymore after the above conditions
            # I just return True
            return True

        # elif comparePosition(line[0].position, char.position) == -1:
        #     # first char in line is less than target char
        #     # target char belongs after line[0] char
        #     if comparePosition(line[-1].position, char.position) == -1:
        #         # target char is after both.
        #         # need to check to see if there are chars in next line, and if it is less than them.
        #         # if so, we prepend char to start of that next line (not append to this line, newline is always last)
        #         pass
        #     elif comparePosition(line[-1].position, char.position) == 0:
        #         # last char
