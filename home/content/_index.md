+++
insert_anchor_links = "right"
title = ""
+++

{% crt() %}
```
                                            __________ ____ ___
         ____ _____  __  ___________ _____ |__  /__  // __ <  /
        / __ `/ __ \/ / / / ___/ __ `/ __ `//_ < /_ </ / / / / 
       / /_/ / / / / /_/ / /  / /_/ / /_/ /__/ /__/ / /_/ / /  
       \__,_/_/ /_/\__,_/_/   \__,_/\__, /____/____/\____/_/   
                                   /____/                      
```
{% end %}

<table>
    <tr>
        <th><a target=_blank href="https://github.com/anurag3301">
            {{nerdicon(color="white", class="nf-fa-github")}} Github</a>
        </th>
        <th><a target=_blank href="https://www.linkedin.com/in/anurag3301/">
            {{nerdicon(color="#0a66c2", class="nf-fa-linkedin_square")}} LinkedIn</a>
        </th>
        <th><a target=_blank href="https://www.youtube.com/@anurag3301YT">
            {{nerdicon(color="#ff4545", class="nf-fa-youtube")}} Youtube</a>
        </th>
        <th><a target=_blank href="/resume">
            {{nerdicon(color="white", class="nf-fa-file_lines")}} Resume</a>
        </th>
        <th><a target=_blank href="/blog">
            {{nerdicon(color="white", class="nf-fa-newspaper_o")}} Blog</a>
        </th>
    </tr>
</table>

<br>

Embedded Linux and Platform Engineer focused on low-level systems development, board bring-up, and custom Linux distributions for embedded hardware. I build complete BSPs using Yocto, work with U-Boot, Linux kernel, and device trees across ARM Cortex-A and Cortex-M platforms. My goal is to understand how software interacts with hardware at every layer, from boot ROM to userspace.

Currently working on NXP i.MX6Q at [SightForge Technologies](https://sightforge.co). I run Arch Linux, edit in Neovim, and tile with DWM.

Check out my blog [here](https://anurag3301.dev/blog).


# Skills

| | |
|:---|:---|
| **Languages** | C (C89/C90), C++ (C++17), Python, Bash, Lua |
| **Embedded Linux** | Yocto, Linux Kernel, Device Tree, U-Boot, Buildroot, Cross Compilation, GStreamer, V4L2 |
| **MCU Development** | Bare Metal, FreeRTOS, OpenOCD, SWD/JTAG, PlatformIO |
| **Application Processors** | NXP i.MX6, TI DM3730, TI AM67A, Raspberry Pi |
| **Microcontrollers** | STM32, RP2040, RP2350, AVR |
| **Interfaces** | I2C, SPI, UART, MMC, Ethernet, CSI, LCD/DSS |
| **Tools** | GDB, Git, Valgrind, Perf/Ftrace, OpenOCD |
| **Networking** | lwIP, MQTT, TCP/IP |

# Projects

## nvim-platformio.lua

> Check the project {{anchor(url="https://github.com/anurag3301/nvim-platformio.lua", title="Link")}} · ⭐ 199 · 🍴 19 · 👥 9 contributors

A Neovim plugin that brings a VS Code-like PlatformIO workflow to Neovim. Supports build, upload, serial monitor, project init, library search, and full keybind customisation via which-key. Uses Telescope for library and board search. One of the most active PlatformIO integrations for Neovim.

{{youtube(id="Jcqat7NhXrc")}}

## TI DM3730 EVK BSP

> Check the project {{anchor(url="https://github.com/TI-DM3730-EVK-BSP", title="Link")}}

Modern Yocto-based BSP for the TI DM3730 (Cortex-A8), replacing the legacy vendor software stack. Ported kernel and U-Boot with updated device tree support; enabled NFS, NAND, and MMC boot along with I2C, SPI, UART, and Ethernet interfaces.

## STM32 PIO Libraries

> Check the project {{anchor(url="https://github.com/STM32-pio-libs", title="Link")}}

A GitHub organisation publishing hardware-agnostic STM32CubeHAL drivers to the {{anchor(url="https://registry.platformio.org/search?q=owner%3Aanurag3301", title="PlatformIO registry", code=true)}}, filling gaps where Arduino libraries exist but STM32 HAL support does not. Pluggable I2C/SPI transport callbacks throughout.

- {{anchor(url="https://github.com/STM32-pio-libs/W25Q64-flash", title="W25Q64-flash")}}: W25Q64 8 MB SPI NOR flash driver with callback-based transport.
- {{anchor(url="https://github.com/STM32-pio-libs/W25Q64-lfs", title="W25Q64-lfs")}}: LittleFS block device adapter for W25Q64-flash, no heap allocation.
- {{anchor(url="https://github.com/STM32-pio-libs/littlefs", title="littlefs")}}: LittleFS v2.11.3 repackaged as a PlatformIO library.
- {{anchor(url="https://github.com/STM32-pio-libs/SSD1306", title="SSD1306")}}: SSD1306 OLED driver over I2C or SPI with full and partial-region updates.
- {{anchor(url="https://github.com/STM32-pio-libs/gfx-mono", title="gfx-mono")}}: Monochrome graphics library with bitmap drawing and scalable glyphs.
- {{anchor(url="https://github.com/STM32-pio-libs/I2C-LCD", title="I2C-LCD")}}: HD44780 LCD via PCF8574 I2C backpack.
- {{anchor(url="https://github.com/STM32-pio-libs/DS1302-RTC", title="DS1302-RTC")}}: GPIO bit-bang driver for DS1302 RTC with 12/24-hour mode and battery-backed RAM.
- {{anchor(url="https://github.com/STM32-pio-libs/NEO-6M", title="NEO-6M")}}: NMEA parser and UART helper for u-blox NEO-6M GPS.
- {{anchor(url="https://github.com/STM32-pio-libs/HC-SR04", title="HC-SR04")}}: Ultrasonic distance sensor driver.
- {{anchor(url="https://github.com/STM32-pio-libs/stm32-Delay", title="stm32-Delay")}}: Microsecond and millisecond delay helpers for STM32Cube HAL.
- {{anchor(url="https://github.com/STM32-pio-libs/stm32f411-blackpill-base", title="stm32f411-blackpill-base")}}: Minimal PlatformIO template for STM32F411CE BlackPill.
- {{anchor(url="https://github.com/STM32-pio-libs/F411-W25Q64-lfs-cli", title="F411-W25Q64-lfs-cli")}}: Interactive LittleFS shell over UART backed by W25Q64 flash, with `pcfstool` for host-side file transfer.

## stm32f401-rtos + stm32f401-cpp-hal

> {{anchor(url="https://github.com/anurag3301/stm32f401-rtos", title="stm32f401-rtos")}} · {{anchor(url="https://github.com/anurag3301/stm32f401-cpp-hal", title="stm32f401-cpp-hal")}}

FreeRTOS on the STM32F401 with a custom linker script and bare-metal startup — no STM32Cube, no vendor HAL, just CMSIS headers and the FreeRTOS kernel (CM4F port, heap_4). The companion `stm32f401-cpp-hal` library provides C++20 peripheral drivers (GPIO, UART, EXTI) built directly on CMSIS. Each peripheral is a class; construction configures the hardware and enables the clock. Register fields are scoped enums for compile-time type checking. Copy is deleted, move is implemented.

## my-linux-setup

> Check the project {{anchor(url="https://github.com/anurag3301/my-linux-setup", title="Link")}} · ⭐ 68

Arch Linux dotfiles and install scripts. DWM + Neovim + Kitty.
