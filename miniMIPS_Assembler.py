import re

DEBUG = True  # variable for debugging

# map of the instructions and their opcodes.
# I could've just used a list an use the index of appearance in the list, but
# dictionary accesses are much better
instructions = {"add": "0000", "sub": "0001", "slt": "0010", "bne": "0011",
                "and": "0100", "sb": "0101", "lb": "0110", "j": "0111",
                "beq": "1000"}

# lookups in sets are a faster than in lists
r_type = set(["add", "sub", "slt", "and"])
# I don't need sets for mem and branch but this design is more modular and
#  allows extensions/changes easier
mem = set(["sb", "lb"])
branch = set(["beq", "bne"])


def print_debug(arg):
    """
    Special print function that only prints on the screen in case of debugging
    """
    global DEBUG
    if DEBUG:
        print(arg)


class Assembler:
    def __init__(self):
        self.file = []
        self.labels = {}

    def assemble_file(self, filename, outfilename):
        # opening the file
        print_debug("Opening the file to read")
        with open(filename, "r") as infile:
            # get all the content of it to memory
            self.file = infile.readlines()
        print_debug("Successfully read file.")
        print_debug("Identifying labels")
        # First pass, identifying labels and comments, and removing empty lines
        # (thank God MIPS doesn't have reflection)
        for l in range(len(self.file)):
            label = re.search(r"^\w+(?=:)", self.file[l])
            if label is not None:
                self.labels[label.group(0)] = l
                # once the label is found, we can remove it from the code
                self.file[l] = self.file[l].replace(label.group(0) + ":", "").strip()
            comment = re.search(r"\s+#.*", self.file[l])
            if comment is not None:
                # if we have a line with just a comment, we can ignore it and remove it
                self.file[l] = self.file[l].replace(comment.group(0), "").strip()

        print_debug("Translating")
        hex_machine_code = []
        # Second pass, translating the instructions to hex machine code
        # We use self.i as iterator because we want class-wide awareness of the
        # assembler PC for label resolution
        for self.i in range(len(self.file)):
            # we get the instruction's equivalent in binary
            instruction = self.file[self.i].strip()
            if instruction == "":
                hex_machine_code.append("0")
                continue
            machine_code = self.translate_instruction(instruction)
            print_debug(machine_code)
            # Then we translate it to hexadecimal
            hex_machine_code.append('{:04x}'.format(int(machine_code, 2)))
            print_debug(hex_machine_code)

        print_debug("Opening file to save")
        with open(outfilename, "w") as outfile:
            outfile.write("v2.0 raw\n")
            for line in hex_machine_code:
                outfile.write(line + " ")
        print_debug("Succesfully saved file")

    def _resolve_label(self, label, relative):
        if relative is False:
            # if we want the asolute position
            return '{0:08b}'.format(self.labels[label])
        else:  # if we want the relative position:
            # We know that Label = (PC+1) + immediate in case of branching
            # so immediate = label - (PC+1)
            immediate = self.labels[label] - self.i - 1
            if immediate < 0:
                # if negative, we return 2s complement of the number
                return '{0:08b}'.format(255 + immediate + 1)
            else:
                return '{0:08b}'.format(immediate)

    def translate_instruction(self, instr):
        print_debug("Recieved: " + instr)
        op = re.match(r"^[a-z]+(?= )", instr)  # match the operation
        if op is None:
            # if an operation was not found we throw an error
            raise Exception("Received wrongly formatted instruction: {instr}")
        else:
            operation = op.group(0)  # get the operation if found
            if operation not in instructions:
                raise Exception(f"Invalid operation: {instr}.")
            m_code = instructions[operation]  # resolve its opcode
            # Check the type of instruction to correctly parse it
            if operation in r_type:
                print_debug("R-type instruction")
                # regex to parse the 3 registers
                regs = re.search(r"(?P<rd>\$?r\d),? ?(?P<rs>\$?r\d),? ?(?P<rt>\$?r\d)",
                                 instr)
                if regs is None:
                    # If the match was not perfect, it is incorrectly formatted
                    raise Exception(f"Received wrongly formatted instruction: {instr}")
                # get the binary address of each register
                print_debug("Regex caught:" + str(regs.groups()))
                rs = '{0:02b}'.format(int(regs.group("rs")[-1]))
                rt = '{0:02b}'.format(int(regs.group("rt")[-1]))
                rd = '{0:02b}'.format(int(regs.group("rd")[-1]))
                # assemble the final machine code in binary
                m_code += rs + rt + rd + "000000"

            elif operation in mem:
                print_debug("Memory access instruction")
                info = re.search(r"(?P<rt>\$?r\d),? ?(?P<immediate>\d+)\((?P<rs>\$?r\d)\)",
                                 instr)
                if info is None:
                    raise Exception(f"Received wrongly formatted instruction: {instr}")
                print_debug("Regex caught:" + str(info.groups()))
                rs = '{0:02b}'.format(int(info.group("rs")[-1]))
                rt = '{0:02b}'.format(int(info.group("rt")[-1]))
                immediate = '{0:08b}'.format(int(info.group("immediate")))
                m_code += rs + rt + immediate
            elif operation in branch:
                print_debug("Branching instruction")
                info = re.search(r"(?P<rs>\$?r\d),? ?(?P<rt>\$?r\d),? ?(?P<immediate>\w+)",
                                 instr)
                if info is None:
                    raise Exception(f"Received wrongly formatted instruction: {instr}")
                print_debug("Regex caught:" + str(info.groups()))
                rs = '{0:02b}'.format(int(info.group("rs")[-1]))
                rt = '{0:02b}'.format(int(info.group("rt")[-1]))
                # resolve the label:
                try:
                    # if the label is a number, we just leave it as is
                    immediate = '{0:08b}'.format(int(info.group("immediate")))
                except ValueError:
                    # if it's letters, we resolve it
                    immediate = self._resolve_label(info.group("immediate"), True)
                m_code += rs + rt + immediate
            elif operation == "j":
                print_debug("Jumping instruction")
                info = re.search(r"j +(?P<label>\w+)", instr)
                if info is None:
                    raise Exception(f"Received wrongly formatted instruction: {instr}")
                print_debug("Regex caught:" + str(info.groups()))
                # resolve the label:
                try:
                    # if the label is a number, we just leave it as is
                    label = '{0:08b}'.format(int(info.group("label")))
                except ValueError:
                    # if it's letters, we resolve it
                    label = self._resolve_label(info.group("label"), False)
                m_code += "0000" + label
            else:
                m_code = ""
            # we now have the variable m_code which is the representation in
            # binary of the instruction
            return m_code


if __name__ == "__main__":
    #DEBUG = False
    assembler = Assembler()
    print("Translating")
    assembler.assemble_file("input.asm", "output.bin")
    print("Success")
