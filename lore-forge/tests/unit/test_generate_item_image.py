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

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from google.adk.tools import ToolContext
from app.agent import generate_item_image, root_agent


def test_generate_item_image_tool_registration():
    tool_names = [
        t.name if hasattr(t, "name") else getattr(t, "__name__", str(t))
        for t in root_agent.tools
    ]
    assert "generate_item_image" in tool_names


def test_generate_item_image_success():
    fake_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIFfakeimagebytes"
    mock_part = MagicMock()
    mock_part.inline_data.data = fake_bytes
    mock_part.inline_data.mime_type = "image/jpeg"

    mock_response = MagicMock()
    mock_response.candidates = [MagicMock()]
    mock_response.candidates[0].content.parts = [mock_part]

    mock_genai_client = MagicMock()
    mock_genai_client.models.generate_content.return_value = mock_response

    mock_blob = MagicMock()
    mock_bucket = MagicMock()
    mock_bucket.blob.return_value = mock_bucket_blob = mock_blob
    mock_storage_client = MagicMock()
    mock_storage_client.bucket.return_value = mock_bucket

    mock_tool_context = MagicMock(spec=ToolContext)
    mock_tool_context.save_artifact = AsyncMock()

    with patch("google.genai.Client", return_value=mock_genai_client) as mock_client_cls, \
         patch("google.cloud.storage.Client", return_value=mock_storage_client):

        url = asyncio.run(
            generate_item_image(
                prompt="an enchanted dragon sword",
                tool_context=mock_tool_context,
            )
        )

        assert url.startswith("https://storage.googleapis.com/loreforge-assets-0f9a780981ba/")
        assert url.endswith(".jpg")
        mock_client_cls.assert_called_once_with(
            vertexai=True,
            project="qwiklabs-gcp-04-0f9a780981ba",
            location="global",
        )
        mock_tool_context.save_artifact.assert_awaited_once()
        mock_blob.upload_from_string.assert_called_once_with(
            fake_bytes, content_type="image/jpeg"
        )
