"""
EuroWeb Ultra - Offline Store & Forward Test
Test the capacity and reliability of mesh offline operations

Industrial-grade testing for 72h offline capability
"""
import json
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

try:
    import yaml
except ImportError:
    # Fallback to basic JSON if PyYAML not available
    import json as yaml_fallback
    yaml = None

from utils.power_model import estimate_storage_bytes, mb

# Load configuration
config_path = Path(__file__).parent / "config.yaml"
if yaml and config_path.exists():
    cfg = yaml.safe_load(config_path.read_text())
else:
    # Fallback configuration if YAML not available
    cfg = {
        "offline": {
            "hours": 72,
            "msg_rate_per_minute": 5,
            "avg_msg_bytes": 1024,
            "storage_mb": 512
        }
    }
reports_dir = Path(__file__).parent / "reports"
reports_dir.mkdir(exist_ok=True, parents=True)

def test_store_and_forward_capacity():
    """Test offline store-and-forward capacity for 72h operation"""
    hours = cfg["offline"]["hours"]
    rate = cfg["offline"]["msg_rate_per_minute"]
    size = cfg["offline"]["avg_msg_bytes"]
    cap_mb = cfg["offline"]["storage_mb"]
    needed_bytes = estimate_storage_bytes(hours, rate, size)
    ok = mb(needed_bytes) <= cap_mb
    
    report = {
        "test_name": "EuroWeb Ultra - Store & Forward Capacity",
        "timestamp": str(Path().cwd()),
        "hours": hours,
        "messages_per_minute": rate,
        "avg_msg_bytes": size,
        "needed_storage_mb": round(mb(needed_bytes), 3),
        "available_storage_mb": cap_mb,
        "fits": ok,
        "status": "PASS" if ok else "FAIL",
        "aviation_compliance": ok  # Aviation requires 72h offline
    }
    
    (reports_dir/"offline_store_forward.json").write_text(json.dumps(report, indent=2))
    print(f"🎯 Store & Forward Test: {'✅ PASS' if ok else '❌ FAIL'}")
    print(f"📊 Storage needed: {round(mb(needed_bytes), 3)}MB / {cap_mb}MB available")
    
    assert ok, "❌ Persistenzspeicher reicht nicht für 72h Store-&-Forward (Aviation Standard)"

if __name__ == "__main__":
    print("🚀 EuroWeb Ultra - Testing Offline Store & Forward...")
    test_store_and_forward_capacity()
    print("✅ Test completed successfully!")
