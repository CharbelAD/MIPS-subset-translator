# MIPS-subset-translator

## Explanation

This piece of code was written to go alongside a project that I was given at university: to create a single-cycle CPU on [Logisim](http://www.cburch.com/logisim/index.html) that would be inspired by the MIPS32 ISA and would run a reduced subset of its instructions.

The supported instructions are: `add`, `sub`, `slt`, `bne`, `and`, `sb`, `lb`, `j`, `beq`.

There are 4 registers, r0 -> r4. And each instruction is represented on 16 bits like so:
 - R-type instructions: opcode (4 bits), rs (2 bits), rt (2 bits), rd (2 bits), unused (6 bits)
 - I-type instructions (inc. jump): opcode (4 bits), rs (2 bits), rt (2 bits), immediate (8 bits)

In order to test out the construction of the CPU on Logisim, we needed the hexadecimal representation of the instructions, so I wrote ths helper code. This Python code translates instructions from this weird ISA to hexadecimal (passing by binary, in case you may need it) and outputs it to a file which adheres to Logisim's format. It also supports labels in the assembly code alongside the instructions, refer to the example code below.

## Running the translator

You can run the code using the editor of your choice, you need to have a file named `input.asm` in the same directory (or modify the filename in the code at line 174), it  will output a file named `output.bin` that respects [Logisim's file format](http://www.cburch.com/logisim/docs/2.7/en/html/guide/mem/menu.html) which is just a header line and then machine code (in Hex) corresponding to each instruction separated by some whitespace. You can also import the module and create a new instance of the class `Assembler`, then call the method `assemble_file(input_filename, output_filename)`. I didn't polish the user interaction because it was not worthwhile at the time.

## Example code

Here is, for exposition purposes, an assembly program that runs [Euclid's GCD algorithm](https://en.wikipedia.org/wiki/Euclidean_algorithm):
```
Start:
    # The values of X and Y to evaluate should be 
    # in positions 0 and 1 in the memory
        lb $r1, 0($r0)      # Load X 
        lb $r2, 1($r0)      # Load Y
GCD:    beq $r1, $r0, L0    # if X=0
        beq $r2, $r0, L0    # if Y=0
        beq $r1, $r2, L1    # if X=Y

        slt $r3, $r1, $r2   # X < Y?
        bne $r3, $r0, Else  # If X<Y go to Else
        sub $r1, $r1, $r2   # X = X - Y
        j GCD
Else:   sub $r2, $r2, $r1   # Y = Y - X
        j GCD
L0:     sb $r0, 2($r0)      # return 0
        j Exit
L1:     sb $r1, 2($r0)      # return X
Exit:
    # The final value will be in the 3rd place in memory
```
Note that this is valid MIPS code if the register names were changed ($r1 -> $s1, for example.)

And here is its translated version:
```
v2.0 raw
0 0 0 6100 6201 8409 8808 8609 0 26c0 3c02 1640 7005 1980 7005 5002 
7012 5102 0 0 
```

## Finally
I do not think that too many people would be interested in actively using this project seeing that the targetted ISA (an odd MIPS subset) isn't really meaningful outside of learning purposes and that there much better solutions out there. However, I personally chose to tackle this problem in ~4-5 hours without looking at other similar programs to see what I could come up with, and this is what came to be. If you think the Logisim files related to this translator could be useful to you then you may contact me. Otherwise, you can raise an issue or contact me if you have anything relevant to this project to say.
