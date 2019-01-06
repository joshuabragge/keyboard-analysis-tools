# keyboard-analysis-tools

This repository contains tools for caputuring and analyzing keyboard data. This data is used to enhance custom QMK keyboard layouts such as the [ergodox-ez][ergodox-ez] and [planck]planck.

[ergodox-ez]: https://github.com/joshuabragge/ergodox
[planck]: https://github.com/joshuabragge/planck/

## Table of Contents

* [Capturing Data](#Capturing-Data)
    - [keyboard_logger.py](#keyboard-logger)
            - [Parameters](#parameters)
    - [Keyboard Configuration](#Keyboard-Configuration)

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

##### Parameters
```
--input-lag=0.05 Poll rate in seconds to checking for keypress changes
```
```
--obfuscate=True randomizes keystroke order before saving to file
``` 
```
--keystroke-log=100 Number of keystrokes before logging to file
``` 

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


