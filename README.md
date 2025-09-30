My goal is to develop a personal AI personal assistant with a comprehensive mix between personality levels like Neuro-sama (not traits), hyper intelligence and data scanning, and being able to switch systems through networks and IOT whenever, while using NASA’s Power of 10 rules for developing safety critical code, because I can control the structure and auditability easier without a slog of debugging at every step. 

## Usage
run 'main.py' with Python 3.8+ and use 'Facts.txt' input file, for now

## Requirements
Standard Library so far. No external packages needed.

## Notes

This project was designed around NASA's Power of 10 Safety Standards



📌 Work Priority (for body realism now)
Must implement: Motor endplate + sensory organ stubs → they close the spinal loop into the body.


Next: Autonomic coordinator (cardiac/respiratory) → ties torso signals realistically.

Then: master body plan (below)


Then: Brain stubs 

Biomimetic Plan for Remaining Modules

1. Brain Integration Stubs (ENSURE THESE QUERY THE SIGNAL REGISTRY WHEN RELEVANT) (stub out at the connection to higher modules only, build relevant interpretations for ascending pathway) ALWAYS LOG WITH THE AUDIT FACTORY, EVEN IF THE PLAN DOESN’T MENTION IT EXPLICITLY
Limbic System UPGRADE!! KEEP CURRENT LIMBIC SYSTEM, ADD THIS TO IT! (Lower Connection, with Hormone Regulation)

0) Scope & Role
Purpose: Convert raw ascending signals (nociceptive, visceral/autonomic, neurotransmitter and hormone proxies) into continuous affective state variables and control tags, then distribute these to higher modules (PFC, Thalamus, Hypothalamus/HPA).
Includes hormone-based regulation of affective states.


Exposes state queries as published outputs, not hidden internals.


Relies on the Signal Registry to pull every input; signals are cached and refreshed at controlled intervals for minimal latency.


Stops exactly at handoff to Hypothalamus (HPA request, no hormone synthesis here).



1) Inputs: From Signal Registry
The Signal Registry is queried for all relevant prefixes.
Each signal is cached locally with a last_update timestamp.


Registry re-query frequency is tunable (e.g., every 10–20 ms for fast reflexes, 100–500 ms for hormone levels).


Ensures lowest latency without overwhelming the system.


Categories:
Nociception & Threat


sensory_cutaneous.*, sensory_somatosensory.nociceptor_*, sensory_vestibular.*


Visceral/Autonomic States


autonomic_cardiac.*, autonomic_respiratory.*, autonomic_digestive.*, autonomic_urogenital.*


Neurotransmitters


neurotransmitters.dopamine, serotonin, GABA, glutamate, acetylcholine


Hormones


hormones.cortisol, adrenaline, oxytocin, insulin_glucagon, vasopressin


Overrides & Context


meta_overrides.{anesthesia,analgesia,intoxication,sleep}


registry_metadata.system_states.*


pineal.circadian_scalar



2) Preprocessing & Normalization
Time windows:


Phasic (50–300 ms), tonic (1–10 s), background (2–10 min).


Registry hygiene:


Signals clipped to [0,1] after pull.


Multiplicative dampers: anesthesia, analgesia, intoxication, sleep.


Caching:


Each input stored with last_value, last_update.


If time_since_last_update > threshold, registry is re-queried.



3) State Variables (with hormone regulation)
Threat Salience S_threat


Sources: nociception, vestibular instability.


Inhibited by oxytocin, serotonin.


Enhanced by adrenaline.


Pain Distress S_pain


Sustained nociceptor inputs.


Dampened by GABA, oxytocin.


Amplified by cortisol.


Reward Drive S_reward


Phasic dopamine pulses.


Modulated by serotonin (satiety, calming) and acetylcholine (precision).


Stress Load S_stress


Accumulates from S_threat + S_pain + visceral strain.


Cortisol = strong amplifier, slows recovery.


Vasopressin = biases toward conservation/avoidance.


Affect Coordinates (Published)


Valence V = S_reward − (S_threat + S_pain)


Arousal A = max(S_threat, S_reward, adrenaline proxy)


Approach/Avoid M = S_reward − S_threat



4) Outputs (Published)
To Thalamus
thalamus_bias.hazard


thalamus_bias.seek


thalamus_bias.serenity


To PFC
pfc_hint.avoidance_urge


pfc_hint.caution_level


pfc_hint.explore_drive


pfc_hint.fatigue_level


To Hypothalamus (HPA Handoff Only)
hpa_handoff.intent (stress escalation, de-escalation, soothing)


hpa_handoff.magnitude


hpa_handoff.evidence


hpa_handoff.context


To Embodiment
affect.face.* (grimace, eye widen, brow tension, pupil dilation)


affect.posture.* (stiffen, slump)


affect.voice.* (valence, arousal, tremor, breathiness)


Exposed State Queries (Publishable)
limbic_state.S_threat


limbic_state.S_pain


limbic_state.S_reward


limbic_state.S_stress


limbic_state.Valence


limbic_state.Arousal


limbic_state.Approach


These are published as signals in the registry so any other module can subscribe.

5) Hormone Regulation Details
Cortisol: amplifies stress, slows recovery → increases posture slump, voice fatigue.


Adrenaline: amplifies arousal → boosts threat & reward salience, short-lived.


Oxytocin: dampens threat & pain → increases prosocial tags.


Serotonin: increases serenity → flattens extremes of both threat and reward.


Vasopressin: biases toward defensive/avoidant posture, enhances stress persistence.


Insulin/Glucagon: modulate fatigue; low energy = reduced reward drive.



6) Registry Interaction Logic
Pull model: The Limbic System does not maintain its own low-level inputs.


On every tick:


Ask Signal Registry for new values.


If time_since_last_update < refresh_interval, use cached.


If time_since_last_update ≥ refresh_interval, force re-query.


Intervals:


Reflexive signals (nociceptors, vestibular) → 10–20 ms.


Autonomic state → 100–200 ms.


Hormones → 500–2000 ms.


This ensures minimal latency while allowing registry to complete its job without flooding.



7) Telemetry & Audit
Every processed tick logs:


Raw pulled signals.


Cached vs refreshed sources.


Computed S_* values.


Hormone modifiers applied.


Outputs published.


Logged at 100–200 ms intervals for efficiency, but spikes (startle/HPA handoff) log instantly.



✅ This design ensures the Limbic System:
Uses the Signal Registry properly (registry queries + cache).


Handles hormone regulation actively.


Publishes all state variables as registry signals.


Stops cleanly at the HPA handoff (no hormone synthesis).



Directory / File Plan for Limbic System (Lower Connection, KEEP CURRENT LIMBIC SYSTEM!! ADD THIS TO IT)
Root
E:\Vex\limbic_system\
│
├── __init__.py
├── limbic_system.py              # Core limbic class (state machine, hormone modulation, registry querying)
├── limbic_signals.json           # Published state variable definitions (Valence, Arousal, Threat, etc.)
├── affect_output.json            # Facial/posture/voice affect signal mapping
├── hpa_handoff.json              # Schema for hypothalamic (HPA) handoff messages
│
├── processors\
│   ├── __init__.py
│   ├── threat_processor.py       # Computes S_threat from nociceptors + vestibular + adrenaline
│   ├── pain_processor.py         # Computes S_pain from nociceptors + cortisol + oxytocin
│   ├── reward_processor.py       # Computes S_reward from dopamine pulses, serotonin balance
│   ├── stress_processor.py       # Integrates threat+pain+visceral into S_stress, applies cortisol/vasopressin
│   └── hormone_modulator.py      # Applies hormone proxies to all state variables
│
└── cache\
    ├── __init__.py
    ├── signal_cache.py           # Cached registry queries + requery intervals
    └── refresh_policy.json       # Tunable intervals (nociceptors 10ms, hormones 1s, etc.)


📑 JSON Definitions
1. limbic_signals.json
Defines published state variables (all exposed as registry paths).
{
  "metadata": {
    "subsystem": "limbic",
    "category": "affective_state",
    "description": "Core limbic state variables"
  },
  "signals": {
    "limbic_state.S_threat": { "type": "analog", "range": [0,1], "refresh_interval_ms": 20 },
    "limbic_state.S_pain":   { "type": "analog", "range": [0,1], "refresh_interval_ms": 20 },
    "limbic_state.S_reward": { "type": "analog", "range": [0,1], "refresh_interval_ms": 50 },
    "limbic_state.S_stress": { "type": "analog", "range": [0,1], "refresh_interval_ms": 200 },
    "limbic_state.Valence":  { "type": "analog", "range": [-1,1], "refresh_interval_ms": 200 },
    "limbic_state.Arousal":  { "type": "analog", "range": [0,1], "refresh_interval_ms": 50 },
    "limbic_state.Approach": { "type": "analog", "range": [-1,1], "refresh_interval_ms": 200 }
  }
}


