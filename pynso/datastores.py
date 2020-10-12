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

"""Datastore type enum."""

from enum import Enum

__all__ = ["DatastoreType"]


class DatastoreType(Enum):
    """
    An enum of the resource types in the API.

    By default all calls to NSO operate on the unified data store.
    If you want only operational or config data one can use NONCONFIG or CONFIG respectively.

    """

    UNIFIED = "all"
    """
    Work on both datastores

    This corrensponds with using the default content=all query parameter or no content query parameter
    """

    CONFIG = "config"
    """
    Only work on the config datastore.

    This corrensponds with using the content=config query parameter
    """

    NONCONFIG = "nonconfig"
    """
    Only work on the operational datastore.

    This corrensponds with using the content=config query parameter
    """
