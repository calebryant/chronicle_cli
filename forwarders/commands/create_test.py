# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Unit tests for create.py."""

import json
import os
from unittest import mock

from click._compat import WIN
from click.testing import CliRunner

from forwarders.commands.create import create
from forwarders.tests.fixtures import create_backup_file
from forwarders.tests.fixtures import TEMP_CREATE_BACKUP_FILE
from mock_test_utility import MockResponse

runner = CliRunner()


@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.preview_changes"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_credential_file_invalid(
    mock_input: mock.MagicMock, mock_client: mock.MagicMock,
    mock_backup_file: mock.MagicMock, mock_prepare_request_body: mock.MagicMock,
    mock_preview_changes: mock.MagicMock, mock_choice: mock.MagicMock) -> None:
  """Test case for checking invalid credential path.

  Args:
    mock_input: Mock object for click prompt.
    mock_client: Mock object for client.
    mock_backup_file: Mock object for backup file.
    mock_prepare_request_body: Mock object for prepare_request_body method.
    mock_preview_changes: Mock object for preview_changes method.
    mock_choice: Mock object for click confirm.
  """
  mock_input.return_value = "123"
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.side_effect = OSError(
      "Credential Path not found.")
  mock_backup_file.return_value = {}
  mock_prepare_request_body.return_value = {}
  mock_preview_changes.return_value = mock.Mock()
  mock_choice.return_value = True
  expected_message = "Failed with exception: Credential Path not found."
  result = runner.invoke(create, ["--credential_file", "dummy.json"])
  assert expected_message in result.output


@mock.patch(
    "forwarders.commands.create.create_collector.create_collector"
)
@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_success(mock_input: mock.MagicMock, mock_client: mock.MagicMock,
                        mock_backup_file: mock.MagicMock,
                        mock_prepare_request_body: mock.MagicMock,
                        mock_choice: mock.MagicMock,
                        mock_collector: mock.MagicMock) -> None:
  """Test case to check successful creation of forwarder.

  Args:
    mock_input: Mock object for click prompt.
    mock_client: Mock object for client.
    mock_backup_file: Mock object for backup file.
    mock_prepare_request_body: Mock object for prepare_request_body method.
    mock_choice: Mock object for click confirm.
    mock_collector: Mock object for create_collector method.
  """
  mock_input.return_value = "123"
  mock_prepare_request_body.return_value = {"display_name": "test"}
  mock_choice.side_effect = [True, True, False]
  mock_backup_file.return_value = {}
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.return_value = MockResponse(
      status_code=200, text="""{"name": "forwarder/123"}""")
  mock_collector.return_value = mock.Mock()
  result = runner.invoke(create)

  if WIN:
    assert """Preview changes:

  - Press ENTER key (scrolls one line at a time) or SPACEBAR key (display next screen).
  - Press 'q' to quit and confirm preview changes.
=============================================================================""" in result.output
  else:
    assert """Preview changes:

  - Press Up/b or Down/z keys to paginate.
  - To switch case-sensitivity, press '-i' and press enter. By default, search
    is case-sensitive.
  - To search for specific field, press '/' key, enter text and press enter.
  - Press 'q' to quit and confirm preview changes.
  - Press `h` for all the available options to navigate the list.
=============================================================================""" in result.output

  assert """Display name: test


Creating forwarder...
Forwarder created successfully with Forwarder ID: 123""" in result.output


@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.preview_changes"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_error_code(mock_input: mock.MagicMock,
                           mock_client: mock.MagicMock,
                           mock_backup_file: mock.MagicMock,
                           mock_prepare_request_body: mock.MagicMock,
                           mock_preview_changes: mock.MagicMock,
                           mock_choice: mock.MagicMock) -> None:
  """Test case to check failure of creation of forwarder.

  Args:
    mock_input: Mock object for click prompt.
    mock_client: Mock object for client.
    mock_backup_file: Mock object for backup file.
    mock_prepare_request_body: Mock object for prepare_request_body method.
    mock_preview_changes: Mock object for preview_changes method.
    mock_choice: Mock object for click confirm.
  """
  mock_input.return_value = "123"
  mock_prepare_request_body.return_value = {}
  mock_preview_changes.return_value = mock.Mock()
  mock_choice.side_effect = [True, False, False]
  mock_backup_file.return_value = {}
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.return_value = MockResponse(
      status_code=400, text="""{"error": {"message": "sample"}}""")

  result = runner.invoke(create)

  expected_output = ("Error occurred while creating forwarder.\nResponse Code: "
                     "400.\nError: sample")
  assert expected_output in result.output


@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.preview_changes"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_verbose(mock_input: mock.MagicMock, mock_client: mock.MagicMock,
                        mock_backup_file: mock.MagicMock,
                        mock_prepare_request_body: mock.MagicMock,
                        mock_preview_changes: mock.MagicMock,
                        mock_choice: mock.MagicMock) -> None:
  """Test case to check creation of forwarder with verbose.

  Args:
    mock_input: Mock object for click prompt.
    mock_client: Mock object for client.
    mock_backup_file: Mock object for backup file.
    mock_prepare_request_body: Mock object for prepare_request_body method.
    mock_preview_changes: Mock object for preview_changes method.
    mock_choice: Mock object for click confirm.
  """
  mock_input.return_value = "123"
  mock_prepare_request_body.return_value = {}
  mock_preview_changes.return_value = mock.Mock()
  mock_choice.side_effect = [True, False, False]
  mock_backup_file.return_value = {}
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.return_value = MockResponse(
      status_code=200, text="""{"name": "forwarder/123"}""")
  result = runner.invoke(create, ["--verbose"])
  assert """Creating forwarder...
Forwarder created successfully with Forwarder ID: 123
==========================================
========== HTTP Request Details ==========
==========================================
Request:
  URL: https://backstory.googleapis.com/v2/forwarders
  Method: POST
  Body: {}
Response:
  Body: {'name': 'forwarder/123'}""" in result.output


