My goal is to develop a personal AI personal assistant with a comprehensive mix between personality levels like Neuro-sama (not traits), hyper intelligence and data scanning, and being able to switch systems through networks and IOT whenever, while using NASA’s Power of 10 rules for developing safety critical code, because I can control the structure and auditability easier without a slog of debugging at every step. 

## Usage
run 'main.py' with Python 3.8+ and use 'Facts.txt' input file, for now

## Requirements
Standard Library so far. No external packages needed.

## Notes

This project was designed around NASA's Power of 10 Safety Standards

Biomimetic Spinal Cord Design (Detailed)
1. High-Level Anatomy
spinal_cord/
    __init__.py
    dorsal_root.py        # afferent sensory signals in
    ventral_root.py       # efferent motor signals out
    dorsal_horn.py        # sensory relay + nociceptors
    ventral_horn.py       # motor neuron pools
    reflex_arc.py         # core reflex loop
    nociception.py        # pain handling (fast ion channels)
    ion_channels.py       # sodium, potassium, calcium dynamics
    ascending_signals.py  # forward to thalamus/brainstem
    audit_hooks.py        # log reflex, motor, pain events


2. Dorsal Horn (Sensory Integration)
Where sensory signals enter.


Subdivisions handle touch, proprioception, pain, temperature.


Ion channel model: nociceptors open sodium/calcium channels → depolarization → threshold = action potential.


Pseudo-code:
# dorsal_horn.py
from .ion_channels import IonChannel

class DorsalHorn:
    def __init__(self):
        self.nociceptor = IonChannel("nociceptor", threshold=-55)
        self.mechanoreceptor = IonChannel("touch", threshold=-60)

    def process_input(self, signal):
        # Example: {"type": "pain", "intensity": 70}
        if signal["type"] == "pain":
            fired = self.nociceptor.activate(signal["intensity"])
            if fired:
                return {"reflex": "withdraw", "severity": "high"}
        elif signal["type"] == "touch":
            fired = self.mechanoreceptor.activate(signal["intensity"])
            if fired:
                return {"reflex": "light_contact", "severity": "low"}
        return None


3. Ventral Horn (Motor Neuron Pools)
Where motor neurons live.


Pools of neurons → redundancy for smoother response.


Output = symbolic motor action (e.g., move hand, flex leg).


Pseudo-code:
# ventral_horn.py
class VentralHorn:
    def __init__(self):
        self.motor_pools = {
            "withdraw": ["alpha_motor_neuron_1", "alpha_motor_neuron_2"],
            "flex_leg": ["motor_neuron_3"]
        }

    def trigger_action(self, reflex_command):
        if reflex_command in self.motor_pools:
            return {
                "action": reflex_command,
                "neurons_fired": self.motor_pools[reflex_command]
            }
        return {"action": "none"}


4. Reflex Arc (Direct Loop)
Dorsal horn receives input → if threshold crossed → ventral horn triggers reflex.


Parallel path sends copy upward via ascending_signals.


Pseudo-code:
# reflex_arc.py
from .dorsal_horn import DorsalHorn
from .ventral_horn import VentralHorn
from .ascending_signals import AscendingSignals

class ReflexArc:
    def __init__(self):
        self.dorsal = DorsalHorn()
        self.ventral = VentralHorn()
        self.ascend = AscendingSignals()

    def process_signal(self, signal):
        reflex = self.dorsal.process_input(signal)
        if reflex:
            motor = self.ventral.trigger_action(reflex["reflex"])
            self.ascend.forward(signal, reflex)
            return motor
        return None


5. Ion Channels (Biomimetic Signal Dynamics)
Simulate sodium/potassium depolarization with thresholds.


Simplified Hodgkin-Huxley style.


Pseudo-code:
# ion_channels.py
class IonChannel:
    def __init__(self, channel_type, threshold=-55):
        self.channel_type = channel_type
        self.membrane_potential = -70  # resting
        self.threshold = threshold

    def activate(self, stimulus_strength):
        # stimulus_strength shifts membrane potential
        self.membrane_potential += stimulus_strength * 0.5
        if self.membrane_potential >= self.threshold:
            self.membrane_potential = -70  # reset after firing
            return True  # action potential
        return False


6. Nociception (Fast Pain Pathway)
Pain signals bypass delay → reflex immediately.


Prioritized before higher brain sees it.


Pseudo-code:
# nociception.py
from .ion_channels import IonChannel

