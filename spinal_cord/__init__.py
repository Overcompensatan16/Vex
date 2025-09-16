"""Core spinal cord abstractions."""

from __future__ import annotations

from . import scheduler


class Brainstem:
    def __init__(self, thalamus, limbic_system, cerebellum, hippocampus, audit_logger, basal_ganglia):
        self.thalamus = thalamus
        self.limbic_system = limbic_system
        self.cerebellum = cerebellum
        self.hippocampus = hippocampus
        self.audit_logger = audit_logger
        self.basal_ganglia = basal_ganglia

        print("[Brainstem] Initialized with all core components.")

    def process_signal(self, input_signal):
        thalamus_output = self.thalamus.score_signal(input_signal)
        limbic_response = self.limbic_system.evaluate_signal(thalamus_output)
        action = self.basal_ganglia.evaluate_decision(limbic_response)
        self.cerebellum.execute_action(action)
        self.audit_logger.log({
            "input": input_signal,
            "thalamus_output": thalamus_output,
            "limbic_response": limbic_response,
            "action": action
        })


__all__ = ["Brainstem", "scheduler"]
