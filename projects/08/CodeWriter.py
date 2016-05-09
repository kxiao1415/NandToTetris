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
        self.functionName = ''
        self.file = open(file, 'w')
        self.writeInit()


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
            true = 'TRUE${0}'.format(self.jumpToFlag)
            false = 'FALSE${0}'.format(self.jumpToFlag)

            if self.functionName:
                true = self.functionName + '$' + true
                false = self.functionName + '$' + false
                
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


    def writeFunction(self, functionName, numLocals):
        """
        (f)                  //Declare a label for the function entry
            repeat k times:  //k = number of local variables
            push 0           //Initialize all of them to 0
        """
        self.functionName = functionName
        self.file.write('({0})\n'.format(functionName))
        for i in range(numLocals):
            self.writePushPop('push', 'constant', 0)


    def writeInit(self):
        self.file.write('@256\n' +
                        'D=A\n' +
                        '@SP\n' +
                        'M=D\n')
        self.writeCall('Sys.init', 0)


    def writeLabel(self, label):
        if self.functionName:
            self.file.write('({0}${1})\n'.format(self.functionName, label))
        else:
            self.file.write('({0})\n'.format(label))

    def writeGoto(self, label):
        if self.functionName:
            self.file.write('@{0}${1}\n'.format(self.functionName, label))
        else:
            self.file.write('@{0}\n'.format(label))
        self.file.write('0;JMP\n')


    def writeIf(self, label):
        self.popToD()
        
        if self.functionName:
            self.file.write('@{0}${1}\n'.format(self.functionName, label))
        else:
            self.file.write('@{0}\n'.format(label))
            
        self.file.write('D;JNE\n')


    def writeReturn(self):
        FRAME = 'R13'
        RET = 'R14'

        #FRAME = LCL //FRAME is a temporary variable
        self.file.write('@LCL\n' +
                        'D=M\n' +
                        '@{0}\n'.format(FRAME) +
                        'M=D\n')
        
        #RET = *(FRAME-5) //Put the return-address in a temp. var.
        self.file.write('@5\n' +
                        'A=D-A\n' +
                        'D=M\n' +
                        '@{0}\n'.format(RET) +
                        'M=D\n')

        #ARG = POP() //Reposition the return value for the caller
        self.popToD()
        self.file.write('@ARG\n' +
                        'A=M\n' +
                        'M=D\n')

        #SP = ARG + 1 //Restore SP of the caller
        self.file.write('D=A+1\n' +
                        '@SP\n' +
                        'M=D\n')

        #THAT = *(FRAME - 1) //Restore THAT of the caller
        self.file.write('@{0}\n'.format(FRAME) +
                        'A=M-1\n' +
                        'D=M\n' +
                        '@THAT\n' +
                        'M=D\n')
        #THIS = *(FRAME - 2) //Restore THIS of the caller
        self.file.write('@{0}\n'.format(FRAME) +
                        'D=M\n' +
                        '@2\n' +
                        'A=D-A\n' +
                        'D=M\n' +
                        '@THIS\n' +
                        'M=D\n')
        #ARG = *(FRAME -3) //Restore ARG of the caller
        self.file.write('@{0}\n'.format(FRAME) +
                        'D=M\n' +
                        '@3\n' +
                        'A=D-A\n' +
                        'D=M\n' +
                        '@ARG\n' +
                        'M=D\n')
        #LCL = *(FRAME -4) //Restore LCL of the caller
        self.file.write('@{0}\n'.format(FRAME) +
                        'D=M\n' +
                        '@4\n' +
                        'A=D-A\n' +
                        'D=M\n' +
                        '@LCL\n' +
                        'M=D\n')
        #goto RET //Goto return-address (in the caller's code)
        self.file.write('@{0}\n'.format(RET) +
                        'A=M\n' +
                        '0;JMP\n')
                        
                        
    def writeCall(self, functionName, numArgs):
        """
        LCL starts at numArgs + 5 away from the bottom of the FRAME
        The 5 spots are used for 1. return address 2. LCL 3. ARG 4. THIS 5. THAT
        """
        offset = numArgs + 5

        returnLabel = 'RETURN${0}'.format(self.jumpToFlag)       
        if self.functionName:
            returnLabel = '{0}${1}'.format(functionName, returnLabel)
            
        self.jumpToFlag += 1

        #push return-address //(Using the label declared below)
        self.file.write('@{0}\n'.format(returnLabel) +
                        'D=A\n')
        self.pushD()

        #push LCL //Save LCL of the calling function
        self.file.write('@LCL\n' +
                        'D=M\n')
        self.pushD()
        
        #push ARG //Save ARG of the calling function
        self.file.write('@ARG\n' +
                        'D=M\n')
        self.pushD()
        
        #push THIS //Save THIS of the calling function
        self.file.write('@THIS\n' +
                        'D=M\n')
        self.pushD()
        
        #push THAT //Save THAT of the calling function
        self.file.write('@THAT\n' +
                        'D=M\n')
        self.pushD()

        #ARG = SP - n - 5 //Reposition ARG (n = number of args.)
        self.file.write('@SP\n' +
                        'D=M\n' +
                        '@{0}\n'.format(offset) +
                        'D=D-A\n' +
                        '@ARG\n' +
                        'M=D\n')
        
        #LCL = SP //Reposition LCL
        self.file.write('@SP\n' +
                        'D=M\n' +
                        '@LCL\n' +
                        'M=D\n')
        
        #goto f //Transfer control
        self.file.write('@{0}\n'.format(functionName) +
                        '0;JMP\n')
        
        #(return-address) //Declare a label for the return-address
        self.file.write('({0})\n'.format(returnLabel))
        

    def close(self):
        '''
        Closes the output file
        '''
        self.file.close()

