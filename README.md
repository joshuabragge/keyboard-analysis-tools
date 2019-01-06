# keyboard-analysis-tools

This repository contains tools for caputuring and analyzing keyboard data. This data is used to enhance my custom QMK keyboard layots for my ergodox-ez and planck.

## Capturing Data
### keyboard_logger.py

The keyboard logger script was built because [existing HID listen solutions required administrative permissions][existing-solutions]. Admin permissions can (apparently) be circumvented in Windows with pywinusb.

At a high level, this script hooks onto a specified HID device - such as an ergodox-ez keyboard - and records the key presses to a file.

The resulting file appears as so:

```
KL|03|03|1|BASE
KL|01|09|1|BASE
KL|02|02|1|BASE
KL|03|09|0|BASE
KL|02|10|1|BASE
KL|01|09|0|BASE
```
## keyboard configuration
QMK keyboards need to be configured to send keystroke information in an infomative way. This is done by adjusting your keymap.c and rules.mk. You can add [a leader key to disable logging][log-leader] for highly sensitive information.

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

Script used for logging QMK console data for analysis.
