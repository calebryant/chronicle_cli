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
"""Parser utility functions."""

import base64
import click

from typing import Dict


def decode_log(log: str) -> str:
  """Decode the log data from the response.

  Args:
    log: Encoded log

  Returns:
    Decoded log
  """
  log_bytes = base64.b64decode(log)
  return log_bytes.decode(encoding='utf-8', errors='surrogateescape')


def process_resource_name(name: str) -> Dict[str, str]:
  """Extract resource components from the resource name.

  Args:
    name (str): The resource name

  Returns:
    (Dict): Resource components
  """
  processed_fields = {}
  name_split = name.split('/')
  for i in range(0, len(name_split), 2):
    processed_fields[name_split[i]] = name_split[i + 1]
  return processed_fields


def json_to_dot_notation(obj, parent=""):
    if isinstance(obj, dict):
        if obj:
          for k in obj.keys():
            next_key = parent + "." + str(k) if parent != "" else str(k)
            json_to_dot_notation(obj[k], next_key)
        else:
          click.echo("\t\t{} : {}".format(parent,"{}"))
    elif isinstance(obj, list):
        if obj:
          for i,k in enumerate(obj):
            next_key = parent + "." + str(i) if parent != "" else str(i)
            json_to_dot_notation(k, parent + "." + str(i))
        else:
          click.echo("\t\t{} : []".format(parent,"{}"))
    else:
        click.echo("\t\t{} : {}".format(parent,str(obj)))