Simple python script to set colours of HUE lamps (via the bridge).

Author: joost witteveen (joosteto@gmail.com)

## Examples

Get a valid access code from the bridge:
1) press the button on the bridge
2) Run the following command:
   `python3 hue.py --getuser yourusername`
3) The access code will be saved in the file `accesscode`, and used for next commands.

Make all lamps as bright as possible, and green. Hue ranges from 0 (red) to 6 (red again), Bri(ghtness) from 0 to 1:

`python3 hue.py  --hue 2 --bri 1`

To make lamp 1 red and lamps 2 and 3 blue:
```
python3 hue.py --lamps 1 --hue 0
python3 hue.py --lamps 1,2 --hue 4
```

Show json response for a '/lights/2' http GET request:

`python3 hue.py --get /lights/2`

Continuously check for long 'off' button press on switch id=4, and loop hue of all lamps when pressed:

`python3 hue.py --checklong0 4`



More info about the HUE lamps:

https://domoticproject.com/controlling-philips-hue-lights-with-raspberry-pi/