@mock.patch(
    "forwarders.commands.create.CREATE_FORWARDER_BACKUP_FILE",
    TEMP_CREATE_BACKUP_FILE)
@mock.patch(
    "forwarders.commands.create.create_collector.create_collector"
)
@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.preview_changes"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_backup_file_present_success(
    mock_input: mock.MagicMock, mock_client: mock.MagicMock,
    mock_backup_file: mock.MagicMock, mock_prepare_request_body: mock.MagicMock,
    mock_preview_changes: mock.MagicMock, mock_choice: mock.MagicMock,
    mock_collector: mock.MagicMock) -> None:
  """Test case to check backup file is removed after successful creation of forwarder.

  Args:
    mock_input: Mock object for click prompt
    mock_client: Mock object for client
    mock_backup_file: Mock object for backup file
    mock_prepare_request_body: Mock object for prepare_request_body method
    mock_preview_changes: Mock object for preview_changes method
    mock_choice: Mock object for click confirm
    mock_collector: Mock object for create_collector method
  """
  content = {
      "displayName": "sample",
      "max_bytes_per_batch": 1048576,
      "max_seconds_per_batch": 10,
      "logType": "sample_log"
  }
  create_backup_file(TEMP_CREATE_BACKUP_FILE, content)
  mock_input.return_value = "123"
  mock_backup_file.return_value = {}
  req_body = {
      "config": {
          "file_settings": {
              "file_path": "sample_folder/sample_file.txt"
          },
          "log_type": "sample_log",
          "max_bytes_per_batch": 1048576,
          "max_seconds_per_batch": 10
      },
      "display_name": "sample"
  }
  mock_prepare_request_body.return_value = req_body
  mock_preview_changes.return_value = mock.Mock()
  mock_choice.side_effect = [True, False, False]
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.return_value = MockResponse(
      status_code=200, text="""{"name": "forwarder/123"}""")
  mock_collector.return_value = mock.Mock()
  result = runner.invoke(create)

  assert "Forwarder created successfully with Forwarder ID: 123" in result.output
  assert not os.path.exists(TEMP_CREATE_BACKUP_FILE)


@mock.patch(
    "forwarders.commands.create.CREATE_FORWARDER_BACKUP_FILE",
    TEMP_CREATE_BACKUP_FILE)
@mock.patch(
    "forwarders.commands.create.create_collector.create_collector"
)
@mock.patch(
    "forwarders.commands.create.click.confirm"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.preview_changes"
)
@mock.patch(
    "forwarders.commands.create.schema_utility.Schema.prepare_request_body"
)
@mock.patch(
    "forwarders.commands.create.forwarder_utility.read_backup"
)
@mock.patch(
    "forwarders.commands.create.chronicle_auth.initialize_http_session"
)
@mock.patch(
    "forwarders.commands.create.click.prompt")
def test_create_backup_file_present_400(
    mock_input: mock.MagicMock, mock_client: mock.MagicMock,
    mock_backup_file: mock.MagicMock, mock_prepare_request_body: mock.MagicMock,
    mock_preview_changes: mock.MagicMock, mock_choice: mock.MagicMock,
    mock_collector: mock.MagicMock) -> None:
  """Test case to check backup file is created if forwarder creation fails.

  Args:
    mock_input: Mock object for click prompt
    mock_client: Mock object for client
    mock_backup_file: Mock object for backup file
    mock_prepare_request_body: Mock object for prepare_request_body method
    mock_preview_changes: Mock object for preview_changes method
    mock_choice: Mock object for click confirm
    mock_collector: Mock object for create_collector method
  """
  content = {
      "displayName": "sample",
      "max_bytes_per_batch": 1048576,
      "max_seconds_per_batch": 10,
      "logType": "sample_log"
  }
  create_backup_file(TEMP_CREATE_BACKUP_FILE, content)
  mock_input.return_value = "123"
  mock_backup_file.return_value = {}
  req_body = {
      "config": {
          "file_settings": {
              "file_path": "sample_folder/sample_file.txt"
          },
          "log_type": "sample_log",
          "max_bytes_per_batch": 1048576,
          "max_seconds_per_batch": 10
      },
      "display_name": "sample"
  }
  mock_prepare_request_body.return_value = req_body
  mock_preview_changes.return_value = mock.Mock()
  mock_choice.side_effect = [True, False, False]
  mock_client.return_value = mock.Mock()
  mock_client.return_value.request.return_value = MockResponse(
      status_code=400, text="""{"error": {"message": "sample"}}""")
  mock_collector.return_value = mock.Mock()
  result = runner.invoke(create)

  expected_output = ("Error occurred while creating forwarder.\nResponse Code: "
                     "400.\nError: sample")
  assert expected_output in result.output
  assert os.path.exists(TEMP_CREATE_BACKUP_FILE)

  with open(TEMP_CREATE_BACKUP_FILE) as file:
    data = json.load(file)
  assert data == req_body
