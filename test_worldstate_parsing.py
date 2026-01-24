import json
import pytest
from datetime import datetime
from pathlib import Path

import msgspec
from msgspec import json as msgspec_json

from app.clients.warframe.worldstate.parsers.worldstate import WorldstateModel
from app.clients.warframe.worldstate.parsers.event import Event, _Message, _Link
from app.clients.warframe.worldstate.parsers.goal import Goal, _Reward, _InterimReward
from app.clients.warframe.worldstate.parsers.invasion import Invasion, _Reward as InvasionReward
from app.clients.warframe.worldstate.parsers.void_storm import VoidStorm
from app.clients.warframe.worldstate.parsers.prime_vault_trader import PrimeVaultTrader


@pytest.fixture
def worldstate_data():
    """Load test data from worldstate.json file."""
    test_file = Path(__file__).parent.parent / "files" / "worldstate.json"
    with open(test_file, 'r') as f:
        return json.load(f)


class TestWorldstateModel:
    """Test the main WorldstateModel against the example JSON."""
    
    def test_model_can_decode_example_data(self, worldstate_data):
        """Test that the WorldstateModel can successfully decode the example JSON."""
        try:
            model = msgspec_json.decode(json.dumps(worldstate_data), type=WorldstateModel)
            assert model is not None
            assert model.world_seed is not None
            assert model.version == 10
            assert model.mobile_version == "5.3.0.0"
            assert model.build_label is not None
            assert model.time == 1769279832
        except Exception as e:
            pytest.fail(f"WorldstateModel failed to decode example data: {e}")
    
    def test_all_top_level_fields_present(self, worldstate_data):
        """Test that all top-level fields from JSON are present in the model."""
        model = msgspec_json.decode(json.dumps(worldstate_data), type=WorldstateModel)
        
        # Check basic fields
        assert hasattr(model, 'world_seed')
        assert hasattr(model, 'version')
        assert hasattr(model, 'mobile_version')
        assert hasattr(model, 'build_label')
        assert hasattr(model, 'time')
        
        # Check arrays that should be present
        assert hasattr(model, 'events')
        assert hasattr(model, 'goals')
        assert hasattr(model, 'invasions')
        assert hasattr(model, 'void_storms')
        assert hasattr(model, 'prime_vault_traders')
        assert hasattr(model, 'alerts')
        assert hasattr(model, 'sorties')
        assert hasattr(model, 'active_missions')


class TestEventParser:
    """Test the Event parser against example data."""
    
    def test_event_parsing(self, worldstate_data):
        """Test that Events can be parsed correctly."""
        events = worldstate_data["Events"]
        assert len(events) > 0
        
        # Test first event
        first_event = events[0]
        event = Event(**first_event)
        
        assert event._id is not None
        assert len(event.messages) > 0
        assert event.prop == "https://discord.com/invite/playwarframe"
        assert event.icon == "/Lotus/Interface/Icons/DiscordIconNoBacker.png"
        assert event.priority is False
        assert event.mobile_only is False
        assert event.community is True
        
        # Test message parsing
        first_message = event.messages[0]
        assert first_message.language_code == "en"
        assert first_message.message == "/Lotus/Language/CommunityMessages/JoinDiscord"
    
    def test_event_with_optional_fields(self, worldstate_data):
        """Test parsing of events with optional fields."""
        # Find an event with optional fields
        event_with_optional = None
        event_data_for_optional = None
        for event_data in worldstate_data["Events"]:
            if "ImageUrl" in event_data:
                event_with_optional = Event(**event_data)
                event_data_for_optional = event_data
                break
        
        if event_with_optional:
            assert event_with_optional.image_url is not None
            # Test date parsing if present
            if event_data_for_optional and "Date" in event_data_for_optional and isinstance(event_data_for_optional["Date"], dict):
                assert isinstance(event_with_optional.date, datetime)


class TestGoalParser:
    """Test the Goal parser against example data."""
    
    def test_goal_parsing(self, worldstate_data):
        """Test that Goals can be parsed correctly."""
        goals = worldstate_data["Goals"]
        assert len(goals) > 0
        
        # Test first goal
        first_goal = goals[0]
        goal = Goal(**first_goal)
        
        assert goal._id is not None
        assert isinstance(goal.activation, datetime)
        assert isinstance(goal.expiry, datetime)
        assert goal.node == "SolNode129"
        assert goal.score_var == "FissuresClosed"
        assert goal.count == 4
        assert goal.health_pct == 0.04
        assert goal.regions == [1]
        assert goal.goal_value == 100
        
        # Test reward parsing
        assert goal.reward.credits == 0
        assert goal.reward.xp == 0
        assert len(goal.reward.items) == 1
        assert goal.reward.items[0] == "/Lotus/StoreItems/Weapons/Corpus/LongGuns/CrpBFG/Vandal/VandalCrpBFG"
        
        # Test interim goals and rewards
        assert goal.interim_goals == [5, 25, 50, 75]
        assert len(goal.interim_rewards) == 4