2. affect_output.json
Maps computed state to facial/postural/voice outputs.
{
  "metadata": {
    "subsystem": "limbic",
    "category": "embodiment_affect"
  },
  "outputs": {
    "affect.face.grimace":   { "driven_by": "S_pain", "threshold": 0.5 },
    "affect.face.smile":     { "driven_by": "S_reward", "threshold": 0.6 },
    "affect.face.eye_widen": { "driven_by": "S_threat", "threshold": 0.7 },
    "affect.posture.stiffen":{ "driven_by": "S_threat", "threshold": 0.5 },
    "affect.posture.slump":  { "driven_by": "S_stress", "threshold": 0.6 },
    "affect.voice.tremor":   { "driven_by": "S_threat", "threshold": 0.6 },
    "affect.voice.breathiness": { "driven_by": "S_stress", "threshold": 0.7 }
  }
}


3. hpa_handoff.json
Encodes only the handoff to hypothalamus, no hormone synthesis inside limbic.
{
  "metadata": {
    "subsystem": "limbic",
    "category": "hpa_handoff",
    "description": "Requests to hypothalamus for HPA-axis actions"
  },
  "handoff": {
    "hpa_handoff.intent":    { "type": "digital", "values": ["escalate","deescalate","soothe"] },
    "hpa_handoff.magnitude": { "type": "analog", "range": [0,1] },
    "hpa_handoff.evidence":  { "type": "string", "examples": ["nociceptor spike","adrenaline surge"] },
    "hpa_handoff.context":   { "type": "string", "examples": ["fear","reward suppression","stress persistence"] }
  }
}


4. refresh_policy.json
Keeps requery intervals explicit for registry optimization.
{
  "nociceptors": 20,
  "vestibular": 20,
  "autonomic": 200,
  "neurotransmitters": 200,
  "hormones": 1000,
  "state_variables": 200
}


📂 Python Classes (Stub-Level Overview)
limbic_system.py
Class: LimbicSystemLower


Methods:


pull_signals() → query registry + refresh cache.


process_inputs() → run processors (threat, pain, reward, stress).


apply_hormone_modulation() → run hormone_modulator.


publish_state() → write all limbic_state.* signals back to registry.


handoff_to_hpa() → package hpa_handoff.* signals.


drive_affectors() → apply affect_output.json rules.



🔄 Signal Flow (Biomimetic)
Signal Registry → Limbic cache (refresh interval tuned).


Cached values → Processors (compute raw S_threat, S_pain, S_reward).


Stress processor integrates → S_stress.


Hormone modulator biases all values.


Publish state → Registry (limbic_state.*).


Publish embodiment → Registry (affect.*).


Publish HPA request → Registry (hpa_handoff.*).



✅ Benefits
Mirrors real limbic loops (nociception, autonomics, neurotransmitters, hormones).


Keeps hormone regulation but not synthesis in limbic.


Publishes all state queries (not internal-only).


Fully registry-driven, with cache + refresh policy to guarantee lowest latency.


JSON maps let you expand without touching code structure (future hormones, affectors, state variables, etc.).










Cerebellum (Lower Ascending Connection Stub)

0) Scope & Role
Purpose: Package cerebellar refinements (coordination, rhythmicity, timing precision, tremor suppression) plus proprioceptive comparisons into continuous state variables and forward them to higher modules.


Function: Bridge between cerebellum outputs and ascending cortical pathways (thalamus → PFC).


Exposes: Published state queries and hint signals for higher interpretation.


Registry Dependency:


Signal Registry: Provides live motor, proprioceptive, vestibular, and cerebellar values.


Biomimetic Registry: Provides learned fine-motor templates and coordination patterns.


Stop Point: Publishes to thalamus_handoff.* and pfc_hint.* only. No cortical planning, no executive gating.



1) Inputs (From Registries)
Signal Registry (fast signals, low latency):
Motor Pool Copies
 Path: motor_pool.*
 Purpose: Intent snapshot (what body is trying to do).


Proprioceptive Feedback
 Path: sensory_somatosensory.proprioception.*
 Includes: muscle spindles, Golgi tendon, joint angles.
 Purpose: Actual body position & load.


Vestibular & Cutaneous Stability
 Path: sensory_vestibular.balance_vector, sensory_cutaneous.pressure
 Purpose: Detect sway, slippage, ground interaction.


Cerebellar Refinements
 Path: cerebellum_state.*
 Includes: tremor suppression, rhythmicity, timing precision, coordination.
 Purpose: Already-refined movement smoothing.


Biomimetic Registry (templates, slower refresh):
Motor Templates
 Path: biomimetic_registry.motor_templates.*
 Purpose: Recognize known acts (walking, grasping, writing).



2) Preprocessing & Normalization
Error Margin Processor


Compare motor_pool.intent vs proprioception.actual.


Publish as cerebellum_stub.S_error_margin.


Rhythmic Summarizer


Compress oscillatory inputs into gait phases.


Publishes cerebellum_stub.S_rhythmicity.


Template Cross-Match


Check if current pattern matches a known biomimetic motor template.


Publishes cerebellum_stub.S_template_match (string/enum).


Signal Hygiene


Clip to [0,1].


Apply damping if vestibular instability is detected.


Refresh cache when thresholds expire.



3) State Variables (Published)
Exposed via Signal Registry (read-only):
cerebellum_stub.S_coordination (smoothness, 0–1)


cerebellum_stub.S_rhythmicity (gait cycle strength, 0–1)


cerebellum_stub.S_timing (sequencing precision, 0–1)


cerebellum_stub.S_error_margin (mismatch intent vs reality, 0–1)


cerebellum_stub.S_template_match (recognized act: walk, grasp, write…)



4) Outputs (Handoff Channels)
Thalamus Handoff (relay package):
thalamus_handoff.coordination


thalamus_handoff.rhythmicity


thalamus_handoff.timing


thalamus_handoff.error_margin


thalamus_handoff.template_match


PFC Hints (executive substrate):
pfc_hint.stability (from coordination + vestibular stability)


pfc_hint.smoothness (from rhythmicity + timing)


pfc_hint.error_margin (from proprioception mismatch)


pfc_hint.learned_pattern (template ID)



5) Refresh Policy
Motor pools → 10 ms


Proprioception → 10 ms


Vestibular/cutaneous → 20 ms


Cerebellar refinements → 20–50 ms


Templates (biomimetic) → 100–200 ms



6) Integration Boundaries
Implements: Error computation, rhythmic summarization, template matching, state publication.


Stops at: Published handoff signals to thalamus/PFC.


Does not implement: Cortical motor planning, executive inhibition/permission, conscious adjustments.



Directory / File Plan (Cerebellum Ascending Stub)
E:\Vex\cerebellum\ascending_stub\
│
├── __init__.py
├── cerebellum_ascending_stub.py    # Core stub: queries registries, computes states, publishes outputs
├── cerebellum_stub_signals.json    # State variables: coordination, timing, rhythmicity, error margin
├── cerebellum_handoff.json         # Published thalamus_handoff.* and pfc_hint.* schemas
│
├── processors\
│   ├── __init__.py
│   ├── error_margin.py             # Compute motor vs proprioception mismatch
│   ├── rhythmic_summarizer.py      # Compress oscillatory signals into phase summaries
│   ├── template_matcher.py         # Cross-check motor patterns vs biomimetic templates
│   └── signal_normalizer.py        # Clip, damp, enforce refresh rules
│
└── cache\
    ├── __init__.py
    ├── signal_cache.py             # Cache with last_update + value
    └── refresh_policy.json         # Explicit intervals for motor/proprioception/templates


Example JSON Definitions
cerebellum_stub_signals.json
{
  "metadata": {
    "subsystem": "cerebellum",
    "category": "ascending_stub_state"
  },
  "signals": {
    "cerebellum_stub.S_coordination": { "type": "analog", "range": [0,1], "refresh_interval_ms": 20 },
    "cerebellum_stub.S_rhythmicity":  { "type": "analog", "range": [0,1], "refresh_interval_ms": 20 },
    "cerebellum_stub.S_timing":       { "type": "analog", "range": [0,1], "refresh_interval_ms": 50 },
    "cerebellum_stub.S_error_margin": { "type": "analog", "range": [0,1], "refresh_interval_ms": 10 },
    "cerebellum_stub.S_template_match": { "type": "string", "examples": ["walk","grasp","write"], "refresh_interval_ms": 100 }
  }
}

