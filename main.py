# GLOBAL
CPU_NAME = "NVARC_16_5"
SIM_VER = "1.0.0"

# LIBS
import dearpygui.dearpygui as dpg
import math
import time
from mybin import *
import charmap
from pynput import keyboard
import memory_con
from threading import Thread

# MEMORY
ram = memory_con.Ram(55415)
kb = memory_con.Keyboard()
text_screen = memory_con.TextScreen(20, 6)
graphics_screen = memory_con.GraphicScreen(50, 50)

memory = memory_con.MemoryController()
memory.map("ram", 0, 62914, ram)
memory.map("kb", 62915, 62915, kb)
memory.map("text_screen", 62916, 63035, text_screen)
memory.map("graphics_screen", 63036, 65535, graphics_screen)

# UTILS
def get_charmap_rev(val):
    if val in charmap.charmap_rev.keys():
        return charmap.charmap_rev[val]
    else:
        return " "

def get_charmap(val):
    if val in charmap.charmap.keys():
        return charmap.charmap[val]
    else:
        return 0

# DPG SETUP
dpg.create_context()

with dpg.font_registry():
    with dpg.font("notomono.ttf", 13, default_font=True, tag="Default font") as f:
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
    
dpg.bind_font("Default font")

dpg.create_viewport(title=f'CPUSIM GUI [CPU: {CPU_NAME}] [SIM VERSION: {SIM_VER}]', vsync=False)
dpg.setup_dearpygui()

# DPG MSG BOX
def show_info(title, message):
    with dpg.mutex():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        with dpg.window(label=title, modal=True) as modal_id:
            dpg.add_text(message)
    dpg.split_frame()
    width = dpg.get_item_width(modal_id)
    height = dpg.get_item_height(modal_id)
    dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])

# PREDEFINE VARS
memory_editor_x = 10
memory_editor_y = 20
memory_editor_scroll = 0
memory_editor_row_start = 20
memory_editor_cell_start_x = 100
memory_editor_cell_start_y = 70
memory_editor_cell_width = 30
memory_editor_cell_height = 20
memory_editor_max_addr = 2 ** 16 - 1
memory_editor_last_cell = (0, 0)
memory_editor_last_addr = 0
memory_editor_max_pages = 0

ram_dump_file = ""

clock_tps = 0
is_hlt = True
is_clock = False
last_instr = ""

reg_a = 0
reg_b = 0
reg_c = 0
reg_d = 0
reg_e = 0
reg_f = 0
reg_ip = 0
cpu_carry = 0
cpu_equal = 0
cpu_less = 0
cpu_greater = 0

text_monitor_x = 20
text_monitor_y = 6

keyboard_on = False
keyboard_current = []

def reg_write(n:int, v:int) -> None:
    global reg_a, reg_b, reg_c, reg_d, reg_e, reg_f, reg_ip
    if n == 1:
        reg_a = v
    if n == 2:
        reg_b = v
    if n == 3:
        reg_c = v
    if n == 4:
        reg_d = v
    if n == 5:
        reg_e = v
    if n == 6:
        reg_f = v
    if n == 7:
        reg_ip = v

def reg_read(n:int) -> int:
    if n == 1:
        return reg_a
    if n == 2:
        return reg_b
    if n == 3:
        return reg_c
    if n == 4:
        return reg_d
    if n == 5:
        return reg_e
    if n == 6:
        return reg_f
    if n == 7:
        return reg_ip
    return 0

