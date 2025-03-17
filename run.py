from lostcitinacki.engine import LostCities
from lostcitinacki.players import BotPlayer, ConsolePlayer
from lostcitinacki.renderers import ConsoleRenderer

LostCities([ConsolePlayer(0, 'Nacki'), BotPlayer(1, 'BullBot')], ConsoleRenderer()).play()
