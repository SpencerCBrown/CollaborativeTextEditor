import tkinter as tk
from threading import *

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs)

        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)

        if command in ("insert", "delete", "replace"):
            self.event_generate("<<TextModified>>")

        return result

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
  
  
text_info = CustomText(root,
                 yscrollcommand=scrollbar.set)
text_info.pack(fill=tk.BOTH)
  
# configuring the scrollbar
scrollbar.config(command=text_info.yview)


def onModification(event):
    chars = event.widget.get("1.0", "end-1c")
    print(chars)

text_info.bind("<<TextModified>>", onModification)

# def printtext():
#     while 1:
#      print(text_info.get("1.0", 'end-1c'))

# thread = Thread(target = printtext)
# thread.start()
  
root.mainloop()