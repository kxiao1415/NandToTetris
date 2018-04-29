import sys, os
import CodeWriter
import Parser


class VMTranslator(object):
    def __init__(self, directory):
        if directory.endswith('/'):
            directory = directory[:-1]
        self.directory = directory


    def translate(self):
        dirVM = os.path.join(os.getcwd(), self.directory)
        fileName = os.path.basename(dirVM)
        codeWriter = CodeWriter.CodeWriter(os.path.join(dirVM, fileName + '.asm'))
        codeWriter.setFileName(fileName)

        vmFiles = [f for f in os.listdir(dirVM) if f.endswith('.vm')]

        for f in vmFiles:
            
            parser = Parser.Parser(os.path.join(dirVM, f))
                                   
            while parser.hasMoreCommands():
                # advance first since the current command starts out empty
                parser.advance()

                print 'current command: ' + repr(parser.currentCommand)
                
                if parser.commandType() == 'C_ARITHMETIC':
                    codeWriter.writeArithmetic(parser.currentCommand)
                elif parser.commandType() == 'C_PUSH':
                    segment = parser.arg1()
                    index = parser.arg2()
                    codeWriter.writePushPop('push',segment,index)
                elif parser.commandType() == 'C_POP':
                    segment = parser.arg1()
                    index = parser.arg2()
                    codeWriter.writePushPop('pop',segment,index)
                elif parser.commandType() == 'C_LABEL':
                    label = parser.arg1()
                    codeWriter.writeLabel(label)
                elif parser.commandType() == 'C_IF':
                    label = parser.arg1()
                    codeWriter.writeIf(label)
                elif parser.commandType() == 'C_GOTO':
                    label = parser.arg1()
                    codeWriter.writeGoto(label)
                elif parser.commandType() == 'C_CALL':
                    functionName = parser.arg1()
                    numArgs = int(parser.arg2())
                    codeWriter.writeCall(functionName, numArgs)
                elif parser.commandType() == 'C_FUNCTION':
                    functionName = parser.arg1()
                    numLocals = int(parser.arg2())
                    codeWriter.writeFunction(functionName, numLocals)
                elif parser.commandType() == 'C_RETURN':
                    codeWriter.writeReturn()
        
        codeWriter.close()
        

def main():
    if len(sys.argv) != 2:
        print("Usage: VMTranslator.py directory")
    else:
        translator = VMTranslator(sys.argv[1])
        translator.translate()

main()