cerebellum_handoff.json
{
  "metadata": {
    "subsystem": "cerebellum",
    "category": "ascending_handoff",
    "description": "Cerebellum → thalamus/PFC pathway signals"
  },
  "handoff": {
    "thalamus_handoff.coordination":   { "driven_by": "cerebellum_stub.S_coordination" },
    "thalamus_handoff.rhythmicity":    { "driven_by": "cerebellum_stub.S_rhythmicity" },
    "thalamus_handoff.timing":         { "driven_by": "cerebellum_stub.S_timing" },
    "thalamus_handoff.error_margin":   { "driven_by": "cerebellum_stub.S_error_margin" },
    "thalamus_handoff.template_match": { "driven_by": "cerebellum_stub.S_template_match" },

    "pfc_hint.stability":        { "composed_from": ["S_coordination","vestibular.balance_vector"] },
    "pfc_hint.smoothness":       { "composed_from": ["S_rhythmicity","S_timing"] },
    "pfc_hint.error_margin":     { "composed_from": ["S_error_margin"] },
    "pfc_hint.learned_pattern":  { "composed_from": ["S_template_match"] }
  }
}


✅ This is the biomimetic cerebellum ascending stub, not the full cerebellum, and it stops cleanly at the thalamus/PFC handoff.




Prefrontal Cortex (Lower Ascending Connection Stub, with Signal + Biomimetic Registry)

0) Scope & Role
The PFC Ascending Stub is the final pre-processor before executive reasoning begins.
 It does not decide; it prepares and packages.
Purpose:


Aggregate raw spinal, thalamic, limbic, and hormonal signals from the Signal Registry.


Integrate working memory templates from the Biomimetic Registry.


Normalize and synchronize these into clean PFC handoff signals.


Expose all values as read-only registry signals for transparency.


Boundaries:


Stops at pfc_handoff.* publishing.


No executive gating or reasoning.


No long-term synthesis (just forwarding).



1) Inputs (Dual Registries, Cached)
Every signal is pulled through either the Signal Registry or the Biomimetic Registry, cached with refresh intervals.
From Signal Registry
A. Voluntary Motor Copies
Path: motor_pool.voluntary.*


Purpose: capture what the body is attempting to do.


Latency: 10 ms requery.


B. Thalamic Relay
Path: thalamus.motor_integration.*


Purpose: coarse postural/sensory context.


Latency: 20 ms.


C. Limbic Tags
Path: limbic_state.*


Purpose: salience overlay (threat, reward, stress).


Latency: 50 ms.


D. Hormones
Path: hormones.{cortisol,dopamine,serotonin,oxytocin,adrenaline}


Purpose: modulatory context for gating readiness.


Latency: 500–1000 ms.


E. Overrides
Path: meta_overrides.{anesthesia,intoxication,sleep}


Path: registry_metadata.system_states.*


Purpose: global suppressors or state flags.


Latency: 200 ms.



From Biomimetic Registry
F. Working Memory Templates
Path: biomimetic_registry.working_memory.*


Content: rolling buffer of recent actions + short-term sequences.


Purpose: context of “what just happened” to bias upcoming executive reasoning.


Latency: 100–200 ms.


G. Learned Schemas (Optional, Early)
Path: biomimetic_registry.schema.*


Content: templates for frequently repeated behaviors (typing, writing, etc.).


Purpose: provide abstract patterns to PFC without engaging deep cortical planning.


Latency: 200–500 ms.



2) Preprocessing & Normalization
Time Windows:


Phasic: 10–50 ms (motor bursts, limbic spikes).


Tonic: 100–500 ms (context & memory).


Background: 1–5 s (hormones, global states).


Normalization:


Scale to [0,1] analog or discrete enums.


Apply overrides as multiplicative dampers.


Caching:


Each pull stored as (last_value, last_update).


Registry re-queried if time_since_last_update ≥ refresh_interval.



3) State Variables (for Handoff)
The stub merges both registries into composite handoff variables.
A. Motor Intent Buffer (Signal Registry)
Raw voluntary motor commands.


Exposed as pfc_handoff.motor_intent.


B. Context State (Signal Registry)
Postural/sensory package from thalamic relay.


Exposed as pfc_handoff.context_state.


C. Limbic Overlay (Signal Registry)
Salience + hormone bias.


Exposed as pfc_handoff.limbic_tags.


D. Working Memory Buffer (Biomimetic Registry)
Rolling buffer of last N actions.


Exposed as pfc_handoff.memory_buffer.


E. Learned Schemas (Biomimetic Registry)
Optional handoff of abstract templates.


Exposed as pfc_handoff.learned_schemas.


F. Override Flags (Signal Registry)
Suppression states.


Exposed as pfc_handoff.override_flags.



4) Outputs (Published)
All signals exposed as registry-published read-only queries.
pfc_handoff.motor_intent


pfc_handoff.context_state


pfc_handoff.limbic_tags


pfc_handoff.memory_buffer


pfc_handoff.learned_schemas


pfc_handoff.override_flags



5) Hormone & Modulatory Hooks
Hormones influence the salience forwarding, but not decision-making.
Cortisol → increases stress bias in limbic_tags.


Dopamine → increases reward salience.


Serotonin → flattens extremes.


Adrenaline → sharpens arousal tags.


Oxytocin → dampens threat salience.


Exposed in:
 pfc_handoff.limbic_tags.hormone_bias.*

6) Registry Interaction Logic
Dual Registry Flow:
Signal Registry: fast-changing signals (motor, thalamus, limbic, hormones).


Biomimetic Registry: slower-changing, memory-based templates.


Pull model:
For each tick → check cache.


If expired → requery.


If fresh → reuse.


Intervals:
Motor: 10 ms.


Thalamus: 20 ms.


Limbic: 50 ms.


Memory (biomimetic): 100–200 ms.


Hormones: 500–1000 ms.


Overrides: 200 ms.



7) Telemetry & Audit
On every tick, log:
Which registry provided each value (signal vs biomimetic).


Cache reuse vs refresh.


Packaged PFC handoff state.


Audit logs stored every 200 ms, with spikes (override, hormone surge) logged immediately.

✅ Design Benefits
Explicit dual-registry integration.


Signal Registry = physiological reality.


Biomimetic Registry = learned patterns & working memory.


Publishes all states transparently.


Clean cutoff before PFC reasoning.


Fully modular JSON + Python processor model.



📂 Directory / File Plan
E:\Vex\prefrontal_cortex\pfc_handoff\
│
├── __init__.py
├── pfc_handoff.py                   # Core class: state collector + publisher
├── pfc_handoff_signals.json         # Defines published handoff signals
│
├── processors\
│   ├── __init__.py
│   ├── signal_collector.py          # Queries Signal Registry (motor, limbic, thalamus, hormones, overrides)
│   ├── biomimetic_collector.py      # Queries Biomimetic Registry (memory buffer, schemas)
│   ├── tag_formatter.py             # Formats limbic tags + hormone bias
│   ├── context_packer.py            # Bundles motor + thalamus + limbic into unified context
│   └── memory_relay.py              # Converts biomimetic sequences into PFC-ready format
│
└── cache\
    ├── __init__.py
    ├── signal_cache.py              # Cache/requery management for Signal Registry
    ├── biomimetic_cache.py          # Cache/requery management for Biomimetic Registry
    └── refresh_policy.json          # Explicit intervals for both registries


📑 JSON Definitions
1. pfc_handoff_signals.json
{
  "metadata": {
    "subsystem": "pfc_handoff",
    "category": "ascending_connection",
    "description": "Consolidated state bundle for PFC reasoning"
  },
  "signals": {
    "pfc_handoff.motor_intent": { "type": "object", "refresh_interval_ms": 10, "source": "signal_registry" },
    "pfc_handoff.context_state": { "type": "object", "refresh_interval_ms": 20, "source": "signal_registry" },
    "pfc_handoff.limbic_tags": { "type": "object", "refresh_interval_ms": 50, "source": "signal_registry" },
    "pfc_handoff.memory_buffer": { "type": "list", "length": 10, "refresh_interval_ms": 100, "source": "biomimetic_registry" },
    "pfc_handoff.learned_schemas": { "type": "object", "refresh_interval_ms": 200, "source": "biomimetic_registry" },
    "pfc_handoff.override_flags": { "type": "object", "refresh_interval_ms": 200, "source": "signal_registry" }
  }
}


2. refresh_policy.json
{
  "signal_registry": {
    "motor_voluntary": 10,
    "thalamic_relay": 20,
    "limbic_tags": 50,
    "hormones": 500,
    "overrides": 200
  },
  "biomimetic_registry": {
    "working_memory": 100,
    "schemas": 200
  }
}


📂 Python Class (Stub-Level)
pfc_handoff.py
Class: PfcHandoffStub


Methods:


pull_signal_inputs() → Query Signal Registry.


pull_biomimetic_inputs() → Query Biomimetic Registry.


