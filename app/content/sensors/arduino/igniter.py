from asyncio import Future, Task
from datetime import timedelta
from typing import Collection, Iterable, Tuple, Type, Union, cast
from uuid import UUID

from dataclasses import dataclass
from app.content.general_commands.enable import DisableCommand, EnableCommand
from app.content.motor_commands.open import OpenCommand, CloseCommand, IgniteCommand
from app.logic.commands.command import Command, Command
from app.content.general_commands.enable import DisableCommand, EnableCommand, ResetCommand
from app.content.microcontroller.arduino_serial import ArduinoSerial
from app.logic.rocket_definition import Part, Rocket

from kivy.utils import platform


class IgniterSensor(Part):
    type = 'Igniter'

    enabled: bool = True

    min_update_period = timedelta(milliseconds=1000)

    min_measurement_period = timedelta(milliseconds=1000)

    arduino: Union[ArduinoSerial, None]


    state: str

    def __init__(self, _id: UUID, name: str, parent: Union[Part, Rocket, None], arduino_parent: Union[ArduinoSerial, None],start_enabled=True):
        self.arduino = arduino_parent
        self.enabled = start_enabled
        self.state = 'ready'
        super().__init__(_id, name, parent, list())  # type: ignore


    def get_accepted_commands(self) -> list[Type[Command]]:
        return [IgniteCommand]

    def update(self, commands: Iterable[Command], now, iteration):
        for c in commands:
            if isinstance(c, IgniteCommand):
                if c.state == 'received':
                    self.arduino.send_message(bytearray([0x7E, 0xFF, 0x4F, 0x02, 0x01, 0x7E]))
                    c.state = 'processing'
                    staet = 'processing'

                elif c.state == 'processing':
                    state = self.arduino.hz(0x02)
                    if state:
                        c.state = state
            else:
                c.state = 'failed'  # Part cannot handle this command
                continue

    # def add_command_to_queue(command_code: int, payload):

    def get_measurement_shape(self) -> Iterable[Tuple[str, Type]]:
        return [
            ('enabled', int),
            ('Ignited', int),
        ]

    def collect_measurements(self, now, iteration) -> Iterable[Iterable[Union[int, int]]]:
        return [[1 if self.enabled else 0, 1 if self.state is 'ignited' else 0]]