class Parser:
    def __init__(self, file):
        '''
        Opens the input file/stream and gets ready to parse it
        '''
        self.count = 0
        self.currentCommand = ''
        self.cleanFile = []
        
        preProcess = open(file, 'r')
        for line in preProcess.readlines():
            line = line.split('/')[0]
            line = line.replace('\r\n', '').rstrip()
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
        self.currentCommand = self.cleanFile[self.count]
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
        if currentCommand == 'label':
            return 'C_LABEL'
        if currentCommand == 'goto':
            return 'C_GOTO'
        if currentCommand == 'function':
            return 'C_FUNCTION'
        if currentCommand == 'return':
            return 'C_RETURN'
        if currentCommand == 'call':
            return 'C_CALL'
        if currentCommand == 'if-goto':
            return 'C_IF'


    def arg1(self):
        '''
        Returns the first arg of the current command
        '''
        if self.commandType() == 'C_RETURN':
            return None
        if self.commandType() == 'C_ARITHMETIC':
            return self.currentCommand.split(' ')[0]

        return self.currentCommand.split(' ')[1]


    def arg2(self):
        '''
        Returns the second arg of the current command
        '''
        if self.commandType() in ['C_PUSH', 'C_POP', 'C_CALL', 'C_FUNCTION']:
            return self.currentCommand.split()[2]
