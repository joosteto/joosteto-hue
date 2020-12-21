Simple python script to set colours of HUE lamps (via the bridge).
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

Continuously check for long 'off' button press on switch id=4, and if 
python3 hue.py --checklong0 4



More info about the HUE lamps:

https://domoticproject.com/controlling-philips-hue-lights-with-raspberry-pi/
