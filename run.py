from gamenacki.lostcitinacki import LostCities
from gamenacki.lostcitinacki.players import BotPlayer, ConsolePlayer
from gamenacki.lostcitinacki import ConsoleRenderer

LostCities([ConsolePlayer(0, 'Nacki'), BotPlayer(1, 'BullBot')], ConsoleRenderer()).play()
