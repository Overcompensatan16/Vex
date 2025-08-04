from primary_auditory_cortex import PrimaryAuditoryCortex
from thalamus.thalamus_module import ThalamusModule
from cerebral_cortex.temporal_lobe import TemporalLobe
from ear import EarModule
from hippocampus.hippocampus_module import HippocampusModule
from memory.memory_store_factory import MemoryStoreFactory


def process_transcript(source=None):
    """Capture audio/text and route through the auditory pipeline."""
    ear = EarModule()
    cortex = PrimaryAuditoryCortex()
    thalamus = ThalamusModule()
    memory_factory = MemoryStoreFactory()
    hippocampus = HippocampusModule(memory_factory=memory_factory)
    temporal = TemporalLobe(hippocampus=hippocampus)

    capture_event = ear.capture(source)
    transcript = capture_event.get("captured")

    signal = cortex.process(transcript)
    scored = thalamus.score_signal(signal)
    result = temporal.process(scored)
    return result


if __name__ == "__main__":
    output = process_transcript("hello from the ear")
    print(output)
