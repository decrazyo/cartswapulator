# Cartswapulator
Intercycle cartridge swapping TAS hardware and software.
This board is designed to replay intercycle cartridge swapping tool assessted speedruns like those created by [100th Coin](https://github.com/100thCoin/TriCNES/tree/main).
<!-- ![Cartswapulator](https://github.com/decrazyo/cartswapulator/blob/master/cartswapulator.jpg) -->
[Demo](https://www.youtube.com/watch?v=atbIClUt5tI)

## Hardware
Schematic and PCB can be found [here](https://oshwlab.com/decrazyo/cartswapulator).
This is prototype hardware and needs to be redesigned to use a Raspberry Pi Pico.

## Software
1) Install [MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) on a Raspberry Pi Pico.
2) Use [Thonny](https://thonny.org/) to upload `main.py` to the Raspberry Pi Pico.

## Usage
1) Connect the Cartswapulator to a top-loading NES or Famicom.
2) Power on the console.
3) Select a desired cartridge with buttons 1-5.
4) Reset the console to use the selected cartridge.
5) Enter TAS replay mode with button 6.
6) Reset the console to run the TAS.
