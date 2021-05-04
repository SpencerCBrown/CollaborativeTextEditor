from char import Char

class EditorChange:
    def __init__(self, line, column, added, removed):
        self.line = line
        self.column = column
        self.added = added
        self.removed = removed

class RemoteChange:
    def __init__(self, command, char):
        self.command = command # "add" or "remove"
        self.char = char # single char