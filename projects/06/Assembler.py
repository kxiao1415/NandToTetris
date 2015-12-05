import sys, os
import Code
import SymbolTable
import Parser


class Assembler(object):
    def __init__(self, filePath):
        self.filePath = filePath
        self.varStart = 16
        self.labelStart = 0
        self.code = Code.Code()
        self.symbolTable = SymbolTable.SymbolTable()

    # add all Lables to the symbols table
    def firstPass(self):
        parser = Parser.Parser(self.filePath)
        while (parser.hasMoreCommands()):
            if parser.commandType() == parser.L_COMMAND:
                self.symbolTable.addEntry(parser.symbol(), self.labelStart)
            else:
                self.labelStart += 1
            parser.advance()
            
    # create the .hack file
    def secondPass(self):
        parser = Parser.Parser(self.filePath)
        fileName = os.path.splitext(os.path.basename(self.filePath))[0]
        hackFile = open(os.path.join(os.path.dirname(self.filePath), '%s.hack'%(fileName)), 'w')

        while (parser.hasMoreCommands()):
            if parser.commandType() == parser.A_COMMAND:
                if parser.symbol().isdigit():
                    hackFile.write('0' + '{0:015b}'.format(int(parser.symbol())) + '\n')
                elif self.symbolTable.contains(parser.symbol()):
                    hackFile.write('0' + '{0:015b}'.format(self.symbolTable.getAddress(parser.symbol())) + '\n')
                else:
                    self.symbolTable.addEntry(parser.symbol(), self.varStart)
                    hackFile.write('0' + '{0:015b}'.format(self.symbolTable.getAddress(parser.symbol())) + '\n')
                    self.varStart += 1
            if parser.commandType() == parser.C_COMMAND:
                binary='111'
                hackFile.write(binary + self.code.comp(parser.comp()) + self.code.dest(parser.dest()) + self.code.jump(parser.jump()) + '\n')
            parser.advance()

        hackFile.close()
            

    def assemble(self):
        self.firstPass()
        self.secondPass()


def main():
    if len(sys.argv) != 2:
        print("Usage: Assembler.py file.asm")
    else:
        asm = Assembler(sys.argv[1])
        asm.assemble()

main()
