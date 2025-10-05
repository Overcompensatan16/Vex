
"""Right leg routing and rig metadata module."""

from __future__ import annotations

from typing import Mapping, Optional

from .limb_base import (
    BoneSegment,
    Joint,
    LimbModuleBase,
    MicroMovementProfile,
    MuscleGroup,
    RigChannel,
    SensorCluster,
)


class RightLegModule(LimbModuleBase):
    """Aggregate structural metadata and micromotion for the right leg."""

    module_name = "right_leg"
    reflex_subsystem = "limbs_lower"

    def __init__(self, *, audit_factory=None) -> None:
        self._bones = [
            BoneSegment(
                name="pelvis_R",
                rig_target="CTRL_Pelvis",
                length_cm=0.0,
                parent="spine_03",
                degrees_of_freedom=("translate", "tilt", "twist"),
                notes="Shared pelvis anchor for bilateral leg coordination.",
            ),
            BoneSegment(
                name="femur_R",
                rig_target="CTRL_R_Thigh",
                length_cm=43.0,
                parent="pelvis_R",
                degrees_of_freedom=("pitch", "yaw", "roll"),
                notes="Primary lever for stance and locomotion arcs.",
            ),
            BoneSegment(
                name="tibia_R",
                rig_target="CTRL_R_Shin",
                length_cm=41.0,
                parent="femur_R",
                degrees_of_freedom=("flex", "twist"),
                notes="Carries knee flexion metadata and tibial rotation.",
            ),
            BoneSegment(
                name="fibula_R",
                rig_target="CTRL_R_Fibula",
                length_cm=40.5,
                parent="femur_R",
                degrees_of_freedom=("support",),
                notes="Auxiliary channel for lateral stability blendshapes.",
            ),
            BoneSegment(
                name="foot_R",
                rig_target="CTRL_R_Foot",
                length_cm=26.0,
                parent="tibia_R",
                degrees_of_freedom=("dorsi", "plantar", "invert", "evert"),
                notes="Publishes plantar roll metadata for gait transitions.",
            ),
            BoneSegment(
                name="toes_R",
                rig_target="CTRL_R_Toe",
                length_cm=7.0,
                parent="foot_R",
                degrees_of_freedom=("curl", "spread"),
                notes="Provides toe-off metadata for locomotion curves.",
            ),
        ]

        self._joints = [
            Joint(
                name="hip_R",
                bones=("pelvis_R", "femur_R"),
                rig_controls=("CTRL_R_HipPitch", "CTRL_R_HipYaw", "CTRL_R_HipRoll"),
                limits_deg=(-110.0, 120.0),
                default_pose=5.0,
                notes="Handles stride envelopes and crossed extensor reflex weighting.",
            ),
            Joint(
                name="knee_R",
                bones=("femur_R", "tibia_R"),
                rig_controls=("CTRL_R_Knee",),
                limits_deg=(0.0, 150.0),
                default_pose=5.0,
                notes="Publishes patellar stretch and load compensation data.",
            ),
            Joint(
                name="ankle_R",
                bones=("tibia_R", "foot_R"),
                rig_controls=("CTRL_R_AnklePitch", "CTRL_R_AnkleRoll"),
                limits_deg=(-50.0, 35.0),
                default_pose=0.0,
                notes="Routes plantar reflex metadata into roll control.",
            ),
            Joint(
                name="subtalar_R",
                bones=("foot_R", "toes_R"),
                rig_controls=("CTRL_R_BallRoll",),
                limits_deg=(-35.0, 45.0),
                notes="Handles toe-off sequencing with gait central pattern metadata.",
            ),
            Joint(
                name="metatarsal_R",
                bones=("foot_R", "toes_R"),
                rig_controls=("CTRL_R_ToeCurl",),
                limits_deg=(0.0, 80.0),
                notes="Provides toe curl amplitude for balance micro-corrections.",
            ),
        ]

        self._muscles = [
            MuscleGroup(
                name="gluteus_med_R",
                actuators=("CTRL_R_HipPitch", "CTRL_R_HipRoll"),
                primary_function="Hip abduction and pelvic stabilization",
                fiber_type="slow",
                notes="Coupled to vestibulospinal sway metadata.",
            ),
            MuscleGroup(
                name="quadriceps_R",
                actuators=("CTRL_R_Knee",),
                primary_function="Knee extension",
                fiber_type="fast",
                notes="Consumes patellar reflex data for stance recovery.",
            ),
            MuscleGroup(
                name="hamstrings_R",
                actuators=("CTRL_R_HipPitch", "CTRL_R_Knee"),
                primary_function="Hip extension and knee flexion",
                fiber_type="mixed",
                notes="Supports swing phase via gait pattern metadata.",
            ),
            MuscleGroup(
                name="gastrocnemius_R",
                actuators=("CTRL_R_AnklePitch", "CTRL_R_BallRoll"),
                primary_function="Plantarflexion and push-off",
                fiber_type="fast",
                notes="Integrates plantar reflex signals to drive protective responses.",
            ),
            MuscleGroup(
                name="tibialis_ant_R",
                actuators=("CTRL_R_AnklePitch", "CTRL_R_ToeCurl"),
                primary_function="Dorsiflexion and toe lift",
                fiber_type="slow",
                notes="Prevents foot drop with gait central pattern metadata.",
            ),
        ]

        self._sensors = [
            SensorCluster(
                name="plantar_cutaneous_R",
                sensor_type="cutaneous",
                afferents=("sensory_cutaneous.plantar_R", "sensory_cutaneous.heel_R"),
                rig_notes="Drives plantar reflex gating for foot roll blendshapes.",
            ),
            SensorCluster(
                name="muscle_spindle_quads_R",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.quadriceps_spindle_R",),
                rig_notes="Feeds knee stabilization metadata to rig curves.",
            ),
            SensorCluster(
                name="golgi_tendon_ankle_R",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.achilles_gto_R",),
                rig_notes="Provides ankle load shedding cues for balance.",
            ),
        ]

        self._rig_channels = [
            RigChannel(
                name="CTRL_R_HipPitch",
                channel_type="control",
                limits=(-110.0, 120.0),
                units="deg",
                description="Hip flexion/extension control.",
            ),
            RigChannel(
                name="CTRL_R_HipYaw",
                channel_type="control",
                limits=(-60.0, 60.0),
                units="deg",
                description="Hip rotation for turn-in/out.",
            ),
            RigChannel(
                name="CTRL_R_HipRoll",
                channel_type="control",
                limits=(-45.0, 45.0),
                units="deg",
                description="Hip tilt for weight shift.",
            ),
            RigChannel(
                name="CTRL_R_Knee",
                channel_type="control",
                limits=(0.0, 150.0),
                units="deg",
                description="Knee hinge control.",
            ),
            RigChannel(
                name="CTRL_R_AnklePitch",
                channel_type="control",
                limits=(-50.0, 35.0),
                units="deg",
                description="Ankle dorsiflex/plantarflex control.",
            ),
            RigChannel(
                name="CTRL_R_AnkleRoll",
                channel_type="control",
                limits=(-30.0, 30.0),
                units="deg",
                description="Ankle inversion/eversion.",
            ),
            RigChannel(
                name="CTRL_R_BallRoll",
                channel_type="control",
                limits=(-35.0, 45.0),
                units="deg",
                description="Ball roll for gait toe-off.",
            ),
            RigChannel(
                name="CTRL_R_ToeCurl",
                channel_type="control",
                limits=(0.0, 80.0),
                units="deg",
                description="Toe curl amount.",
            ),
        ]

        self._micromovements = [
            MicroMovementProfile(
                name="stance_sway",
                target="CTRL_R_HipRoll",
                axis="roll",
                amplitude=1.45,
                frequency_hz=0.19,
                baseline=0.0,
                breathing_scale=0.42,
                description="Transfers vestibulospinal sway into the hip.",
            ),
            MicroMovementProfile(
                name="arterial_pulse",
                target="CTRL_R_AnklePitch",
                axis="pulse",
                amplitude=0.33,
                frequency_hz=1.02,
                phase=0.35,
                tension_scale=0.32,
                description="Ankle pulse shimmer reflecting circulation.",
            ),
            MicroMovementProfile(
                name="toe_micro_wiggle",
                target="CTRL_R_ToeCurl",
                axis="curl",
                amplitude=0.75,
                frequency_hz=0.64,
                phase=1.4,
                tension_scale=0.58,
                description="Idle toe curl response influenced by plantar sensors.",
            ),
            MicroMovementProfile(
                name="heel_roll",
                target="CTRL_R_BallRoll",
                axis="roll",
                amplitude=0.85,
                frequency_hz=0.24,
                baseline=-2.0,
                breathing_scale=0.28,
                description="Low-amplitude heel to ball rocking during quiet stance.",
            ),
        ]

        super().__init__(audit_factory=audit_factory)
        self.log_structure_summary()

    def compose_frame(
        self,
        time_s: float,
        *,
        stride: float = 0.0,
        turn: float = 0.0,
        hip_roll: float = 0.0,
        knee: float = 0.0,
        ankle: float = 0.0,
        toe: float = 0.0,
        tension: float = 0.1,
        breathing: float = 0.1,
        overrides: Optional[Mapping[str, float]] = None,
    ) -> Mapping[str, float]:
        """Compose a rig-ready channel dictionary for the given frame."""

        idle_packet = self.generate_idle_packet(time_s, tension=tension, breathing=breathing, overrides=overrides)
        frame = dict(idle_packet["channels"])
        frame.update(
            {
                "CTRL_R_HipPitch": max(-110.0, min(120.0, stride)),
                "CTRL_R_HipYaw": max(-60.0, min(60.0, turn)),
                "CTRL_R_HipRoll": max(-45.0, min(45.0, hip_roll)),
                "CTRL_R_Knee": max(0.0, min(150.0, knee)),
                "CTRL_R_AnklePitch": max(-50.0, min(35.0, ankle)),
                "CTRL_R_ToeCurl": max(0.0, min(80.0, toe)),
            }
        )

        self.audit.log_event(
            "frame_composed",
            {
                "time": time_s,
                "stride": stride,
                "turn": turn,
                "hip_roll": hip_roll,
                "knee": knee,
                "ankle": ankle,
                "toe": toe,
                "tension": tension,
                "breathing": breathing,
            },
        )
        return frame


__all__ = ["RightLegModule"]