class TestInvasionParser:
    """Test the Invasion parser against example data."""
    
    def test_invasion_parsing(self, worldstate_data):
        """Test that Invasions can be parsed correctly."""
        invasions = worldstate_data.get("Invasions", [])
        if not invasions:
            pytest.skip("No invasions in test data")
        
        first_invasion = invasions[0]
        invasion = Invasion(**first_invasion)
        
        assert invasion._id is not None
        assert invasion.faction is not None
        assert invasion.defender_faction is not None
        assert invasion.node is not None
        assert invasion.count >= 0
        assert invasion.goal > 0
        assert isinstance(invasion.completed, bool)
        assert invasion.chain_id is not None
        
        # Test reward parsing
        assert invasion.attacker_reward.credits >= 0
        assert invasion.attacker_reward.items is not None
        assert invasion.defender_reward.credits >= 0
        assert invasion.defender_reward.items is not None


class TestVoidStormParser:
    """Test the VoidStorm parser against example data."""
    
    def test_void_storm_parsing(self, worldstate_data):
        """Test that VoidStorms can be parsed correctly."""
        void_storms = worldstate_data.get("VoidStorms", [])
        if not void_storms:
            pytest.skip("No void storms in test data")
        
        first_storm = void_storms[0]
        storm = VoidStorm(**first_storm)
        
        assert storm._id is not None
        assert storm.node is not None
        assert isinstance(storm.activation, datetime)
        assert isinstance(storm.expiry, datetime)
        assert storm.seed > 0
        assert storm.modifier is not None


class TestPrimeVaultTraderParser:
    """Test the PrimeVaultTrader parser against example data."""
    
    def test_prime_vault_trader_parsing(self, worldstate_data):
        """Test that PrimeVaultTraders can be parsed correctly."""
        traders = worldstate_data.get("PrimeVaultTraders", [])
        if not traders:
            pytest.skip("No prime vault traders in test data")
        
        first_trader = traders[0]
        trader = PrimeVaultTrader(**first_trader)
        
        assert trader._id is not None
        assert isinstance(trader.activation, datetime)
        assert isinstance(trader.expiry, datetime)
        assert trader.node is not None
        assert trader.item is not None
        assert trader.item_icon is not None
        assert trader.item_name is not None
        assert trader.item_rarity is not None
        assert isinstance(trader.vaulted, bool)


class TestAlertParser:
    """Test the Alert parser (existing functionality) against example data."""
    
    def test_alert_parsing(self, worldstate_data):
        """Test that Alerts can be parsed correctly."""
        alerts = worldstate_data["Alerts"]
        assert len(alerts) > 0
        
        # Test first alert
        first_alert = alerts[0]
        from app.clients.warframe.worldstate.parsers.alert import Alert
        alert = Alert(**first_alert)
        
        assert alert._id is not None
        assert isinstance(alert.activation, datetime)
        assert isinstance(alert.expiry, datetime)
        assert alert.tag == "LotusGift"
        assert alert.mission_info.location is not None
        assert alert.mission_info.mission_type is not None
        assert alert.mission_info.faction is not None
        assert alert.mission_info.mission_reward.credits == 10000


class TestValidation:
    """Test validation of msgspec against JSON structure."""
    
    def test_no_missing_fields_in_model(self, worldstate_data):
        """Test that our model doesn't have fields that are missing from the JSON."""
        json_fields = set(worldstate_data.keys())
        model_fields = set(WorldstateModel.__annotations__.keys())
        
        # All model fields should be in JSON or have defaults
        for model_field in model_fields:
            if model_field not in json_fields:
                # Check if field has a default value
                field_obj = WorldstateModel.__annotations__[model_field]
                # If it's a list or dict with default_factory, it's OK
                if hasattr(field_obj, 'default_factory'):
                    continue
                pytest.fail(f"Model field '{model_field}' not found in JSON and has no default")
    
    def test_data_types_match(self, worldstate_data):
        """Test that parsed data types match expectations."""
        model = msgspec_json.decode(json.dumps(worldstate_data), type=WorldstateModel)
        
        # Test basic types
        assert isinstance(model.world_seed, str)
        assert isinstance(model.version, int)
        assert isinstance(model.mobile_version, str)
        assert isinstance(model.time, int)
        
        # Test list types
        assert isinstance(model.events, list)
        assert isinstance(model.goals, list)
        assert isinstance(model.alerts, list)
        assert isinstance(model.sorties, list)
        
        # Test nested structures
        if model.events:
            assert isinstance(model.events[0], Event)
        if model.goals:
            assert isinstance(model.goals[0], Goal)
        if model.alerts:
            from app.clients.warframe.worldstate.parsers.alert import Alert
            assert isinstance(model.alerts[0], Alert)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])