# keyboard-analysis-tools

This repository contains tools for caputuring and analyzing keyboard data. This data is used to enhance my custom QMK keyboard layots for my ergodox-ez and planck.

## Capturing Data
### keyboard_logger.py

The keyboard logger script was built because [existing HID listen solutions required administrative permissions][existing-solutions]. Admin permissions can (apparently) be circumvented in Windows with pywinusb.

At a high level, this script hooks onto a specified HID device - such as an ergodox-ez keyboard - and records the key presses to a CSV.

The resulting data appears as so:

```
KL|03|03|1|BASE
KL|01|09|1|BASE
KL|02|02|1|BASE
KL|03|09|0|BASE
KL|02|10|1|BASE
KL|01|09|0|BASE
```

[existing-solutions]: https://www.pjrc.com/teensy/hid_listen.html

Script used for logging QMK console data for analysis.
