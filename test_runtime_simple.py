import sys
sys.path.insert(0, '/opt/clisonix.com')
from ocean_core.runtime.init import initialize_runtime
rt = initialize_runtime()
print("✅ Runtime OK")
print("Providers:", rt["providers"].list_providers())
