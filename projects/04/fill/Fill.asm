// This file is part of the materials accompanying the book
// "The Elements of Computing Systems" by Nisan and Schocken,
// MIT Press. Book site: www.idc.ac.il/tecs
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed,
// the screen should be cleared.

// Put your code here.

@COUNTER //number of words currently filled
M=0

(LOOP)
    @KBD
    D=M

    @UNFILL
    D;JEQ

    @FILL
    0;JMP

(FILL)
    @COUNTER
    D=M
    @8192 //max number of words on screen is  16*512 = 8192
    D=D-A //if RAM[i] = 8192, the screen is already filled, do nothing

    @LOOP
    D;JEQ
    
    //otherwise, fill the next word
    @COUNTER
    D=M-1 //first word starts at index 0
    @SCREEN
    A=A+D
    M=-1 //-1 is 1111111111111111 in binary

    //inc RAM[COUNTER] by 1
    @COUNTER
    M=M+1

    @LOOP
    0;JMP

(UNFILL)
    @COUNTER
    D=M

    @LOOP
    D;JEQ

    @COUNTER
    D=M-1 //first word starts at index 0
    @SCREEN
    A=A+D
    M=0

    @COUNTER
    M=M-1

    @LOOP
    0;JMP
