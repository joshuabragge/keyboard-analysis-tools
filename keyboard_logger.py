import argparse
import ctypes
import time
import random

import pywinusb.hid as hid

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_pos():
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return { "x": pt.x, "y": pt.y, 'time': time.time()}

def raw_data_handler(binary_data):
	raw_data = bytearray(binary_data).decode('utf-8')
	data = raw_data.strip('\x00').strip('\n')
	global keystroke_previous
	keystroke_previous = data
	if obfuscate:
		random_insert(keystrokes, data)
	else:
		keystrokes.append(data)

def random_insert(lst, item):
    lst.insert(random.randrange(len(lst)+1), item)

def setup_keyboard():
	ergodox_vendor = 0xfeed
	ergodox_product = 0x1307
	ergodox_version = 0x0001

	ergodox_filter = hid.HidDeviceFilter(vendor_id = ergodox_vendor, 
	                                     product_id = ergodox_product)

	ergodox_devices = ergodox_filter.get_devices()

	if ergodox_devices:
	    print("Successful connection to Ergodox...")
	    ergo_device = None
	    for device in ergodox_devices:
	        # this device identifier is 
	        # responsible for sending out data
	        if '#vid_feed&pid_1307&mi_02#7&1e2751cd&0&0000#' in str(device):
	            ergo_device = device
	            print("Successful connection to HID...")
	            return ergo_device
	    if not ergo_device: 
	        raise ValueError('Failed to connect to HID...') 
	else:
	    raise ValueError('Failed to connect to Ergodox...') 

def mouse_changed(mouse_pos_previous, mouse_pos_current):
	changes_x = mouse_pos_previous['x'] - mouse_pos_current['x']
	changes_y = mouse_pos_previous['y'] - mouse_pos_current['y']
	if changes_x + changes_y == 0:
		return False
	else:
		return True

def count_changed(number_before, number_after):
	if number_before - number_after == 0:
		return False
	else:
		return True

def append_list_to_file(lst, filename):
	with open(filename, "a") as f:
		for item in lst:
			f.write("%s\n" % item)

def cleanup_logging_list(lst):
	return [i.split("\n", 1)[0] for i in lst]

def main(opts):
	# variables
	global obfuscate
	obfuscate = opts.obfuscate
	keystrokes_before_logging = opts.keystrokes_before_logging
	input_lag = opts.input_lag
	filename_keystrokes = 'keystrokes.csv'
	filename_mousestrokes = 'mousestrokes.csv'

	# __init__
	log_mouse_results = True
	global keystrokes
	global mousestrokes
	global keystroke_previous
	keystrokes = []
	mousestrokes = []
	keystroke_previous = None
	mouse_pos_previous = get_mouse_pos()
	keystroke_count_previous = len(keystrokes)
	ergo_device = setup_keyboard()
	ergo_device.open()

	print("Starting logging...")
	time.sleep(1)

	while True:
		try: 
			mouse_pos_current = get_mouse_pos()
			ergo_device.set_raw_data_handler(raw_data_handler)

			if len(keystrokes) == 1:
				print('Successfully logging keystrokes...') 

			keystroke_count_current = len(keystrokes)
			keys_pressed_since_mouse_stopped = count_changed(keystroke_count_previous, 
															 keystroke_count_current)
			if mouse_changed(mouse_pos_previous, mouse_pos_current):
				log_mouse_results = True
			else:
				if log_mouse_results is True and keys_pressed_since_mouse_stopped is True:
					log_mouse_results = False
					keystrokes.append('M|0|0|0|STOPPED')
					# log the key that made us move our hand away from mouse
					# this data is useful if we turn on obfuscate
					mousestrokes.append(keystroke_previous)

			keystroke_count_previous = keystroke_count_current
			mouse_pos_previous = mouse_pos_current
			time.sleep(input_lag)

			if len(keystrokes) > keystrokes_before_logging*2:
				# cleaning up the data in case 
				# receiving signal gets jumbled
				try:
					keystrokes = cleanup_logging_list(lst=keystrokes)
					mousestrokes = cleanup_logging_list(lst=mousestrokes)
				except AttributeError:
					continue

				if obfuscate:
					random.shuffle(keystrokes)
					random.shuffle(mousestrokes)

				append_list_to_file(lst=keystrokes, filename=filename_keystrokes)
				append_list_to_file(lst=mousestrokes, filename=filename_mousestrokes)

				print("{0} saving data...".format(time.time()))

				keystrokes = []
				mousestrokes = []

		except KeyboardInterrupt:
			print("{0} saving data...".format(time.time()))
			append_list_to_file(lst=keystrokes, filename=filename_keystrokes)
			append_list_to_file(lst=mousestrokes, filename=filename_mousestrokes)
			print("Closing HID connection...")
			ergo_device.close()
			break

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Log QMK keystrokes and mousestrokes")
	#parser.add_argument('outputdir', action = 'store', help='Output directory')
	parser.add_argument('--input-lag', dest='input_lag', 
						action='store', type=int,
						default=0.05, 
						help="Refresh rate before checking for next keystroke")
	parser.add_argument('--obfuscate', dest='obfuscate',
						action='store',	type=bool,
						default=True, 
						help="Randomize keystroke order in memory and before saving to file")
	parser.add_argument('--keystroke-log', dest='keystrokes_before_logging',
						action='store', type=int, default=100, 
						help="Number of keystrokes before logging to file")
	args = parser.parse_args()
	main(args)
