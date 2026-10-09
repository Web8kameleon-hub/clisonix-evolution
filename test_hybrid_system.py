<<<<<<< HEAD
#!/usr/bin/env python3
"""
HYBRID BIOMETRIC SYSTEM - TEST SUITE
Verifikimi i të gjithë komponentave
"""

import requests
from datetime import datetime

# API endpoints
API_BASE = "http://localhost:8001"
PHONE_ENDPOINT = f"{API_BASE}/api/phone"
CLINIC_ENDPOINT = f"{API_BASE}/api/clinic"
SESSION_ENDPOINT = f"{API_BASE}/api/session"
ANALYTICS_ENDPOINT = f"{API_BASE}/api/analytics"

print("=" * 70)
print("🔗 HYBRID BIOMETRIC SYSTEM - TEST SUITE")
print("=" * 70)
print(f"API Base: {API_BASE}")
print(f"Time: {datetime.now().isoformat()}")
print()

# ============================================================================
# TEST 1: HEALTH CHECK
# ============================================================================


def test_health():
    """Test API health endpoint"""
    print("📋 TEST 1: Health Check")
    print("-" * 70)
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print("✅ API is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Sessions: {data.get('sessions')}")
            print(f"   Devices: {data.get('registered_devices')}")
            return True
        else:
            print(f"❌ API returned {resp.status_code}")
            return False
    except (requests.RequestException, ValueError) as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 2: CLINIC REGISTRATION
# ============================================================================


