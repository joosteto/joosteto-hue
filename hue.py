#!/usr/bin/python3

"""

Script to set colours of HUE lamps (via the bridge).
Author: joost witteveen (joosteto@gmail.com)

Examples:

Get a valid access code from the bridge:
1) press the button on the bridge
2) Run the following command:
   python3 hue.py --getuser yourusername
3) The access code will be saved in the file 'accesscode', and used for next commands.

Make all lamps as bright as possible, and green:
python3 hue.py  --hue 2 --bri 1

Show json response for a '/lights/2' http GET request:
python3 hue.py --get /lights/2

(Very) warm white:
python3 hue.py --xy 0.6,0.4 --bri 1


Continuously check for long 'off' button press on switch id=4, and if 
python3 hue.py --checklong0 4



More info about the HUE lamps:

https://domoticproject.com/controlling-philips-hue-lights-with-raspberry-pi/


sudo apt-get install avahi-utils python3-requests

# Get address of the bridge:
avahi-browse -rt _hue._tcp

#################################################
python3 hue.py --get /lights/2
{'capabilities': {'certified': True,
                  'control': {'colorgamut': [[0.6915, 0.3083],
                                             [0.17, 0.7],
                                             [0.1532, 0.0475]],
                              'colorgamuttype': 'C',
                              'ct': {'max': 500, 'min': 153},
                              'maxlumen': 800,
                              'mindimlevel': 200},
                  'streaming': {'proxy': True, 'renderer': True}},
 'config': {'archetype': 'classicbulb',
            'direction': 'omnidirectional',
            'function': 'mixed',
            'startup': {'configured': True, 'mode': 'powerfail'}},
 'manufacturername': 'Signify Netherlands B.V.',
 'modelid': 'LCA001',
 'name': 'Hue color lamp 2',
 'productid': 'Philips-LCA001-5-A19ECLv6',
 'productname': 'Hue color lamp',
 'state': {'alert': 'select',
           'bri': 25,
           'colormode': 'hs',
           'ct': 500,
           'effect': 'none',
           'hue': 0,
           'mode': 'homeautomation',
           'on': True,
           'reachable': True,
           'sat': 127,
           'xy': [0.5359, 0.3425]},
 'swconfigid': 'BD38721C',
 'swupdate': {'lastinstall': '2020-12-05T13:42:29', 'state': 'noupdates'},
 'swversion': '1.65.9_hB3217DF',
 'type': 'Extended color light',
 'uniqueid': '00:17:88:01:06:7a:a7:59-0b'}

"""

bridgeAddr="Philips-hue.local"
user=None
verbose=None

import argparse
import os
import pprint
import requests
import time

class LinkButtonNotPressed(Exception):
    def __init__(self, info):
        self.info=info
class BridgeError(Exception):
    def __init__(self, info):
        self.info=info

def getcmd(arg=""):
    if arg[0]=='/':
        arg=arg[1:]
    url = f'http://{bridgeAddr}/api/{user}/{arg}'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    if verbose:
        print(f"URL={url}")
    r = requests.get(url,headers=headers)
    answ=r.json()
    try:
        if 'error' in answ[0]:
            raise BridgeError(answ[0]['error'])
    except KeyError: #normally answ is a dict, and test for 'error' in answ[0] will fail
        pass
    if verbose:
        print(f"  -> {r.json()}")
    return answ
    
def getuser(name):
    """
curl -d '{"devicetype":"[joosteto]"}' -H "Content-Type: application/json" -X POST 'http://philips-hue.local/api'
[{"success":{"username":"asdjkflasdjfksdfjsklfjsdkla-ajfdklasdjk"}}]

"""
    url = f'http://{bridgeAddr}/api/'
    payload =f'{{"devicetype": "[{name}]"}}'
    #print(f"payload={payload}")
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r=requests.post(url, data=payload, headers=headers)
    #print(f"r.text={r.text}")
    answ=r.json()[0]
    #answ=[{"success":{"yourusername":"asdjkflasdjfksdfjsklfjsdkla-ajfdklasdjk"}}][0]
    if 'success' in answ:
        usercode=answ['success']
        name=tuple(usercode.keys())[0]
        code=usercode[name]
        print(f'access code for name {name}: {code}')
        if os.path.exists('accesscode'):
            print("Erase old accesscode file to store new accesscode?")
            input("^C to abort, Enter to continue ")
        open('accesscode', 'w').write(code)
    else:
        if 'error' in answ:
            if answ['error']['description']=='link button not pressed':
                raise LinkButtonNotPressed(answ['error'])
            print(f'Error: {answ["error"]["description"]}')
        else:
            print(f'Error: {answ}')

def parsecolorgamuts(lightinfo):
    cg={}
    for (lightid, li) in lightinfo.items():
        cg[lightid]=li['capabilities']['control']['colorgamut']
    return cg

def set_lightstate(lightid, name, value):
    url = f'http://{bridgeAddr}/api/{user}/lights/{lightid}/state'
    payload =f'{{"{name}":{value}, "on": true}}'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    if verbose:
        print(f'url={url}\ndata={payload}\nheaders={headers}')
    r = requests.put(url, data=payload, headers=headers)
    if verbose:
        print(f"  -> response: {r.text}")
    
    
