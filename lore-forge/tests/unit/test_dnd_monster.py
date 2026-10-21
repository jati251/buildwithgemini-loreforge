# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from unittest.mock import MagicMock, patch
from app.agent import lookup_dnd_monster_stats


def test_lookup_dnd_monster_stats_success():
    mock_data = {
        "name": "Goblin",
        "size": "Small",
        "type": "humanoid",
        "alignment": "neutral evil",
        "challenge_rating": 0.25,
        "hit_points": 7,
        "hit_points_roll": "2d6",
        "armor_class": [{"value": 15}],
        "strength": 8,
        "dexterity": 14,
        "constitution": 10,
        "intelligence": 10,
        "wisdom": 8,
        "charisma": 8,
        "actions": [{"name": "Scimitar"}, {"name": "Shortbow"}]
    }

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps(mock_data).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = lookup_dnd_monster_stats("goblin")
        assert "Monster Stat Block: Goblin" in result
        assert "0.25" in result
        assert "15" in result


def test_lookup_dnd_monster_stats_empty_query():
    result = lookup_dnd_monster_stats("")
    assert "Please provide a monster name or query" in result
