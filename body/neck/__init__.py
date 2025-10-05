"""Neck routing and rig metadata module."""

from __future__ import annotations

from typing import Mapping, Optional

from body.limbs.limb_base import (
    BoneSegment,
    Joint,
    LimbModuleBase,
    MicroMovementProfile,
    MuscleGroup,
    RigChannel,
    SensorCluster,
)


class NeckModule(LimbModuleBase):
    """Aggregate structural metadata and micromotion for the neck."""

    module_name = "neck"
    reflex_subsystem = "neck_cervical"

    def __init__(self, *, audit_factory=None) -> None:
        self._bones = [
            BoneSegment(
                name="occiput",
                rig_target="CTRL_Head",
                length_cm=11.5,
                parent=None,
                degrees_of_freedom=("pitch", "yaw", "roll"),
                notes="Represents skull base for coupling to head orientation controls.",
            ),
            BoneSegment(
                name="atlas_c1",
                rig_target="CTRL_Neck_C1",
                length_cm=2.3,
                parent="occiput",
                degrees_of_freedom=("pitch", "roll"),
                notes="Primary joint surface for nodding and lateral tilt motions.",
            ),
            BoneSegment(
                name="axis_c2",
                rig_target="CTRL_Neck_C2",
                length_cm=2.2,
                parent="atlas_c1",
                degrees_of_freedom=("yaw",),
                notes="Handles axial rotation coupling for head turns.",
            ),
            BoneSegment(
                name="cervical_mid",
                rig_target="CTRL_Neck_Mid",
                length_cm=4.5,
                parent="axis_c2",
                degrees_of_freedom=("pitch", "yaw"),
                notes="Bundles C3-C5 motion for simplified rig driving.",
            ),
            BoneSegment(
                name="cervical_base",
                rig_target="CTRL_Neck_Base",
                length_cm=4.8,
                parent="cervical_mid",
                degrees_of_freedom=("pitch", "yaw", "slide"),
                notes="Collects lower cervical sway transitioning into thoracic spine.",
            ),
            BoneSegment(
                name="thoracic_t1",
                rig_target="CTRL_SpineUpper",
                length_cm=3.1,
                parent="cervical_base",
                degrees_of_freedom=("pitch", "yaw"),
                notes="Anchor for clavicle linkage tying the neck into the torso stack.",
            ),
        ]

        self._joints = [
            Joint(
                name="atlanto_occipital",
                bones=("occiput", "atlas_c1"),
                rig_controls=("CTRL_HeadPitch", "CTRL_HeadRoll"),
                limits_deg=(-35.0, 35.0),
                default_pose=5.0,
                notes="Nodding interface transferring vestibular head pose cues.",
            ),
            Joint(
                name="atlanto_axial",
                bones=("atlas_c1", "axis_c2"),
                rig_controls=("CTRL_HeadYaw",),
                limits_deg=(-70.0, 70.0),
                notes="Dedicated axial rotation channel for head turning arcs.",
            ),
            Joint(
                name="cervicothoracic",
                bones=("cervical_base", "thoracic_t1"),
                rig_controls=("CTRL_NeckBasePitch", "CTRL_ClavicleBridge"),
                limits_deg=(-25.0, 25.0),
                default_pose=2.0,
                notes="Bridges lower neck posture into shoulder girdle elevation cues.",
            ),
        ]

        self._muscles = [
            MuscleGroup(
                name="sternocleidomastoid_LR",
                actuators=("CTRL_HeadYaw", "CTRL_HeadPitch", "CTRL_ClavicleBridge"),
                primary_function="Head rotation, flexion, and clavicle coupling",
                fiber_type="fast",
                notes="Pairs vestibular orientation with upper thoracic lift for breath tension.",
            ),
            MuscleGroup(
                name="splenius_capitis",
                actuators=("CTRL_HeadPitch", "CTRL_HeadRoll"),
                primary_function="Head extension and ipsilateral tilt",
                fiber_type="mixed",
                notes="Offsets forward flexion to keep horizon leveling signals steady.",
            ),
            MuscleGroup(
                name="levator_scapulae",
                actuators=("CTRL_NeckBasePitch", "CTRL_ClavicleBridge"),
                primary_function="Raises scapula and stabilises cervical base",
                fiber_type="slow",
                notes="Feeds shoulder shrug data into lower cervical alignment cues.",
            ),
            MuscleGroup(
                name="upper_trapezius",
                actuators=("CTRL_NeckBasePitch", "CTRL_ClavicleBridge"),
                primary_function="Extends neck and supports clavicle elevation",
                fiber_type="slow",
                notes="Links postural sway from torso into subtle head float motions.",
            ),
        ]

        self._sensors = [
            SensorCluster(
                name="vestibular_head_pose",
                sensor_type="vestibular",
                afferents=("sensory_vestibular.head_pose", "sensory_visual.gaze_alignment"),
                rig_notes="Aligns head orientation with gaze stabilisation metadata.",
            ),
            SensorCluster(
                name="cervical_proprioceptors",
                sensor_type="proprioceptive",
                afferents=("sensory_proprioceptive.cervical", "sensory_cutaneous.neck"),
                rig_notes="Provides neck tension feedback for micromotion scaling.",
            ),
        ]

        self._rig_channels = [
            RigChannel(
                name="CTRL_NeckBasePitch",
                channel_type="control",
                limits=(-25.0, 25.0),
                units="deg",
                description="Lower cervical flexion driving thoracic linkage.",
            ),
            RigChannel(
                name="CTRL_NeckBaseYaw",
                channel_type="control",
                limits=(-45.0, 45.0),
                units="deg",
                description="Lower cervical rotation blending into torso sway.",
            ),
            RigChannel(
                name="CTRL_HeadPitch",
                channel_type="control",
                limits=(-40.0, 40.0),
                units="deg",
                description="Primary head nodding channel.",
            ),
            RigChannel(
                name="CTRL_HeadYaw",
                channel_type="control",
                limits=(-75.0, 75.0),
                units="deg",
                description="Primary head turn channel.",
            ),
            RigChannel(
                name="CTRL_HeadRoll",
                channel_type="control",
                limits=(-30.0, 30.0),
                units="deg",
                description="Head side tilt channel.",
            ),
            RigChannel(
                name="CTRL_ClavicleBridge",
                channel_type="control",
                limits=(-10.0, 18.0),
                units="deg",
                description="Shoulder bridge control tying into clavicle lift cues.",
            ),
        ]

        self._micromovements = [
            MicroMovementProfile(
                name="breath_extension",
                target="CTRL_NeckBasePitch",
                axis="pitch",
                amplitude=0.8,
                frequency_hz=0.3,
                baseline=1.0,
                breathing_scale=0.7,
                description="Respiratory-linked extension that lifts the throat subtly.",
            ),
            MicroMovementProfile(
                name="head_float",
                target="CTRL_HeadRoll",
                axis="roll",
                amplitude=0.6,
                frequency_hz=0.18,
                phase=1.1,
                tension_scale=0.4,
                description="Slow horizon-leveling sway reacting to vestibular input.",
            ),
            MicroMovementProfile(
                name="clavicle_pulse",
                target="CTRL_ClavicleBridge",
                axis="elevate",
                amplitude=0.9,
                frequency_hz=0.9,
                phase=0.25,
                tension_scale=0.55,
                description="Tiny rhythmic lift that indicates shoulder stabiliser tone.",
            ),
        ]

        super().__init__(audit_factory=audit_factory)
        self.log_structure_summary()

    def compose_frame(
        self,
        time_s: float,
        *,
        head_pitch: float = 0.0,
        head_yaw: float = 0.0,
        head_roll: float = 0.0,
        neck_yaw: float = 0.0,
        shoulder_bridge: float = 0.0,
        tension: float = 0.1,
        breathing: float = 0.1,
        overrides: Optional[Mapping[str, float]] = None,
    ) -> Mapping[str, float]:
        """Compose rig channel data for the neck and head."""

        idle_packet = self.generate_idle_packet(
            time_s,
            tension=tension,
            breathing=breathing,
            overrides=overrides,
        )
        frame = dict(idle_packet["channels"])
        frame.update(
            {
                "CTRL_NeckBaseYaw": max(-45.0, min(45.0, neck_yaw)),
                "CTRL_HeadPitch": max(-40.0, min(40.0, head_pitch)),
                "CTRL_HeadYaw": max(-75.0, min(75.0, head_yaw)),
                "CTRL_HeadRoll": max(-30.0, min(30.0, head_roll)),
                "CTRL_ClavicleBridge": max(-10.0, min(18.0, shoulder_bridge)),
            }
        )

        self.audit.log_event(
            "frame_composed",
            {
                "time": time_s,
                "head_pitch": head_pitch,
                "head_yaw": head_yaw,
                "head_roll": head_roll,
                "neck_yaw": neck_yaw,
                "shoulder_bridge": shoulder_bridge,
                "tension": tension,
                "breathing": breathing,
            },
        )
        return frame


__all__ = ["NeckModule"]