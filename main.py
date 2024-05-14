from sys import argv
from time import time

if len(argv) == 2:
    fn = argv[1]
elif len(argv) < 2:
    raise FileNotFoundError('No file name given.')

with open(fn, 'r', encoding='utf-8') as f:
    file = f.read()

DEBUGMODE = False
# ACCEPTED_VARNAME_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
# ^^ because of the way vars are treated, this is actually very useless.

RED_TEXT_BOLD = '\033[1;31mbold\b\b\b\b'
YELLOW_TEXT_BOLD = '\033[1;33mbold\b\b\b\b'
RED_TEXT = '\033[0;31m'
YELLOW_TEXT = '\033[0;33m'

NORMAL_TEXT = '\033[0m'

COMMENT_CHAR = ';'

def printSpecial(text, color):
    print(f'{color}{text}{NORMAL_TEXT}')

lines = file.split('\n')

def extractStrings(args):
    strings = []
    quoted = False
    this_str = ''
    for char in list(' '.join(args)):
        if char == '/': quoted = not quoted
        if quoted and char != '/': this_str += char
        if not quoted: strings.append(this_str); this_str = ''
        if DEBUGMODE: printSpecial(f'DEBUG: {str((strings, this_str, quoted))}', YELLOW_TEXT)
    for entry in strings:
        if entry == '':
            strings.remove(entry)
    if DEBUGMODE: printSpecial(f'DEBUG: {strings}', YELLOW_TEXT)
    return strings

def err(line, details, name):
    printSpecial(f'Unhandled exception in {name}:{line},\n\t{details}',RED_TEXT_BOLD)

def warn(line, details, name):
    printSpecial(f'Warning in {name}:{line}, \n\t{details}', YELLOW_TEXT_BOLD)

lineno = 0
parse = True
LOGFILE = None
if lines[0].startswith('@debug'):
    lines = lines[1:]
    DEBUGMODE = True
    lineno += 1
if lines[0].startswith('@logfile'):
    args = extractStrings(lines[0].split(' ')[1:])
    if len(args) != 1:
        keyw = 'was'
        if abs(len(args)) != 1: keyw = 'were'
        err(lineno, f'@logfile takes 1 argument, but {len(args)} {keyw} given', fn)
        parse = False
    lines = lines[1:]
    LOGFILE = args[0]
    lineno += 1

nprint = print
def print(*args):
    text = ''
    for arg in args:
        text += str(arg) + ' '
    nprint(text)
    if LOGFILE != None:
        with open(LOGFILE, 'a', encoding='utf-8') as f:
            f.write(text + '\n')

Globals = {}
Stack = []

parsingStart = time()
for line in lines:
    if not parse: break
    lineno += 1
    n_line = ''
    for char in list(line):
        if char == COMMENT_CHAR: break
        n_line += char
    line = n_line.strip()
    if line == '': continue
    tokens = line.split(' ')
    op = tokens[0]
    args = tokens[1:]
    if op == '@debug' or op == '@logfile':
        err(lineno, '@ commands have to be ran at the top of the file.', fn)
        break
    if op == 'line':
        args2 = extractStrings(args)
        actualStrings = []
        for entry in args2:
            if entry in Globals:
                actualStrings.append(Globals[entry])
            else:
                actualStrings.append(entry)
        print(' '.join(actualStrings))
    elif op == 'remember':
        args2 = extractStrings(args)
        if len(args2) != 2:
            keyw = 'was'
            if abs(len(args2)) != 1: keyw = 'were'
            err(lineno, f'Remember takes 2 arguments, but {len(args2)} {keyw} given', fn)
            break
        varname = args2[0]
        varvalue = args2[1]
        # for char in list(varname):
        #     if char not in ACCEPTED_VARNAME_CHARS:
        #         err(lineno, f'Invalid variable name \'{varname}\'', fn)
        #         break
        Globals[varname] = varvalue
    elif op == 'forget':
        args2 = extractStrings(args)
        for entry in args2:
            if entry in Globals:
                del Globals[entry]
            else:
                err(lineno, f'Global \'{entry}\' not found.', fn)
                break
    elif op == 'push':
        args2 = extractStrings(args)
        for entry in args2:
            Stack.append(entry)
            if DEBUGMODE:
                printSpecial(f'DEBUG: Add {entry} to stack', YELLOW_TEXT)
    elif op == 'pop':
        if len(args) != 0:
            keyw = 'was'
            if abs(len(args)) != 1: keyw = 'were'
            err(lineno, f'Pop takes 0 arguments, but {len(args)} {keyw} given', fn)
            break
        if len(Stack) < 1:
            err(lineno, 'Stack underflow.', fn)
            break
        print(Stack.pop())
    elif op == 'quit':
        if len(args) != 0:
            keyw = 'was'
            if abs(len(args)) != 1: keyw = 'were'
            warn(lineno, f'Quit takes 0 arguments, but {len(args)} {keyw} given', fn)
        break
    else:
        err(lineno, f'Unknown operation \'{op}\'', fn)
        break

if DEBUGMODE:
    printSpecial(f'DEBUG: Took {time() - parsingStart:.02f}s to interpret file.', YELLOW_TEXT)