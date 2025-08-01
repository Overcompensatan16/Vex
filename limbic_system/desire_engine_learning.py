"""Wake-Sleep learner for the DesireEngine DBN."""
from __future__ import annotations

from typing import List

from limbic_system.desire_engine import _DBN

_LEARNING_RATE = 0.05
_DECAY = 0.99


def update_weights_positive(self: _DBN, input_vec: List[float], beliefs: List[float]) -> None:
    """Strengthen weights after a reinforced outcome."""
    activations = [input_vec]
    for layer in self.layers:
        activations.append(layer.forward(activations[-1]))
    activations[-1] = beliefs
    vec = activations[0]
    for idx, layer in enumerate(self.layers):
        out = activations[idx + 1]
        for i in range(layer.visible):
            for j in range(layer.hidden):
                layer.weights[i][j] += _LEARNING_RATE * vec[i] * out[j]
        for j in range(layer.hidden):
            layer.h_bias[j] += _LEARNING_RATE * out[j]
        vec = out


def update_weights_negative(self: _DBN, input_vec: List[float], beliefs: List[float]) -> None:
    """Weaken connections for a blocked outcome."""
    activations = [input_vec]
    for layer in self.layers:
        activations.append(layer.forward(activations[-1]))
    activations[-1] = beliefs
    vec = activations[0]
    for idx, layer in enumerate(self.layers):
        out = activations[idx + 1]
        for i in range(layer.visible):
            for j in range(layer.hidden):
                layer.weights[i][j] -= _LEARNING_RATE * vec[i] * out[j]
        for j in range(layer.hidden):
            layer.h_bias[j] -= _LEARNING_RATE * out[j]
        vec = out


def stabilize_weights(self: _DBN, input_vec: List[float], beliefs: List[float]) -> None:
    """Gently decay weights when an outcome is ignored."""
    for layer in self.layers:
        for i in range(layer.visible):
            for j in range(layer.hidden):
                layer.weights[i][j] *= _DECAY
        for j in range(layer.hidden):
            layer.h_bias[j] *= _DECAY


_DBN.update_weights_positive = update_weights_positive  # type: ignore[attr-defined]
_DBN.update_weights_negative = update_weights_negative  # type: ignore[attr-defined]
_DBN.stabilize_weights = stabilize_weights  # type: ignore[attr-defined]


class WakeSleepLearner:
    """Minimal wake-sleep algorithm for DBN weight adjustment."""

    def __init__(self, rbm_model, memory_interface) -> None:
        self.rbm = rbm_model
        self.memory = memory_interface  # expects .append(entry: dict)

    def wake_phase(self, input_vector: List[float]):
        """Return belief activations from the RBM."""
        return self.rbm.forward(input_vector)

    def sleep_phase(self, input_vector: List[float], beliefs: List[float], outcome: str) -> None:
        """Adjust RBM weights based on symbolic outcome."""
        if outcome == "reinforced":
            self.rbm.update_weights_positive(input_vector, beliefs)
        elif outcome == "blocked":
            self.rbm.update_weights_negative(input_vector, beliefs)
        elif outcome == "ignored":
            self.rbm.stabilize_weights(input_vector, beliefs)
        self.memory.append(
            {
                "input_vector": input_vector,
                "belief_activations": beliefs,
                "outcome": outcome}
        )