# CPU
def clk():
    global is_hlt, last_instr, reg_a, reg_b, reg_c, reg_d, reg_e, reg_f, reg_ip, cpu_carry, cpu_equal, cpu_less, cpu_greater
    if not is_hlt:
        if memory.read(reg_ip) == 1:
            last_instr = "ADD"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            c = bin_to_dec(args_str[6:9])
            result, carry = bin_sum(reg_read(a), reg_read(b), 16)
            cpu_carry = carry
            reg_write(c, result)
            reg_ip += 3
        elif memory.read(reg_ip) == 2:
            last_instr = "SUB"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            c = bin_to_dec(args_str[6:9])
            result, carry = bin_sub(reg_read(a), reg_read(b), 16)
            cpu_carry = carry
            reg_write(c, result)
            reg_ip += 3
        elif memory.read(reg_ip) == 3:
            last_instr = "ST"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8) + bin_ext(memory.read(reg_ip + 3), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:19])
            reg_write(a, b)
            reg_ip += 4
        elif memory.read(reg_ip) == 4:
            last_instr = "CPY"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(a, reg_read(b))
            reg_ip += 2
        elif memory.read(reg_ip) == 5:
            last_instr = "RD"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(a, memory.read(reg_read(b)))
            reg_ip += 2
        elif memory.read(reg_ip) == 6:
            last_instr = "RDW"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(a, bin_to_dec(bin_8_ext(memory.read(reg_read(b))) + bin_8_ext(memory.read(reg_read(b) + 1))))
            reg_ip += 2
        elif memory.read(reg_ip) == 7:
            last_instr = "WR"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            memory.write(reg_read(b), bin_8_lim(reg_read(a)))
            reg_ip += 2
        elif memory.read(reg_ip) == 8:
            last_instr = "WRW"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            memory.write(reg_read(b), bin_16_lim(reg_read(a)))
            reg_ip += 2
        elif memory.read(reg_ip) == 9:
            last_instr = "SW"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            a_val = reg_read(a)
            b_val = reg_read(b)
            reg_write(a, b_val)
            reg_write(b, a_val)
            reg_ip += 2
        elif memory.read(reg_ip) == 10:
            last_instr = "NOT"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(b, bin_16_not(a))
            reg_ip += 2
        elif memory.read(reg_ip) == 11:
            last_instr = "AND"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            c = bin_to_dec(args_str[6:9])
            reg_write(c, bin_16_and(reg_read(a), reg_read(b)))
            reg_ip += 3
        elif memory.read(reg_ip) == 12:
            last_instr = "OR"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            c = bin_to_dec(args_str[6:9])
            reg_write(c, bin_16_or(reg_read(a), reg_read(b)))
            reg_ip += 3
        elif memory.read(reg_ip) == 13:
            last_instr = "XOR"
            args_str = bin_ext(memory.read(reg_ip + 1), 8) + bin_ext(memory.read(reg_ip + 2), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            c = bin_to_dec(args_str[6:9])
            reg_write(c, bin_16_xor(reg_read(a), reg_read(b)))
            reg_ip += 3
        elif memory.read(reg_ip) == 14:
            last_instr = "SHL"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(b, bin_16_shl(reg_read(a)))
            reg_ip += 2
        elif memory.read(reg_ip) == 15:
            last_instr = "SHR"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            reg_write(b, bin_16_shr(reg_read(a)))
            reg_ip += 2
        elif memory.read(reg_ip) == 16:
            last_instr = "JMP"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            reg_ip = reg_read(bin_to_dec(args_str[0:3]))
        elif memory.read(reg_ip) == 17:
            last_instr = "CMP"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            a = bin_to_dec(args_str[0:3])
            b = bin_to_dec(args_str[3:6])
            a_val = reg_read(a)
            b_val = reg_read(b)
            cpu_equal = int(a_val == b_val)
            cpu_less = int(a_val < b_val)
            cpu_greater = int(a_val > b_val)
            reg_ip += 2
        elif memory.read(reg_ip) == 18:
            last_instr = "JE"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            if cpu_equal: reg_ip = reg_read(bin_to_dec(args_str[0:3]))
            else: reg_ip += 2
        elif memory.read(reg_ip) == 19:
            last_instr = "JL"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            if cpu_less: reg_ip = reg_read(bin_to_dec(args_str[0:3]))
            else: reg_ip += 2
        elif memory.read(reg_ip) == 20:
            last_instr = "JG"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            if cpu_greater: reg_ip = reg_read(bin_to_dec(args_str[0:3]))
            else: reg_ip += 2
        elif memory.read(reg_ip) == 21:
            last_instr = "JC"
            args_str = bin_ext(memory.read(reg_ip + 1), 8)
            if cpu_carry: reg_ip = reg_read(bin_to_dec(args_str[0:3]))
            else: reg_ip += 2
        elif memory.read(reg_ip) == 22:
            last_instr = "NOC"
            cpu_carry = 0
            reg_ip += 1
        elif memory.read(reg_ip) == 0:
            last_instr = "NOP"
            reg_ip += 1
        elif memory.read(reg_ip) == 255:
            last_instr = "HLT"
            is_hlt = True
            reg_ip += 1
        else:
            last_instr = "Unknown"
            is_hlt = 1
            reg_ip += 1
        if reg_ip > 65535:
            reg_ip = 0
            is_hlt = 1

# RAM EDITOR THEMES
with dpg.theme() as memory_editor_instr_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button, (41, 72, 186), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (29, 50, 130), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (34, 58, 148), category=dpg.mvThemeCat_Core)

