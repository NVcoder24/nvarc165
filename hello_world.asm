vars:
    text_screen_start 62916
data:
    string 12 "Hello, world#"
text:
    &loop
    # read char
    ST E &string
    ST D 2
    ADD E D E
    ADD E A E
    RD C E

    # write char to screen
    ST B $text_screen_start
    ADD B A B
    WR C B

    # i += 1
    ST C 1
    ADD A C A

    # if i < string length: jump
    ST C &loop
    ST E &string
    RDW D E
    CMP A D
    JL C

    # else: halt
    HLT