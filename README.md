My goal is to develop a personal AI personal assistant with a comprehensive mix between personality levels like Neuro-sama (not traits), hyper intelligence and data scanning, and being able to switch systems through networks and IOT whenever, while using NASA’s Power of 10 rules for developing safety critical code, because I can control the structure and auditability easier without a slog of debugging at every step. 

## Usage
run 'main.py' with Python 3.8+ and use 'Facts.txt' input file, for now

## Requirements
Standard Library so far. No external packages needed.

## Notes

This project was designed around NASA's Power of 10 Safety Standards

Biomimetic Spinal Cord Design (Event-Driven, Full Integration, Expanded)


---

1. High-Level Structure

The spinal cord module mimics real physiology while staying efficient:

Dorsal root → sensory input (afferents).

Dorsal horn → integration + thresholding.

Reflex circuits → fast loops for survival.

Ventral horn → motor pools (efferents).

Ventral root → symbolic motor actions.

Ascending pathways → copies to higher centers.

Integration stubs → placeholders for brain modules.

Scheduler → event-driven, only runs when spikes occur.



---

2. Event-Driven Scheduler

Keeps a priority queue of (time, priority, fn, args).

Idle baseline, bursts only when events fire.


def schedule(time_ms, priority, fn, *args):
    # Insert into queue
    event_q.push((time_ms, priority, fn, args))

def run_until(t_stop):
    while queue_not_empty and next_event.time <= t_stop:
        t, pri, fn, args = pop_next_event()
        fn(t, *args)   # fire the event handler


---

3. Sensory Afferents (Dorsal Root Fibers)

A-β: touch/pressure.

Ia/II: muscle spindle (length/velocity).

Ib: Golgi tendon (force/tension).

A-δ: fast sharp pain (15 m/s).

C: slow dull pain (1 m/s).


Conduction modeled by distance / velocity → ms delay.

def afferent_fire(fiber, distance_cm, weight, target):
    velocity = fiber_velocity[fiber]   # e.g. Aδ=15 m/s
    delay_ms = (distance_cm/100)/velocity * 1000
    schedule(now + delay_ms, 0, target, weight, fiber)


---

4. Dorsal Horn (Integration)

Uses leaky integrate-and-fire (LIF) style neurons.

Only crosses threshold when stimulus is strong enough.

Generates symbolic reflex triggers.


if signal.type == "pain":
    if nociceptor.integrate(weight=signal.intensity):
        return {"reflex":"withdraw", "fiber":"Aδ", "severity":"high"}
elif signal.type == "touch":
    if mechanoreceptor.integrate(weight=signal.intensity):
        return {"reflex":"light_contact", "fiber":"Aβ", "severity":"low"}


---

5. Nociception (Pain Specialization)

Fast A-δ pain → instant withdrawal.

Slow C pain → delayed, persistent, limbic tagging.

Wind-up: repeated C input within window → amplify severity.


if fiber == "C":
    c_event_log.append(now)
    if len(events_within(1500_ms)) >= 5:
        reflex["severity"] = "high"   # wind-up effect


---

6. Ventral Horn (Motor Pools)

Pools of α-motor neurons grouped per action.

Each action = redundant neurons for smooth firing.


motor_pools = {
  "withdraw_arm": ["alpha1","alpha2","alpha3"],
  "flex_leg": ["alpha4","alpha5"]
}

def trigger_action(reflex_cmd):
    return {"action": reflex_cmd, "neurons_fired": motor_pools.get(reflex_cmd, [])}


---

7. Reflex Circuits (Core Loops)

Stretch reflex: spindle → α agonist.

Reciprocal inhibition: antagonist suppressed.

Golgi tendon reflex: too much force → agonist inhibited.

Withdrawal reflex: flexor excite, extensor inhibit.

Crossed extensor reflex: contralateral extensor excite.

Renshaw cells: α collateral → inhibition of same pool to stop runaway bursts.


if reflex == "withdraw":
    excite("flexor_pool")
    inhibit("extensor_pool")          
    excite("contralateral_extensors") 
    renshaw_feedback("flexor_pool")   # recurrent inhibition


---

8. Ascending Pathways

Always forward a copy of input + reflex upward.

Adds fiber metadata for context.


forward = {
  "to_thalamus": original_signal,
  "reflex_copy": reflex,
  "fiber": reflex.get("fiber","unknown")
}


---

9. Integration Stubs

Symbolic placeholders to wire into future modules:

ThalamusStub: logs reception.

BrainstemStub: survival-level regulation.

CerebellumStub: fine-tunes motor outputs.

LimbicStub: tags pain with emotions.

PFCStub: allows voluntary override.

OccipitalStub / AuditoryStub: orienting reflexes.


class LimbicStub:
    def tag_emotion(self, pain_signal):
        return {"emotion":"fear", "source":pain_signal}


---

10. Audit & Logging

Each event written to AuditLoggerFactory:

Timestamp

Fiber type & delay

Reflex type

Motor pool output

Ascending copies + emotional tags


logger.log({
  "t": now,
  "fiber": "Aδ",
  "reflex": "withdraw",
  "motor_pool": ["alpha1","alpha2"],
  "ascending": ["thalamus","limbic"],
  "emotion": "fear"
})


---

11. Biomimetic Efficiency Principles

Always alive, rarely active — idle ionic baseline until input arrives.

Event-driven — compute only on spikes/reflexes.

Delays & refractory periods — natural timing + reduced compute.

Procedural reflex rules — symbolic state machines instead of dense sim.

Integration stubs — allow future modules to expand without rewriting.



Addendum: Reflex Timing (A-δ vs C fibers)

Fast Pain (A-δ fiber)

Stimulus: pinprick to finger.

Conduction: ~15 m/s, distance 1 m → ~67 ms delay.

Dorsal horn: threshold crossed quickly → reflex generated.

Ventral horn: flexor pool fires → withdrawal before brain notices.

Ascending copy: thalamus & limbic receive context within ~100 ms total.


Pseudo-code timing sketch:

afferent_fire("Aδ", distance=100, weight=80, target=dorsal_horn)  
# ~67 ms later → dorsal_horn triggers withdrawal reflex
# reflex_arc completes + ascending copy sent ~100 ms


---

Slow Pain (C fiber)

Stimulus: burn to hand.

Conduction: ~1 m/s, distance 1 m → ~1000 ms delay.

Dorsal horn: slow arrival, weaker signal, but sustained.

Ventral horn: reflex may still fire, but delayed & weaker.

Ascending copy: limbic tagging stronger (“fear/ache”), arrives much later.


Pseudo-code timing sketch:

afferent_fire("C", distance=100, weight=60, target=dorsal_horn)  
# ~1000 ms later → dorsal_horn processes
# reflex delayed, limbic tagging amplified


---

Key Takeaway

A-δ fibers = sharp, immediate withdrawal → ~0.1 sec.

C fibers = dull, aching pain → ~1 sec or more, adds emotional weight.



---

✅ Result: A spinal cord that runs like biology —

Fast local reflexes, modulated by higher centers.

Minimal compute (event-driven bursts).

Symbolic hooks for Vex’s larger architecture.

Full logging for audit and override.






