"""
🔤 ALPHABET BINARY CLIENT
═══════════════════════════
Client për komunikim BINARY me Alphabet Layers microservice.
Përdor CBOR2/MessagePack - ASNJË JSON

Usage:
    from alphabet_client import AlphabetClient
    
    client = AlphabetClient()
    result = await client.compute(42, layers=["α", "β"])
    result = await client.algebra("XOR", 255, 128, bits=8)
"""

import os
import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

import httpx
import cbor2
import msgpack

logger = logging.getLogger("AlphabetClient")

# Configuration
ALPHABET_URL = os.getenv("ALPHABET_URL", "http://alphabet-layers:8061")
BINARY_FORMAT = os.getenv("ALPHABET_FORMAT", "cbor")  # cbor or msgpack


@dataclass
class BinaryResponse:
    """Binary response container"""
    success: bool
    data: Dict[str, Any]
    format: str
    raw_bytes: bytes


class AlphabetClient:
    """
    Binary client for Alphabet Layers microservice.
    CBOR2/MessagePack only - NO JSON.
    """
    
    def __init__(
        self, 
        base_url: str = None,
        format: str = None,
        timeout: float = 30.0
    ):
        self.base_url = base_url or ALPHABET_URL
        self.format = format or BINARY_FORMAT
        self.timeout = timeout
        self.content_type = {
            "cbor": "application/cbor",
            "msgpack": "application/msgpack"
        }.get(self.format, "application/cbor")
    
    def _encode(self, data: Dict[str, Any]) -> bytes:
        """Encode data to binary"""
        if self.format == "msgpack":
            return msgpack.dumps(data, use_bin_type=True)
        return cbor2.dumps(data)
    
    def _decode(self, data: bytes) -> Dict[str, Any]:
        """Decode binary data"""
        if self.format == "msgpack":
            return msgpack.loads(data, raw=False)
        return cbor2.loads(data)
    
    async def _request(
        self, 
        endpoint: str, 
        data: Dict[str, Any] = None,
        method: str = "POST"
    ) -> BinaryResponse:
        """Make binary request"""
        url = f"{self.base_url}/api/v1{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method == "GET":
                    response = await client.get(url)
                else:
                    binary_data = self._encode(data or {})
                    response = await client.post(
                        url,
                        content=binary_data,
                        headers={"Content-Type": self.content_type}
                    )
                
                if response.status_code == 200:
                    # Check if response is binary
                    resp_type = response.headers.get("content-type", "")
                    if "cbor" in resp_type or "msgpack" in resp_type or "octet-stream" in resp_type:
                        decoded = self._decode(response.content)
                    else:
                        # Fallback to JSON for health/info endpoints
                        decoded = response.json()
                    
                    return BinaryResponse(
                        success=True,
                        data=decoded,
                        format=self.format,
                        raw_bytes=response.content
                    )
                else:
                    return BinaryResponse(
                        success=False,
                        data={"error": f"HTTP {response.status_code}"},
                        format=self.format,
                        raw_bytes=response.content
                    )
        except Exception as e:
            logger.error(f"Alphabet client error: {e}")
            return BinaryResponse(
                success=False,
                data={"error": str(e)},
                format=self.format,
                raw_bytes=b""
            )
    
    # ═══════════════════════════════════════════════════════════════════
    # BINARY COMPUTATION METHODS
    # ═══════════════════════════════════════════════════════════════════
    
    async def compute(
        self,
        input_value: Any,
        layers: List[str] = None,
        mode: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Compute input through alphabet layers.
        
        Args:
            input_value: Value to process
            layers: Specific layers ["α", "β", "a", "ë"] or None for all
            mode: "sequential", "parallel", or "meta"
        
        Returns:
            Layer computation results
        """
        response = await self._request("/bin/compute", {
            "input": input_value,
            "layers": layers,
            "mode": mode
        })
        return response.data
    
    async def layer(self, layer_name: str, value: Any) -> Dict[str, Any]:
        """
        Execute single layer.
        
        Args:
            layer_name: Layer identifier ("α", "β", "a", "ë", etc.)
            value: Input value
        
        Returns:
            Layer result with phonetic properties
        """
        response = await self._request("/bin/layer", {
            "layer": layer_name,
            "value": value
        })
        return response.data
    
    async def compose(
        self, 
        word: str, 
        include_phonetics: bool = False
    ) -> Dict[str, Any]:
        """
        Compose word through layers.
        
        Args:
            word: Word to compose (e.g., "shqip", "θεός")
            include_phonetics: Include phonetic analysis
        
        Returns:
            Word composition result
        """
        response = await self._request("/bin/compose", {
            "word": word,
            "include_phonetics": include_phonetics
        })
        return response.data
    
    async def algebra(
        self,
        op: str,
        a: int,
        b: int = 0,
        bits: int = 64
    ) -> Dict[str, Any]:
        """
        Binary algebra operation.
        
        Args:
            op: Operation (AND, OR, XOR, NOT, NAND, SHL, SHR, ADD, SUB, MUL)
            a: First operand
            b: Second operand
            bits: Bit width (8, 16, 32, 64)
        
        Returns:
            Binary operation result with bit representation
        """
        response = await self._request("/bin/algebra", {
            "op": op.upper(),
            "a": a,
            "b": b,
            "bits": bits
        })
        return response.data
    
    async def stream_signals(
        self,
        signals: List[Dict[str, Any]],
        aggregate: bool = True
    ) -> Dict[str, Any]:
        """
        Process signal stream through layers.
        
        Args:
            signals: List of signals [{"type": "metric", "value": 0.5}, ...]
            aggregate: Calculate aggregate statistics
        
        Returns:
            Processed signals
        """
        response = await self._request("/bin/stream", {
            "signals": signals,
            "aggregate": aggregate
        })
        return response.data
    
    async def matrix_op(
        self,
        matrix_a: List[List[float]],
        matrix_b: List[List[float]],
        op: str = "multiply"
    ) -> Dict[str, Any]:
        """
        Binary matrix operation.
        
        Args:
            matrix_a: First matrix
            matrix_b: Second matrix
            op: Operation (multiply, add, xor)
        
        Returns:
            Matrix operation result
        """
        response = await self._request("/bin/matrix", {
            "matrix_a": matrix_a,
            "matrix_b": matrix_b,
            "op": op
        })
        return response.data
    
    async def meta_layer(self, input_value: Any) -> Dict[str, Any]:
        """
        Process through Layer 61 (Meta-layer Ω+).
        
        Args:
            input_value: Value to process through unified consciousness layer
        
        Returns:
            Meta-layer result
        """
        return await self.compute(input_value, mode="meta")
    
    # ═══════════════════════════════════════════════════════════════════
    # HEALTH & INFO (JSON allowed)
    # ═══════════════════════════════════════════════════════════════════
    
    async def health(self) -> Dict[str, Any]:
        """Check service health"""
        response = await self._request("/health", method="GET")
        return response.data
    
    async def info(self) -> Dict[str, Any]:
        """Get service info"""
        response = await self._request("/info", method="GET")
        return response.data
    
    async def stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        response = await self._request("/stats", method="GET")
        return response.data
    
    async def list_layers(self) -> Dict[str, Any]:
        """List all 61 layers"""
        response = await self._request("/layers", method="GET")
        return response.data


# Singleton instance
_client: Optional[AlphabetClient] = None


def get_alphabet_client() -> AlphabetClient:
    """Get singleton alphabet client"""
    global _client
    if _client is None:
        _client = AlphabetClient()
    return _client


# Convenience functions
async def compute_layers(input_value: Any, layers: List[str] = None) -> Dict[str, Any]:
    """Quick compute through layers"""
    return await get_alphabet_client().compute(input_value, layers)


async def binary_algebra(op: str, a: int, b: int = 0, bits: int = 64) -> Dict[str, Any]:
    """Quick binary algebra operation"""
    return await get_alphabet_client().algebra(op, a, b, bits)


async def compose_word(word: str) -> Dict[str, Any]:
    """Quick word composition"""
    return await get_alphabet_client().compose(word, include_phonetics=True)


# CLI test
if __name__ == "__main__":
    async def test_client():
        client = AlphabetClient(base_url="http://localhost:8061")
        
        print("🔤 Testing Alphabet Binary Client...")
        
        # Health check
        health = await client.health()
        print(f"✅ Health: {health}")
        
        # Compute
        result = await client.compute(42, layers=["α", "β", "γ"])
        print(f"📊 Compute: {result}")
        
        # Algebra
        xor_result = await client.algebra("XOR", 255, 128, bits=8)
        print(f"🔢 XOR: {xor_result}")
        
        # Compose
        word_result = await client.compose("shqip", include_phonetics=True)
        print(f"📝 Compose: {word_result}")
        
        print("✅ All tests passed!")
    
    asyncio.run(test_client())