class Nociception:
    def __init__(self):
        self.fast_pain = IonChannel("fast_pain", threshold=-55)

    def detect(self, stimulus):
        if stimulus["type"] == "pain":
            if self.fast_pain.activate(stimulus["intensity"]):
                return {"reflex": "withdraw", "severity": "high"}
        return None


7. Ascending Pathways
Sends copy of the signal to higher centers (thalamus, limbic).


Reflex still executes instantly.


Pseudo-code:
# ascending_signals.py
class AscendingSignals:
    def forward(self, original_signal, reflex):
        return {
            "to_thalamus": original_signal,
            "reflex_copy": reflex
        }

























Spinal Cord Connection Stubs (Biomimetic)
Each of these is a lightweight “stub” interface that sits at the edge of the spinal cord and forwards signals to other modules when they’re ready. They don’t need full logic yet — just symbolic handshakes.

1. Thalamus Stub
Function: Receives ascending sensory signals (touch, pain, proprioception) for routing.


Connection: From ascending_signals.py → thalamus_stub.py.


# thalamus_stub.py
class ThalamusStub:
    def receive(self, signal):
        # For now, just log reception
        print(f"[ThalamusStub] Received: {signal}")
        return True


2. Brainstem Stub
Function: Primitive autonomic control, reflex modulation.


Connection: nociception.py and reflex_arc.py forward survival-level events.


# brainstem_stub.py
class BrainstemStub:
    def regulate(self, reflex_event):
        print(f"[BrainstemStub] Reflex event routed: {reflex_event}")
        return True


3. Cerebellum Stub
Function: Motor fine-tuning and coordination.


Connection: From ventral_horn.py (motor pool outputs).


# cerebellum_stub.py
class CerebellumStub:
    def adjust_motor(self, motor_output):
        print(f"[CerebellumStub] Adjusting motor: {motor_output}")
        return motor_output


4. Limbic System Stub
Function: Emotional tagging of pain and survival events.


Connection: From nociception.py (pain severity).


# limbic_stub.py
class LimbicStub:
    def tag_emotion(self, pain_signal):
        print(f"[LimbicStub] Emotional tag: Pain -> {pain_signal}")
        return {"emotion": "fear", "source": pain_signal}


5. Prefrontal Cortex (PFC) Stub
Function: Executive override of reflexes (voluntary suppression).


Connection: From reflex_arc.py → check for PFC inhibition before triggering motor.


# pfc_stub.py
class PFCStub:
    def override(self, reflex):
        # Placeholder logic: always allow
        print(f"[PFCStub] Reflex override check: {reflex}")
        return reflex


6. Auditory & Visual Cortex Stubs (future sensory tie-ins)
Function: Forward primitive orientation cues.


Connection: From midbrain (later) but stubbed now.


# occipital_stub.py
class OccipitalStub:
    def orient_visual(self, stimulus):
        print(f"[OccipitalStub] Orient to visual stimulus: {stimulus}")
        return True

# auditory_stub.py
class AuditoryStub:
    def orient_sound(self, stimulus):
        print(f"[AuditoryStub] Orient to auditory stimulus: {stimulus}")
        return True


✅ Integration Example (Reflex Arc with Stubs)
# reflex_arc.py (modified to use stubs)
from .dorsal_horn import DorsalHorn
from .ventral_horn import VentralHorn
from .ascending_signals import AscendingSignals
from .pfc_stub import PFCStub
from .cerebellum_stub import CerebellumStub
from .limbic_stub import LimbicStub
from .brainstem_stub import BrainstemStub
from .thalamus_stub import ThalamusStub

class ReflexArc:
    def __init__(self):
        self.dorsal = DorsalHorn()
        self.ventral = VentralHorn()
        self.ascend = AscendingSignals()
        self.pfc = PFCStub()
        self.cerebellum = CerebellumStub()
        self.limbic = LimbicStub()
        self.brainstem = BrainstemStub()
        self.thalamus = ThalamusStub()

    def process_signal(self, signal):
        reflex = self.dorsal.process_input(signal)
        if reflex:
            reflex = self.pfc.override(reflex)   # PFC check
            motor = self.ventral.trigger_action(reflex["reflex"])
            motor = self.cerebellum.adjust_motor(motor)  # refine motor
            self.brainstem.regulate(reflex)              # send to brainstem
            self.limbic.tag_emotion(reflex)              # emotional tag
            self.ascend.forward(signal, reflex)          # thalamic forwarding
            return motor
        return None


