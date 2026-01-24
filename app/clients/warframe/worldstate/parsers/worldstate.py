import msgspec
from msgspec import field

from app.clients.warframe.worldstate.parsers.alert import Alert
from app.clients.warframe.worldstate.parsers.archon import ArchonHunt
from app.clients.warframe.worldstate.parsers.baro import Baro
from app.clients.warframe.worldstate.parsers.circuit import Circuit
from app.clients.warframe.worldstate.parsers.darvo import Darvo
from app.clients.warframe.worldstate.parsers.event import Event
from app.clients.warframe.worldstate.parsers.fissure import Fissure
from app.clients.warframe.worldstate.parsers.goal import Goal
from app.clients.warframe.worldstate.parsers.invasion import Invasion
from app.clients.warframe.worldstate.parsers.nightwave import Nightwave
from app.clients.warframe.worldstate.parsers.prime_vault_trader import PrimeVaultTrader
from app.clients.warframe.worldstate.parsers.sortie import Sortie
from app.clients.warframe.worldstate.parsers.void_storm import VoidStorm

# Use defstruct for msgspec 0.19.0 compatibility
WorldstateModel = msgspec.defstruct(
    "WorldstateModel",
    [
        "WorldSeed", "Version", "MobileVersion", "BuildLabel", "Time",
        "Events", "Goals", "FlashSales", "SkuSales", "InGameMarket", "Invasions", 
        "HubEvents", "NodeOverrides", "VoidStorms", "PrimeVaultTraders", 
        "PrimeVaultAvailabilities", "PrimeTokenAvailability", "LibraryInfo", 
        "PVPChallengeInstances", "PersistentEnemies", "PVPAlternativeModes", 
        "PVPActiveTournaments", "ProjectPct", "ConstructionProjects", "TwitchPromos", 
        "ExperimentRecommended", "ForceLogoutVersion", "FeaturedGuilds", 
        "KnownCalendarSeasons", "Conquests", "Descents", "Alerts", "LiteSorties", 
        "Sorties", "VoidTraders", "DailyDeals", "EndlessXpChoices", "SeasonInfo", 
        "ActiveMissions", "GlobalUpgrades", "SyndicateMissions", "Tmp"
    ]
)
