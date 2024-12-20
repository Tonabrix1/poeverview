#! /usr/bin/python3

from pynput import keyboard, mouse
from multiprocessing import Process
from ui import UI
from pyperclip import paste
from Xlib import display
from time import sleep
from re import compile, findall, sub
import json



proc = None
ms = mouse.Controller()
kb = keyboard.Controller()
c = keyboard.Key.ctrl
delim = '\n--------\n'
nl = '\n'

melee_weapons = ['Bows','Quarterstaves', 'Two Hand Maces', 'Claws', 
                'Daggers', 'One Hand Swords', 'One Hand Maces', 'Spears',
                'Flails', 'Two Hand Swords', 'Two Hand Axes' ,'Crossbows']
armour = ['Body Armours', 'Belts', 'Gloves', 'Boots', 'Helmets']
flasks = ['Life Flasks','Mana Flasks', 'Charms']
regexes = {
    'itemclass': compile('Item Class: (.*?)\n'),
    'damage': compile('Damage: (.*?)\n'),
    'attackspeed': compile('Attacks per Second: (.*?)\n'),
    'crit': compile('Critical Hit Chance: (.*?)\n'),
    'percent': compile('(\+|-?)(\d+)%'),
    'flat': compile('(\+|-?)(\d+)(?!%)'),
    'range': compile('((\d+)-(\d+))|(\d+ to \d+)'),
    'rarity': compile('Rarity: (.*?)\n'),
    'basetype': compile('')
}
crit_bonus = 3
crit_increase = 2.01

with open('/home/tona/Desktop/poe/bases.json') as f: bases = json.load(f)
with open('/home/tona/Desktop/poe/betteruniques.json') as f: uniques = json.load(f)
#with open('truemods.json') as f: allmods = json.load(f)

def on_press():
    global proc
    win = get_active_window().get_wm_name()
    if win and 'Path of Exile 2' in win and not proc:
        sleep(.075)
        clipboard = paste()
        parse_func = parse_class(clipboard)
        data = parse_func(clipboard)
        rarity, additional = parse_chanceable(clipboard)
        parse_mods(clipboard)
        if rarity: 
            data = rarity
            proc = Process(target=UI, args=(ms.position,data,additional), daemon=True)
        else:proc = Process(target=UI, args=(ms.position,data), daemon=True)
        proc.start()
        
def on_release(key):
    global proc
    if key == c and proc: 
        proc.terminate()
        proc = None

def parse_chanceable(x):
    rarity = parse_re_one(x, 'rarity')
    if rarity == "Normal": 
        base = x.split(delim)[0].splitlines()[-1].strip().replace('Advanced ','').replace('Expert ','')
        if uniq:=bases.get(base): 
            windows = [build_unique_windows(u) for u in uniq]
                
            return f"Chance Orb-able!!{nl}This item could become:", windows
    return '',...

def parse_re_one(x, name): return next((v for v in findall(regexes[name], x)), None)

def parse_re_all(x, name): return [v for v in findall(regexes[name], x)]

def build_unique(name):
    unique = uniques.get(name)
    base_item = unique['baseItem']
    body = unique['name']+delim

    mods = unique['itemStats']
    for mod in mods:
        desc = mod['stat']['descriptions'][0]['description']
        max_val = mod['levels'][0]['values'][0]['max']
        if ':+d' in desc or ':d' in desc: max_val = int(max_val)
        desc = sub(r'\[([A-Za-z]+ *)+\|(.*?)\]', lambda m: m.group(2), desc).replace('[','').replace(']','')
        body += desc.format(max_val)+nl
    req = ' '.join(f"{x['name']}: {x.get('value',0)}" for x in base_item['attributeRequirements'])
    body = body[:-1]
    if req.replace(' ',''): body += delim+req #use [:-1] to remove the trailing newline 
    body += delim+'\n'.join(x for x in unique['description'].splitlines() if x)
    return body

def build_unique_windows(u):
    return {'name': u ,'text': build_unique(u),'type': 'window'}

def parse_mods(x):
    rarity = parse_re_one(x,'rarity')
    itemclass = parse_re_one(x,'itemclass')
    x = x.split(delim)
    mods = x[-1].splitlines()
    if rarity == "Unique" or itemclass in flasks: mods = x[-2].splitlines()
    for mod in mods:
        ...

def parse_class(x):
    cls = parse_re_one(x,'itemclass')
    return classes.get(cls,lambda x: 'Unknown')

def parse_melee_weapon(x): 
    #all this .split()[0] stuff is to remove any " (augmented)" suffixes from gear and the like
    damages = [v.split()[0] for v in parse_re_all(x,'damage')]
    speed = parse_re_one(x,'attackspeed').split()[0]
    crit = parse_re_one(x,'crit').split()[0]
    dps = calculate_dps(damages, speed, crit)
    return f"DPS: {dps}"

def calculate_dps(damages, speed, crit):
    mins, maxes = zip(*map(lambda x: x.split('-'), damages))
    avg = (sum(map(int, mins)) + sum(map(int, maxes))) / 2
    crit = float(crit.replace('%',''))/100 + .01 # adding .01 for the +1% flat crit node on tree
    crit *= (1+crit_increase)
    dps = round(avg*float(speed)*(1+crit*crit_bonus), 2)
    return dps

def parse_currency(x): return x

def get_active_window():
    d = display.Display()
    root = d.screen().root
    window_id = root.get_full_property(d.intern_atom('_NET_ACTIVE_WINDOW'), display.X.AnyPropertyType).value[0]
    window_obj = d.create_resource_object('window', window_id)
    return window_obj

def parse_armour(x):
    return x

#some dumb shit pynput is designed to do
def for_canonical(f):
    return lambda k: f(listener.canonical(k))

classes = {'Stackable Currency': parse_currency, **dict.fromkeys(melee_weapons, parse_melee_weapon),**dict.fromkeys(armour, parse_armour)}

hotkey = keyboard.HotKey(
    keyboard.HotKey.parse('<ctrl>+c'),
    on_press)
with keyboard.Listener(on_press=for_canonical(hotkey.press), on_release=lambda x: on_release(x) or hotkey.release(x)) as listener: listener.join()
