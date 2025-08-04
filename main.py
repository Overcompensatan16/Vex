import json

from spinal_cord import Brainstem

from thalamus.thalamus_module import ThalamusModule
from limbic_system.limbic_system_module import LimbicSystem
from cerebellum.cerebellum_module import Cerebellum
from hippocampus.hippocampus_module import HippocampusModule
from audit.audit_logger import AuditLogger
from basal_ganglia.basal_ganglia import BasalGanglia


def main():
    # ✅ Load Cerebellum config
    with open("cerebellum/cerebellum_config.json", "r") as f:
        cerebellum_config = json.load(f)

    # ✅ Instantiate brain components
    thalamus = ThalamusModule()
    limbic_system = LimbicSystem(thalamus=thalamus)
    cerebellum = Cerebellum(config=cerebellum_config)
    hippocampus = HippocampusModule()
    audit_logger = AuditLogger("cerebral_cortex/parietal_lobe/parietal_audit_log.jsonl")
    basal_ganglia = BasalGanglia()

    # ✅ Construct SpinalCord with explicit components
    spinal_cord = Brainstem(
        thalamus=thalamus,
        limbic_system=limbic_system,
        cerebellum=cerebellum,
        hippocampus=hippocampus,
        audit_logger=audit_logger,
        basal_ganglia=basal_ganglia,

    )


if __name__ == "__main__":
    main()
