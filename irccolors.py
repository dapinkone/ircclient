# implementing functionality to replace/display irc colors
from colored import fg, bg, attr
import re
# unfortunately irc's standard colors suck and don't match colored's
# there's also only 16 of them :( as apposed to colored's term-256
# support, so here they are.
irc_colors = [
    'white', 'black', 'blue', 'green', 'light_red', 'sandy_brown',
    'medium_purple', 'orange_4a', 'yellow', 'light_green', 'cyan',
    'light_cyan', 'light_blue', 'pink_1', 'dark_gray', 'light_gray']


def subcolors(input_data):
    # for each match in $string =~ m/(^K|^C)([0-9A-F])?,([0-9A-F])?/
    # replace with fg($2) + bg($3); append attr('reset') to end of line.
    # if $2 or $3 are None, replace $1 with attr('reset') instead.

    # return index of all matches of ctrl codes (^C|^c)
    # ^K and ^C respectively
    c_matches = re.sub(r'[\x0b\x03](\d{1,2}),(\d{1,2})',
                       derive_color, input_data)  # regex are sin.

    # there shouldn't be any ctrl chars left, but just in case.
    c_matches = re.sub(r'[\x0b\x03]', attr('reset'), c_matches)

    # we want to throw a reset on the end to avoid multiline colorbleeding
    return c_matches + attr('reset')


def derive_color(matchobj):
    try:
        m = int(matchobj.expand(r'\1'))
        n = int(matchobj.expand(r'\2'))
    except ValueError as e:  # matched, but doesn't have both fg and bg colors
        # print(e)
        return attr('reset')

    colo_value = ''

    # non-valid colors == 'default' color, so reset before we set the other
    # color.
    if m >= 16 or n >= 16:
        colo_value = attr('reset')
    if m < 16:
        colo_value += fg(irc_colors[m])
    if n < 16:
        colo_value += bg(irc_colors[n])
    return colo_value


if __name__ == '__main__':
    # test to see if all the colors are working proper on terminal.
    valid_colors = list(map(str, list(range(16))))
    print('valid_colors: ' + repr(valid_colors))
    for i in valid_colors:
        newstring = ''
        for j in valid_colors:
            newstring += f'\x0b{i},{j}X'
        print(subcolors(newstring))