# MEMORY EDITOR FUNCTIONS
def memory_editor_update_scrollbar():
    if memory_editor_scroll == 0:
        value = 0
    else:
        value = -(memory_editor_scroll / memory_editor_max_pages)
    dpg.set_value("memory_editor_scroller", value)

def memory_editor_scroll_1():
    global memory_editor_scroll
    memory_editor_scroll += 1
    if memory_editor_scroll > memory_editor_max_pages:
        memory_editor_scroll = memory_editor_max_pages
    memory_editor_update_scrollbar()

def memory_editor_scroll_10():
    global memory_editor_scroll
    memory_editor_scroll += 10
    if memory_editor_scroll > memory_editor_max_pages:
        memory_editor_scroll = memory_editor_max_pages
    memory_editor_update_scrollbar()

def memory_editor_scroll_100():
    global memory_editor_scroll
    memory_editor_scroll += 100
    if memory_editor_scroll > memory_editor_max_pages:
        memory_editor_scroll = memory_editor_max_pages
    memory_editor_update_scrollbar()

def memory_editor_scroll__1():
    global memory_editor_scroll
    memory_editor_scroll -= 1
    if memory_editor_scroll < 0:
        memory_editor_scroll = 0
    memory_editor_update_scrollbar()

def memory_editor_scroll__10():
    global memory_editor_scroll
    memory_editor_scroll -= 10
    if memory_editor_scroll < 0:
        memory_editor_scroll = 0
    memory_editor_update_scrollbar()

def memory_editor_scroll__100():
    global memory_editor_scroll
    memory_editor_scroll -= 100
    if memory_editor_scroll < 0:
        memory_editor_scroll = 0
    memory_editor_update_scrollbar()

def memory_editor_get_addr_for(x, y):
    global_offset = memory_editor_x * memory_editor_scroll
    local_offset = memory_editor_x * y + x
    return global_offset + local_offset

def memory_editor_goto():
    global memory_editor_last_addr
    global memory_editor_scroll

    addr = dpg.get_value("memory_editor_goto")
    memory_editor_last_addr = addr
    memory_editor_scroll = int(addr / memory_editor_x)
    if memory_editor_scroll > memory_editor_max_pages:
        memory_editor_scroll = memory_editor_max_pages
    memory_editor_update_scrollbar()

def memory_editor_get_start_end_addr(y):
    global_offset = memory_editor_x * memory_editor_scroll
    start = global_offset + memory_editor_x * y
    end = global_offset + memory_editor_x * y + memory_editor_x - 1
    max_addr = memory_editor_max_addr - 1
    if end > max_addr:
        end = max_addr
    return start, end

def memory_editor_callback(sender:str):
    global memory_editor_last_cell
    global memory_editor_last_addr

    s1 = sender.split("[")
    s2 = s1[1].split("]")
    s3 = s2[0]
    nums_s = s3.split(";")
    nums = (int(nums_s[0]), int(nums_s[1]))
    x = nums[0]
    y = nums[1]
    addr = memory_editor_get_addr_for(x, y)

    memory_editor_last_cell = nums
    memory_editor_last_addr = addr

def memory_editor_update_info():
    dpg.set_value("memory_editor_info", f"Скролл: {memory_editor_scroll} | Выбранная ячейка: X{memory_editor_last_cell[0]} Y{memory_editor_last_cell[1]} | Адрес: {memory_editor_last_addr}")

def memory_editor_scroller_callback(sender):
    global memory_editor_scroll
    memory_editor_scroll = round(-dpg.get_value(sender) * memory_editor_max_pages)

def memory_editor_change_x(sender):
    global memory_editor_x
    memory_editor_clear_group()
    memory_editor_x = dpg.get_value(sender)
    memory_editor_construct_group()

