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
        self.call_count = 0
        self.bool_count = 0
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
        self.file.write('A=M\n' +
                        'D=M\n')


    def set_A_to_stack(self):
        self.file.write('@SP\n' +
                        'A=M\n')


    def pushD(self):
        '''
        push the value of the D register to the stack
        '''
        self.file.write('@SP\n' +
                        'A=M\n' +
                        'M=D\n')

        self.incrementSP()


    def from_stack_to_memory(self, segment, index):
        self.file.write('@{}\n'.format(index) +
                        'D=A\n' +
                        '@{}\n'.format(segment) +
                        'D=D+M\n' +
                        '@R13\n' +
                        'M=D\n')  # Store memory index where we want to store in R13
        self.pushD()

        self.file.write('@R13\n' +
                        'A=M\n' +
                        'M=D\n')

    
    def writeArithmetic(self, command):
        '''
        Writes the assembly code that is the translation
        of the given arithmetic command
        '''
        if command in binary_ops:
            self.popToD()
            self.decrementSP()
            self.set_A_to_stack()
            self.file.write('M=M%sD\n'%binary_ops[command])

        elif command in unary_ops:
            self.decrementSP()
            self.set_A_to_stack()
            self.file.write('M=%sM\n'%unary_ops[command])

        elif command in compares:
            self.popToD()
            self.decrementSP()
            self.set_A_to_stack()
            self.file.write('D=M-D\n' +
                            '@BOOL_{}\n'.format(self.bool_count) +
                            'D;{}\n'.format(compares[command]))
            self.set_A_to_stack()
            self.file.write('M=0\n' +
                            '@ENDBOOL_{}\n'.format(self.bool_count) +
                            '0;JMP\n' +
                            '(BOOL_{})\n'.format(self.bool_count))
            self.set_A_to_stack()
            self.file.write('M=-1\n' +
                            '(ENDBOOL_{})\n'.format(self.bool_count))

            self.bool_count += 1

        self.incrementSP()


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
                self.file.write('@R%d\n' %(Segments[segment] + int(index)) +
                                'D=M\n')

            elif segment == 'static':
                varName = '{}_{}'.format(self.fileName, index)
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
            if segment in ('temp','pointer'):
                self.file.write('@R%d\n' %(Segments[segment] + int(index)))
            elif segment == 'static':
                varName = '{}_{}'.format(self.fileName, index)
                self.file.write('@%s\n' %(varName))
            else:
                self.file.write('@%s\n' %(Segments[segment]) +
                                'D=M\n' +
                                '@%s\n' %(index) +
                                'A=D+A\n')

            self.file.write('D=A\n' +
                            '@R13\n' + # Store resolved address in R13
                            'M=D\n')
            self.popToD()
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
        for i in range(int(numLocals)):
            self.file.write('D=0\n')
            self.pushD()


    def writeInit(self):
        self.file.write('@256\n' +
                        'D=A\n' +
                        '@SP\n' +
                        'M=D\n')
        self.writeCall('Sys.init', 0)


    def writeLabel(self, label):
        self.file.write('({0})\n'.format(label))

    def writeGoto(self, label):
        self.file.write('@{0}\n'.format(label) +
                        '0;JMP\n')


    def writeIf(self, label):
        self.popToD()
        self.file.write('@{0}\n'.format(label) +
                        'D;JNE\n')


    def writeReturn(self):
        FRAME = 'R13'
        RET = 'R14'

        #FRAME = LCL //FRAME is a temporary variable
        self.file.write('@LCL\n' +
                        'D=M\n' +
                        '@{0}\n'.format(FRAME) +
                        'M=D\n')
        
        #RET = *(FRAME-5) //Put the return-address in a temp. var.
        self.file.write('@{}\n'.format(FRAME) +
                        'D=M\n' +
                        '@5\n' +
                        'D=D-A\n' +
                        'A=D\n' +
                        'D=M\n' +
                        '@{0}\n'.format(RET) +
                        'M=D\n')

        #ARG = POP() //Reposition the return value for the caller
        self.popToD()
        self.file.write('@ARG\n' +
                        'A=M\n' +
                        'M=D\n')

        #SP = ARG + 1 //Restore SP of the caller
        self.file.write('@ARG\n' +
                        'D=M\n' +
                        '@SP\n' +
                        'M=D+1\n')

        # THAT = *(FRAME-1)
        # THIS = *(FRAME-2)
        # ARG = *(FRAME-3)
        # LCL = *(FRAME-4)
        offset = 1
        for address in ['@THAT', '@THIS', '@ARG', '@LCL']:
            self.file.write('@{0}\n'.format(FRAME) +
                            'D=M\n' +
                            '@{}\n'.format(offset) +
                            'D=D-A\n' + # Adjust address
                            'A=D\n' + # Prepare to load value at address
                            'D=M\n' + # Store value
                            '{}\n'.format(address) +
                            'M=D\n') # Save value
            offset += 1

        #goto RET //Goto return-address (in the caller's code)
        self.file.write('@{0}\n'.format(RET) +
                        'A=M\n' +
                        '0;JMP\n')
                        
                        
    def writeCall(self, functionName, numArgs):
        """
        LCL starts at numArgs + 5 away from the bottom of the FRAME
        The 5 spots are used for 1. return address 2. LCL 3. ARG 4. THIS 5. THAT
        """
        returnLabel = 'RETURN_{0}_{1}'.format(functionName, self.call_count)
            
        self.call_count += 1

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

        #LCL = SP //Reposition LCL
        self.file.write('@SP\n' +
                        'D=M\n' +
                        '@LCL\n' +
                        'M=D\n')

        #ARG = SP - n - 5 //Reposition ARG (n = number of args.)
        self.file.write('@{}\n'.format(5+ int(numArgs)) +
                        'D=D-A\n' +
                        '@ARG\n' +
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
