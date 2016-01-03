import sys, os
import CodeWriter
import Parser


class VMTranslator(object):
    def __init__(self, filePath):
        self.filePath = filePath


    def translate(self):
        fileName = os.path.splitext(os.path.basename(self.filePath))[0]
        codeWriter = CodeWriter.CodeWriter(fileName + '.asm')
        codeWriter.setFileName(fileName)
        
        parser = Parser.Parser(self.filePath)
        while (parser.hasMoreCommands()):
            # advance first since the currentcommand starts out empty
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
        
        codeWriter.close()
        

def main():
    if len(sys.argv) != 2:
        print("Usage: VMTranslator.py file.vm")
    else:
        translator = VMTranslator(sys.argv[1])
        translator.translate()

main()