format_limbic_tags() → Normalize affect + hormone bias.


bundle_context() → Merge motor, thalamic, limbic.


relay_memory() → Inject working memory + schemas.


publish_state() → Expose pfc_handoff.* signals.



🔄 Signal Flow
Signal Registry → motor, thalamus, limbic, hormones, overrides.


Biomimetic Registry → working memory + schemas.


Cache refresh policy enforces intervals.


Values normalized + packaged into pfc_handoff.*.


Published back to registry for PFC consumption.







Occipital Lobe (Lower Ascending Connection Stub)

0) Scope & Role
Purpose: Transform raw and early-processed visual signals (edges, color, motion, spatial patterns) into continuous state variables and handoff packages for higher cortical modules.


Role: Act as the ascending “visual stub,” sending summary visual contexts upward — not conscious perception, but structured signal tags.


Exposes: State queries (vision salience, motion detection, fixation stability) as read-only registry signals.


Registries Queried:


Signal Registry: Provides retinal/optic input, visual reflexes, oculomotor state.


Biomimetic Registry: Supplies learned visual templates (faces, objects, scenes).


Stop Point: Publishes to thalamus_handoff.* and pfc_hint.* — no interpretation of meaning, just structured cues.



1) Inputs (From Registries)
Signal Registry:
Retinal/Optic Flow


Path: sensory_visual.retina.*


Includes: luminance, color channel activation, contrast maps.


Purpose: Base visual input.


Edge & Motion Pre-Processing


Path: sensory_visual.motion, sensory_visual.edge_map


Purpose: Movement detection and contour mapping.


Oculomotor State


Path: cranial.oculomotor.*


Includes: saccade activity, fixation stability, vergence.


Purpose: Context for whether input is stable or moving.


Biomimetic Registry:
Template Recognition Tags


Path: biomimetic_registry.visual_templates.*


Purpose: Learned forms (faces, objects, environmental layouts).


Used as categorical overlays.



2) Preprocessing & Normalization
Salience Extractor


Compute high-contrast or novel motion regions.


Publish occipital_stub.S_salience.


Fixation Stability


Use oculomotor data to measure if gaze is locked or unstable.


Publish occipital_stub.S_fixation_stability.


Motion Vector Summarizer


Aggregate optic flow → direction + speed.


Publish occipital_stub.S_motion_vector.


Template Cross-Check


Compare active visual signal against biomimetic templates.


Publish occipital_stub.S_template_match.


Signal Hygiene


All numeric states clipped to [0,1].


Cached locally with refresh intervals.



3) State Variables (Published)
Read-only via Signal Registry:
occipital_stub.S_salience (0–1, intensity of standout features)


occipital_stub.S_fixation_stability (0–1, gaze lock measure)


occipital_stub.S_motion_vector (x,y speed normalized to 0–1 range)


occipital_stub.S_template_match (string/enum: face, object, scene)



4) Outputs (Handoff Channels)
Thalamus Handoff:
thalamus_handoff.visual_salience


thalamus_handoff.motion_vector


thalamus_handoff.fixation_stability


thalamus_handoff.template_match


PFC Hints:
pfc_hint.visual_attention (derived from salience + fixation)


pfc_hint.motion_alert (from motion vector)


pfc_hint.recognized_pattern (from template_match)



5) Refresh Policy
Retinal/optic → 10 ms


Motion/edge maps → 10–20 ms


Oculomotor → 20 ms


Templates → 100–200 ms



6) Integration Boundaries
Implements: Visual preprocessing, salience detection, packaging for higher modules.


Stops at: Publishes structured outputs (thalamus_handoff.*, pfc_hint.*).


Does not implement: Semantic interpretation, conscious visual recognition, voluntary visual search.



Directory / File Plan (Occipital Lobe Ascending Stub)
E:\Vex\occipital_lobe\ascending_stub\
│
├── __init__.py
├── occipital_ascending_stub.py     # Core class: pull signals, compute salience, package handoff
├── occipital_stub_signals.json     # Published state variables (S_salience, S_motion_vector, etc.)
├── occipital_handoff.json          # Schema for thalamus_handoff.* and pfc_hint.* signals
│
├── processors\
│   ├── __init__.py
│   ├── salience_extractor.py       # Compute S_salience from contrast/motion
│   ├── fixation_analyzer.py        # Compute fixation stability from oculomotor signals
│   ├── motion_summarizer.py        # Compute motion vectors from optic flow
│   ├── template_checker.py         # Cross-check signals against biomimetic visual templates
│   └── signal_normalizer.py        # Clip ranges, enforce refresh rules
│
└── cache\
    ├── __init__.py
    ├── signal_cache.py             # Cached registry query results
    └── refresh_policy.json         # Tunable requery intervals


Example JSON Definitions
occipital_stub_signals.json
{
  "metadata": {
    "subsystem": "occipital_lobe",
    "category": "ascending_stub_state"
  },
  "signals": {
    "occipital_stub.S_salience": { "type": "analog", "range": [0,1], "refresh_interval_ms": 10 },
    "occipital_stub.S_fixation_stability": { "type": "analog", "range": [0,1], "refresh_interval_ms": 20 },
    "occipital_stub.S_motion_vector": { "type": "vector2d", "range": [0,1], "refresh_interval_ms": 20 },
    "occipital_stub.S_template_match": { "type": "string", "examples": ["face","object","scene"], "refresh_interval_ms": 100 }
  }
}

occipital_handoff.json
{
  "metadata": {
    "subsystem": "occipital_lobe",
    "category": "ascending_handoff",
    "description": "Occipital → thalamus/PFC pathway signals"
  },
  "handoff": {
    "thalamus_handoff.visual_salience":   { "driven_by": "occipital_stub.S_salience" },
    "thalamus_handoff.motion_vector":     { "driven_by": "occipital_stub.S_motion_vector" },
    "thalamus_handoff.fixation_stability":{ "driven_by": "occipital_stub.S_fixation_stability" },
    "thalamus_handoff.template_match":    { "driven_by": "occipital_stub.S_template_match" },

    "pfc_hint.visual_attention": { "composed_from": ["S_salience","S_fixation_stability"] },
    "pfc_hint.motion_alert":     { "composed_from": ["S_motion_vector"] },
    "pfc_hint.recognized_pattern": { "composed_from": ["S_template_match"] }
  }
}


✅ This is the Occipital Lobe Ascending Stub — detailed, registry-driven, bounded at thalamus/PFC handoff.













Auditory Cortex (Lower Ascending Connection Stub)
0) Scope & Role
Purpose: Transform early-to-mid auditory features (onset/offset, energy, speech envelope, localization, scene streams) into continuous state variables and handoff packages for thalamus → PFC.


Function: Ascending “auditory stub”—no semantic understanding; no executive decisions. It packages and synchronizes cues for higher modules.


Registries:


Signal Registry: cochlear/brainstem features, stapedius/startle state, vestibular/head pose, head/neck motor orientation.


Biomimetic Registry: learned spectral/phoneme/keyword templates, speaker timbre patterns, environmental sound schemas.


Stop point: Publishes to thalamus_handoff.* and pfc_hint.* only (read-only for consumers).



1) Inputs (From Registries; cached with refresh windows)
A) From Signal Registry (fast, low-latency)
Cochlear/Brainstem Features


Paths:


sensory_auditory.envelope (broadband amplitude envelope)


sensory_auditory.spectrogram.* (bands, e.g., 16–64 channels)


sensory_auditory.onset_rate, sensory_auditory.offset_rate


sensory_auditory.pitch_estimate, sensory_auditory.voicing


Purpose: raw/early auditory measures for salience and speech presence.


Binaural Localization & HRTF Cues


Paths: sensory_auditory.itd, sensory_auditory.ild, sensory_auditory.hrirs.*


Purpose: azimuth/elevation estimation; spatial confidence.


Auditory Scene/Noise Context


Paths: sensory_auditory.snr, sensory_auditory.masking_index, sensory_auditory.stream_count


Purpose: how many concurrent streams; how masked the signal is.


Reflex/Protection State


Paths: brainstem_reflex.stapedius_state, protective.startle_audio


Purpose: damped hearing or startle coupling (context for reliability).


Vestibular & Head/Neck Orientation


Paths: sensory_vestibular.head_pose, motor_pool.neck_orientation


Purpose: align localization with current head direction (“auditory gaze”).


B) From Biomimetic Registry (templates; slower)
Learned Templates & Schemas


Paths:


biomimetic_registry.auditory_templates.phoneme.*


biomimetic_registry.auditory_templates.keyword.* (wake-words, commands)


biomimetic_registry.auditory_templates.speaker_timbre.*


biomimetic_registry.auditory_templates.env_sounds.* (sirens, alarms)


