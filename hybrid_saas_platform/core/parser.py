"""
Protocol Parser - Multi-Protocol Input Handler
===============================================
Converts inputs from any protocol (REST, GraphQL, gRPC, Webhook, File)
into the canonical table format.

Maps external data to standard columns:
cycle, layer, variant, input_type, source_protocol
"""

import json
import re
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass
class ParsedInput:
    """Standardized parsed input ready for canonical table"""
    cycle: int
    layer: str
    variant: str
    input_type: str
    source_protocol: str
    raw_data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_canonical_row(self) -> Dict[str, Any]:
        """Convert to canonical row format"""
        return {
            'cycle': self.cycle,
            'layer': self.layer,
            'variant': self.variant,
            'input_type': self.input_type,
            'source_protocol': self.source_protocol,
            'status': 'RAW',
            'metadata': {
                'raw_data': self.raw_data,
                **self.metadata,
                'parsed_at': datetime.utcnow().isoformat()
            }
        }


class ProtocolParser(ABC):
    """Abstract base class for protocol-specific parsers"""
    
    @property
    @abstractmethod
    def protocol_name(self) -> str:
        """Name of the protocol this parser handles"""
        pass
    
    @abstractmethod
    def parse(self, payload: Any) -> ParsedInput:
        """Parse the input payload into standardized format"""
        pass
    
    def extract_layer(self, data: Dict[str, Any]) -> str:
        """Extract or infer layer from data"""
        if 'layer' in data:
            return str(data['layer'])
        # Infer from structure
        if 'api' in str(data).lower():
            return 'L1'  # API Layer
        if 'business' in str(data).lower():
            return 'L2'  # Business Logic Layer
        if 'data' in str(data).lower():
            return 'L3'  # Data Layer
        return 'L1'  # Default
    
    def extract_variant(self, data: Dict[str, Any]) -> str:
        """Extract or infer variant from data"""
        if 'variant' in data:
            return str(data['variant'])
        if 'version' in data:
            return f"v{data['version']}"
        return 'A'  # Default variant


class RESTParser(ProtocolParser):
    """Parser for REST API inputs"""
    
    @property
    def protocol_name(self) -> str:
        return "REST"
    
    def parse(self, payload: Any) -> ParsedInput:
        """
        Parse REST request payload
        
        Expected format:
        {
            "method": "POST",
            "path": "/api/v1/resource",
            "headers": {...},
            "body": {...}
        }
        """
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        body = payload.get('body', payload.get('data', payload))
        
        # Extract cycle from path or body
        cycle = body.get('cycle', 1)
        if isinstance(cycle, str):
            cycle = int(re.search(r'\d+', cycle).group()) if re.search(r'\d+', cycle) else 1
        
        return ParsedInput(
            cycle=cycle,
            layer=self.extract_layer(body),
            variant=self.extract_variant(body),
            input_type=body.get('input_type', body.get('type', 'unknown')),
            source_protocol=self.protocol_name,
            raw_data=payload,
            metadata={
                'method': payload.get('method', 'POST'),
                'path': payload.get('path', '/'),
                'content_type': payload.get('headers', {}).get('Content-Type', 'application/json')
            }
        )


class GraphQLParser(ProtocolParser):
    """Parser for GraphQL inputs"""
    
    @property
    def protocol_name(self) -> str:
        return "GraphQL"
    
    def parse(self, payload: Any) -> ParsedInput:
        """
        Parse GraphQL request
        
        Expected format:
        {
            "query": "mutation {...}",
            "variables": {...},
            "operationName": "..."
        }
        """
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        variables = payload.get('variables', {})
        query = payload.get('query', '')
        
        # Determine type from query
        is_mutation = 'mutation' in query.lower()
        input_type = 'mutation' if is_mutation else 'query'
        
        return ParsedInput(
            cycle=variables.get('cycle', 1),
            layer=self.extract_layer(variables),
            variant=self.extract_variant(variables),
            input_type=input_type,
            source_protocol=self.protocol_name,
            raw_data=payload,
            metadata={
                'operation_name': payload.get('operationName', 'anonymous'),
                'is_mutation': is_mutation
            }
        )


class WebhookParser(ProtocolParser):
    """Parser for Webhook inputs"""
    
    @property
    def protocol_name(self) -> str:
        return "Webhook"
    
    def parse(self, payload: Any) -> ParsedInput:
        """
        Parse Webhook payload
        
        Expected format: Any JSON with optional event type
        {
            "event": "order.created",
            "data": {...}
        }
        """
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        data = payload.get('data', payload)
        event = payload.get('event', payload.get('type', 'unknown'))
        
        return ParsedInput(
            cycle=data.get('cycle', 1),
            layer=self.extract_layer(data),
            variant=self.extract_variant(data),
            input_type=event,
            source_protocol=self.protocol_name,
            raw_data=payload,
            metadata={
                'event_type': event,
                'webhook_id': payload.get('id', payload.get('webhook_id'))
            }
        )


