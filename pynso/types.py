# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Mypy Types needed for pynso-restconf."""

from typing import Any, Dict, Union

__all__ = ["Params", "JSON"]

Params = Dict[str, Union[str, int, bool]]
"""Dictionary of query string parametes.

See NSO documentation for meaning of possible parameters:

- commit-queue
- commit-queue-atomic
- commit-queue-block-others
- commit-queue-lock
- commit-queue-tag
- commit-queue-timeout
- commit-queue-error-option
- depth
- dry-run
- dry-run-reverse
- insert
- no-networking
- no-out-of-sync-check
- no-overwrite
- no-revision-drop
- no-deploy
- no-lsa
- point
- rollback-comment
- rollback-label
- fields
- unhide
- use-lsa
- with-defaults

"""

JSON = Any