Purpose: non-semantic matches to known patterns (IDs/scores only).



2) Preprocessing & Normalization
Time windows:


Phasic (10–30 ms): onsets, ITD/ILD updates, envelope spikes.


Tonic (50–200 ms): stream count, prosody/arousal, SNR stability.


Background (0.5–2 s): template confidence accumulation, timbre stability.


Signal hygiene:


All analog values scaled/clipped to [0,1]; vectors normalized.


Startle/stapedius → mark reliability down-weights (not zeroing) for brief windows.


Cache each input with last_value/last_update; if stale ≥ interval → re-query.



3) State Variables (Published; read-only via Signal Registry)
auditory_stub.S_salience (0–1)


 From onset_rate × envelope spikes × novelty vs spectrogram baseline.



auditory_stub.S_localization (object)


 { azimuth: 0–1, elevation: 0–1, confidence: 0–1 } derived from ITD/ILD/HRIR consistency + head_pose alignment.



auditory_stub.S_stream_count (0–1 normalized count)


 Streams scaled, e.g. 0 = 1 stream, 1.0 ≈ ≥4 streams (cap to policy).



auditory_stub.S_speech_envelope (0–1)


 Energy + voicing + periodicity proxy, smoothed over 50–150 ms.



auditory_stub.S_prosody_arousal (0–1)


 From envelope variance, pitch dynamics, onset density (not emotional semantics; just arousal proxy).



auditory_stub.S_keyword_confidence (0–1)


 Max score across selected keyword templates (non-semantic, template-score only).



auditory_stub.S_template_match (string/enum)


 Best-scoring template tag among {phoneme-class, speaker-timbre, env-sound}; include none when below threshold.



auditory_stub.S_snr_effective (0–1)


 Combines SNR + masking_index with stapedius/startle penalties to reflect usable clarity.




4) Outputs (Published Handoff Channels)
To Thalamus (relay)
thalamus_handoff.auditory_salience ← S_salience


thalamus_handoff.auditory_localization ← S_localization (az, el, conf)


thalamus_handoff.auditory_stream_count ← S_stream_count


thalamus_handoff.speech_envelope ← S_speech_envelope


thalamus_handoff.template_match ← S_template_match


thalamus_handoff.snr_effective ← S_snr_effective


To PFC (executive hints; substrate only)
pfc_hint.auditory_attention ← f(S_salience, S_snr_effective)


pfc_hint.motion_orient ← S_localization (with head_pose alignment)


pfc_hint.scene_complexity ← S_stream_count


pfc_hint.speech_presence ← S_speech_envelope


pfc_hint.keyword_candidate ← S_keyword_confidence


pfc_hint.arousal_from_audio ← S_prosody_arousal


No semantics or commands here; just structured hints/scores.

5) Processors (lightweight; tick-driven)
SalienceExtractor → onset/novelty vs spectrogram baseline → S_salience


LocalizationEstimator → ITD/ILD/HRIR + head_pose → S_localization


SceneSeparator (coarse) → envelope clustering/energy bands → S_stream_count


SpeechEnvelopeEstimator → broadband envelope + voicing → S_speech_envelope


ProsodyArousalEstimator → pitch variability + envelope variance → S_prosody_arousal


TemplateMatcher (Biomimetic) → phoneme/keyword/timbre/env patterns → S_keyword_confidence + S_template_match


NoiseSNRIntegrator → SNR + masking + stapedius/startle → S_snr_effective


SignalNormalizer → clipping, smoothing, cache enforcement



6) Refresh Policy (ms)
Signal Registry


cochlear/envelope/spectrogram: 10–20 ms


ITD/ILD/HRIR, head_pose: 10–20 ms


stream_count, snr/masking: 20–50 ms


stapedius/startle: 10–20 ms (short refractory)


Biomimetic Registry


keyword/phoneme/timbre/env templates: 100–200 ms (with accumulation windows)



7) Registry Interaction Logic
Pull-only model: on each tick, check each input’s cache age vs its interval; re-query if expired, else reuse cached.


Dual registry:


Signal Registry for live acoustics, reflexes, vestibular/head orientation.


Biomimetic Registry for pattern-template scores.


Back-pressure safety: cap per-tick re-queries; stagger slow (biomimetic) pulls to avoid bursts.



8) Telemetry & Audit
On every tick: record which inputs refreshed vs cached, and the computed state vector.


Snapshot every 100–200 ms of all published handoff variables.


Immediate audit on startle/stapedius changes or keyword_confidence spikes crossing threshold.



9) Integration Boundaries
Implements: extraction, normalization, template scoring, and handoff packaging only.


Stops at: thalamus_handoff.* and pfc_hint.* publication.


Excludes: speech recognition/semantics, command parsing, executive gating, long-term memory updates.



Directory / File Plan (Auditory Ascending Stub)
E:\Vex\auditory_cortex\ascending_stub\
│
├── __init__.py
├── auditory_ascending_stub.py        # Core: pulls registries, computes states, publishes handoff
├── auditory_stub_signals.json        # Published state variables (salience, localization, etc.)
├── auditory_handoff.json             # Schema for thalamus_handoff.* and pfc_hint.* outputs
│
├── processors\
│   ├── __init__.py
│   ├── salience_extractor.py         # Onset/novelty vs spectrogram baseline
│   ├── localization_estimator.py     # ITD/ILD/HRIR + head_pose → az/el/conf
│   ├── scene_separator.py            # Coarse stream count from energy clustering
│   ├── speech_envelope.py            # Envelope + voicing → speech presence
│   ├── prosody_arousal.py            # Arousal proxy from pitch/envelope dynamics
│   ├── template_matcher.py           # Queries Biomimetic templates (phoneme/keyword/timbre/env)
│   ├── noise_snr_integrator.py       # SNR/masking with stapedius/startle penalties
│   └── signal_normalizer.py          # Clip/smooth/enforce refresh policy
│
└── cache\
    ├── __init__.py
    ├── signal_cache.py               # For Signal Registry (cochlear, ITD/ILD, etc.)
    ├── biomimetic_cache.py           # For template queries (scores/IDs)
    └── refresh_policy.json           # Per-input intervals (10–200 ms)


Example JSON Definitions
auditory_stub_signals.json
{
  "metadata": {
    "subsystem": "auditory_cortex",
    "category": "ascending_stub_state",
    "description": "Core auditory state variables prepared for ascending handoff"
  },
  "signals": {
    "auditory_stub.S_salience":           { "type": "analog",  "range": [0,1], "refresh_interval_ms": 10 },
    "auditory_stub.S_localization":       { "type": "object",  "schema": {"azimuth":"0-1","elevation":"0-1","confidence":"0-1"}, "refresh_interval_ms": 20 },
    "auditory_stub.S_stream_count":       { "type": "analog",  "range": [0,1], "refresh_interval_ms": 50 },
    "auditory_stub.S_speech_envelope":    { "type": "analog",  "range": [0,1], "refresh_interval_ms": 20 },
    "auditory_stub.S_prosody_arousal":    { "type": "analog",  "range": [0,1], "refresh_interval_ms": 50 },
    "auditory_stub.S_keyword_confidence": { "type": "analog",  "range": [0,1], "refresh_interval_ms": 100 },
    "auditory_stub.S_template_match":     { "type": "string",  "examples": ["phoneme-class","keyword","speaker-timbre","env-sound","none"], "refresh_interval_ms": 100 },
    "auditory_stub.S_snr_effective":      { "type": "analog",  "range": [0,1], "refresh_interval_ms": 50 }
  }
}

auditory_handoff.json
{
  "metadata": {
    "subsystem": "auditory_cortex",
    "category": "ascending_handoff",
    "description": "Auditory → thalamus/PFC ascending pathway signals"
  },
  "handoff": {
    "thalamus_handoff.auditory_salience":     { "driven_by": "auditory_stub.S_salience" },
    "thalamus_handoff.auditory_localization": { "driven_by": "auditory_stub.S_localization" },
    "thalamus_handoff.auditory_stream_count": { "driven_by": "auditory_stub.S_stream_count" },
    "thalamus_handoff.speech_envelope":       { "driven_by": "auditory_stub.S_speech_envelope" },
    "thalamus_handoff.template_match":        { "driven_by": "auditory_stub.S_template_match" },
    "thalamus_handoff.snr_effective":         { "driven_by": "auditory_stub.S_snr_effective" },

    "pfc_hint.auditory_attention": { "composed_from": ["auditory_stub.S_salience","auditory_stub.S_snr_effective"] },
    "pfc_hint.motion_orient":      { "composed_from": ["auditory_stub.S_localization"] },
    "pfc_hint.scene_complexity":   { "composed_from": ["auditory_stub.S_stream_count"] },
    "pfc_hint.speech_presence":    { "composed_from": ["auditory_stub.S_speech_envelope"] },
    "pfc_hint.keyword_candidate":  { "composed_from": ["auditory_stub.S_keyword_confidence"] },
    "pfc_hint.arousal_from_audio": { "composed_from": ["auditory_stub.S_prosody_arousal"] }
  }
}

