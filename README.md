# keyboard-analysis-tools

This repository contains tools for caputuring and analyzing keyboard data. This data is used to enhance custom QMK keyboard layouts such as the [ergodox-ez][ergodox-ez] and [planck][planck].

[ergodox-ez]: https://github.com/joshuabragge/ergodox
[planck]: https://github.com/joshuabragge/planck/

## Table of Contents

* [Capturing Data](#Capturing-Data)
    - [Keyboard Logging](#keyboard-logger)
        - [Parameters](#parameters)
    - [Keyboard Configuration](#Keyboard-Configuration)
    - [Privacy and Security Concerns](#data-leakage)
* [Analyzing Data](#Analyzing-Data)
* [Todo](#todo)

## Capturing Data
### Keyboard Logging

keyboard_logger.py was built because [existing HID listen solutions required administrative permissions][existing-solutions]. Admin permissions can be circumvented in Windows with pywinusb.

At a high level, this script hooks onto an HID device, begins listening to the device and stores the messages it receives to a file. More specifically, it records the location of the keys that were pressed (not the configured value of the keys pressed) by QMK keyboards. For example, with one keystroke of "m" we are recording the  down press `KL|01|09|1|BASE` and release of the key `KL|01|09|0|BASE`.

The data structure is a result of how one configures their keyboard to emit data on keystrokes [(see keyboard configuration)](#keyboard-configuration). I have found the following structure to be acceptable. 

```
Device | Key row | Key column | Key pressed down | Layer
KL|03|03|1|BASE
KL|01|09|1|BASE
KL|02|02|1|BASE
KL|03|09|0|BASE
KL|02|10|1|BASE
KL|01|09|0|BASE
```

#### Parameters

`--input-lag=0.05` poll rate in seconds to check for keypress changes

`--obfuscate=True` randomizes keystroke order before saving to file

`--keystroke-log=100` number of keystrokes before logging to file

### Keyboard Configuration
QMK keyboards need to be configured to send keystrokes in an infomative way. This is done by adjusting your keymap.c and rules.mk.

##### rules.mk
```
CONSOLE_ENABLE = yes
```
##### keymap.c
```c
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    uint8_t layer = biton32(layer_state);
    if (log_enable) {
      uprintf ("KL|%02d|%02d|%d|%s\n", record->event.key.col, record->event.key.row, record->event.pressed, "BASE");
```
Best practice is to [add a leader key to disable logging at the keyboard level][log-leader]. Being able to disable logging without turning off the logging script is preferred when dealing with sensitive information. As mentioned earlier, QMK is unable to return information on the value of the key which was pressed. We can however, return the location of the key that was pressed (row 1 column 10, for example) and then map that location to the corresponding value in keymap.c.

[existing-solutions]: https://www.pjrc.com/teensy/hid_listen.html
[log-leader]: https://github.com/joshuabragge/ergodox/blob/325429ef3de1e1997918541ce7b1e3b89b066b6b/keymap.c#L564

### Data Leakage Concerns Regarding Logged Data

Keystroke data generated with `obfuscate=True` should be sufficient to protect your information should the raw data file fall into the wrong hands. The data is pseudorandomly saved in memory by inserting it into the current keystroke list (the longer the list the better). Once the number of keystrokes hits it's maximum length times two (`keystroke-log=100`) the list is pseudorandomlized before appending to the target file. The raw keystroke data is then just chuncks of pseudorandomlized keystrokes the lengh of the `keystroke-log` parameter times two. 

That said, I would not recommend logging passwords and any other sensitive information even with `obfuscate` enabled. Instead, one should look at disabling the logger temporarily at the keyboard level via [a specified key or with leaer functionality][log-leader]. It should go without saying that I don't recommend running this script with `obfuscate` disabled. Logging should be disabled by default and turned on when required.

All of this is irrelevant if a malicious agent has direct access to your computer and can monitor HID device messages directly. However, you will most likely have other major issues if that is the case.

## Analyzing Data

With `obfuscate` on, the data set generated is the equivalent of a keystroke count. With `obfuscate` off, you have a time series dataset of your keystrokes.

### Heatmaps

Heatmaps are generated with the generate_heatmap.py. The keystroke heatmap colour distributions and the heatmap colours can be configured in heatmap_settings.py. The distribution is manually adjusted because automaticly generated distributions did not provide informative graphics. A [keyboard-layout-editor][keyboard-layout-editor] .json template is referenced in keyboard_layouts.py and all the key colours are updated to have the corresponding heatmap colour according to their keystroke count distribution. The process results in a .json which is pasted into [keyboard-layout-editor's][keyboard-layout-editor] raw data tab to generate the images below. 

[keyboard-layout-editor]: http://keyboard-layout-editor.com/

####  Keyboard Layers
![Base layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-b ase.png)
![Movement layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-mvmnt.png)
![Number layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-nmbr.png)

#### Keys Pressed After Taking Hand off Mouse
(right keyboard is only applicable)

![Mouse layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-mouse.png)

### Design Influences
#### Ergodox Ez v1.8
- CTRL was moved from a pinky location to a prime thumb location due to amount of use
- Number layer key was moved to pinky trigger due from prime thumb location due to lack of use
- Removed PGUP/PGDWN keys from prime locations due to lack of use and replaced with useful program shortcuts to windows snipping tool and divvy 
- Cleared up a ton of unused keys

## Todo
- map keycodes onto heatmaps
- map keycodes onto heatmaps from keymaps.c 
- make searching for hid devices on key_logger.py dynamic
