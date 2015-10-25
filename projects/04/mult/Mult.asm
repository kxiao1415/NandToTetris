// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

    @R1
    D=M
    @y
    M=D // y = R1

    @R2
    M=0 // initiate R2 to 0
(LOOP)
    @y
    D=M
    @END
    D;JLE // if y <=0 goto END

    @1
    D=D-A
    @y
    M=D // y = y - 1

    @R2
    D=M
    @R0
    D=D+M
    @R2
    M=D // R2 = R2 + R0
    
    @LOOP
    0;JMP // restart the LOOP

(END)
    @END
    0;JMP // Infinite loop
