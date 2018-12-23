import re
import json
import pandas as pd

import heatmap_settings as hms
import keyboard_layouts as kl


keyboard_layout = kl.ergodox_layout.replace("\n","")

def load_keyboard_layout(keyboard_layout=kl.ergodox_layout):
	return kl.ergodox_layout.replace("\n","")

def load_key_data(filename='keystrokes.csv', sep="|"):
	df = pd.read_csv(filename, header=None,delimiter=sep)
	df.columns = ['Type','Row','Col', 'Pressed', 'Layer']
	return df

def filter_key_data(dataframe, layer='BASE', event='KL'):
	pf = dataframe[dataframe['Pressed']=='1']
	pf = pf[pf['Layer']=='BASE']
	pf = pf[pf['Type']=='KL']
	return pf

def add_key_data(dataframe):
	dataframe['Key'] = dataframe['Row'] + "." + dataframe['Col']
	return dataframe

def group_key_count(dataframe):
	keystrokes_grouped = dataframe.groupby("Key").count()['Pressed'].reset_index().sort_values('Pressed',ascending=False)
	return keystrokes_grouped

def generate_heatmap_bins(keystrokes_grouped):
	number_of_keys = keystrokes_grouped['Key'].unique().shape[0]
	# Convert category distribution into number of strokes based on data set
	keystrokes_grouped = keystrokes_grouped.sort_values("Pressed",ascending=True).reset_index().drop('index',axis=1)
	distribution_values = {}
	values_distribution = {}
	counter_distribution = 0
	counter_percentages = 0
	min_press = 0
	max_press = 0

	for i in keystrokes_grouped.index:
	    mins = hms.distribution[counter_distribution][0]
	    maxs = hms.distribution[counter_distribution][1]
	    
	    counter_percentages +=1
	    
	    if counter_percentages/number_of_keys >= maxs/100:
	        min_press = max_press
	        max_press = keystrokes_grouped['Pressed'].ix[i]
	        distribution_values[counter_distribution] = [min_press, max_press]
	        values_distribution[min_press] = counter_distribution
	        counter_distribution += 1

	return values_distribution

def high_tech_binner(value, values_distribution):
    for key, v in values_distribution.items():
        if key >= value:
            bucket = values_distribution[key]
            if bucket == 0:
                return bucket
            else:
                return bucket - 1
    return values_distribution[key] # return max

def ready_heatmap_data(keystrokes_grouped, values_distribution):
	count = keystrokes_grouped['Pressed'].sum()
	keystrokes_grouped['Bin Target'] = keystrokes_grouped['Pressed'].apply(lambda x: high_tech_binner(x, values_distribution))
	keystrokes_grouped['Colour'] = keystrokes_grouped['Bin Target'].apply(lambda x: hms.heatmap_colours[x])
	keystrokes_grouped['Comment'] = keystrokes_grouped['Pressed'].apply(lambda x:"{0:.2f}%".format((x/count)*100))
	return keystrokes_grouped

def generate_heatmap(keystrokes_grouped, keyboard_layout):

	for i in keystrokes_grouped.index:
	    key = keystrokes_grouped['Key'].ix[i]
	    colour = keystrokes_grouped['Colour'].ix[i]
	    reg = kl.regex_mapping_colour(key)
	    p = re.compile(reg)
	    try:
	        replacement_colour = '#' + p.findall(keyboard_layout)[0]
	    except:
	        print("Error finding:", key)
	    keyboard_layout = keyboard_layout.replace(replacement_colour, colour)
	    
	    comment =  keystrokes_grouped['Comment'].ix[i]
	    key = key.replace(".","|")
	    updated_key = key + "\n\n\n\n" + comment
	    keyboard_layout = keyboard_layout.replace(key, updated_key)
	return keyboard_layout

def save_heatmap(heatmap, layer='BASE', keyboard_layout='ergodox'):
	filename = keyboard_layout + '-' + layer + '.json'
	with open(filename, 'w') as outfile:
		json.dump(heatmap, outfile)

def main(layer='BASE'):
	keyboard_layout = load_keyboard_layout(keyboard_layout=kl.ergodox_layout)
	df = load_key_data(filename='keystrokes.csv', sep="|")
	df = filter_key_data(df, layer='BASE', event='KL')
	df = add_key_data(df)
	keystrokes_grouped = group_key_count(df)
	values_distribution = generate_heatmap_bins(keystrokes_grouped)
	keystrokes_grouped = ready_heatmap_data(keystrokes_grouped, values_distribution)
	heatmap = generate_heatmap(keystrokes_grouped, keyboard_layout)
	save_heatmap(heatmap, layer='BASE', keyboard_layout='ergodox')


if __name__ == '__main__':
	main()










