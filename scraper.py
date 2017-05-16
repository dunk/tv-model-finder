import re
from collections import namedtuple
import fileinput

Parser = namedtuple('Parser', 'brand regex mapping')

samsung_normal = Parser(
    brand='samsung',
    regex=r'''
    # e.g. UE55MU6400
    (?P<product_code>
    (?P<type>[KU])      # OLED or LED
    E                   # Market (Europe)
    (?P<size>[0-9]{2})  # Screen Size
    (?P<year>[MKJH])    # Year
    (?P<matrix>[SU]?)   # Matrix Type
    (?P<model>[^ ]*)    # Model
    )
    ''',
    mapping={'type': {
        'K': 'OLED',
        'U': 'LED'},
     'year': {
        'M': '2017',
        'K': '2016',
        'J': '2015',
        'H': '2014'},
     'model2': { '*': ''},
     'matrix': {
        'S': 'SUHD',
        'U': 'UHD',
        '*': 'Full HD'}})

samsung_qled = Parser(
    brand='samsung',
    regex=r'''
    # e.g. QE65Q7C
    (?P<product_code>
    Q                   # QLED
    E                   # Market (Europe)
    (?P<size>[0-9]{2})  # Screen Size
    Q                   # QLED, again
    (?P<model>[^ ]*)    # Model
    )
    ''',
    mapping={'matrix': {'*': 'QLED'},
     'model2': { '*': ''},
     'year': {'*': '2017'}})


panasonic = Parser(
    brand='panasonic',
    regex=r'''
    # e.g. 40DX700B
    (?P<product_code>
    (?P<size>[0-9]{2})  # Screen Size
    (?P<year>[ACDE])    # Year
    (?P<matrix>[SXRZ])  # Matrix Type
    (?P<model>[^ ]*)       # Model
    B                   # Market (UK)
    )
    ''',
    mapping={'year': {
        'E': '2017',
        'D': '2016',
        'C': '2015',
        'A': '2014'},
     'model2': { '*': ''},
     'matrix': {
        'S': 'Full HD',
        'X': 'UHD',
        'R': 'Curved UHD',
        'Z': 'OLED'}})


lg_normal = Parser(
    brand='lg',
    regex=r'''
    # e.g. 50UH635V
    (?P<product_code>
    (?P<size>[0-9]{2})  # Screen Size
    (?P<matrix>[SUELP]) # Matrix Type
    (?P<year>[JHFG])    # Year
    (?P<model>[^ ]*)    # Model
    )
    ''',
    mapping={'year': {
        'J': '2017',
        'H': '2016',
        'F': '2015',
        'G': '2014'},
    'model2': { '*': ''},
    'matrix': {
        'S': 'SUHD',
            'U': 'UHD',
            'E': 'Old (2016) OLED',
            'L': 'LED'}})


lg_oled = Parser(
    brand='lg',
    regex=r'''
    # e.g. OLED65B6V
    (?P<product_code>
    OLED
    (?P<size>[0-9]{2})  # Screen Size
    (?P<model>.)        # Model
    (?P<year>[67])      # Year
    [^ ]                # Other
    )
    ''',
    mapping={'year': {
        '7': '2017',
        '6': '2016'},
     'model2': { '*': ''},
     'matrix': {
        '*': 'OLED'}})

sony = Parser(
    brand='sony',
    regex=r'''
    # e.g. ???
    (?P<product_code>
    (?P<size>[0-9]{2})       # Screen Size
    (?P<model>[RWSX][0-9]+)  # Model
    (?P<year>[ABCDE])        # Year
    )
    [ ]
    ''',
    mapping={'year': {
        'E': '2017',
        'D': '2016',
        'C': '2015'},
     'model2': { '*': ''},
     'matrix': {
        '*': 'none-for-sony'}})

sony_eu_since_2016 = Parser(
    brand='sony',
    regex=r'''
    # e.g. 85XD8505
    (?P<product_code>
    (?P<size>[0-9]{2})  # Screen Size
    (?P<model>[RWSX])   # Model
    (?P<year>[EDC])     # Year
    (?P<model2>[^ ]*)   # Model
    )
    ''',
    mapping={'year': {
        'E': '2017',
        'D': '2016',
        'C': '2015'},
     'matrix': {
        '*': 'none-for-sony'}})

parsers = [
    samsung_normal,
    samsung_qled,
    panasonic,
    lg_normal,
    lg_oled,
    sony,
    sony_eu_since_2016]


def find_match(line, parser):
    match = re.search(re.compile(parser.regex, re.VERBOSE), line)
    if match:
        return render_data(match, parser.mapping)
    else:
        return False


def render_data(match, mapping):
    result = []
    for key in ['product_code', 'size', 'matrix', 'year', 'model', 'model2']:
        if key not in mapping:
            # Something dumb, like size
            result.append(match.group(key))
        else:
            if key in match.groupdict() and match.group(key) != '':
                # Genuine mappings
                result.append(mapping[key][match.group(key)])
            else:
                # General mapping, one-type things, and fall-through
                result.append(mapping[key]['*'])
    return result


if __name__ == '__main__':
    for line in fileinput.input('-'):
        for parser in parsers:
            match = find_match(line, parser)
            if match:
                print parser.brand, match
                break
        else:
            print 'NO MATCH FOR:', line.rstrip()
