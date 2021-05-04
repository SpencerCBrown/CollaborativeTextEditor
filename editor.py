from uuid import uuid1
from crdt import CRDT
from crdt import updateLocalToRemote

class Editor:
    def __init__(self):
        self.crdt = CRDT()
        self.lamport = 0
        self.siteID = uuid1()

    def applyLocalChange(self, change):
        #print(change.added + change.removed)
        self.lamport = self.lamport + 1
        changes = updateLocalToRemote(self.crdt, self.lamport, self.siteID.int, change)
        # sendChange(change, self.lamport)