class GRPCParser(ProtocolParser):
    """Parser for gRPC inputs"""
    
    @property
    def protocol_name(self) -> str:
        return "gRPC"
    
    def parse(self, payload: Any) -> ParsedInput:
        """
        Parse gRPC message (assuming converted to dict)
        
        Expected format:
        {
            "service": "MyService",
            "method": "Create",
            "message": {...}
        }
        """
        if isinstance(payload, str):
            payload = json.loads(payload)
        
        message = payload.get('message', payload)
        
        return ParsedInput(
            cycle=message.get('cycle', 1),
            layer=self.extract_layer(message),
            variant=self.extract_variant(message),
            input_type=f"{payload.get('service', 'Unknown')}.{payload.get('method', 'unknown')}",
            source_protocol=self.protocol_name,
            raw_data=payload,
            metadata={
                'service': payload.get('service'),
                'method': payload.get('method')
            }
        )


class FileParser(ProtocolParser):
    """Parser for File inputs (CSV, JSON, XML)"""
    
    @property
    def protocol_name(self) -> str:
        return "File"
    
    def parse(self, payload: Any) -> ParsedInput:
        """
        Parse file content
        
        Expected format:
        {
            "filename": "data.json",
            "content_type": "application/json",
            "content": {...} or "..."
        }
        """
        if isinstance(payload, str):
            # Assume it's file content
            try:
                content = json.loads(payload)
            except json.JSONDecodeError:
                content = {'raw': payload}
            payload = {'content': content}
        
        content = payload.get('content', payload)
        if isinstance(content, str):
            try:
                content = json.loads(content)
            except json.JSONDecodeError:
                content = {'raw': content}
        
        return ParsedInput(
            cycle=content.get('cycle', 1) if isinstance(content, dict) else 1,
            layer=self.extract_layer(content) if isinstance(content, dict) else 'L1',
            variant=self.extract_variant(content) if isinstance(content, dict) else 'A',
            input_type=payload.get('content_type', 'file'),
            source_protocol=self.protocol_name,
            raw_data=payload,
            metadata={
                'filename': payload.get('filename'),
                'content_type': payload.get('content_type', 'application/octet-stream')
            }
        )


class ParserRegistry:
    """Registry of protocol parsers"""
    
    def __init__(self):
        self.parsers: Dict[str, ProtocolParser] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default parsers"""
        self.register(RESTParser())
        self.register(GraphQLParser())
        self.register(WebhookParser())
        self.register(GRPCParser())
        self.register(FileParser())
    
    def register(self, parser: ProtocolParser):
        """Register a parser for a protocol"""
        self.parsers[parser.protocol_name.upper()] = parser
    
    def get_parser(self, protocol: str) -> Optional[ProtocolParser]:
        """Get parser for a protocol"""
        return self.parsers.get(protocol.upper())
    
    def parse(self, payload: Any, protocol: str) -> ParsedInput:
        """Parse input using appropriate parser"""
        parser = self.get_parser(protocol)
        if not parser:
            raise ValueError(f"Unknown protocol: {protocol}")
        return parser.parse(payload)


# Global parser registry
_parser_registry: Optional[ParserRegistry] = None

def get_parser_registry() -> ParserRegistry:
    """Get or create the global parser registry"""
    global _parser_registry
    if _parser_registry is None:
        _parser_registry = ParserRegistry()
    return _parser_registry


def parse_input(payload: Any, protocol: str) -> Dict[str, Any]:
    """
    Main entry point: Parse input from any protocol into canonical row format
    
    Args:
        payload: Input payload (dict, string, or protocol-specific format)
        protocol: Protocol type (REST, GraphQL, gRPC, Webhook, File)
        
    Returns:
        Dictionary ready for canonical table insertion
    """
    registry = get_parser_registry()
    
    try:
        parsed = registry.parse(payload, protocol)
        return parsed.to_canonical_row()
    except Exception as e:
        # On parse error, create minimal row with error info
        return {
            'cycle': 0,
            'layer': 'L1',
            'variant': 'A',
            'input_type': 'error',
            'source_protocol': protocol,
            'status': 'RAW',
            'metadata': {
                'parse_error': str(e),
                'raw_payload': str(payload)[:1000]  # Truncate for safety
            }
        }
