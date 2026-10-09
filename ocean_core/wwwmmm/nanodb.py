# -*- coding: utf-8 -*-
"""WWWMMM NodeDB - fluid in-memory graph store."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class NanoNode:
	node_id: str
	kind: str
	payload: Dict[str, Any]
	created_at: float = field(default_factory=time.time)
	edges: Set[str] = field(default_factory=set)


class NodeDB:
	def __init__(self):
		self._nodes: Dict[str, NanoNode] = {}

	def create_node(self, kind: str, payload: Dict[str, Any]) -> str:
		node_id = f"{kind}_{uuid.uuid4().hex[:10]}"
		self._nodes[node_id] = NanoNode(node_id=node_id, kind=kind, payload=payload)
		return node_id

	def connect(self, node_a: str, node_b: str) -> bool:
		a = self._nodes.get(node_a)
		b = self._nodes.get(node_b)
		if not a or not b:
			return False
		a.edges.add(node_b)
		b.edges.add(node_a)
		return True

	def get_node(self, node_id: str) -> Optional[NanoNode]:
		return self._nodes.get(node_id)

	def neighbors(self, node_id: str) -> List[NanoNode]:
		node = self._nodes.get(node_id)
		if not node:
			return []
		return [self._nodes[nid] for nid in node.edges if nid in self._nodes]

	@property
	def stats(self) -> Dict[str, Any]:
		return {"nodes": len(self._nodes)}


_nanodb_instance: Optional[NodeDB] = None


def get_nanodb() -> NodeDB:
	global _nanodb_instance
	if _nanodb_instance is None:
		_nanodb_instance = NodeDB()
	return _nanodb_instance

