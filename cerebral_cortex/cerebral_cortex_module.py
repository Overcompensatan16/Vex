# hyper_ai_core/cerebral_cortex/cerebral_cortex_module.py

from frontal_lobe.frontal_lobe import FrontalLobe
from cerebral_cortex.parietal_lobe.parietal_lobe import ParietalLobe
from cerebral_cortex.temporal_lobe import TemporalLobe
from .primary_auditory_cortex import PrimaryAuditoryCortex
from ear import EarModule
from mouth import MouthModule
from thalamus.thalamus_module import ThalamusModule
import json
import datetime


def combine_outputs(frontal, parietal, temporal):
    """Merge outputs from individual cortex regions."""
    return {
        "frontal": frontal,
        "parietal": parietal,
        "temporal": temporal,
        "timestamp": datetime.datetime.now().isoformat()
    }


class CerebralCortex:
    def __init__(self, config_path="hyper_ai_core/cerebral_cortex/config.json", hippocampus=None, thalamus=None):
        # Initialize instance attributes
        self.config = {}
        self.frontal = FrontalLobe()
        self.parietal = ParietalLobe()
        self.temporal = TemporalLobe(hippocampus=hippocampus)
        self.auditory = PrimaryAuditoryCortex()
        self.ear = EarModule()
        self.mouth = MouthModule()
        self.audit_log_path = "hyper_ai_core/cerebral_cortex/parietal_audit_log.jsonl"

        self.load_config(config_path)

    def load_config(self, path):
        """Load cortex configuration file into memory."""
        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
            print(f"[CerebralCortex] Config loaded: {path}")
        except Exception as e:
            print(f"[CerebralCortex] Failed to load config: {e}")
            self.config = {}

    def process_input(self, raw_audio):
        """Run the basic auditory->linguistic pipeline."""
        print(f"[CerebralCortex] Processing signal: {raw_audio}")

        captured = self.ear.capture(raw_audio)
        auditory_signal = self.auditory.process(captured.get("captured"))

        scored = self.thalamus.score_signal(auditory_signal)

        temporal_out = self.temporal.process(scored)

        parietal_out = self.parietal.process({"raw_input": temporal_out.get("original", "")})
        frontal_out = self.frontal.process(temporal_out.get("original", ""))

        combined_output = self.combine_outputs(frontal_out, parietal_out, temporal_out)
        self.log_cortex_meta_fact(combined_output)
        return combined_output

    @staticmethod
    def combine_outputs(frontal, parietal, temporal):
        """
        Combine outputs from lobes — placeholder for now.
        In future: apply confidence weights, context relevance, etc.
        """
        return {
            "frontal": frontal,
            "parietal": parietal,
            "temporal": temporal,
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def log_cortex_meta_fact(self, fact_obj):
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(fact_obj) + "\n")
            print(f"[CerebralCortex] Logged meta fact.")
        except Exception as e:
            print(f"[CerebralCortex] Failed to log meta fact: {e}")
