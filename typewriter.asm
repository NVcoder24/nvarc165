vars:
    text_screen_start 62916
    keyboard 62915
    backspace 157
    space 158
text:
    # A - index
    # B - char
    # C - prev char

    ST D &loop
    JMP D

    &normchar
    # write to screen B
    ST D $text_screen_start
    ADD D A D
    WR B D
    # i += 1
    ST D 1
    ADD A D A
    # cont
    ST D &cont
    JMP D

    &backspace
    # cont if i == 0
    ST D 0
    ST E &cont
    CMP A D
    JE E
    # i -= 1
    ST D 1
    SUB A D A
    # write to screen 0
    ST D $text_screen_start
    ADD D A D
    ST E 0
    WR E D
    # cont
    ST D &cont
    JMP D

    &space
    # write to screen 0
    ST D $text_screen_start
    ADD D A D
    ST E 0
    WR E D
    # i += 1
    ST D 1
    ADD A D A
    # cont
    ST D &cont
    JMP D

    &loop
    
    # read curr char
    ST D $keyboard
    RD B D

    # cmp char
    ST D &cont
    ST E 0
    CMP B C
    JE D
    CMP B E
    JE D

    # if backspace
    ST E $backspace
    CMP B E
    ST D &backspace
    JE D

    # if space
    ST E $space
    CMP B E
    ST D &space
    JE D

    # if normchar
    ST D &normchar
    JMP D

    &cont
    # set prev char
    CPY C B
    # loop
    ST D &loop
    JMP D