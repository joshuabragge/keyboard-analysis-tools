# keyboard-analysis-tools

This repository contains tools for caputuring and analyzing keyboard data. This data is used to enhance custom QMK keyboard layouts such as the [ergodox-ez][ergodox-ez] and [planck][planck].

[ergodox-ez]: https://github.com/joshuabragge/ergodox
[planck]: https://github.com/joshuabragge/planck/

## Table of Contents

* [Capturing Data](#Capturing-Data)
    - [Keyboard Logging](#keyboard-logger)
        - [Parameters](#parameters)
    - [Keyboard Configuration](#Keyboard-Configuration)
    - [Privacy and Security Concerns](#privacy-security)
* [Analyzing Data](#Analyzing-Data)
* [TODO](#todo)

## Capturing Data
### Keyboard Logging

keyboard_logger.py was built because [existing HID listen solutions required administrative permissions][existing-solutions]. Admin permissions can (apparently) be circumvented in Windows with pywinusb.

At a high level, this script hooks onto a specified HID device - such as an ergodox-ez keyboard - and records the keys pressed to a file.

The resulting file is a list of the keys that pressed, not the value those keys represent (that information can obviously be determined when combined with the keymap.c).

The data structure is obviously a result of how you configure it in your keymap.c [(see keyboard configuration for more details)](#keyboard-configuration). I have found the following structure to be acceptable.

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
QMK keyboards need to be configured to send keystroke information in an infomative way. This is done by adjusting your keymap.c and rules.mk. You can add [a leader key to disable logging][log-leader] for highly sensitive information. The best we can do is send the location of the key that was pressed (row 1 column 10 for example).

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

[existing-solutions]: https://www.pjrc.com/teensy/hid_listen.html
[log-leader]: https://github.com/joshuabragge/ergodox/blob/325429ef3de1e1997918541ce7b1e3b89b066b6b/keymap.c#L564

### Privacy and Security Concerns with Logged Data

The storing of keystroke data with `--obfuscate=True` should be sufficient to protect your information if it ever falls into the hands of malicious agent. The data is pseudorandomly saved in memory by inserting it into the current keystroke list which exists only in memory (the longer the list the better). Once the number of keystrokes hits it's specified parameter (`--keystroke-log=100`) the list is pseudorandomlized again before appending to the file. You end up with chuncks of pseudorandomlized data the lengh of the --keystroke-log parameter times two (for example with one keystroke of "m" we are recording the press down and release of the key `KL|01|09|0|BASE` and `KL|01|09|1|BASE`).

That said, I would still recommend not logging passwords and other sensitive information even with `--obfuscate=True` on. Instead, one should look at disabling the logger temporarily via [a leader key for example][log-leader]. I certainly don't recommend running without `--obfuscate=  False` because becomes a keylogger in it's truest form.

## Analyzing Data

### Heatmaps

####  Keyboard Layers
![Base layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-base.png)
![Movement layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-mvmnt.png)
![Number layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-nmbr.png)

#### Keys Pressed After Taking Hand off Mouse
(right keyboard is only applicable)

![Mouse layer](https://github.com/joshuabragge/keyboard-analysis-tools/blob/master/images/ergodox-mouse.png)

## Todo
- map keycodes onto heatmaps
- map keycodes onto heatmaps from keymaps.c 
- make searching for hid devices on key_logger.py dynamic
