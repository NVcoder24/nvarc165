vars:
    gs_start 63036
    gs_max 2500
    max_color 256
text:
    &loop
    # A - index
    # B - color

    # write color to screen
    ST D $gs_start
    ADD D A D
    WR B D

    # i += 1
    ST C 1
    ADD A C A

    # calc new color
    ST C 1
    ADD B C B
    ST D &cont
    ST C $max_color
    CMP B C
    JL D
    ST B 0

    &cont

    # if i < string length: jump
    ST C &loop
    ST E $gs_max
    CMP A E
    JL C

    # else: halt
    HLT