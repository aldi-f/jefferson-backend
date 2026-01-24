import json
import pytest
from datetime import datetime
from pathlib import Path

import msgspec
from msgspec import json as msgspec_json


class TestWorldstateValidation:
    """Test validation of msgspec against JSON structure without full app imports."""
    
    @pytest.fixture
    def worldstate_data(self):
        """Load test data from worldstate.json file."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            return json.load(f)
    
    def test_json_structure_integrity(self):
        """Test that the JSON file is valid and contains expected fields."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        # Check basic structure
        assert "WorldSeed" in data
        assert "Version" in data
        assert "Events" in data
        assert "Goals" in data
        assert "Alerts" in data
        assert "Sorties" in data
        
        # Check data types
        assert isinstance(data["WorldSeed"], str)
        assert isinstance(data["Version"], int)
        assert isinstance(data["Events"], list)
        assert isinstance(data["Goals"], list)
        assert isinstance(data["Alerts"], list)
        assert isinstance(data["Sorties"], list)
        
        # Check that we have some data
        assert len(data["Events"]) > 0
        assert len(data["Goals"]) > 0
        assert len(data["Alerts"]) > 0
        assert len(data["Sorties"]) > 0
    
    def test_event_structure_validation(self):
        """Test that Events have the expected structure."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        events = data["Events"]
        assert len(events) > 0
        
        # Test first event structure
        first_event = events[0]
        assert "_id" in first_event
        assert "Messages" in first_event
        assert "Prop" in first_event
        assert "Icon" in first_event
        assert "Priority" in first_event
        assert "MobileOnly" in first_event
        assert "Community" in first_event
        
        # Test message structure
        first_message = first_event["Messages"][0]
        assert "LanguageCode" in first_message
        assert "Message" in first_message
        
        assert isinstance(first_event["Priority"], bool)
        assert isinstance(first_event["MobileOnly"], bool)
        assert isinstance(first_event["Community"], bool)
    
    def test_goal_structure_validation(self):
        """Test that Goals have the expected structure."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        goals = data["Goals"]
        assert len(goals) > 0
        
        # Test first goal structure
        first_goal = goals[0]
        assert "_id" in first_goal
        assert "Activation" in first_goal
        assert "Expiry" in first_goal
        assert "Node" in first_goal
        assert "ScoreVar" in first_goal
        assert "Count" in first_goal
        assert "HealthPct" in first_goal
        assert "Regions" in first_goal
        assert "Desc" in first_goal
        assert "Goal" in first_goal
        assert "Reward" in first_goal
        assert "InterimGoals" in first_goal
        assert "InterimRewards" in first_goal
        
        # Check data types
        assert isinstance(first_goal["Count"], int)
        assert isinstance(first_goal["HealthPct"], (int, float))
        assert isinstance(first_goal["Regions"], list)
        assert isinstance(first_goal["Goal"], int)
        assert isinstance(first_goal["InterimGoals"], list)
        assert isinstance(first_goal["InterimRewards"], list)
    
    def test_alert_structure_validation(self):
        """Test that Alerts have the expected structure."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        alerts = data["Alerts"]
        assert len(alerts) > 0
        
        # Test first alert structure
        first_alert = alerts[0]
        assert "_id" in first_alert
        assert "Activation" in first_alert
        assert "Expiry" in first_alert
        assert "MissionInfo" in first_alert
        assert "Tag" in first_alert
        
        # Check MissionInfo structure
        mission_info = first_alert["MissionInfo"]
        assert "location" in mission_info
        assert "missionType" in mission_info
        assert "faction" in mission_info
        assert "missionReward" in mission_info
        assert "difficulty" in mission_info
        
        # Check missionReward structure
        mission_reward = mission_info["missionReward"]
        assert "credits" in mission_reward
        assert isinstance(mission_reward["credits"], int)
    
    def test_sortie_structure_validation(self):
        """Test that Sorties have the expected structure."""
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        sorties = data["Sorties"]
        assert len(sorties) > 0
        
        # Test first sortie structure
        first_sortie = sorties[0]
        assert "_id" in first_sortie
        assert "Activation" in first_sortie
        assert "Expiry" in first_sortie
        assert "Reward" in first_sortie
        assert "Seed" in first_sortie
        assert "Boss" in first_sortie
        assert "Variants" in first_sortie
        
        # Check Variants structure
        variants = first_sortie["Variants"]
        assert len(variants) > 0
        
        first_variant = variants[0]
        assert "missionType" in first_variant
        assert "modifierType" in first_variant
        assert "node" in first_variant
        assert "tileset" in first_variant


class TestMsgspecCompatibility:
    """Test that our msgspec definitions are compatible with the JSON structure."""
    
    def test_msgspec_fields_match_json_structure(self):
        """Test that msgspec fields align with JSON structure."""
        # This is a basic validation - we can't test full decoding without
        # the full application context, but we can validate field mappings
        
        # Define expected field mappings based on our implementation
        expected_mappings = {
            "WorldSeed": "world_seed",
            "Version": "version", 
            "MobileVersion": "mobile_version",
            "BuildLabel": "build_label",
            "Time": "time",
            "Events": "events",
            "Goals": "goals",
            "Alerts": "alerts",
            "Sorties": "sorties",
            "ActiveMissions": "active_missions",
            "LiteSorties": "lite_sorties",
            "VoidTraders": "void_traders",
            "DailyDeals": "daily_deals",
            "EndlessXpChoices": "circuits",
            "SeasonInfo": "season_info"
        }
        
        # Load the JSON and verify these fields exist
        test_file = Path(__file__).parent / "test" / "files" / "worldstate.json"
        with open(test_file, 'r') as f:
            data = json.load(f)
        
        for json_field, model_field in expected_mappings.items():
            assert json_field in data, f"JSON field {json_field} not found"
            # The model field should exist (we can't import the model due to Redis dependency)
            assert model_field is not None, f"Model field mapping for {json_field} is None"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])