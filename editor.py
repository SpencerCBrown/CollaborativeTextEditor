from uuid import uuid1
from crdt import CRDT
from crdt import updateLocalToRemote
from crdt import updateRemoteToLocal
from change import RemoteChange

import jsonpickle

class Editor:
    def __init__(self, mailbox):
        self.crdt = CRDT()
        self.lamport = 0
        self.siteID = uuid1()
        self.mailbox = mailbox

    def applyLocalChange(self, change):
        #print(change.added + change.removed)
        self.lamport = self.lamport + 1
        changes = updateLocalToRemote(self.crdt, self.lamport, self.siteID.int, change)

        # serialize RemoteChange object to json
        change_message = jsonpickle.encode(changes)

        self.mailbox.broadcast_message(change_message)

    def applyRemoteChange(self, change):
        self.lamport = max(self.lamport, change.char.lamport) + 1
        newCrdtString = updateRemoteToLocal(self.crdt, change)
        #print("applyRemoteChange: " + newCrdtString)
        return newCrdtString

    
    def getString(self):
        return self.crdt.toString()