def memory_editor_change_y(sender):
    global memory_editor_y
    memory_editor_clear_group()
    memory_editor_y = dpg.get_value(sender)
    memory_editor_construct_group()

def memory_editor_change_bank(sender):
    global memory_editor_curr_bank
    memory_editor_curr_bank = int(dpg.get_value(sender).split(" ")[1])

def memory_editor_set_ram_value():
    memory.write(memory_editor_last_addr, dpg.get_value("memory_editor_set_value"))

def memory_editor_construct_group():
    global memory_editor_x
    global memory_editor_y
    global memory_editor_max_pages
    global memory_editor_scroll

    start_x = memory_editor_cell_start_x
    start_y = memory_editor_cell_start_y

    for y in range(0, memory_editor_y):
        dpg.add_text("0-0", parent="memory_editor_group",
                        tag=f"memory_editor_row_{y}",
                        pos=(memory_editor_row_start, y * memory_editor_cell_height + start_y),
                        )
        for x in range(0, memory_editor_x):
            dpg.add_button(label="0", parent="memory_editor_group",
                        tag=f"memory_editor_cell_[{x};{y}]",
                        pos=(x * memory_editor_cell_width + start_x, y * memory_editor_cell_height + start_y),
                        width=memory_editor_cell_width - 1,
                        height=memory_editor_cell_height - 1,
                        callback=memory_editor_callback,
                        )
    
    memory_editor_max_pages = math.ceil(memory_editor_max_addr / memory_editor_x) - memory_editor_y
    memory_editor_scroll = 0
    dpg.set_value("memory_editor_scroller", 0)
    dpg.configure_item("memory_editor_scroller", height=memory_editor_y * memory_editor_cell_height, pos=(memory_editor_cell_width * memory_editor_x + start_x + 10, start_y))

def memory_editor_clear_group():
    global memory_editor_x
    global memory_editor_y

    for y in range(0, memory_editor_y):
        dpg.delete_item(f"memory_editor_row_{y}")
        for x in range(0, memory_editor_x):
            dpg.delete_item(f"memory_editor_cell_[{x};{y}]")

def memory_editor_set_data():
    for y in range(0, memory_editor_y):
        el1 = f"memory_editor_row_{y}"
        start, end = memory_editor_get_start_end_addr(y)
        try:
            dpg.set_value(el1, f"{start}-{end}")
        except Exception as e:
            #print(f"NOT FOUND ELEMENT {el1}")
            pass
        for x in range(0, memory_editor_x):
            el2 = f"memory_editor_cell_[{x};{y}]"
            try:
                addr = memory_editor_get_addr_for(x, y)
                dpg.configure_item(el2, label=str(memory.read(addr)))
                dpg.configure_item(el2, enabled=True)
                if addr == reg_ip:
                    dpg.bind_item_theme(el2, memory_editor_instr_theme)
                else:
                    dpg.bind_item_theme(el2, dpg.theme())
            except Exception as e:
                try:
                    dpg.configure_item(el2, label="")
                    dpg.configure_item(el2, enabled=False)
                except Exception as e:
                    #print(f"NOT FOUND ELEMENT {el2}")
                    pass

# RAM DUMP FUNCTIONS
def ram_dump_file_selected(sender, app_data):
    global ram_dump_file
    try:
        temp_path = app_data["selections"][list(app_data["selections"].keys())[0]]
        with open(temp_path, "r", encoding="UTF-8") as f:
            f.read()
        # всё получилось
        ram_dump_file = temp_path
        dpg.set_value("ram_dump_file_text", ram_dump_file)
    except Exception as e:
        show_info("Ошибка!", f"Не удалось открыть файл:\n{e}")

def ram_dump_select_file():
    dpg.show_item("ram_dump_file_dialog")

def ram_dump_load_def():
    try:
        with open(ram_dump_file, "r") as f:
            addr = 0
            for val in f.read().split(","):
                memory.memory_map["ram"][2].write(addr, int(val))
                addr += 1
                    
            show_info("Успех!", f"Дамп загружен!")
    except Exception as e:
        show_info("Ошибка!", f"Не удалось загрузить дамп:\n{e}")

