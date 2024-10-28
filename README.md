# juice

# Installation

There is no installation ¯\\_(ツ)\_/¯  
The script is provided as-is. Git clone and import objects or just copy-paste the contents into Python interpreter.

# How to

Configure and run the script, you will need:
* drones (eg. Mavic)
* devices (eg. Starlink, computers, displays, tablets, etc.)
* power stations (eg. Ecoflow, Allpowers)
* power generators (eg. Honda, Kraft & Dele)
* mission start and end times with approximate sunset and sunrise times


```python
mavic_3t = Drone(name="Mavic 3T", drones=1, batteries=6, chargers=3, wh=77, flight_time=30, charge_time=70, night=True)
air_2s = Drone(name="Air 2S", drones=1, batteries=5, chargers=1, wh=40, flight_time=20, charge_time=100, night=False)

starlink = Device(w=25, n=1)

fossibot = Station(wh=512, charge_time=90)
allpowers = Station(wh=299, charge_time=60)

kraft = Generator(consumption=0.75)

run(
    drones=[mavic_3t, air_2s],
    devices=[starlink],
    stations=[fossibot, allpowers],
    generator=kraft,
    start=datetime.datetime(year=2024, month=11, day=29, hour=16),
    end=datetime.datetime(year=2024, month=12, day=1, hour=12),
    sunset=datetime.time(hour=15, minute=35),
    sunrise=datetime.time(hour=7, minute=50),
)
```
