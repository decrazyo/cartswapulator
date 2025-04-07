from machine import Pin, mem32
import rp2
import time


@rp2.asm_pio(
    sideset_init=(
        rp2.PIO.OUT_HIGH, # Super Mario Bros.
        rp2.PIO.OUT_HIGH, # Dash Galaxy
        rp2.PIO.OUT_HIGH, # Kung Fu
        rp2.PIO.OUT_HIGH, # Pipe Dream
        rp2.PIO.OUT_LOW,  # Super Mario Bros. 3 (active)
    ),
)
def smb3tas():
    # Get the NES's clock cycle duration.
    # This serves as a timeout value to detect a console reset.
    pull().side(0b01111)
    set(y, 6).side(0b01111)

    # Watch the clock signal (M2) from the NES.
    # Set a timeout value as long as M2 is high.
    label("set_timeout")
    mov(x, osr).side(0b01111)
    label("poll_loop")
    jmp(pin, "set_timeout").side(0b01111)
    # Decrement our timeout value as long as M2 is low.
    jmp(x_dec, "poll_loop").side(0b01111)

    # If we reached this point then the M2 stayed low for longer than 1 clock cycle.
    # This suggests that the reset button is being pressed.
    # When M2 goes high again then reset was released.

    # Super Mario Bros. 3
    label("tas_start")
    wait(1, pin, 0).side(0b01111)
    wait(0, pin, 0).side(0b01111)
    jmp(y_dec, "tas_start").side(0b01111)
    # Super Mario Bros.
    wait(1, pin, 0).side(0b11110)
    wait(0, pin, 0).side(0b11110)
    # Dash Galaxy
    wait(1, pin, 0).side(0b11101)
    wait(0, pin, 0).side(0b11101)
    # Kung Fu
    wait(1, pin, 0).side(0b11011)
    wait(0, pin, 0).side(0b11011)
    # Pipe Dream
    wait(1, pin, 0).side(0b10111)
    wait(0, pin, 0).side(0b10111)
    # Super Mario Bros. 3
    label("tas_done")
    jmp("tas_done").side(0b01111)


# Take an iterable of integers and returns a single integer as a result.
# Each integer in the iterable represents the position of a "1" bit in the result.
def bitmask(iterable, init=0):
    mask = init
    for i in iterable:
        mask |= (1<<i)
    return mask


# Define GPIO memory map.
SIO_BASE = 0xD0000000
GPIO_IN  = SIO_BASE + 0x04
GPIO_OUT = SIO_BASE + 0x10

# Define our input key pins.
KEY_GPIO_START = 0
KEY_GPIO_COUNT = 6
key_gpios = list(range(KEY_GPIO_START, KEY_GPIO_START+KEY_GPIO_COUNT))
key_pins = list(Pin(i, Pin.IN, Pin.PULL_UP) for i in key_gpios)
key_mask = bitmask(key_gpios)

# Define out cartridge select pins.
CART_GPIO_START = KEY_GPIO_START + KEY_GPIO_COUNT
CART_GPIO_COUNT = 5
cart_gpios = list(range(CART_GPIO_START, CART_GPIO_START+CART_GPIO_COUNT))
cart_pins = list(Pin(i, Pin.OUT) for i in cart_gpios)
cart_mask = bitmask(cart_gpios)

# Define the clock signal (M2) input pin.
clock_gpio = CART_GPIO_START + CART_GPIO_COUNT
clock_pin = Pin(clock_gpio, Pin.IN, Pin.PULL_DOWN)

# Select the last cartridge at boot.
mem32[GPIO_OUT] = cart_mask ^ (1<<cart_gpios[-1])

# We'll initialize the TAS state machine once we actually need it.
tas_sm = None

while True:
    # Read the state of all input keys.
    keys = mem32[GPIO_IN] & key_mask

    # Handle inputs.
    if keys == key_mask:
        # No keys pressed.
        # Nothing to do.
        continue
    elif bin(keys).count('1') < len(key_gpios) - 1:
        # 2 or more keys pressed at the same time.
        # The user probably didn't mean to do that.
        # Do nothing instead.
        continue
    elif not (keys & (1<<key_gpios[-1])):
        # The last key (the one not associated with a single cartridge) was pressed.
        # Initialize the TAS state machine.
        tas_sm = rp2.StateMachine(
            0,
            smb3tas,
            in_base=clock_pin,
            jmp_pin=clock_pin,
            sideset_base=cart_pins[0]
        )
        # Start the state machine.
        tas_sm.active(1)
        # Tell the state machine how long an NES clock cycle is.
        tas_sm.put(100)
        # The state machine is now monitoring the the NES's clock signal (M2).
        # The user can now press the console's reset button to run the TAS.
    elif tas_sm is None:
        # A cartridge selection key was pressed and we aren't running the TAS yet.
        # Select the cartridge associated with the key that was pressed.
        mem32[GPIO_OUT] = ((keys << len(key_gpios)) & cart_mask)
    else:
        # A cartridge selection key was pressed but we are already running the TAS.
        # idk how to regain control of the cartridge select pins.
        # The console needs to be power cycled before we can select a cartridge.
        pass
