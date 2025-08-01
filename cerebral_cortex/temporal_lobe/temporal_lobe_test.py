import importlib
import importlib.util


class MockHippocampus:
    def __init__(self):
        self.stored = []

    def store_record(self, record, category=None):
        self.stored.append(record)


def run_temporal_lobe_tests():
    if importlib.util.find_spec("spacy") is None:
        print("[TemporalLobeTest] SpaCy not installed; skipping test.")
        return
    from cerebral_cortex.temporal_lobe import TemporalLobe
    from symbolic_signal import SymbolicSignal
    hippocampus = MockHippocampus()
    tl = TemporalLobe(hippocampus=hippocampus)
    signal = SymbolicSignal(data={"text": "Hello world"}, modality="text", source="test")
    result = tl.process(signal)

    assert result["tokens"], "Tokens should be produced"
    assert result["analysis"], "Analysis should be produced"
    assert tl.get_recent_context(), "Context tracker should contain the entry"
    assert hippocampus.stored, "Hippocampus should store the processed fact"
    print("[TemporalLobeTest] All assertions passed.")


if __name__ == "__main__":
    run_temporal_lobe_tests()
