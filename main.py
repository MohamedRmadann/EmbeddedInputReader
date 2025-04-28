from machine import Pin, ADC, Timer
from utime import sleep_ms, ticks_ms, ticks_diff
import math

SEVEN_SEGMENT_START_PIN = 0
DISPLAY_COUNT_START_PIN = 8
DISPLAY_COUNT = 4
DECIMAL_PRECISION = 3
segment_pins = []
display_pins = []
display_value = 0.0
current_display_index = DISPLAY_COUNT - 1

ADC_RESOLUTION = float((math.pow(2, 16) - 1))
Input_pin = ADC(26)

button = Pin(16, Pin.IN, Pin.PULL_UP)

digit_list_hex = [
    0x40, 0x79, 0x24, 0x30, 0x19, 0x12, 0x02, 0x78, 0x00, 0x10, 
    0x08, 0x03, 0x46, 0x21, 0x06, 0x0E, 0x7F
]

def setup():
    global segment_pins, display_pins

    for i in range(4):
        pin = Pin(11 - i, Pin.OUT)
        pin.value(0)
        display_pins.append(pin)

    for i in range(SEVEN_SEGMENT_START_PIN, SEVEN_SEGMENT_START_PIN + 8):
        pin = Pin(i, Pin.OUT)
        pin.value(1)
        segment_pins.append(pin)

def scan_display(display_value):
    global current_display_index

    # Convert the display_value to a string with the specified precision
    value_str = f"{display_value:.{DECIMAL_PRECISION}f}"

    # Calculate the length of the string without the decimal point
    str_len = len(value_str.replace('.', ''))
    value_str=value_str.replace('.', '')
    # Ensure the current_display_index is within the range
    if current_display_index >= str_len:
        current_display_index = str_len - 1

    # Extract the character corresponding to the current display index
    char = value_str[current_display_index]

    # Determine if the decimal point should be enabled for this digit
    #dp_enable = (current_display_index + 1 < len(value_str)) and (value_str[current_display_index + 1] == '.')
    if current_display_index == 0:
        dp_enable = True
    else:
     dp_enable = False
    # Convert the character to a digit
    if char.isdigit():
        digit = int(char)
    else:
        digit = 1

    # Display the digit
    display_digit(digit, current_display_index, dp_enable)

    # Move to the next display
    current_display_index -= 1
    if current_display_index < 0:
        current_display_index = DISPLAY_COUNT - 1

def display_digit(digit_value, digit_index, dp_enable=False):
    # Ensure the value is valid
    if digit_value < 0 or digit_value >= len(digit_list_hex):
        return

    # Deselect all display select pins
    for pin in display_pins:
        pin.value(0)

    # Set the segments according to the digit value
    mask = digit_list_hex[digit_value]
    for i in range(7):  # 7 segments from A to G
        segment_pins[i].value((mask >> i) & 1)

    # Set the DP if it's enabled
    segment_pins[7].value(1 if not dp_enable else 0)

    # If digit_index is -1, activate all display select pins
    if digit_index == -1:
        for pin in display_pins:
            pin.value(1)
    # Otherwise, ensure the index is valid and activate the relevant display select pin
    elif 0 <= digit_index < DISPLAY_COUNT:
        display_pins[digit_index].value(1)

def Button_handler(Pin):
    global display_value
    digital_reading = Input_pin.read_u16()
    Analog_reading = float(digital_reading / ADC_RESOLUTION * 3.3)
    # print(Analog_reading)
    display_value = Analog_reading

def main():
    button.irq(
        trigger=Pin.IRQ_FALLING,
        handler=Button_handler
    )
    while True:
        scan_display(display_value)
        print(display_value)
        sleep_ms(10)

if __name__ == '__main__':
    setup()
    main()