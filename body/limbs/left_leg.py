"""Left leg routing and rig metadata module."""

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


class LeftLegModule(LimbModuleBase):
    """Aggregate structural metadata and micromotion for the left leg."""

    module_name = "left_leg"
    reflex_subsystem = "limbs_lower"

    def __init__(self, *, audit_factory=None) -> None:
        self._bones = [
            BoneSegment(
                name="pelvis_L",
                rig_target="CTRL_Pelvis",
                length_cm=0.0,
                parent="spine_03",
                degrees_of_freedom=("translate", "tilt", "twist"),
                notes="Anchor for lower-limb rig metadata; shared across legs.",
            ),
            BoneSegment(
                name="femur_L",
                rig_target="CTRL_L_Thigh",
                length_cm=43.0,
                parent="pelvis_L",
                degrees_of_freedom=("pitch", "yaw", "roll"),
                notes="Primary lever for stance and locomotion arcs.",
            ),
            BoneSegment(
                name="tibia_L",
                rig_target="CTRL_L_Shin",
                length_cm=41.0,
                parent="femur_L",
                degrees_of_freedom=("flex", "twist"),
                notes="Carries knee flexion metadata and tibial rotation.",
            ),
            BoneSegment(
                name="fibula_L",
                rig_target="CTRL_L_Fibula",
                length_cm=40.5,
                parent="femur_L",
                degrees_of_freedom=("support",),
                notes="Auxiliary channel for lateral stability blendshapes.",
            ),
            BoneSegment(
                name="foot_L",
                rig_target="CTRL_L_Foot",
                length_cm=26.0,
                parent="tibia_L",
                degrees_of_freedom=("dorsi", "plantar", "invert", "evert"),
                notes="Publishes plantar roll metadata for gait transitions.",
            ),
            BoneSegment(
                name="toes_L",
                rig_target="CTRL_L_Toe",
                length_cm=7.0,
                parent="foot_L",
                degrees_of_freedom=("curl", "spread"),
                notes="Provides toe-off metadata for locomotion curves.",
            ),
        ]

        self._joints = [
            Joint(
                name="hip_L",
                bones=("pelvis_L", "femur_L"),
                rig_controls=("CTRL_L_HipPitch", "CTRL_L_HipYaw", "CTRL_L_HipRoll"),
                limits_deg=(-110.0, 120.0),
                default_pose=5.0,
                notes="Handles stride envelopes and crossed extensor reflex weighting.",
            ),
            Joint(
                name="knee_L",
                bones=("femur_L", "tibia_L"),
                rig_controls=("CTRL_L_Knee",),
                limits_deg=(0.0, 150.0),
                default_pose=5.0,
                notes="Publishes patellar stretch and load compensation data.",
            ),
            Joint(
                name="ankle_L",
                bones=("tibia_L", "foot_L"),
                rig_controls=("CTRL_L_AnklePitch", "CTRL_L_AnkleRoll"),
                limits_deg=(-50.0, 35.0),
                default_pose=0.0,
                notes="Routes plantar reflex metadata into roll control.",
            ),
            Joint(
                name="subtalar_L",
                bones=("foot_L", "toes_L"),
                rig_controls=("CTRL_L_BallRoll",),
                limits_deg=(-35.0, 45.0),
                notes="Handles toe-off sequencing with gait central pattern metadata.",
            ),
            Joint(
                name="metatarsal_L",
                bones=("foot_L", "toes_L"),
                rig_controls=("CTRL_L_ToeCurl",),
                limits_deg=(0.0, 80.0),
                notes="Provides toe curl amplitude for balance micro-corrections.",
            ),
        ]

        self._muscles = [
            MuscleGroup(
                name="gluteus_med_L",
                actuators=("CTRL_L_HipPitch", "CTRL_L_HipRoll"),
                primary_function="Hip abduction and pelvic stabilization",
                fiber_type="slow",
                notes="Coupled to vestibulospinal sway metadata.",
            ),
            MuscleGroup(
                name="quadriceps_L",
                actuators=("CTRL_L_Knee",),
                primary_function="Knee extension",
                fiber_type="fast",
                notes="Consumes patellar reflex data for stance recovery.",
            ),
            MuscleGroup(
                name="hamstrings_L",
                actuators=("CTRL_L_HipPitch", "CTRL_L_Knee"),
                primary_function="Hip extension and knee flexion",
                fiber_type="mixed",
                notes="Supports swing phase via gait pattern metadata.",
            ),
            MuscleGroup(
                name="gastrocnemius_L",
                actuators=("CTRL_L_AnklePitch", "CTRL_L_BallRoll"),
                primary_function="Plantarflexion and push-off",
                fiber_type="fast",
                notes="Integrates plantar reflex signals to drive protective responses.",
            ),
            MuscleGroup(
                name="tibialis_ant_L",
                actuators=("CTRL_L_AnklePitch", "CTRL_L_ToeCurl"),
                primary_function="Dorsiflexion and toe lift",
                fiber_type="slow",
                notes="Prevents foot drop with gait central pattern metadata.",
            ),
        ]

        self._sensors = [
            SensorCluster(
                name="plantar_cutaneous_L",
                sensor_type="cutaneous",
                afferents=("sensory_cutaneous.plantar_L", "sensory_cutaneous.heel_L"),
                rig_notes="Drives plantar reflex gating for foot roll blendshapes.",
            ),
            SensorCluster(
                name="muscle_spindle_quads_L",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.quadriceps_spindle_L",),
                rig_notes="Feeds knee stabilization metadata to rig curves.",
            ),
            SensorCluster(
                name="golgi_tendon_ankle_L",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.achilles_gto_L",),
                rig_notes="Provides ankle load shedding cues for balance.",
            ),
        ]

        self._rig_channels = [
            RigChannel(
                name="CTRL_L_HipPitch",
                channel_type="control",
                limits=(-110.0, 120.0),
                units="deg",
                description="Hip flexion/extension control.",
            ),
            RigChannel(
                name="CTRL_L_HipYaw",
                channel_type="control",
                limits=(-60.0, 60.0),
                units="deg",
                description="Hip rotation for turn-in/out.",
            ),
            RigChannel(
                name="CTRL_L_HipRoll",
                channel_type="control",
                limits=(-45.0, 45.0),
                units="deg",
                description="Hip tilt for weight shift.",
            ),
            RigChannel(
                name="CTRL_L_Knee",
                channel_type="control",
                limits=(0.0, 150.0),
                units="deg",
                description="Knee hinge control.",
            ),
            RigChannel(
                name="CTRL_L_AnklePitch",
                channel_type="control",
                limits=(-50.0, 35.0),
                units="deg",
                description="Ankle dorsiflex/plantarflex control.",
            ),
            RigChannel(
                name="CTRL_L_AnkleRoll",
                channel_type="control",
                limits=(-30.0, 30.0),
                units="deg",
                description="Ankle inversion/eversion.",
            ),
            RigChannel(
                name="CTRL_L_BallRoll",
                channel_type="control",
                limits=(-35.0, 45.0),
                units="deg",
                description="Ball roll for gait toe-off.",
            ),
            RigChannel(
                name="CTRL_L_ToeCurl",
                channel_type="control",
                limits=(0.0, 80.0),
                units="deg",
                description="Toe curl amount.",
            ),
        ]

        self._micromovements = [
            MicroMovementProfile(
                name="stance_sway",
                target="CTRL_L_HipRoll",
                axis="roll",
                amplitude=1.5,
                frequency_hz=0.18,
                baseline=0.0,
                breathing_scale=0.4,
                description="Transfers vestibulospinal sway into the hip.",
            ),
            MicroMovementProfile(
                name="arterial_pulse",
                target="CTRL_L_AnklePitch",
                axis="pulse",
                amplitude=0.35,
                frequency_hz=1.05,
                phase=0.2,
                tension_scale=0.3,
                description="Ankle pulse shimmer reflecting circulation.",
            ),
            MicroMovementProfile(
                name="toe_micro_wiggle",
                target="CTRL_L_ToeCurl",
                axis="curl",
                amplitude=0.8,
                frequency_hz=0.6,
                phase=1.1,
                tension_scale=0.6,
                description="Idle toe curl response influenced by plantar sensors.",
            ),
            MicroMovementProfile(
                name="heel_roll",
                target="CTRL_L_BallRoll",
                axis="roll",
                amplitude=0.9,
                frequency_hz=0.25,
                baseline=-2.0,
                breathing_scale=0.3,
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
                "CTRL_L_HipPitch": max(-110.0, min(120.0, stride)),
                "CTRL_L_HipYaw": max(-60.0, min(60.0, turn)),
                "CTRL_L_HipRoll": max(-45.0, min(45.0, hip_roll)),
                "CTRL_L_Knee": max(0.0, min(150.0, knee)),
                "CTRL_L_AnklePitch": max(-50.0, min(35.0, ankle)),
                "CTRL_L_ToeCurl": max(0.0, min(80.0, toe)),
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


__all__ = ["LeftLegModule"]