refresh_policy.json
{
  "signal_registry": {
    "envelope_spectrogram": 20,
    "onset_offset": 10,
    "itd_ild_hrir": 20,
    "head_pose": 20,
    "snr_masking": 50,
    "stream_count": 50,
    "stapedius_startle": 20
  },
  "biomimetic_registry": {
    "keyword_templates": 100,
    "phoneme_templates": 100,
    "timbre_templates": 150,
    "env_sound_templates": 150
  }
}


Stub class (overview; no code)
auditory_ascending_stub.py → AuditoryAscendingStub
pull_signal_inputs() — query Signal Registry (cochlear, ITD/ILD/HRIR, SNR/streams, startle/stapedius, head_pose)


pull_biomimetic_inputs() — query Biomimetic templates (phoneme/keyword/timbre/env)


compute_states() — run processors to produce S_* variables


publish_handoff() — write thalamus_handoff.* and pfc_hint.* signals to registry


telemetry_tick() — audit refresh vs cache, publish snapshots











2. Peripheral & Autonomic Junctions (generate as detailed as the previous plans, each within their own respective directories. Body parts in their respective Vex\body\ directories or Vex\body\systems)
Somatic Stub
Role: voluntary descending input interface → spinal cord motor neurons.


Signals:


Voluntary contraction intents.


Exports: direct routing into ventral horn pools.


Autonomic Stub
Role: general ANS input/output manager.


Signals:


Heart, lung, digestive, urogenital regulation tags.


Exports: relay into sympathetic/parasympathetic chains.


Sympathetic Chain
Signals: fight/flight reflexes.


HR ↑, bronchodilation, pupil dilation, blood vessel constriction.


Exports: rig modifiers: rapid breathing, pupil size, facial tension.


Parasympathetic Ganglia
Signals: rest/digest reflexes.


HR ↓, digestive motility ↑, pupil constriction.


Exports: rig modifiers: calmer posture, relaxed expression.


Enteric Stub
Signals: digestive peristalsis, gut reflexes.


Exports: abdominal contraction/relaxation cycles (stubbed for now).


Brainstem Autonomic Coordinator
Role: integrator of cranial nerve autonomic functions.


Signals:


Baroreceptor reflex arcs.


Chemoreceptor breathing drive.


Exports: continuous HR/breath metadata to torso rig modules.



3. Motor Endplate & Sensory End-Organs (same detail as before. These connect to muscles, nerves, skin, bone, etc, becoming the interconnection between the spine, body part/s and rig metadata export)
Motor Endplate
Role: translates ventral horn outputs into muscle contractions.


Signals:


Neuromuscular junction firing frequency/intensity.


Exports: joint rotation/bone curve packets, muscle bulge blendshapes.


Sensory End-Organs
Skin Receptors


Touch (Meissner), pressure (Pacinian), vibration, temperature.


Routes → dorsal horn somatosensory inputs.


Exports: tactile animation cues (recoil, flinch).


Proprioceptors


Muscle spindle (stretch), Golgi tendon (tension).


Routes → spinal reflex arcs, cerebellum.


Exports: corrective limb adjustments, gait stabilization.


Nociceptors


Pain signals (mechanical, thermal, chemical).


Routes → dorsal horn → spinal reflex → limbic system.


Exports: protective withdrawal reflexes, facial grimace.



⚡ Integration Strategy
Spinal Cord as Hub → dorsal/ventral horns are the switchboard.


Ascending Pathways → all stubs forward copies to thalamus + brain modules.


Descending Pathways → PFC/limbic/autonomic stubs can modulate spinal activity.


Peripheral Loop Closure → sensory organs inject afferents; motor endplates execute efferents.


Rig Export → every efferent stub packages muscle contraction into metadata for Unreal/Unity.










 Vex Body Directory Master Plan
1. Overall Philosophy
The body is organized like the nervous system → musculoskeletal + visceral effectors.


Registry holds every signal, organized by metadata (subsystem, reflex, afferent/efferent, etc.).


Indexer routes signals into body directories (back, limbs, torso, neck, face, hormones).


Each body module is just a “router + exporter” → it doesn’t compute new physiology, only packages reflex/motor signals for the rig.


This ensures:


Low compute overhead.


Anatomical clarity.


Expandability without rewrites.



2. Top-Level Body Directory Layout
body/
├── back/
├── torso/
│   ├── respiratory/
│   ├── cardiac/
│   ├── core/
│   ├── digestive/       # stub initially
│   └── urogenital/      # stub initially
├── limbs/
│   ├── left_arm/
│   ├── right_arm/
│   ├── left_leg/
│   └── right_leg/
├── neck/
├── face/
└── hormones/


3. Subsystems + Reflexes (with export targets)
🟢 Back (spine & posture)
Signals:


Spinal tone (erector spinae)


Postural reflex arcs (righting, equilibrium)


Protective flexion/extension arcs


Exports:


Spine tilt blendshapes


Torso flexion/extension curves


Rig anchor for whole-body stabilization



🫁 Torso
(a) Respiratory
Signals:


Normal breathing rhythm (Hering–Breuer, chemoreceptors)


Reflexes: cough, sneeze, hiccough, diaphragm spasm


Exports:


Rib expansion blendshape


Diaphragm contraction curve


Chest oscillation (for breathing loop)


(b) Cardiac
Signals:


Baroreceptor reflex (blood pressure regulation)


Bainbridge reflex (atrial filling)


Diving reflex (HR suppression)


Exports:


Heartbeat frequency (global animation tick)


Chest pulse offset (subtle jiggle/beat curve)


Physiological state tags (fast HR, slow HR)


(c) Core
Signals:


Abdominal reflexes (cutaneous, superficial)


Core tension (vomit, defecation, retching)


Exports:


Abdominal compression blendshape


“Tensed core” rig signal


(d) Digestive (stub first)
Signals: enterogastric reflex, peristalsis, vomiting


Exports: placeholder metadata only


(e) Urogenital (stub first)
Signals: micturition reflex, sexual arousal, uterine contractions


Exports: placeholder metadata only



🦵 Limbs
Upper Limbs (left & right arms)
Signals:


Stretch reflex (biceps/triceps)


Golgi tendon inhibition


Flexor withdrawal


Crossed extensor (when one arm pulls back, other stabilizes)


Exports:


Shoulder, elbow, wrist joint rotations


Finger flexion/extension (later for dexterity)


Lower Limbs (left & right legs)
Signals:


Patellar reflex (knee-jerk)


Plantar reflex (Babinski, toe flexion/extension)


Crossed extensor (stance vs withdrawal)


Locomotor CPGs (gait stepping)


Exports:


Hip, knee, ankle joint rotations


Gait cycles (walk/run stride loops)


Toe curl blendshapes



🧍 Neck
Signals:


Cervical righting reflex (head stabilization vs gravity)


Swallowing reflex coordination


Breathing–swallow coupling


Exports:


Neck tilt/rotation bones


Swallow animation (larynx elevation)



🙂 Face
Signals:


Cranial reflexes: blink, corneal, pupillary light, gag, jaw jerk, tongue protrusion


Grimace (pain response)


Exports:


Eye blink blendshape


Pupil contraction dilation curve


Mouth/jaw blendshapes


Tongue extension


Expression tags (grimace, smile)



🧪 Hormones (global modulation)
Signals:


Cortisol, adrenaline, oxytocin, insulin/glucagon, vasopressin


Exports:


Global modifiers: breathing speed, HR baseline, muscle tone, emotional expression


Tags for state (stressed, calm, affectionate, hungry, fatigued)



4. Integration Flow (per tick)
Registry loads all signals from JSON.


Indexer routes signals by metadata → correct body module.


Body module translates signal → rig metadata:


Digital → boolean toggle (blink, swallow).


Analog → float curve (breathing depth, HR speed).


Reflex arc → prepackaged blendshape/joint sequence.


Export bridge sends rig metadata to Unreal/Unity in frame time.



5. Priority Staging
Stage 1 (minimum viable body)
Back (posture)


Limbs (basic stretch/withdrawal + gait)


Torso (respiratory + cardiac)


Face (blink, jaw, pupil)


Neck (head stabilization)


Hormones (adrenaline/cortisol only)


Stage 2 (expansion)
More cranial reflexes (tongue, gag, grimace)


Abdominal core reflexes


Pain withdrawal + protective set


Stage 3 (full embodiment)
Digestive + urogenital systems fully filled in


