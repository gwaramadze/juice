import datetime
import threading
from collections import namedtuple

ONE_MINUTE = datetime.timedelta(minutes=1)

Window = namedtuple("Window", ["start", "end"])
Station = namedtuple("Station", ["wh", "charge_time"])
Generator = namedtuple("Generator", ["consumption"])
Device = namedtuple("Device", ["w", "n"])


class Drone:
    def __init__(self, name, drones, batteries, chargers, wh, flight_time, charge_time, night):
        self.name = name
        self.drones = threading.Semaphore(drones)
        self.batteries = threading.Semaphore(batteries)
        self.chargers = threading.Semaphore(chargers)
        self.wh = wh
        self.flight_time = datetime.timedelta(minutes=flight_time)
        self.charge_time = datetime.timedelta(minutes=charge_time)
        self.flights = []
        self.chargings = []
        self.empty_batteries = 0
        self.pause_start = None
        self.night = night
        self.consumed_wh = 0

    def start_flights(self, time, sunset, sunrise):
        if not self.night and (time.time() > sunset or time.time() < sunrise):
            return

        if not self.drones.acquire(blocking=False):
            return

        if self.batteries.acquire(blocking=False):
            if self.pause_start:
                print(f"{self.name} - flight unpaused - {time} ({time - self.pause_start})")
                self.pause_start = None
            self.flights.append(Window(start=time, end=time + self.flight_time))
            print(f"{self.name} - flight started - {time}")
        else:
            self.drones.release()
            if not self.pause_start:
                self.pause_start = time
                print(f"{self.name} - flights paused - {time}")

    def finish_flight(self, flight, time):
        self.flights.remove(flight)
        self.drones.release()
        self.empty_batteries += 1
        print(f"{self.name} - flight ended - {time}")

    def finish_flights(self, time, force=False):
        for flight in self.flights.copy():
            if force or flight.end <= time:
                self.finish_flight(flight, time)

    def start_charging(self, time):
        if self.empty_batteries and self.chargers.acquire(blocking=False):
            self.chargings.append(Window(start=time, end=time + self.charge_time))
            self.empty_batteries -= 1
            print(f"{self.name} - charging started - {time}")
    
    def finish_charging(self, time):
        for charging in self.chargings.copy():
            if charging.end <= time:
                self.chargings.remove(charging)
                self.batteries.release()
                self.chargers.release()
                self.consumed_wh += self.wh
                print(f"{self.name} - charging ended - {time}")


def run(drones, devices, stations, generator, start, end, sunset, sunrise):
    time = start
    while time < end:
        for drone in drones:
            drone.finish_flights(time)
            drone.finish_charging(time)
            drone.start_charging(time)
            drone.start_flights(time, sunset, sunrise)
        time += ONE_MINUTE
    else:
        for drone in drones:
            drone.finish_flights(time, force=True)
    
    hours = (end - start).total_seconds() / 60 / 60
    wh_consumed_by_devices = 0
    for device in devices:
        wh_consumed_by_devices = device.n * device.w * hours

    wh_capacity = sum(station.wh for station in stations)
    wh_consumed = sum(drone.consumed_wh for drone in drones) + wh_consumed_by_devices
    wh_charged_per_hour = sum(station.wh * 60 / station.charge_time for station in stations)
    fuel_required = round((wh_consumed - wh_capacity) / wh_charged_per_hour * generator.consumption, 2)
    generator_running_h = round(fuel_required / generator.consumption, 2)

    print("Mission ended.")
    print("Consumed Wh", wh_consumed)
    print("Generator fuel liters required", fuel_required)
    print("Generator will run for hours", generator_running_h)
