class Parser(object):
    def __init__(self):
        self.state = InitialState(self)
        self.depends = []
        self.after = []
        self.phpbb_version = []
        self.db = []
    
    def feed(self, line):
        self.state = self.state.advance(line)

class State(object):
    def __init__(self, parser):
        self.parser = parser

class InitialState(State):
    def advance(self, line):
        if line == 'depends:':
            return DependsState(self.parser)
        elif line == 'after:':
            return AfterState(self.parser)
        elif line == 'phpbb_version:':
            return PhpbbVersionState(self.parser)
        elif line == 'db:':
            return DbState(self.parser)
        else:
            raise ValueError("Bogus input: %s" % line)

class DependsState(State):
    def advance(self, line):
        if len(line) == 0:
            return InitialState(self.parser)
        else:
            self.parser.depends.append(line)
            return self

class AfterState(State):
    def advance(self, line):
        if len(line) == 0:
            return InitialState(self.parser)
        else:
            self.parser.after.append(line)
            return self

class PhpbbVersionState(State):
    def advance(self, line):
        if len(line) == 0:
            return InitialState(self.parser)
        else:
            self.parser.phpbb_version.append(line)
            return self

class DbState(State):
    def advance(self, line):
        if len(line) == 0:
            return InitialState(self.parser)
        else:
            self.parser.db.append(line)
            return self