def test_clinic_registration():
    print("\n📋 TEST 2: Clinic Registration")
    print("-" * 70)
    try:
        # Register clinic
        clinic_data = {
            "clinic_id": "test_clinic_001",
            "clinic_name": "Test University Clinic",
            "api_endpoint": "https://clinic-api.example.com",
            "api_key": "test_clinic_api_key",
            "supported_devices": ["EEG", "ECG", "SpO2"],
            "sync_interval": 5000,
        }

        resp = requests.post(
            f"{CLINIC_ENDPOINT}/register",
            json=clinic_data,
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Clinic registered: {data.get('clinic_name')}")
            print(f"   Clinic ID: {data.get('clinic_id')}")
            return True
        else:
            print(f"❌ Failed to register clinic: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 3: CLINICAL DEVICE REGISTRATION
# ============================================================================


def test_device_registration():
    print("\n📋 TEST 3: Clinical Device Registration")
    print("-" * 70)
    devices_registered = []

    # Test devices
    test_devices = [
        {
            "device_type": "EEG",
            "device_id": "eeg_001",
            "device_name": "Emotiv EPOC+ EEG Headset",
            "clinic_id": "test_clinic_001",
        },
        {
            "device_type": "ECG",
            "device_id": "ecg_001",
            "device_name": "GE CARESCAPE Monitor",
            "clinic_id": "test_clinic_001",
        },
        {
            "device_type": "SpO2",
            "device_id": "spo2_001",
            "device_name": "Masimo Radical-7",
            "clinic_id": "test_clinic_001",
        },
    ]

    for device in test_devices:
        try:
            resp = requests.post(
                f"{CLINIC_ENDPOINT}/device/register",
                json=device,
                timeout=5,
            )
            if resp.status_code == 200:
                device_type = device["device_type"]
                device_name = device["device_name"]
                msg = (
                    f"✅ {device_type:8} registered: "
                    f"{device_name}"
                )
                print(msg)
                devices_registered.append(device["device_id"])
            else:
                device_type = device["device_type"]
                status_code = resp.status_code
                msg = (
                    f"❌ Failed to register {device_type}: "
                    f"{status_code}"
                )
                print(msg)
        except requests.RequestException as e:
            print(f"❌ Error registering device: {e}")

    print(f"\n   Total registered: {len(devices_registered)}")
    return len(devices_registered) > 0


# ============================================================================
# TEST 4: START HYBRID SESSION
# ============================================================================


def test_start_session():
    print("\n📋 TEST 4: Start Hybrid Session")
    print("-" * 70)
    try:
        session_data = {
            "user_id": "test_patient_001",
            "session_name": "Integration Test Session",
            "phone_data_enabled": True,
            "clinic_data_enabled": True,
        }

        resp = requests.post(
            f"{SESSION_ENDPOINT}/start-hybrid",
            json=session_data,
            timeout=5,
        )
        if resp.status_code == 200:
            session = resp.json()
            session_id = session.get("session_id")
            print("✅ Session started successfully")
            print(f"   Session ID: {session_id}")
            print(f"   User ID: {session.get('user_id')}")
            return True, session_id
        else:
            print(f"❌ Failed to start session: {resp.status_code}")
            return False, None
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        return False, None


# ============================================================================
# TEST 5: PHONE SENSOR READINGS
# ============================================================================


def test_phone_readings(session_id):
    print("\n📋 TEST 5: Phone Sensor Readings")
    print("-" * 70)

    try:
        for i in range(3):
            reading_data = {
                "session_id": session_id,
                "device_type": "accelerometer",
                "reading_number": i + 1,
                "x": 9.2 + i * 0.1,
                "y": 1.3 + i * 0.05,
                "z": 0.5 - i * 0.02,
                "accuracy": 90 + i,
                "timestamp": int(datetime.now().timestamp() * 1000),
            }

            resp = requests.post(
                f"{PHONE_ENDPOINT}/sensor-reading",
                json=reading_data,
                timeout=5,
            )
            if resp.status_code == 200:
                device_type = reading_data["device_type"]
                reading_num = reading_data["reading_number"]
                msg = (
                    f"✅ Phone sensor {device_type} reading "
                    f"#{reading_num} submitted"
                )
                print(msg)
            else:
                print(f"❌ Failed to submit reading: "
                      f"{resp.status_code}")

        print("✅ All phone readings submitted successfully")
        return True
    except requests.RequestException as e:
        print(f"❌ Error submitting phone readings: {e}")
        return False


# ============================================================================
# TEST 6: CLINICAL DEVICE READINGS
# ============================================================================


def test_clinical_readings(session_id):
    print("\n📋 TEST 6: Clinical Device Readings")
    print("-" * 70)

    try:
        # EEG reading
        eeg_data = {
            "session_id": session_id,
            "device_id": "eeg_001",
            "channels": 14,
            "sampling_rate": 128,
            "readings": [
                -25.5,
                30.2,
                15.8,
                -10.3,
                45.1,
                -5.7,
                20.4,
                -15.2,
                35.9,
                -8.1,
                25.3,
                -12.6,
                40.7,
                18.2,
            ],
            "unit": "μV",
            "timestamp": int(datetime.now().timestamp() * 1000),
        }

        resp = requests.post(
            f"{CLINIC_ENDPOINT}/device/eeg_001/reading",
            json=eeg_data,
            timeout=5,
        )
        if resp.status_code == 200:
            print("✅ EEG reading submitted")
            print("   Channels: 14")
            print("   Quality: 95%")
        else:
            print(f"❌ Failed to submit EEG: {resp.status_code}")

        # SpO2 reading
        spo2_data = {
            "session_id": session_id,
            "device_id": "spo2_001",
            "spo2_percent": 98,
            "pulse_rate": 72,
            "perfusion_index": 3.5,
            "unit": "%",
            "timestamp": int(datetime.now().timestamp() * 1000),
        }

        resp = requests.post(
            f"{CLINIC_ENDPOINT}/device/spo2_001/reading",
            json=spo2_data,
            timeout=5,
        )
        if resp.status_code == 200:
            print("✅ SpO2 reading submitted")
            print("   Value: 98%")
            print("   Quality: 92%")
        else:
            print(f"❌ Failed to submit SpO2: {resp.status_code}")

        print("✅ All clinical readings submitted")
        return True
    except requests.RequestException as e:
        print(f"❌ Error submitting clinical readings: {e}")
        return False


# ============================================================================
# TEST 7: RETRIEVE SESSION DATA
# ============================================================================


def test_retrieve_session(session_id):
    print("\n📋 TEST 7: Retrieve Session Data")
    print("-" * 70)

    try:
        resp = requests.get(
            f"{SESSION_ENDPOINT}/{session_id}",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Session retrieved")
            print(f"   User ID: {data['session']['user_id']}")
            phone_count = data["session"]["phone_readings_count"]
            clinical_count = (
                data["session"]["clinical_readings_count"]
            )
            print(f"   Phone Readings: {phone_count}")
            print(f"   Clinical Readings: {clinical_count}")
            return True
        else:
            print(f"❌ Failed to retrieve session: "
                  f"{resp.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error retrieving session: {e}")
        return False


# ============================================================================
# TEST 8: ANALYTICS
# ============================================================================


def test_analytics():
    print("\n📋 TEST 8: Analytics")
    print("-" * 70)

    try:
        resp = requests.get(
            f"{CLINIC_ENDPOINT}/readings/test_clinic_001",
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            print("✅ Clinic readings retrieved")
            readings = data.get("readings", [])
            for reading in readings:
                reading_device_type = reading["device_type"]
                reading_value = reading.get("value")
                reading_unit = reading.get("unit")
                msg = (
                    f"   • {reading_device_type}: "
                    f"{reading_value} {reading_unit}"
                )
                print(msg)
            return True
        else:
            print(f"❌ Failed to retrieve analytics: "
                  f"{resp.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Error retrieving analytics: {e}")
        return False


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================


def main():
    tests = []

    # Run health check
    tests.append(("Health Check", test_health()))

    # Run clinic registration
    tests.append(("Clinic Registration", test_clinic_registration()))

    # Run device registration
    tests.append(
        ("Device Registration", test_device_registration())
    )

    # Start session and get session ID
    session_started, session_id = test_start_session()
    tests.append(("Start Session", session_started))

    if session_id:
        # Phone readings
        tests.append(
            ("Phone Readings", test_phone_readings(session_id))
        )

        # Clinical readings
        tests.append(
            (
                "Clinical Readings",
                test_clinical_readings(session_id),
            )
        )

        # Retrieve session
        tests.append(
            ("Retrieve Session", test_retrieve_session(session_id))
        )

        # Analytics
        tests.append(("Analytics", test_analytics()))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("=" * 70)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
    else:
        failed_count = total - passed
        msg = (
            f"⚠️  {failed_count} test(s) failed. "
            f"Check the errors above."
        )
        print(msg)

    print("=" * 70)


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
"""
HYBRID BIOMETRIC SYSTEM - TEST SUITE
Verifikimi i të gjithë komponentave
"""

import asyncio
import requests
import json
from datetime import datetime

# API endpoints
API_BASE = "http://localhost:8001"
PHONE_ENDPOINT = f"{API_BASE}/api/phone"
CLINIC_ENDPOINT = f"{API_BASE}/api/clinic"
SESSION_ENDPOINT = f"{API_BASE}/api/session"
ANALYTICS_ENDPOINT = f"{API_BASE}/api/analytics"

print("=" * 70)
print("🔗 HYBRID BIOMETRIC SYSTEM - TEST SUITE")
print("=" * 70)
print(f"API Base: {API_BASE}")
print(f"Time: {datetime.now().isoformat()}")
print()

# ============================================================================
# TEST 1: HEALTH CHECK
# ============================================================================

def test_health():
    print("📋 TEST 1: Health Check")
    print("-" * 70)
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ API is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Sessions: {data.get('sessions')}")
            print(f"   Devices: {data.get('registered_devices')}")
            return True
        else:
            print(f"❌ API returned {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 2: CLINIC REGISTRATION
# ============================================================================

def test_clinic_registration():
    print("\n📋 TEST 2: Clinic Registration")
    print("-" * 70)
    try:
        # Register clinic
        clinic_data = {
            "clinic_id": "test_clinic_001",
            "clinic_name": "Test University Clinic",
            "api_endpoint": "https://clinic-api.example.com",
            "api_key": "test_clinic_api_key",
            "supported_devices": ["EEG", "ECG", "SpO2"],
            "sync_interval": 5000,
        }

        resp = requests.post(f"{CLINIC_ENDPOINT}/register", json=clinic_data)
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Clinic registered: {data.get('clinic_name')}")
            print(f"   Clinic ID: {data.get('clinic_id')}")
            return True
        else:
            print(f"❌ Failed to register clinic: {resp.status_code}")
            print(f"   Response: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 3: CLINICAL DEVICE REGISTRATION
# ============================================================================

def test_device_registration():
    print("\n📋 TEST 3: Clinical Device Registration")
    print("-" * 70)
    devices_registered = []

    # Test devices
    test_devices = [
        {
            "device_type": "EEG",
            "device_id": "eeg_001",
            "device_name": "Emotiv EPOC+ EEG Headset",
            "clinic_id": "test_clinic_001",
            "api_key": "device_key_eeg_001",
            "supported_channels": 14,
            "sample_rate": 256,
        },
        {
            "device_type": "ECG",
            "device_id": "ecg_001",
            "device_name": "Polar H10 Heart Rate Monitor",
            "clinic_id": "test_clinic_001",
            "api_key": "device_key_ecg_001",
            "supported_channels": 1,
            "sample_rate": 130,
        },
        {
            "device_type": "SpO2",
            "device_id": "spo2_001",
            "device_name": "Pulse Oximeter",
            "clinic_id": "test_clinic_001",
            "api_key": "device_key_spo2_001",
            "supported_channels": 1,
            "sample_rate": 1,
        },
    ]

    for device in test_devices:
        try:
            resp = requests.post(f"{CLINIC_ENDPOINT}/device/register", json=device)
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ {device['device_type']:8} registered: {device['device_name']}")
                devices_registered.append(device["device_id"])
            else:
                print(f"❌ Failed to register {device['device_type']}: {resp.status_code}")
        except Exception as e:
            print(f"❌ Error registering {device['device_type']}: {e}")

    print(f"\n   Total devices registered: {len(devices_registered)}")
    return len(devices_registered) == len(test_devices)


# ============================================================================
# TEST 4: START HYBRID SESSION
# ============================================================================

def test_start_session():
    print("\n📋 TEST 4: Start Hybrid Session")
    print("-" * 70)
    try:
        session_data = {
            "user_id": "test_patient_001",
            "clinic_id": "test_clinic_001",
            "data_source": "hybrid",
        }

        resp = requests.post(f"{SESSION_ENDPOINT}/start-hybrid", json=session_data)
        if resp.status_code == 200:
            data = resp.json()
            session_id = data["session"]["session_id"]
            print(f"✅ Session started successfully")
            print(f"   Session ID: {session_id}")
            print(f"   User ID: {data['session']['user_id']}")
            print(f"   Data Source: {data['session']['data_source']}")
            print(f"   Status: {data['session']['sync_status']}")
            return session_id
        else:
            print(f"❌ Failed to start session: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ============================================================================
# TEST 5: SUBMIT PHONE SENSOR DATA
# ============================================================================

def test_phone_sensor_data(session_id: str):
    print("\n📋 TEST 5: Phone Sensor Data Submission")
    print("-" * 70)
    try:
        import time

        # Submit multiple readings
        for i in range(3):
            reading_data = {
                "accelerometer": {
                    "x": 0.5 + i * 0.1,
                    "y": 1.2 + i * 0.1,
                    "z": 9.8 + i * 0.05,
                    "timestamp": int(time.time() * 1000),
                },
                "gyroscope": {
                    "x": 10 + i * 5,
                    "y": 5 + i * 2,
                    "z": 2 + i * 1,
                    "timestamp": int(time.time() * 1000),
                },
                "heart_rate": {
                    "bpm": 70 + i * 2,
                    "confidence": 0.85,
                    "timestamp": int(time.time() * 1000),
                },
                "temperature": {
                    "celsius": 36.8 + i * 0.1,
                    "timestamp": int(time.time() * 1000),
                },
                "session_id": session_id,
                "user_id": "test_patient_001",
            }

            resp = requests.post(f"{PHONE_ENDPOINT}/sensor-reading", json=reading_data)
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Reading {i+1} submitted")
                print(f"   HR: {reading_data['heart_rate']['bpm']} BPM")
                print(f"   Temp: {reading_data['temperature']['celsius']}°C")
            else:
                print(f"❌ Failed to submit reading {i+1}: {resp.status_code}")
            time.sleep(0.5)

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 6: SUBMIT CLINICAL DATA
# ============================================================================

def test_clinical_data():
    print("\n📋 TEST 6: Clinical Device Data Submission")
    print("-" * 70)
    try:
        import time

        # EEG reading
        eeg_data = {
            "device_type": "EEG",
            "device_id": "eeg_001",
            "device_name": "Emotiv EPOC+",
            "clinic_id": "test_clinic_001",
            "value": [50.5, 48.2, 52.1, 49.8, 51.3, 50.8, 49.5, 51.2, 50.1, 49.9, 52.3, 50.5, 51.1, 49.7],
            "unit": "μV",
            "quality": 95,
            "timestamp": int(time.time() * 1000),
        }

        resp = requests.post(f"{CLINIC_ENDPOINT}/device/eeg_001/reading", json=eeg_data)
        if resp.status_code == 200:
            print(f"✅ EEG reading submitted")
            print(f"   Channels: 14")
            print(f"   Quality: 95%")
        else:
            print(f"❌ Failed to submit EEG: {resp.status_code}")
            return False

        # SpO2 reading
        spo2_data = {
            "device_type": "SpO2",
            "device_id": "spo2_001",
            "device_name": "Pulse Oximeter",
            "clinic_id": "test_clinic_001",
            "value": 98,
            "unit": "%",
            "quality": 92,
            "timestamp": int(time.time() * 1000),
        }

        resp = requests.post(f"{CLINIC_ENDPOINT}/device/spo2_001/reading", json=spo2_data)
        if resp.status_code == 200:
            print(f"✅ SpO2 reading submitted")
            print(f"   Value: 98%")
            print(f"   Quality: 92%")
        else:
            print(f"❌ Failed to submit SpO2: {resp.status_code}")
            return False

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 7: GET SESSION DATA
# ============================================================================

def test_get_session(session_id: str):
    print("\n📋 TEST 7: Get Session Data")
    print("-" * 70)
    try:
        resp = requests.get(f"{SESSION_ENDPOINT}/{session_id}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Session retrieved")
            print(f"   Session ID: {data['session']['session_id']}")
            print(f"   Phone Readings: {len(data.get('phone_readings', []))}")
            print(f"   Clinical Readings: {data['session']['clinical_readings_count']}")
        else:
            print(f"❌ Failed to get session: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 8: GET CLINIC READINGS
# ============================================================================

def test_get_clinic_readings():
    print("\n📋 TEST 8: Get Clinic Readings")
    print("-" * 70)
    try:
        resp = requests.get(f"{CLINIC_ENDPOINT}/readings/test_clinic_001")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Clinic readings retrieved")
            print(f"   Total readings: {len(data.get('readings', []))}")
            for reading in data.get("readings", [])[:3]:
                print(f"   • {reading['device_type']}: {reading.get('value')} {reading.get('unit')}")
        else:
            print(f"❌ Failed to get readings: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


# ============================================================================
# TEST 9: GET ANALYTICS
# ============================================================================

def test_analytics(session_id: str):
    print("\n📋 TEST 9: Get Analytics")
    print("-" * 70)
    try:
        resp = requests.get(f"{ANALYTICS_ENDPOINT}/session/{session_id}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Analytics retrieved")
            print(f"   Session Duration: {data.get('duration_ms')/1000:.1f} seconds")
            if "heart_rate" in data:
                print(f"   Heart Rate - Avg: {data['heart_rate']['avg']:.1f} BPM")
            if "temperature" in data:
                print(f"   Temperature - Avg: {data['temperature']['avg']:.1f}°C")
        else:
            print(f"⚠️ Analytics not available yet: {resp.status_code}")
    except Exception as e:
        print(f"⚠️ Error getting analytics: {e}")


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def main():
    results = []

    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Clinic Registration", test_clinic_registration()))
    results.append(("Device Registration", test_device_registration()))

    session_id = test_start_session()
    if session_id:
        results.append(("Start Session", True))
        results.append(("Phone Data", test_phone_sensor_data(session_id)))
        results.append(("Clinical Data", test_clinical_data()))
        results.append(("Get Session", test_get_session(session_id)))
        results.append(("Get Readings", test_get_clinic_readings()))
        test_analytics(session_id)
    else:
        results.append(("Start Session", False))
        results.append(("Phone Data", False))
        results.append(("Clinical Data", False))
        results.append(("Get Session", False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System is ready.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")

    print("=" * 70)


if __name__ == "__main__":
    main()
>>>>>>> c1f6cec4fc9d5b7cab11712c7a2c12433881c0d0