def ram_dump_save_def():
    try:
        with open(ram_dump_file, "w") as f:
            f.write(",".join([ str(i) for i in memory.memory_map["ram"][2].ram ]))
            show_info("Успех!", f"Дамп сохранён!")
    except Exception as e:
        show_info("Ошибка!", f"Не удалось сохранить дамп:\n{e}")

# CPU CON FUNCTIONS
def tps_change_callback(sender):
    global clock_tps
    clock_tps = dpg.get_value(sender)

def hlt():
    global is_hlt
    is_hlt = True

def unhlt():
    global is_hlt
    is_hlt = False

def start_clock():
    global is_clock
    is_clock = True

def stop_clock():
    global is_clock
    is_clock = False

def set_a_reg():
    global reg_a
    reg_a = dpg.get_value("reg_a_input")

def set_b_reg():
    global reg_b
    reg_b = dpg.get_value("reg_b_input")

def set_c_reg():
    global reg_c
    reg_c = dpg.get_value("reg_c_input")

def set_d_reg():
    global reg_d
    reg_d = dpg.get_value("reg_d_input")

def set_e_reg():
    global reg_e
    reg_e = dpg.get_value("reg_e_input")

def set_f_reg():
    global reg_f
    reg_f = dpg.get_value("reg_f_input")

def set_ip_reg():
    global reg_ip
    reg_ip = dpg.get_value("reg_ip_input")

def set_carry_on():
    global cpu_carry
    cpu_carry = 1

def set_carry_off():
    global cpu_carry
    cpu_carry = 0

def set_equal_on():
    global cpu_equal
    cpu_equal = 1

def set_equal_off():
    global cpu_equal
    cpu_equal = 0

def set_less_on():
    global cpu_less
    cpu_less = 1

def set_less_off():
    global cpu_less
    cpu_less = 0

def set_greater_on():
    global cpu_greater
    cpu_greater = 1

def set_greater_off():
    global cpu_greater
    cpu_greater = 0

# TEXT MONITOR
def text_monitor_change_bank(sender):
    global text_monitor_bank
    text_monitor_bank = int(dpg.get_value(sender).split(" ")[1])

def text_monitor_change_x(sender):
    global text_monitor_x
    text_monitor_x = dpg.get_value(sender)

def text_monitor_change_y(sender):
    global text_monitor_y
    text_monitor_y = dpg.get_value(sender)

def text_monitor_update():
    s = ""
    for y in range(text_monitor_y):
        for x in range(text_monitor_x):
            #val = memory.memory_map["text_screen"][2].get_char_xy(x, y)
            val = memory.read(62916 + x + text_monitor_x * y)
            s += get_charmap_rev(val)
            #s += " "
        s += "\n"
    dpg.set_value("text_monitor_text", s)

# KEYBOARD
def keyboard_on_callback():
    global keyboard_on
    keyboard_on = True

def keyboard_off_callback():
    global keyboard_on
    keyboard_on = False

def keyboard_clear_callback():
    global keyboard_current
    keyboard_current = []

def keyboard_update():
    s = ""
    val = 0
    if keyboard_on and len(keyboard_current) > 0:
        s = keyboard_current[0]
        val = charmap.charmap[s]
    memory.memory_map["kb"][2].set_char(val)

    dpg.set_value("keyboard_text", f"""
Состояние: {"включена" if keyboard_on else "выключена"}
Текущие кнопки: [{ ",".join(keyboard_current) }] Ввод: {s}
    """)

def on_press(key):
    global keyboard_current
    if key == keyboard.Key.space:
        if "SPACE" not in keyboard_current:
            keyboard_current.append("SPACE")
    if key == keyboard.Key.backspace:
        if "BACKSPACE" not in keyboard_current:
            keyboard_current.append("BACKSPACE")
    else:
        try:
            char = key.char
            if char not in keyboard_current:
                keyboard_current.append(char)
        except Exception as e:
            pass

def on_release(key):
    global keyboard_current
    if key == keyboard.Key.space:
        if "SPACE" in keyboard_current:
            keyboard_current.remove("SPACE")
    if key == keyboard.Key.backspace:
        if "BACKSPACE" in keyboard_current:
            keyboard_current.remove("BACKSPACE")
    else:
        try:
            char = key.char
            if char in keyboard_current:
                keyboard_current.remove(char)
        except Exception as e:
            pass

