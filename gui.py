import tkinter as tk
from threading import *
import jsonpickle
import os

from editor import Editor
from change import EditorChange
from change import RemoteChange
from message import Mailbox

def cleanup():
    # text_info.mailbox.stop()
    # This is beyond inelegent, but...
    os._exit(0)

def onMessageReceived(ch, method, properties, body):
    remoteChangeRequest = jsonpickle.decode(body)
    #print(remoteChangeRequest.command)
    newstring = text_info.editor.applyRemoteChange(remoteChangeRequest)
    text_info.suspend_modify_callback()
    text_info.delete(1.0,"end")
    text_info.insert(1.0, newstring)
    text_info.resume_modify_callback()

def onModification(event):
    if event.widget.event_callback_suspended:
        return
    # print(event.widget.beforePosition)
    # print(event.widget.afterPosition)
    (beforeLine, beforeColumn) = event.widget.beforePosition.split(".")
    (afterLine, afterColumn) = event.widget.afterPosition.split(".")
    beforeLine = int(beforeLine)
    beforeColumn = int(beforeColumn)
    afterLine = int(afterLine)
    afterColumn = int(afterColumn)

    # 3 possibilities:
    #column goes backward (before-after = 1): character at "after" was deleted
    #column goes forward (before-after = -1): character was inserted at "before"
    #column doesn't change: (before-after = 0): character at after/before was deleted.
    # line possibilities:
    # increases lbefore-lafter = -1: newline was inserted at before
    # decreases lbefore-lafter = 1: newline was deleted
    # line doesn't change: character at position was deleted (could be newline)
    # to make these consistent, newlines should be considered at the end of a line

    lineDelta = beforeLine - afterLine
    columnDelta = beforeColumn - afterColumn
    beforeLines = event.widget.beforeText.splitlines(True)

    if (lineDelta == 0 and columnDelta == 0):
        # once in a while this is seemingly called before the first character is inserted.
        # Seems like maybe a sporadic bug in tkinter. Not worth fixing, in my mind. 
        # It doesn't prevent me from showing off the actual point of the project - the CRDT and communication.
        
        # Character at (beforeLine, beforeColumn) == (afterLine, afterColumn) deleted
        #print(repr(beforeLines[beforeLine-1][beforeColumn]))
        change = EditorChange(beforeLine, beforeColumn, "", beforeLines[beforeLine-1][beforeColumn])
    elif (columnDelta == 1 and lineDelta == 0): # edge case: have to ensure that we don't mistake 'linefeed effect' for deletion
        # Character at (afterLine, afterColumn) deleted
        change = EditorChange(afterLine, afterColumn, "", beforeLines[afterLine-1][afterColumn])
    elif (columnDelta == -1):
        # Character inserted at (beforeLine, beforeColumn)
        change = EditorChange(beforeLine, beforeColumn, event.widget.eventChar, "")
    elif (lineDelta == -1):
        # Newline inserted at (beforeLine, beforeColumn)
        change = EditorChange(beforeLine, beforeColumn, event.widget.eventChar, "")
    elif (lineDelta == 1):
        # Newline deleted at (afterLine, afterColumn) Remember, newlines are at the end
        change = EditorChange(afterLine, afterColumn, "", beforeLines[afterLine-1][afterColumn])

    event.widget.editor.applyLocalChange(change)
    #broadcast.broadcast_message(change)

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs)
        self.event_callback_suspended = False

        # create Mailbox object
        self.mailbox = Mailbox(onMessageReceived, "config.txt")

        # custom editor object
        self.editor = Editor(self.mailbox)
        self.mailbox.startListening()

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args

        if command in ("insert", "delete", "replace"):
            self.beforePosition = self.index(tk.INSERT)
            self.beforeText = self.get("1.0", "end-1c")
            if (len(args) > 1): # have to check because deletions don't include content
                self.eventChar = args[1]
                # print(args)
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.afterPosition = self.index(tk.INSERT)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

    # Have to stop my modification callback before I apply remote changes from the CRDT to the text widget
    # Otherwise it generates two extraneous events which break everything - Crazy recursion.
    def suspend_modify_callback(self):
        self.event_callback_suspended = True
    def resume_modify_callback(self):
        self.event_callback_suspended = False

root = tk.Tk()
root.geometry("350x250")
root.title("Sticky Notes")
root.minsize(height=250, width=350)
root.maxsize(height=250, width=350)
  
  
# adding scrollbar
scrollbar = tk.Scrollbar(root)
  
# packing scrollbar
scrollbar.pack(side=tk.RIGHT,
               fill=tk.Y)
  
# create custom text widget
text_info = CustomText(root,
                 yscrollcommand=scrollbar.set)
text_info.pack(fill=tk.BOTH)
  
# configuring the scrollbar
scrollbar.config(command=text_info.yview)

# bind callback for custom onModification event in custom text widget
text_info.bind("<<TextModified>>", onModification)

# setup callback:
# When received message, send to editor to process. Blocking. (is this wise? Tentatively, I think so.)
# When returned, set the text widget content with editor.getString

root.protocol("WM_DELETE_WINDOW", cleanup)
  
root.mainloop()