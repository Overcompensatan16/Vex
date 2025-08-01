import os
from cerebral_cortex.primary_auditory_cortex.ear import EarModule

# Initialize ear module
ear = EarModule()

# === 1. Single mic capture with audio file === #
mic_result = ear.capture_from_mic()
print("[Test] Mic Capture Result:", mic_result)


# === 2. Start background listening (can be run once) === #
ear.listen_forever()

# Simulate brief runtime (optional sleep or user interrupt)
# time.sleep(10)  # Uncomment this if you want passive listen to run

# === 3. Stop listening manually === #
ear.stop_listening()
