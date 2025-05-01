+++
title = "Baremetal Atmega Lesson 1: AVR toolchain setup and flash demo program"
date = 2024-09-24

[taxonomies]
tags = ["atmega32", "avr"]
+++

# Introduction

Hey, you must be fimilier with the classic Arduino Uno. This was my first ever microcontroller board and frankly the most used one too, I loved it. But first what is Arduino software stack, Arduino is a abstraction layer on top of the baremetal AVR utilities. This abstraction layer makes things so easy that even a highscool kid can learn microcontroller programming and make stuff out of it. This comes at a cost, you are restricted with the arduino framework, design pattern, the arduino IDE. To make things easy, arduino framework hides lot of features and configuration is provided in the MCU. If you want to be a good embedded engineer you cant stay with Arduino framework forever.

<!-- more -->

So now its time to level up. Lets understand how can we program our arduino board without the arduino software framework:
1. Writing raw C code with standered `int main()` function and compile ourself with the `avr-gcc` compiler.
2. Operating the peripherals by manupulating registers with bitwise operations.
3. Flasing the code using the `avrdude` utility.
4. (Optional) Get rid of the arduino bootloader and use external programmers.

## Toolchain installation
#### Linux
```sh
# Arch Linux
sudo pacman -S avr-gcc avr-libc avrdude avr-gdb avr-binutils

# Ubuntu
sudo apt-get install gcc-avr binutils-avr avr-libc gdb-avr avrdude

# Fedora
sudo dnf install avr-binutils avr-gcc avr-gcc-c++ avr-libc avrdude
```

#### Windows
For windows you can install [`WinAVR`](https://winavr.sourceforge.net/download.html) which is collection of tools for AVR.

#### MacOS
For mac checkout. [`hohmebrew-avr`](https://github.com/osx-cross/homebrew-avr)

<hr><br>

# Hello world
Now that you have the avr toolchain installed, its time to write a simple program, compile and flash on to the microcontroller. Create a new directory with a file `main.c` and write following code in it.

```c
int main(){
    while();
}
```
This is a very minimal code to be compiled and flashed on to the microcontroller. Lets compile it using `avr-gcc`. The arguments for `avr-gcc` is pretty much like standered `gcc` compiler, we just have to give extra flag `-mmcu` which tells the compiler what microcontroller we are using, in our case Arduino Uno has the `ATmega328P` mcu.
```sh
avr-gcc -mmcu=atmega328p main.c -o main.elf
```
The `elf` file is to be converted to a `hex` format which will be flashed on to the microcontroller. We will use the `avr-objcopy` utility which will converted the `elf` to `ihex`([Intex Hex](https://en.wikipedia.org/wiki/Intel_HEX)) format. The `-O` flag set the output format which is `ihex` in this case. `-R .eeprom` which remove the eeprom section from the final hex file.
```sh
avr-objcopy -O ihex -R .eeprom main.elf main.hex
```
## Uploading code
Now that we have the firmware to be flashed onto the microcontroller, we have two methods(There are more, but these two are most common).
### Arduino bootloader
The Arduino bootloader is a small program pre-installed on Arduino boards, allowing easy uploading of code via USB without requiring an external programmer, by handling serial communication and program flashing. To flash the code we will use the `avrdude` utility. To flash through serial we need to know what serial port the Arduino uno is connected, for that I have nice utility called [`lsserial`](https://github.com/anurag3301/my-linux-setup/blob/main/scripts/lsserial) which is a python script to print info about all the serial devices connected to the computer.
```sh
avrdude -F -c arduino -p atmega328p -P /dev/ttyACM0 -b 115200 -U flash:w:main.hex
```
Lets examine the avrdude flags:
+ `-F` This flag is to disable mcu signature matching, every avr board has some signature eg `Device signature = 1E 95 16 (ATmega328PB)` and if your Arduino board may be using some different varient of Atmega32 mcu, it will abort the upload. We will see how to correctly find which mcu we are using later.
+ `-c` This flas is used to specify what programmer we are using, in this case the arduino bootloader.
+ `-p` We specify what mcu we intend to flash, for now we are using the standered atmega328p for Arduino uno.
+ `-P` Here we specify the serial port Arduino is connected to, you can find that using the `lsserial` utility
+ `-b` The baud rate for the serial data line
+ `-U` This is used to carry out any kind of memory operation, here we specify the hex file to be flashed. We will discuss this in detail later.

### In-circuit serial programming(ICSP)
AVR ICSP (In-Circuit Serial Programming) is a method used to program AVR microcontrollers directly on a circuit without removing them. It uses the SPI interface (MISO, MOSI, SCK) to upload firmware, enabling faster and more efficient development and debugging.

**I highly recommend using external ICSP programmer.** Here are list of reasons which makes ICSP programmer better than arduino bootloader:
1. Allows programming of fuse bits.
2. Works without pre-loaded bootloader.
3. Faster than bootloader-based uploads.

There are many ICSP programmer, I am going to use the `USBasp` and you can get one too for under $10. Finally you can make use of the ICSP Pin header in arduino board.

{{image(src="/img/usbasp_direct.jpg", position="center")}}

> If you dont want to manual wiring, you can get a `AVR-ISP 10Pin to 6pin Adapter`
{{image(src="/img/usbasp_adapter.jpg", position="center", style="width:80%;")}}

Now lets finally upload the code, this is the command for that. The only change is the `-c` flag as we are using `usbasp`
```sh
avrdude -F -c usbasp -p atmega328p -U flash:w:main.hex
```
If you see output like this, congrats!!!! You just progrmmed your Arduino uno without the Arduino IDE.
```
Writing 166 bytes to flash
Writing | ################################################## | 100% 0.23 s 
Reading | ################################################## | 100% 0.13 s 
166 bytes of flash verified
```
