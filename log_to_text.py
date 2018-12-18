import charmap

def map_input_to_key(column, row, layer='BASE'):
    
    if layer in charmap:
        keystrokes = charmap[layer]
    else:
        return None
    
    for key, mapping in keystrokes.items():    
        if mapping == [[column, row]]:
            return key
    
    return None