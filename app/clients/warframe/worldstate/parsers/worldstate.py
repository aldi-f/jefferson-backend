from msgspec import Struct, field

from app.clients.warframe.worldstate.parsers.alert import Alert
from app.clients.warframe.worldstate.parsers.archon import ArchonHunt
from app.clients.warframe.worldstate.parsers.baro import Baro
from app.clients.warframe.worldstate.parsers.circuit import Circuit
from app.clients.warframe.worldstate.parsers.darvo import Darvo
from app.clients.warframe.worldstate.parsers.fissure import Fissure
from app.clients.warframe.worldstate.parsers.nightwave import Nightwave
from app.clients.warframe.worldstate.parsers.sortie import Sortie


class WorldstateModel(Struct, kw_only=True):
    version: int = field(name="Version")
    mobile_version: str = field(name="MobileVersion")
    build_label: str = field(name="BuildLabel")
    time: int = field(name="Time")

    # Alerts
    alerts: list[Alert] = field(name="Alerts", default_factory=list)

    # Archon hunt:
    lite_sorties: list[ArchonHunt] = field(name="LiteSorties")

    # Baro
    void_traders: list[Baro] = field(name="VoidTraders")

    # Circuit
    circuits: list[Circuit] = field(name="EndlessXpChoices")

    # Darvo deals
    daily_deals: list[Darvo] = field(name="DailyDeals")

    # Fissures
    active_missions: list[Fissure] = field(name="ActiveMissions")

    # Nightwave
    season_info: Nightwave = field(name="SeasonInfo")

    # Sortie
    sorties: list[Sortie] = field(name="Sorties")
