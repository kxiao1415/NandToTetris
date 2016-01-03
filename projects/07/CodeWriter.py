binary_ops = {'add' : '+',
              'sub' : '-',
              'and' : '&',
              'or' : '|'
              }
              
unary_ops = {'neg' : '-',
             'not' : '!'
             }

compares = {'eq' : 'JEQ',
            'gt' : 'JGT',
            'lt' : 'JLT'
            }

Segments = {'local' : 'LCL',
            'argument' : 'ARG',
            'this' : 'THIS',
            'that' : 'THAT',
            'pointer' : 3,
            'temp' : 5
            }


class CodeWriter:
    def __init__(self, file):
        '''
        Opens the output file/stream and gets ready to
        write into it
        '''
        self.jumpToFlag = 0
        self.file = open(file, 'w')


    def setFileName(self, fileName):
        '''
        Informs the code writer that the translation of a
        new VM file is started
        '''
        self.fileName = fileName
        print "translating file: %s"%(fileName)


    def decrementSP(self):
        '''
        decrement the stack pointer by 1
        '''
        self.file.write('@SP\n' +
                        'M=M-1\n')


    def incrementSP(self):
        '''
        increment the stack pointer by 1
        '''
        self.file.write('@SP\n' +
                        'M=M+1\n')
        

    def popToD(self):
        '''
        pops the top of the stack to the D register
        '''
        self.decrementSP()
        self.file.write('@SP\n' +
                        'A=M\n' +
                        'D=M\n')
        

    def popToA(self):
        '''
        pops the top of the stack to the A register
        '''
        self.decrementSP()
        self.file.write('@SP\n' +
                        'A=M\n' +
                        'A=M\n')
        

    def pushD(self):
        '''
        push the value of the D register to the stack
        '''
        self.file.write('@SP\n' +
                        'A=M\n' +
                        'M=D\n')
        self.incrementSP()
        
    
    def writeArithmetic(self, command):
        '''
        Writes the assembly code that is the translation
        of the given arithmetic command
        '''
        if command in binary_ops:
            self.popToD()
            self.popToA()
            self.file.write('D=A%sD\n'%binary_ops[command])
            self.pushD()

        elif command in unary_ops:
            self.popToD()
            self.file.write('D=%sD\n'%unary_ops[command])
            self.pushD()

        elif command in compares:
            #(TRUE) and (FALSE) labels
            true = 'TRUE%s' %(self.jumpToFlag)
            false = 'FALSE%s' %(self.jumpToFlag)
            self.jumpToFlag += 1
            
            self.popToD()
            self.popToA()
            self.file.write('D=A-D\n' +
                            '@%s\n'%(true) +
                            'D;%s\n' %(compares[command])) #goto (TRUE) if true
            
            #if false
            self.file.write('@SP\n' +
                            'A=M\n' +
                            'M=0\n') # 0 is false
            self.incrementSP()
            self.file.write('@%s\n' %(false) +
                            '0;JMP\n') #skip over (TRUE) clause
            
            #(TRUE)
            self.file.write('(%s)\n'%(true) +
                            '@SP\n' +
                            'A=M\n' +
                            'M=-1\n')
            self.incrementSP()
            
            #(FALSE)
            self.file.write('(%s)\n' %false)
    

    def writePushPop(self, command, segment, index):
        '''
        Writes the assembly code that is the translation
        of the given command, where command is either
        C_PUSH or C_POP
        '''
        if command == 'push':
            if segment == 'constant':
                self.file.write('@%s\n' %(index) +
                                'D=A\n')
            elif segment in ('temp','pointer'):
                self.file.write('@%d\n' %(Segments[segment] + int(index)) +
                                'D=M\n')
            elif segment == 'static':
                varName = self.fileName + '.' + index
                self.file.write('@%s\n' %(varName) +
                                'D=M\n')            
            else:
                self.file.write('@%s\n' %(Segments[segment]) +
                                'D=M\n' +
                                '@%s\n' %(index) +
                                'A=D+A\n' +
                                'D=M\n')
                
            # push value stored on D register to the stack, then increment the stack
            self.pushD()
            
        elif command == 'pop':
            
            # stored the address of the varible segment+index into register R13
            if segment in ('temp','pointer'):
                self.file.write('@%d\n' %(Segments[segment] + int(index)) +
                                'D=A\n' +
                                '@R13\n' +
                                'M=D\n')
            elif segment == 'static':
                varName = self.fileName + '.' + index
                self.file.write('@%s\n' %(varName) +
                                'D=A\n' +
                                '@R13\n' +
                                'M=D\n')
            else:
                self.file.write('@%s\n' %(Segments[segment]) +
                                'D=M\n' +
                                '@%s\n' %(index) +
                                'D=D+A\n' +
                                '@R13\n' +
                                'M=D\n')
                
            # pop the stack to the D registert, then decrement the stack
            self.popToD()

            # stored the value of D register into the address of the variable segment+index that is stored in register R13 
            self.file.write('@R13\n' +
                            'A=M\n' +
                            'M=D\n') 
        

    def close(self):
        '''
        Closes the output file
        '''
        self.file.close()
    
