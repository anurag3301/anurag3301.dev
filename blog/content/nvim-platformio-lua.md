+++
title = "Intro to nvim-platformio.lua"
date = 2024-08-04

[taxonomies]
tags = ["nvim", "platformio"]
+++

{{ youtube(id="Jcqat7NhXrc", class="youtube") }}


If you work with microcontrollers you must have heard of `PlatformIO`. It is a tool which we can use to program and debug multiple families of microcontrollers in various frameworks with little to no manual setup work. PlatformIO takes care of installing the tool, setting up the project, build, upload and debug. PlatformIO comes with an extension for VS Code which wraps the underlaying `PlatformIO cli` tool and exposes a very nice interface to setup project and use other tools. But if you are a n/vim user like me, you only have the cli. I was fine with cli but I wanted that ease of use like VS Code extension so I made this neovim plugin called [nvim-platformio.lua](https://github.com/anurag3301/nvim-platformio.lua)

<!-- more -->

# Installation process

1. Install the PlatformIO core
```sh
curl -fsSL -o get-platformio.py https://raw.githubusercontent.com/platformio/platformio-core-installer/master/get-platformio.py
python3 get-platformio.py
```

2. Now check if you have PlatformIO cli ready to use
```sh
pio --version
```

3. Added [`anurag3301/nvim-platformio.lua`](https://github.com/anurag3301/nvim-platformio.lua) plugin and its dependencies for installation in your neovim package manager, here I have given example for `lazy.nvim`
```lua
return {
    "anurag3301/nvim-platformio.lua",
    dependencies = {
        { "akinsho/nvim-toggleterm.lua" },
        { "nvim-telescope/telescope.nvim" },
        { "nvim-lua/plenary.nvim" },
    },
}
```

And that's you have `nvim-platformio.lua` and `PlatformIO` ready to be used 🥳.

# Usage

### Setup a project
1. Create a new directory for the project and cd into it, in my case ill be using a ESP32.
```
mkdir esp_project
cd esp_project
```
2. Open neovim and run `:Pioinit`, this will open a telescope picker where you can fuzzy find and select the board you want to use. Then press enter.

{{ image(src="https://raw.githubusercontent.com/anurag3301/anurag3301.com/master/blog/static/img/pioinit.gif", position="left") }}

3. After selecting the board, you'll have option to select the desired framework such as `Arduino`, `ESP-IDF`, `STM32 Cube` etc. And press enter.
4. Now a toggleterm window will pop up which will run the `pio` project setup command and install any missing tools or dependencies.
5. Now you should have a `PlatformIO` project setup with `.ccls` file which will let your `LSP` make aware of the include path for the libraries.
6. Open the `src/main.c` file and write the code. In my case I wrote a simple `ESP-IDF` code which blink led and print to Serial line.
```c
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "esp_log.h"

#define BLINK_GPIO 12

void app_main() {
    gpio_pad_select_gpio(BLINK_GPIO);
    gpio_set_direction(BLINK_GPIO, GPIO_MODE_OUTPUT);
    while(1) {
        gpio_set_level(BLINK_GPIO, 1);
        ESP_LOGI("LED", "LED ON");
        vTaskDelay(1000 / portTICK_PERIOD_MS);
        gpio_set_level(BLINK_GPIO, 0);
        ESP_LOGI("LED", "LED OFF");
        vTaskDelay(1000 / portTICK_PERIOD_MS);
    }
}
```
7. Compile and flash the code by running `:Piorun`.
8. Open the serial monitor to see the output by running `:Piomon`

This was a brief introduction to `PlatformIO` and `nvim-platformio.lua`. 
>+ **Run `:help PlatformIO`** to see the detailed usage and option for each command.
>+ Checkout [platformio.ini](https://docs.platformio.org/en/latest/projectconf/sections/env/index.html) docs for project configuration.
>+ [PlatformIO cli](https://docs.platformio.org/en/latest/core/userguide/index.html) to extend usage.
