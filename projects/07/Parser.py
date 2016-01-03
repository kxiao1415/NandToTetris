import re

class Parser:
    def __init__(self, file):
        '''
        Opens the input file/stream and gets ready to parse it
        '''
        self.count = 0
        self.currentCommand = ''
        self.cleanFile = []
        
        preProcess = open(file, 'r')
        for line in preProcess:
            line = line.split(r'//')[0]
            if line:
                self.cleanFile.append(line)
        preProcess.close()

        
    def hasMoreCommands(self):
        '''
        Are there more commands in the input?
        '''
        return self.count < len(self.cleanFile)

    
    def advance(self):
        '''
        Reads the next command from the input and makes it the current command
        '''
        self.currentCommand = re.sub(r'\r\n', '', self.cleanFile[self.count])
        self.count += 1
        

    def commandType(self):
        '''
        Returns the type of the current VM command.
        C_ARITHMETIC is returned for all the arithmetic commands
        '''
        currentCommand = self.currentCommand.split(' ')[0]
        if currentCommand in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not'):
            return 'C_ARITHMETIC'
        if currentCommand == 'push':
            return 'C_PUSH'
        if currentCommand == 'pop':
            return 'C_POP'


    def arg1(self):
        '''
        Returns the first arg of the current command
        '''
        if self.commandType() == 'C_ARITHMETIC':
            return self.currentCommand
        else:
            return self.currentCommand.split()[1]
        

    def arg2(self):
        '''
        Returns the second arg of the current command
        '''
        return self.currentCommand.split()[2]
        
