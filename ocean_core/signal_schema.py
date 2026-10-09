#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import uuid
from typing import Any, Dict

from pydantic import BaseModel, Field


class SignalPulse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str
    type: str
    timestamp: float = Field(default_factory=lambda: time.time())
    payload: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
