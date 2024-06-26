### MPPT solar regulator - Bluetooth (GATT) communication 

#### Description
Exploration of communication methods with MPPT solar regulator using bluetooth and modbus protocol.

#### Motivation
I recently bought a MPPT solar regulator to use in my future off-grid projects. 
I set everything up, connected PV panel, 12V AGM battery
added some dummy load (in this case 6W LED) and everything worked like a charm.

Then I discovered I can use the manufacturer's mobile app to view the regulator's parameters,
which means that this device supports some communication protocol, so it can exchange data with mobile app.

That was perfect because before I decided to buy it I wanted to build MPPT solar regulator myself mostly because I
wanted to have access to parameters such as PV voltage, load voltage etc. 

Having a way to read and control this solar regulator was what I wanted to archive, so I started looking for a way to make
it happen.

#### Exploration

I searched for a way to communicate with this solar regulator, found almost nothing, just this [repository](https://github.com/majki09/lumiax_solar_bt).
I downloaded necessary dependencies, launched python script and to my surprise it worked, now I had proof it can be done.
I started looking further.

Then I thought to myself, maybe it supports modbus protocol, googled it and found official
[documentation](https://www.lumiax.com/kindeditor/attached/file/User%20Manuals/Accessories/Lumiax%20Modbus%20Communication%20Protocol%20%20V4.3.pdf).

First part is done, now I need a way to write and read data, let's take a closer look at device's bluetooth.

```
> sudo bluetoothctl
> scan on
```

I got device MAC address (in the next parts referred to as [MAC])

```
> scan off
> exit
```

```
> gatttool -b [MAC] -I
> connect
> characteristics
```

got following output

```
handle: 0x0002, char properties: 0x7b, char value handle: 0x0003, uuid: 00002a05-0000-1000-8000-00805f9b34fb
handle: 0x0005, char properties: 0x02, char value handle: 0x0006, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0007, char properties: 0x02, char value handle: 0x0008, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x0009, char properties: 0x02, char value handle: 0x000a, uuid: 00002a02-0000-1000-8000-00805f9b34fb
handle: 0x000b, char properties: 0x02, char value handle: 0x000c, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x000d, char properties: 0x02, char value handle: 0x000e, uuid: 00002aa6-0000-1000-8000-00805f9b34fb
handle: 0x0010, char properties: 0x10, char value handle: 0x0011, uuid: 0000ff01-0000-1000-8000-00805f9b34fb
handle: 0x0013, char properties: 0x0c, char value handle: 0x0014, uuid: 0000ff02-0000-1000-8000-00805f9b34fb
handle: 0x0015, char properties: 0x1c, char value handle: 0x0016, uuid: 0000ff03-0000-1000-8000-00805f9b34fb
handle: 0x0018, char properties: 0x1e, char value handle: 0x0019, uuid: 0000ff04-0000-1000-8000-00805f9b34fb
```

alright now we have something to work with

```
> exit
> sudo bluetoothctl
> menu gatt 
```

now let's look for `write` and `notify` characteristic, after some time (trial and error), I found

```
> attribute-info 0000ff02-0000-1000-8000-00805f9b34fb
```

```
Characteristic - Unknown
	UUID: 0000ff02-0000-1000-8000-00805f9b34fb
	Service: ...
	Flags: write-without-response
	Flags: write
```

and 

```
> attribute-info 0000ff01-0000-1000-8000-00805f9b34fb
```

```
Characteristic - Unknown
    UUID: 0000ff01-0000-1000-8000-00805f9b34fb
    Service: ...
    Notifying: no
    Flags: notify
```

We got everything let's write some code.

I decided to use `bleak` for bluetooth communication using GATT (`pygatt` is deprecated).
After modifying the `bleak` example I created `read_parameters.py`

```
> python3 scripts/read_parameters.py --address [MAC] --write_char "0000ff02-0000-1000-8000-00805f9b34fb" --notify_char "0000ff01-0000-1000-8000-00805f9b34fb" --read_target "3046"
```

Where `3046` (hex) is target address to read, in this case battery voltage.

In response I got
```
010402055a3a5b 
```

Where according to documentation:
- `01` - device id (always 01)
- `04` - function code
- `02` - bytes count
- `055a` - value
- `3a5b` - crc checksum

converting value to decimal I got `1370`, divided by `100` gives `13,7` which equals to current
battery voltage.

`read_parameter.py` also supports reading multiple addresses, let's analyze this case
```
> python3 read_parameters.py --address [MAC] --write_char "0000ff02-0000-1000-8000-00805f9b34fb" --notify_char "0000ff01-0000-1000-8000-00805f9b34fb" --read_target "3046" --targets_to_read 11
```

Response
```
[Notification] Vendor specific: 01041605
[Notification] Vendor specific: 5a002e02760000055a002101c400000ce4002504
[Notification] Vendor specific: c53184
```

which gives
```
010416055a002e02760000055a002101c400000ce4002504c53184
```

where values we are looking for are
```
055a002a023f0000055a002401ed00000ce4002504c5
```

just in case we will check if crc is correct which means data is complete
```
> python3 scripts/calc_crc.py --msg 010416055a002e02760000055a002101c400000ce4002504c5

3184
```

data is ok, now let's break it down and decode
```
hex value - address (dec) - value info - dec value - final value

055a - 0d12358 - Current battery voltage - 1370 - 13,7 V
002e - 0d12359 - Current battery current - 46 - 0,4 A
0276 - 0d12360 - Battery power - 630 - 6,3 W
0000 - 0d12361 - Battery power - 0
055a - 0d12362 - Load Voltage - 1370 - 13,7 V
0021 - 0d12363 - Load current - 33 0,3 A
01c4 - 0d12364 - Load power - 452 = 4.52 W
0000 - 0d12365 - Load power - 0
0ce4 - 0d12366 - The voltage of the solar panel - 3300 - 33 V
0025 - 0d12367 - The current of the solar panel - 37 - 0,37 A
04c5 - 0d12368 - PV cell array current generated power - 1221 - 12,2 W
```

now write script to automate the whole process
```
> python3 read_mppt_data.py --address [MAC]

Battery remaining capacity -> 84.0 %
Battery voltage -> 13.1 V
Battery current -> 654.98 A
Battery power -> 650.39 W
Load voltage -> 13.1 V
Load current -> 0.45 A
Load power -> 5.89 W
Solar voltage -> 16.8 V
Solar current -> 0.07 A
```

it works, well, kind of, it looks like there is a issue with parsing negative values.

after tweaking
```
> python3 read_mppt_data.py --address [MAC]

Battery remaining capacity -> 99.0 %
Battery voltage -> 13.1 V
Battery current -> -0.31 A
Battery power -> -4.06 W
Load voltage -> 13.1 V
Load current -> 0.31 A
Load power -> 4.06 W
Solar voltage -> 9.1 V
Solar current -> 0.0 A
```

And here we are, having foundations to build upon.

#### Micropython (Raspberry Pi Pico W)
Ah here we go again, it is time to utilize MicroPython on RaspberryPi Pico W.
This time we will use following packages:

- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble) - for working with async bluetooth.
- [rshell](https://github.com/dhylands/rshell) - as MicroPython remote shell.

For local development:
```
pip3 install -r micropython/requirements.txt
```

To flash files
```
rshell -f micropython/commands/flash_w_repl
```

We won't go into details as everything was nicely described above. As proof that it can be done using `aioble` I wrote simple bare reader without 
support for data parsing, this file is called `bare_mppt_reading.py`.

I flashed microcontroller, run code, got following output

```
[Notification] CRC 938e | 0104160063055a001c017f0000055a002c025a00
data: 0104160063055a001c017f0000055a002c025a00000cc600222496
done
```

Having proof that bluetooth library works fine I started porting Python `read_mppt_data.py` to MicroPython.
The result of this work is `mppt_reader.py`. Which produces following output.

```
Battery remaining capacity -> 99.0 %
Battery voltage -> 13.7 V
Battery current -> 0.29 A
Battery power -> 3.97 W
Battery power -> 0.0 W
Load voltage -> 13.7 V
Load current -> 0.43 A
Load power -> 5.89 W
Load power -> 0.0 W
Solar voltage -> 32.4 V
Solar current -> 0.34 A
```

Now having both implementations allowing me to use any small factor board running Linux or microcontroller with WiFi and MicroPython support,
I can't wait to build something with it.

#### Resources
- [communication proof of concept](https://github.com/majki09/lumiax_solar_bt)
- [modbus documentation](https://www.lumiax.com/kindeditor/attached/file/User%20Manuals/Accessories/Lumiax%20Modbus%20Communication%20Protocol%20%20V4.3.pdf)
- [GATT introduction](https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt)
- [modbus CRC checksum](https://stackoverflow.com/questions/69369408/calculating-crc16-in-python-for-modbus)
- [signed dec in python](https://stackoverflow.com/questions/24563786/conversion-from-hex-to-signed-dec-in-python)