def loopcolors(cg):
    tStart=time.time()
    while True:
        t=(time.time()-tStart)/5
        for lightid in cg:
            tid=(t+int(lightid))%3
            it0=int(tid)
            it1=(it0+1)%3
            xy0=cg[lightid][it0]
            xy1=cg[lightid][it1]
            x=(tid-it0)*xy0[0]+(1-tid+it0)*xy1[0]
            y=(tid-it0)*xy0[1]+(1-tid+it0)*xy1[1]
            set_lightstate(lightid, "xy", [x,y])
        time.sleep(0.3)

def checkLong0(sensorid, cg):
    oldstate=None
    tStart=time.time()
    while True:
        sensinf=getcmd(f'/sensors/{sensorid}')
        sensstate=sensinf['state']['buttonevent']
        if sensstate==4003 and oldstate != 'longdown':
            oldstate='longdown'
            #print(f'long off press: {sensinf["state"]}')
            tStart=time.time()
        elif sensstate!=4003:
            #print(f'no long off press: {sensinf["state"]}')
            oldstate=None
        if oldstate=='longdown':
            t=time.time()-tStart
            for lightid in cg:
                tid=(t/16-(int(lightid)/3))%1
                hue=int(tid*(2**16-1))
                set_lightstate(lightid, "hue", hue)
            time.sleep(0.2)
        else:
            time.sleep(1)



    
#gi=getinfo()
#pprint.pprint(gi)

#tryouts()    
#setlight(1, [0.6, 0.4])
#setlight(2, [0.6, 0.4])
#setlight(3, [0.6, 0.4])


def main():
    global bridgeAddr
    global user
    global verbose
    parser = argparse.ArgumentParser(description='Communicate with Phillips Hue Bridge (lamps, switches).')
    #configuration
    parser.add_argument('--user',
                        help='user (effectively password) at the bridge. If not given, read from file username')
    parser.add_argument('--bridge',
                        help='hostname/IP of the bridge. Default: philips-hue.local, or the contents of the file "bridge" in the current directory')
    parser.add_argument('--getuser',
                        help='get username (security code) from bridge (after button on bridge is pressed)')

    #actions:
    parser.add_argument('--get',
                        help='do a GET request, show the result. Example: --get /lights')
    parser.add_argument('--loop',
                        action='store_true',
                        help='change colors of the lights in a loop')
    parser.add_argument('--checklong0',
                        help='continuously check for long 0 press on sensor id')
    parser.add_argument('--hue',
                        help="set hue of specified lamps (range: 0..360)")
    parser.add_argument('--sat',
                        help='set saturation of specified lamps (range: 0..1)')
    parser.add_argument('--bri',
                        help='set brightness of specified lamps (range: 0..1)')
    parser.add_argument('--briB',
                        help='set brightness of specified lamps (range: 0..255)')
    parser.add_argument('--xy',
                        help='set xy color of specified lamps. Example: --xy 0.3,0.7')

    #Others
    parser.add_argument('--lamps',
                        help='hue,sat,bri,xy -commands work on lamps in this list. Example: --lamps 1,3')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    verbose=args.verbose
    #configuration
    if args.bridge is not None:
        bridgeAddr=args.bridge
    else:
        if os.path.exists('bridge'):
            bridgeAddr=open('bridge','r').read().strip()
    try:
        if args.getuser is not None:
            getuser(args.getuser)
            
        if args.user is not None:
            user=args.user
        else:
            user=open('accesscode','r').read().strip()

        
        lightsinfo=getcmd('/lights')
        colorgammuts=parsecolorgamuts(lightsinfo)
            
        if args.lamps is not None:
            lstr=args.lamps
            if ',' not in lstr: #add "," if only one lamp is given (--lamps 1)
                lstr=lstr+","
            lamps=tuple(str(l) for l in eval(lstr))
        else:
            lamps=tuple(lightsinfo.keys())
        #print(f"lamps={lamps}")
    
        #actions
        if args.get is not None:
            answ=getcmd(args.get)
            pprint.pprint(answ)
    
        if args.loop:
            loopcolors(colorgammuts)
    
        if args.checklong0 is not None:
            checkLong0(args.checklong0, colorgammuts)
    
        for lid in lamps:
            if args.hue is not None:
                hue=int(float(args.hue)*2**16//360) % 2**16
                #print(f"setting {lid} to hue={hue}")
                set_lightstate(lid, "hue", hue)
                
            if args.sat is not None:
                sat=int(float(args.sat)*255)
                set_lightstate(lid, "sat", sat)
                
            if args.xy is not None:
                xy=list(eval(args.xy))
                set_lightstate(lid, "xy", xy)

            bri=None
            if args.bri is not None:
                bri=int(255*eval(args.bri))
            if args.briB is not None:
                bri=int(eval(args.briB))
            if bri is not None:
                set_lightstate(lid, "bri", bri)
                
    except LinkButtonNotPressed as e:
        print("To get a valid user access code, the button on the bridge needs to be pressed shortly before the --getaccess command is used")
    except BridgeError as e:
        print(f"Error message from bridge: {e}")
        if e.info['description']=='unauthorized user':
            print("Access code was not accepted by bridge. Run again with the '--getaccess name' argument")
        
if __name__=="__main__":
    main()