# GRAPHICS SCREEN
def graphics_screen_update():
    new_texture_data = []
    """for y in range(0, 100):
        for i in range(graphics_screen_upscale):
            for x in range(0, 100):
                for j in range(graphics_screen_upscale):
                    _bin = dec_to_bin(memory.read(55536 + x + y * 100))
                    new_texture_data.append(bin_to_dec(_bin[0:3]) / 2 ** 3)
                    new_texture_data.append(bin_to_dec(_bin[3:6]) / 2 ** 3)
                    new_texture_data.append(bin_to_dec(_bin[6:8]) / 2 ** 2)
                    new_texture_data.append(1)"""
    for i in range(0, 50 * 50):
        _bin = dec_to_bin(memory.read(63036 + i))
        new_texture_data.append(bin_to_dec(_bin[0:3]) / 2 ** 3)
        new_texture_data.append(bin_to_dec(_bin[3:6]) / 2 ** 3)
        new_texture_data.append(bin_to_dec(_bin[6:8]) / 2 ** 2)
        new_texture_data.append(1)
    
    dpg.set_value("texture_tag", new_texture_data)

# CPU CON
with dpg.window(label="Управление процессором", no_close=True):
    dpg.add_text("Работа:")
    # Работа
    with dpg.group(horizontal=True):
        dpg.add_button(label="остановить (HLT)", callback=hlt)
        dpg.add_button(label="продолжить (un HLT)", callback=unhlt)
    
    # Автотактирование
    dpg.add_text("Тактирование:")
    dpg.add_slider_int(label="Тактов в секунду", max_value=500, callback=tps_change_callback)
    with dpg.group(horizontal=True):
        dpg.add_button(label="остановить авт.такт.", callback=stop_clock)
        dpg.add_button(label="запустить авт.такт.", callback=start_clock)
    dpg.add_button(label="Сделать такт", callback=clk)
    
    # Регистры
    dpg.add_text("Регистры:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_a_reg)
        dpg.add_input_int(label="A", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_a_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_b_reg)
        dpg.add_input_int(label="B", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_b_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_c_reg)
        dpg.add_input_int(label="C", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_c_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_d_reg)
        dpg.add_input_int(label="D", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_d_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_e_reg)
        dpg.add_input_int(label="E", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_e_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_f_reg)
        dpg.add_input_int(label="F", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_f_input", width=100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Применить", callback=set_ip_reg)
        dpg.add_input_int(label="IP", min_value=0, max_value=2 ** 16 - 1, min_clamped=True, max_clamped=True, tag="reg_ip_input", width=100)

    # Флаги
    dpg.add_text("Флаги:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установ. carry", callback=set_carry_on)
        dpg.add_button(label="Сбросить carry", callback=set_carry_off)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установ. equal", callback=set_equal_on)
        dpg.add_button(label="Сбросить equal", callback=set_equal_off)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установ. less", callback=set_less_on)
        dpg.add_button(label="Сбросить less", callback=set_less_off)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установ. greater", callback=set_greater_on)
        dpg.add_button(label="Сбросить greater", callback=set_greater_off)

# CPU STATUS
with dpg.window(label="Состояние процессора", no_close=True):
    dpg.add_text(tag="cpu_status")

# RAM EDITOR
with dpg.window(label="Редактор памяти", no_close=True):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Установить", callback=memory_editor_set_ram_value)
        dpg.add_input_int(label="Значение", min_value=0, max_value=255, min_clamped=True, max_clamped=True, tag="memory_editor_set_value", width=100)
    dpg.add_text("", tag="memory_editor_info")
    with dpg.group(horizontal=True):
        dpg.add_group(tag="memory_editor_group")
        dpg.add_slider_float(vertical=True, tag="memory_editor_scroller", min_value=-1, max_value=0, callback=memory_editor_scroller_callback)
    memory_editor_construct_group()
    dpg.add_text("Скролл:")
    with dpg.group(horizontal=True):
        dpg.add_button(label="+1", callback=memory_editor_scroll_1)
        dpg.add_button(label="+10", callback=memory_editor_scroll_10)
        dpg.add_button(label="+100", callback=memory_editor_scroll_100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="-1", callback=memory_editor_scroll__1)
        dpg.add_button(label="-10", callback=memory_editor_scroll__10)
        dpg.add_button(label="-100", callback=memory_editor_scroll__100)
    with dpg.group(horizontal=True):
        dpg.add_button(label="Перейти", callback=memory_editor_goto)
        dpg.add_input_int(label="Адрес", min_value=0, max_value=memory_editor_max_addr - 1, min_clamped=True, max_clamped=True, tag="memory_editor_goto", width=100)

# RAM DUMP
with dpg.file_dialog(
directory_selector=False, show=False, callback=ram_dump_file_selected,
tag="ram_dump_file_dialog",
width=700 ,height=400, default_path="."):
    dpg.add_file_extension(".*")

with dpg.window(label="Дамп ОЗУ", no_close=True):
    dpg.add_text("Файл")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Выбрать", callback=ram_dump_select_file)
        dpg.add_text("Файл не выбран", tag="ram_dump_file_text")
    with dpg.group(horizontal=True):
        dpg.add_button(label="Загрузить [текст]", callback=ram_dump_load_def)
        dpg.add_button(label="Сохранить [текст]", callback=ram_dump_save_def)

# TEXT SCREEN
with dpg.window(label="текстовый экран", no_close=True):
    dpg.add_text("", tag="text_monitor_text")

# KEYBOARD
with dpg.window(label="Клавиатура", no_close=True):
    with dpg.group(horizontal=True):
        dpg.add_button(label="Включить", callback=keyboard_on_callback)
        dpg.add_button(label="Выключить", callback=keyboard_off_callback)
    dpg.add_button(label="СБРОС", callback=keyboard_clear_callback)
    dpg.add_text("", tag="keyboard_text")

graphics_screen_upscale = 1

texture_data = []
"""for y in range(0, 100):
    for i in range(graphics_screen_upscale):
        for x in range(0, 100):
            for j in range(graphics_screen_upscale):
                texture_data.append(0)
                texture_data.append(0)
                texture_data.append(0)
                texture_data.append(255 / 255)"""
for i in range(50 * 50):
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(255 / 255)

# GRAPHICS SCREEN
with dpg.texture_registry(show=False):
    dpg.add_dynamic_texture(width=50 * graphics_screen_upscale, height=50 * graphics_screen_upscale, default_value=texture_data, tag="texture_tag")

with dpg.window(label="Графический экран", no_close=True):
    dpg.add_image("texture_tag")

# SHOW STUFF
dpg.show_viewport()

# KEYBOARD LISTENER
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()

def cpu_thread():
    global is_clock, clock_tps, last_time
    # CPU CLK
    while dpg.is_dearpygui_running():
        try:
            if is_clock:
                if clock_tps and time.time() > last_time + (1 / clock_tps):
                    clk()
                    last_time = time.time()
        except Exception as e:
            print(e)

Thread(target=cpu_thread).start()

# MAIN CYCLE
last_time = 0
while dpg.is_dearpygui_running():
    """# CPU CLK
    if is_clock:
        if clock_tps and time.time() > last_time + (1 / clock_tps):
            clk()
            last_time = time.time()"""
    
    # CPU STATUS
    dpg.set_value("cpu_status", f"""Состояние: {"ОСТАНОВЛЕН" if is_hlt else "РАБОТАЕТ"}
Автотактирование: {clock_tps} Т/С - {"работает" if is_clock else "остановлен"}
==========
Последняя инструкция: {last_instr}
==========
Регистр A: {reg_a}
Регистр B: {reg_b}
Регистр C: {reg_c}
Регистр D: {reg_d}
Регистр E: {reg_e}
Регистр F: {reg_f}
Регистр IP: {reg_ip}
==========
Флаг carry: {cpu_carry}
Флаг equal: {cpu_equal}
Флаг less: {cpu_less}
Флаг greater: {cpu_greater}
""")
    # RAM EDITOR UPDATE
    memory_editor_set_data()
    memory_editor_update_info()

    # TEXT MONITOR UPDATE
    text_monitor_update()

    # KEYBOARD UPDATE
    keyboard_update()

    # UPDATE GRAPHICS SCREEN
    graphics_screen_update()

    # RENDER WINDOWS
    dpg.render_dearpygui_frame()

# ENDs
dpg.destroy_context()