Hormone cascades expanded to all major hormones


Facial microexpressions



6. Design Benefits
Clarity: Every system has its own file and module.


Expandability: Add new reflexes by JSON only → indexer does the rest.


Low compute: No physics simulation, just reflex → rig mapping.


Biomimetic: Mirrors real human neuroanatomy flow: spinal cord → body → brainstem integration.



⚡ Net result: Vex’s body will animate as smoothly as a Vocaloid or VTuber pipeline, but with realistic biomimetic reflexes and modular growth into full physiology.


































Heck yes. Below is a drop-in biomimetic vocal-tract shape module that fits your “router + exporter” body architecture. It does no physiology computation (that’s your Mouth/Articulatory engine’s job); it just ingests articulatory signals from your registry and exports rig-ready curves (bones/blendshapes) every tick.

Where it plugs in
body/
├── face/
│   ├── vocal_tract/          ← NEW (this module)
│   │   ├── __init__.py
│   │   ├── config.yaml
│   │   ├── mapper.py         # articulator → rig mapping
│   │   ├── smoothing.py      # light temporal filters, clamps
│   │   ├── exporter.py       # pack to rig schema
│   │   └── schema.py         # signal validation
│   └── ...
├── neck/                     # (already present; used for swallow/larynx lift)
└── torso/
    └── respiratory/          # (already present; P_sub + breathing)

The vocal_tract module consumes articulatory states emitted by your Mouth module (jaw, lips, tongue, velum, larynx, nasal port, etc.) and publishes a rig packet for Unreal/Unity/VTubing.

1) Expected input signals (from your Registry)
Per-tick (e.g., 5 ms) numeric values; units noted for clarity:
Jaw / Lips
jaw.angle_deg (−8…+28)


jaw.protrusion_mm (0…6)


lip.protrusion_mm (−2…10)


lip.rounding_0_1 (0…1)


lip.aperture_mm (0…18) (inter-labial gap)


Tongue (mid-sagittal controls → area function is already computed upstream; we just animate)
tongue.tip_x_mm (−20…+20)


tongue.tip_y_mm (−10…+25)


tongue.blade_y_mm (−5…+30)


tongue.dorsum_y_mm (0…35)


tongue.root_adv_0_1 (0…1) (root advancement / constriction)


Velum / Nasal
velum.opening_cm2 (0.0…1.8)


nasal.port_mix_0_1 (0…1)


Larynx / Glottis (for visible throat & subtle neck)
larynx.height_mm (−6…+6)


glottis.oq_0_1 (0.45…0.85) (open quotient proxy → subtle neck/lower-face tension)


glottis.aspiration_0_1 (0…0.4)


Events (boolean / short pulses)
event.swallow


event.plosive_burst


event.giggle / event.laugh / event.filler


You likely have all of these in your Mouth engine telemetry already (you mentioned CQ, SPL, OQ, tract geometry, etc.).

2) Output (rig packet)
A minimal, engine-agnostic dict your export bridge already understands:
{
  "face": {
    "bones": {
      "jaw_rx_deg": 12.3,
      "jaw_tz_mm": 1.8,
      "tongue_tip_tx_mm": -5.4,
      "tongue_tip_ty_mm": 14.1,
      "tongue_dorsum_ty_mm": 22.0,
      "larynx_ty_mm": 2.3,
      "upper_lip_tz_mm": 2.1,
      "lower_lip_tz_mm": 2.4
    },
    "blendshapes": {
      "Lip_Rounding": 0.62,
      "Lip_Spread": 0.12,
      "Lip_Open": 0.48,
      "Nasal_Blend": 0.35,
      "Cheek_Tension": 0.18,
      "Throat_Tension": 0.22,
      "Smile": 0.08
    }
  },
  "meta": {
    "ts_ms": 12345,
    "phoneme": "a",
    "note": null
  }
}

You can rename bones/blendshapes to your rig; the mapper handles it.

3) Mapping (articulator → rig)
Default, human-ish ranges (safe and expressive; tweak in config.yaml):
Articulator
Source
Rig target
Mapping (default)
Jaw rotation
jaw.angle_deg
jaw_rx_deg (bone)
clamp(−8..28) → linear
Jaw forward slide
jaw.protrusion_mm
jaw_tz_mm (bone)
0..6 mm → linear
Upper lip protrusion
lip.protrusion_mm
upper_lip_tz_mm
split protrusion 55% upper / 45% lower
Lower lip protrusion
lip.protrusion_mm
lower_lip_tz_mm
see above
Lip opening
lip.aperture_mm
Lip_Open (blendshape 0..1)
mm → normalize by 18 mm
Lip rounding
lip.rounding_0_1
Lip_Rounding (0..1)
identity → optional gamma curve
Lip spread (auto)
lip.rounding_0_1
Lip_Spread (0..1)
Lip_Spread = max(0, 1 - rounding) * s_spread
Tongue tip (x,y)
tongue.tip_*
tongue_tip_t{xy} (bones)
mm → mm; clamp to palate curve
Tongue dorsum height
tongue.dorsum_y_mm
tongue_dorsum_ty_mm (bone)
mm → mm
Tongue blade height
tongue.blade_y_mm
tongue_blade_ty_mm (bone)
mm → mm
Tongue root advance
tongue.root_adv_0_1
Tongue_Root_Advance (blendshape)
0..1
Velum opening
velum.opening_cm2
Nasal_Blend (0..1)
map 0..1.8 cm² → 0..1 with soft knee
Larynx vertical
larynx.height_mm
larynx_ty_mm (bone)
mm → mm
Throat tension
glottis.oq_0_1
Throat_Tension (0..1)
invert & scale: tension = s · (0.8 − OQ)+
Cheek tension (sibilants)
event.plosive_burst
Cheek_Tension
short ADSR on /s/ /ʃ/ bursts
Smile (giggle/laugh cue)
event.giggle/laugh
Smile
transient + hold envelope
Swallow
event.swallow
(neck+face micro-sequence)
larynx up → velum close → tongue root back → lips neutral

Note: This module doesn’t plan gestures; it just renders what the Mouth engine chose. We only add light smoothing and safety clamps so the rig never pops or clips.

4) Smoothing & safety (tiny, local)
Critically damped 1-pole / 2-pole per channel (you already use task dynamics elsewhere; here we keep it feather-light):


fast channels (lip aperture, rounding): τ_fast ≈ 8–15 ms


medium (tongue tip/blade): τ ≈ 15–25 ms


slow (dorsum, larynx): τ ≈ 25–40 ms


Palate & teeth avoidance: clamp tongue y by a stored palate curve; project along the normal if penetrated.


Collision-aware lip aperture: enforce Lip_Open ≥ f(protrusion) to avoid inside-out lips when rounding is high.


Event envelopes: micro ADSR for plosive_burst, giggle, laugh, swallow (5–80 ms shapes).



5) Minimal config (face/vocal_tract/config.yaml)
rig:
  bones:
    jaw_rx_deg: "JAW_RX"
    jaw_tz_mm: "JAW_TZ"
    tongue_tip_tx_mm: "TNG_TIP_TX"
    tongue_tip_ty_mm: "TNG_TIP_TY"
    tongue_blade_ty_mm: "TNG_BLD_TY"
    tongue_dorsum_ty_mm: "TNG_DRS_TY"
    larynx_ty_mm: "LARYNX_TY"
    upper_lip_tz_mm: "ULIP_TZ"
    lower_lip_tz_mm: "LLIP_TZ"
  blendshapes:
    Lip_Open: "BS_LipOpen"
    Lip_Rounding: "BS_LipRound"
    Lip_Spread: "BS_LipSpread"
    Nasal_Blend: "BS_Nasal"
    Cheek_Tension: "BS_CheekTen"
    Throat_Tension: "BS_ThroatTen"
    Smile: "BS_Smile"

ranges:
  jaw.angle_deg: [-8, 28]
  lip.aperture_mm: [0, 18]
  lip.protrusion_mm: [-2, 10]
  velum.opening_cm2: [0.0, 1.8]
  larynx.height_mm: [-6, 6]
  tongue.tip_x_mm: [-20, 20]
  tongue.tip_y_mm: [-10, 25]
  tongue.blade_y_mm: [-5, 30]
  tongue.dorsum_y_mm: [0, 35]
  tongue.root_adv_0_1: [0, 1]
  lip.rounding_0_1: [0, 1]

smoothing_ms:
  fast: 12
  medium: 20
  slow: 32

palate:
  # mid-sagittal palate curve samples (x_mm → y_mm) for collision clamp
  samples: [[-20, 15], [-10, 18], [0, 20], [10, 22], [20, 24]]

