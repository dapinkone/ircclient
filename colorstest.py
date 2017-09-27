# experiment testing to see if i can catch interrupts or something
# like C-c C-k etc.
from colored import fg, bg, attr

def subcolors(input_data):
    # for each match in $string =~ m/(^K|^C)([0-9A-F])?,([0-9A-F])?/
    # replace with fg($2) + bg($3); append attr('reset') to end of line.
    # if $2 or $3 are None, replace $1 with attr('reset') instead.

    # return index of all matches of ctrl codes (^C|^K)
    c_match_indexes = [ i for i, c in enumerate(input_data)
                               if c in "\x0b\x03"]  # ^K and ^C respectively
    # we're going to start from the end, to avoid moving the indexes
    # that we're working with before we get to them.
    valid_color_codes = "0123456789ABCDEFabcdef"
    input_arr = list(input_data)
    for i in reversed(c_match_indexes):
        try:
            if ((str(input_arr[i+1]) in valid_color_codes) and
            (input_arr[i+2] is ',') and
            ( str(input_arr[i+3]) in valid_color_codes )):
                # convert the color code to decimal,
                # feed to color function, replace.
                input_arr[i+3] = bg(int(input_arr[i+3], 16))
                input_arr[i+2] = '' # remove the required ,
                # convert .....etc for the fg color
                input_arr[i+1] = fg(int(input_arr[i+1], 16))
                # remove the ctrl character.
                input_arr.pop(i) # remove index i from the list.
            else: # reset character if user doesn't match the pattern.
                input_arr[i] = attr('reset')
        except IndexError:
            # something went wrong, remove control character.
            input_arr.pop(i)
    # we want to throw a reset on the end to avoid multiline colorbleeding
    return ''.join(input_arr) + attr('reset')

teststring = "color\x0b1,6test"
print(subcolors(teststring))
valid_colors = list('0123456789ABCDEFabcdef')
for i in valid_colors:
    newstring  = ''
    for j in valid_colors:
        newstring += f'\x0b{i},{j}X'
    print(subcolors(newstring))
