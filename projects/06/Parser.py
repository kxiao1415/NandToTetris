import re

class Parser(object):
    A_COMMAND = 1
    L_COMMAND = 2
    C_COMMAND = 3
    
    def __init__(self, filePath):
        self.count = 0
        self.cleanFile = []
        
        preProcess = open(filePath, 'r')
        for line in preProcess:
            line = re.sub(r'[\s]', '', line.split(r'//')[0])
            if line:
                self.cleanFile.append(line)
        preProcess.close()

        self.currentCommand = self.cleanFile[0]


    def hasMoreCommands(self):
        return self.count < len(self.cleanFile)


    def advance(self):
        self.count += 1
        if self.hasMoreCommands():
            self.currentCommand = self.cleanFile[self.count]

    def commandType(self):
        if self.currentCommand[0] == '@':
            return self.A_COMMAND
        elif self.currentCommand[0] == '(':
            return self.L_COMMAND
        else:
            return self.C_COMMAND
    

    def symbol(self):
        if self.commandType() == self.A_COMMAND:
            return self.currentCommand[1:]
        if self.commandType() == self.L_COMMAND:
            return self.currentCommand[1:-1]


    def dest(self):
        if '=' in self.currentCommand:
            return self.currentCommand.split('=')[0]
        else:
            return 'null'


    def comp(self):
        s = re.sub(r'.*=', '', self.currentCommand)
        return re.sub(r';.*', '', s)


    def jump(self):
        if ';' in self.currentCommand:
            return self.currentCommand.split(';')[-1]
        else:
            return 'null'