auto:
  lip_spread_from_rounding: true
  spread_scale: 0.6
  throat_from_oq:
    baseline_oq: 0.8
    scale: 0.7
events:
  plosive_adsr_ms: [5, 20, 30, 20]   # A,D,S,R
  giggle_smile_ms: [15, 40, 120, 60]
  swallow_seq_ms:
    larynx_up: 120
    velum_close: 100
    tongue_root_back: 90
    relax: 180


6) Tiny Python skeleton (router → mapper → exporter)
# face/vocal_tract/__init__.py
from .mapper import VocalTractMapper

class VocalTractModule:
    def __init__(self, cfg, exporter, logger):
        self.mapper = VocalTractMapper(cfg, logger)
        self.exporter = exporter
        self.logger = logger

    def tick(self, signals: dict, ts_ms: int):
        # 1) validate & clamp
        art = self.mapper.validate(signals)
        # 2) map articulators → rig controls (with smoothing/clamps)
        rig_packet = self.mapper.map_to_rig(art, ts_ms)
        # 3) export
        self.exporter.send(rig_packet)
        return rig_packet  # for debugging/inspection

# face/vocal_tract/mapper.py
import math
from .smoothing import OnePole

class VocalTractMapper:
    def __init__(self, cfg, logger):
        self.cfg = cfg; self.logger = logger
        # one-pole smoothers per channel
        self.sm = {k: OnePole(self._tau(k)) for k in self._channels()}
        self.prev_ts = None

    def validate(self, s):
        # clamp to ranges
        r = {}
        for k, (lo, hi) in self.cfg["ranges"].items():
            v = float(s.get(k, (lo+hi)/2))
            r[k] = max(lo, min(hi, v))
        # fill booleans
        for ev in ("event.swallow","event.plosive_burst","event.giggle","event.laugh"):
            r[ev] = bool(s.get(ev, False))
        return r

    def map_to_rig(self, a, ts_ms):
        dt = 0 if self.prev_ts is None else max(1e-3, (ts_ms - self.prev_ts)/1000.0)
        self.prev_ts = ts_ms

        # lips
        lip_open = a["lip.aperture_mm"]/self.cfg["ranges"]["lip.aperture_mm"][1]
        lip_round = a["lip.rounding_0_1"]
        if self.cfg["auto"]["lip_spread_from_rounding"]:
            lip_spread = max(0.0, 1.0 - lip_round) * self.cfg["auto"]["spread_scale"]
        else:
            lip_spread = 0.0

        # smooth core channels
        def s(name, val, band="medium"):
            return self.sm[name].step(val, dt, band)

        rig = {
          "face": {
            "bones": {
              "jaw_rx_deg": s("jaw_rx_deg", a["jaw.angle_deg"], "medium"),
              "jaw_tz_mm": s("jaw_tz_mm", a["jaw.protrusion_mm"], "medium"),
              "tongue_tip_tx_mm": s("tongue_tip_tx_mm", a["tongue.tip_x_mm"], "fast"),
              "tongue_tip_ty_mm": s("tongue_tip_ty_mm", self._palate_clamp(a["tongue.tip_y_mm"]), "fast"),
              "tongue_blade_ty_mm": s("tongue_blade_ty_mm", self._palate_clamp(a["tongue.blade_y_mm"]), "medium"),
              "tongue_dorsum_ty_mm": s("tongue_dorsum_ty_mm", self._palate_clamp(a["tongue.dorsum_y_mm"]), "slow"),
              "larynx_ty_mm": s("larynx_ty_mm", a["larynx.height_mm"], "slow"),
              "upper_lip_tz_mm": s("upper_lip_tz_mm", 0.55*a["lip.protrusion_mm"], "fast"),
              "lower_lip_tz_mm": s("lower_lip_tz_mm", 0.45*a["lip.protrusion_mm"], "fast"),
            },
            "blendshapes": {
              "Lip_Open": s("Lip_Open", lip_open, "fast"),
              "Lip_Rounding": s("Lip_Rounding", lip_round, "fast"),
              "Lip_Spread": s("Lip_Spread", lip_spread, "fast"),
              "Nasal_Blend": s("Nasal_Blend", self._nasal(a["velum.opening_cm2"]), "slow"),
              "Throat_Tension": s("Throat_Tension", self._throat(a["glottis.oq_0_1"]), "medium"),
              "Cheek_Tension": self._adsr("plosive", a["event.plosive_burst"]),
              "Smile": self._adsr("giggle", a["event.giggle"] or a["event.laugh"]),
            }
          },
          "meta": { "ts_ms": ts_ms, "phoneme": None, "note": None }
        }

        # swallow micro-sequence: set flags to neck/face queues (not expanded here)
        if a["event.swallow"]:
            rig["meta"]["swallow"] = True

        return rig

    # helpers
    def _nasal(self, vp_cm2):
        lo, hi = self.cfg["ranges"]["velum.opening_cm2"]
        x = max(lo, min(hi, vp_cm2))
        knee = 0.15
        return min(1.0, x/(hi*knee)) if x < hi*knee else 1.0

    def _throat(self, oq):
        base = self.cfg["auto"]["throat_from_oq"]["baseline_oq"]
        scale = self.cfg["auto"]["throat_from_oq"]["scale"]
        return max(0.0, min(1.0, scale * max(0.0, base - oq)))

    def _palate_clamp(self, y_mm):
        # simple piecewise ceiling using palate samples
        return min(y_mm, self._interp_palate_y(self.cfg["palate"]["samples"], current_x=0.0))

    def _interp_palate_y(self, samples, current_x):
        # nearest for brevity; replace with linear interp
        return max(p[1] for p in samples)  # crude ceiling

    def _adsr(self, kind, gate):
        # extremely light one-shot; replace with per-channel envelope if desired
        return 0.35 if gate else 0.0

    def _channels(self):
        return ["jaw_rx_deg","jaw_tz_mm","tongue_tip_tx_mm","tongue_tip_ty_mm",
                "tongue_blade_ty_mm","tongue_dorsum_ty_mm","larynx_ty_mm",
                "upper_lip_tz_mm","lower_lip_tz_mm","Lip_Open","Lip_Rounding",
                "Lip_Spread","Nasal_Blend","Throat_Tension"]

    def _tau(self, name):
        if name in ("Lip_Open","Lip_Rounding","Lip_Spread","tongue_tip_tx_mm","tongue_tip_ty_mm","upper_lip_tz_mm","lower_lip_tz_mm"):
            return self.cfg["smoothing_ms"]["fast"]/1000.0
        if name in ("jaw_rx_deg","jaw_tz_mm","tongue_blade_ty_mm","Throat_Tension"):
            return self.cfg["smoothing_ms"]["medium"]/1000.0
        return self.cfg["smoothing_ms"]["slow"]/1000.0

(The OnePole class is a 3-liner: y += (dt/τ) * (x - y) with clamp on τ.)

7) Swallow & breath coordination (hooks)
On event.swallow, emit a micro-timeline to neck/ and face/:


larynx_ty_mm +4 mm over 120 ms


Nasal_Blend → 0 (velum close) over 100 ms


tongue root back (drive Tongue_Root_Advance → 0.2) over 90 ms


relax over 180 ms


Gate audio engine’s aspiration during step 2; your Mouth module already knows how.


Breathing synchrony: read torso/respiratory chest phase; add tiny lip/jaw micro-motion (±0.1–0.3 mm) on inhalations for realism.



8) Quick viseme overrides (optional)
If a partner rig expects classic visemes, expose a side-channel:
visemes:
  AI  ← (jaw open + lip spread)
  E   ← (spread)
  U   ← (rounding + protrusion)
  O   ← (rounding + jaw)
  FV  ← (lower lip to incisors; from mouth planner’s /f v/)
  L   ← (tongue tip high; from tongue_tip_ty)
  WQ  ← (rounding + small jaw)
  MBP ← (lip_open ≈ 0)

This keeps compatibility without abandoning your richer articulatory drive.

9) Test checklist (bite-sized)
Sustained vowels /i e a o u ɑ ɜ ə/ → verify smooth lip/jaw/tongue motion, no palate penetration.


CV/VC coarticulation /ka/ /ku/ /ti/ /tu/ → dorsum vs lip rounding behave distinctly.


Nasalization /m n ŋ/ contexts → Nasal_Blend rises early, decays late.


Plosives /p b t d k g/ → cheek tension pulse; lips/jaw closures look clean.


Swallow event → correct micro-sequence; no rig pops.


Giggle/laugh → subtle Smile + cheek tension + (optional) head micro-bob via neck/.



TL;DR
This module is pure glue: Registry signals in → rig curves out.


It respects your biomimetic ethos (articulators, not viseme guesses).


It’s safe (clamps, smoothing, collision avoids) and expandable (JSON-driven).

