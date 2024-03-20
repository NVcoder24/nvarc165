from charmap import *
from mybin import *
import sys

def error(line, description):
    print(f"error in: {line} - {description}")
    quit()

var_lines = []
data_lines = []
text_lines = []

filename = "test.asm"
output = "test.txt"

filename = sys.argv[1]
output = sys.argv[2]

content = []
with open(filename, "r") as f:
    content = f.readlines()

content = [ i.strip() for i in content ]

_content = []
for i in content:
    if i != "": _content.append(i)
content = _content

mode = ""
for i in content:
    if i.lower() == "vars:":
        mode = "vars"
        continue
    elif i.lower() == "data:":
        mode = "data"
        continue
    elif i.lower() == "text:":
        mode = "text"
        continue
    
    if mode == "vars":
        var_lines.append(i)
    elif mode == "data":
        data_lines.append(i)
    elif mode == "text":
        text_lines.append(i)
    else:
        error(i, "no mode")


_text_lines = []
for i in text_lines:
    line = ""
    for j in i:
        if j == "#":
            break
        line += j
    if line != "":
        _text_lines.append(line)
text_lines = _text_lines

_var_lines = []
for i in var_lines:
    line = ""
    for j in i:
        if j == "#":
            break
        line += j
    if line != "":
        _var_lines.append(line)
var_lines = _var_lines

var = {}
for i in var_lines:
    try:
        var[i.split(" ")[0]] = int(i.split(" ")[1])
    except Exception as e:
        error(i, "failed to parse var")

_data_lines = []
for i in data_lines:
    line = ""
    is_string = False
    for j in i:
        if j == '"':
            is_string = not is_string
        if j == "#" and not is_string:
            break
        line += j
    if line != "":
        _data_lines.append(line)
data_lines = _data_lines

all_size = 0
text_size = 0
data_size = 0

pointers = {}

instr_to_size = {
    "add": 3,
    "sub": 3,
    "st": 4,
    "cpy": 2,
    "rd": 2,
    "rdw": 2,
    "wr": 2,
    "wrw": 2,
    "sw": 2,
    "not": 2,
    "and": 3,
    "or": 3,
    "xor": 3,
    "shl": 2,
    "shr": 2,
    "jmp": 2,
    "cmp": 2,
    "je": 2,
    "jl": 2,
    "jg": 2,
    "jc": 2,
    "noc": 1,
    "nop": 1,
    "hlt": 1,
}

_text_lines = []
for i in text_lines:
    if i[0] == "&":
        pointers[i[1:]] = text_size
    else:
        instr = i.lower().split(" ")[0]
        try:
            text_size += instr_to_size[instr]
        except Exception as e:
            error(i, "unknown instr")
        _text_lines.append(i)
text_lines = _text_lines

all_size += text_size

data_code = []

for i in data_lines:
    try:
        if '"' in i:
            a = i.split(" ")
            pointers[a[0]] = all_size + data_size
            data_size += 2 + int(a[1])
            s = " ".join(a[2:])[1:-1]
            s_data = []
            for j in s:
                try:
                    s_data.append(charmap[j])
                except Exception as e:
                    s_data.append(0)
            data_code += list(bin_16_8_split(int(a[1]))) + s_data
        else:
            a = i.split(" ")
            pointers[a[0]] = all_size + data_size
            data_size += 2
            data_code += list(bin_16_8_split(int(a[1])))
    except Exception as e:
        error(i, "failed to parse data")

text_code = []

reg_to_num = {
    "a": 1,
    "b": 2,
    "c": 3,
    "d": 4,
    "e": 5,
    "f": 6,
    "ip": 7,
}

for i in text_lines:
    instr = i.lower().split(" ")[0]
    code = []
    try:
        if instr == "add":
            a = i.lower().split(" ")
            s = bin_8_ext(1) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + bin_ext(reg_to_num[a[3]], 3) + "0000000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
        elif instr == "sub":
            a = i.lower().split(" ")
            s = bin_8_ext(2) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + bin_ext(reg_to_num[a[3]], 3) + "0000000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
        elif instr == "st":
            a = i.split(" ")
            s = bin_8_ext(3) + bin_ext(reg_to_num[a[1].lower()], 3)
            if a[2][0] == "$":
                s += bin_16_ext(var[a[2][1:]])
            elif a[2][0] == "&":
                s += bin_16_ext(pointers[a[2][1:]])
            else:
                s += bin_16_ext(int(a[2]))
            s += "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
            code.append(bin_to_dec(s[24:32]))
        elif instr == "cpy":
            a = i.lower().split(" ")
            s = bin_8_ext(4) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "rd":
            a = i.lower().split(" ")
            s = bin_8_ext(5) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "rdw":
            a = i.lower().split(" ")
            s = bin_8_ext(6) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "wr":
            a = i.lower().split(" ")
            s = bin_8_ext(7) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "wrw":
            a = i.lower().split(" ")
            s = bin_8_ext(8) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "sw":
            a = i.lower().split(" ")
            s = bin_8_ext(9) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "not":
            a = i.lower().split(" ")
            s = bin_8_ext(10) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "and":
            a = i.lower().split(" ")
            s = bin_8_ext(11) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + bin_ext(reg_to_num[a[3]], 3) + "0000000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
        elif instr == "or":
            a = i.lower().split(" ")
            s = bin_8_ext(12) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + bin_ext(reg_to_num[a[3]], 3) + "0000000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
        elif instr == "xor":
            a = i.lower().split(" ")
            s = bin_8_ext(13) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + bin_ext(reg_to_num[a[3]], 3) + "0000000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
            code.append(bin_to_dec(s[16:24]))
        elif instr == "shl":
            a = i.lower().split(" ")
            s = bin_8_ext(14) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "shr":
            a = i.lower().split(" ")
            s = bin_8_ext(15) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "jmp":
            a = i.lower().split(" ")
            s = bin_8_ext(16) + bin_ext(reg_to_num[a[1]], 3) + "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "cmp":
            a = i.lower().split(" ")
            s = bin_8_ext(17) + bin_ext(reg_to_num[a[1]], 3) + bin_ext(reg_to_num[a[2]], 3) + "00"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "je":
            a = i.lower().split(" ")
            s = bin_8_ext(18) + bin_ext(reg_to_num[a[1]], 3) + "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "jl":
            a = i.lower().split(" ")
            s = bin_8_ext(19) + bin_ext(reg_to_num[a[1]], 3) + "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "jg":
            a = i.lower().split(" ")
            s = bin_8_ext(20) + bin_ext(reg_to_num[a[1]], 3) + "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "jc":
            a = i.lower().split(" ")
            s = bin_8_ext(21) + bin_ext(reg_to_num[a[1]], 3) + "00000"
            code.append(bin_to_dec(s[0:8]))
            code.append(bin_to_dec(s[8:16]))
        elif instr == "noc":
            s = bin_8_ext(22)
            code.append(bin_to_dec(s))
        elif instr == "nop":
            s = bin_8_ext(0)
            code.append(bin_to_dec(s))
        elif instr == "hlt":
            s = bin_8_ext(255)
            code.append(bin_to_dec(s))
        else:
            error(i, "unknown instr")
    except Exception as e:
        error(i, f"parsing error {e}")
    text_code += code

code = text_code + data_code

print(f"""ASSEMBLED
size: {all_size} bytes""")

with open(output, "w") as f:
    f.write(",".join([ str(i) for i in code ]))