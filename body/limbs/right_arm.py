"""Right arm routing and rig metadata module."""

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


class RightArmModule(LimbModuleBase):
    """Aggregate structural metadata and micromotion for the right arm."""

    module_name = "right_arm"
    reflex_subsystem = "limbs_upper"

    def __init__(self, *, audit_factory=None) -> None:
        self._bones = [
            BoneSegment(
                name="clavicle_R",
                rig_target="CTRL_R_Clavicle",
                length_cm=14.0,
                parent="sternum",
                degrees_of_freedom=("elevate", "protract", "roll"),
                notes="Mirrors left clavicle rig mapping with mirrored axes.",
            ),
            BoneSegment(
                name="scapula_R",
                rig_target="CTRL_R_Scapula",
                length_cm=17.5,
                parent="clavicle_R",
                degrees_of_freedom=("up_down", "tilt", "slide"),
                notes="Handles scapular glide metadata for dominant-hand emphasis.",
            ),
            BoneSegment(
                name="humerus_R",
                rig_target="CTRL_R_UpperArm",
                length_cm=32.0,
                parent="scapula_R",
                degrees_of_freedom=("pitch", "yaw", "roll"),
                notes="Publishes reach, throw, and bracing arcs for right arm.",
            ),
            BoneSegment(
                name="ulna_R",
                rig_target="CTRL_R_Forearm",
                length_cm=26.5,
                parent="humerus_R",
                degrees_of_freedom=("flex", "pronate"),
                notes="Carries medial deviation metadata for stylus/pen handling.",
            ),
            BoneSegment(
                name="radius_R",
                rig_target="CTRL_R_Radius",
                length_cm=25.5,
                parent="humerus_R",
                degrees_of_freedom=("supinate", "twist"),
                notes="Feeds supination micro-adjusts for pointing precision.",
            ),
            BoneSegment(
                name="hand_R",
                rig_target="CTRL_R_Hand",
                length_cm=18.0,
                parent="ulna_R",
                degrees_of_freedom=("cup", "spread", "twist"),
                notes="Exports right-hand pose sets with stylus-ready bias.",
            ),
        ]

        self._joints = [
            Joint(
                name="sternoclavicular_R",
                bones=("sternum", "clavicle_R"),
                rig_controls=("CTRL_R_Clavicle",),
                limits_deg=(-25.0, 35.0),
                default_pose=4.0,
                notes="Balances torso sway and breathing on dominant side.",
            ),
            Joint(
                name="glenohumeral_R",
                bones=("scapula_R", "humerus_R"),
                rig_controls=("CTRL_R_ShoulderPitch", "CTRL_R_ShoulderYaw", "CTRL_R_ShoulderRoll"),
                limits_deg=(-90.0, 120.0),
                default_pose=10.0,
                notes="Primary articulation for reaching, bracing, and waving.",
            ),
            Joint(
                name="elbow_R",
                bones=("humerus_R", "ulna_R"),
                rig_controls=("CTRL_R_ElbowFlex",),
                limits_deg=(0.0, 145.0),
                default_pose=12.0,
                notes="Shares stretch reflex metadata with tool-usage overlays.",
            ),
            Joint(
                name="radioulnar_R",
                bones=("radius_R", "ulna_R"),
                rig_controls=("CTRL_R_ForearmTwist",),
                limits_deg=(-85.0, 85.0),
                notes="Handles pronation/supination transitions for stylus control.",
            ),
            Joint(
                name="wrist_R",
                bones=("radius_R", "hand_R"),
                rig_controls=("CTRL_R_WristPitch", "CTRL_R_WristYaw"),
                limits_deg=(-70.0, 80.0),
                notes="Feeds right wrist micro motions for writing precision.",
            ),
        ]

        self._muscles = [
            MuscleGroup(
                name="deltoid_R",
                actuators=("CTRL_R_ShoulderPitch", "CTRL_R_ShoulderYaw"),
                primary_function="Arm elevation and abduction",
                fiber_type="mixed",
                notes="Pairs with reach overlays for gestural emphasis.",
            ),
            MuscleGroup(
                name="biceps_brachii_R",
                actuators=("CTRL_R_ElbowFlex", "CTRL_R_ForearmTwist"),
                primary_function="Elbow flexion and forearm supination",
                fiber_type="fast",
                notes="Uses stretch reflex metadata to stabilize object lifting.",
            ),
            MuscleGroup(
                name="triceps_brachii_R",
                actuators=("CTRL_R_ElbowFlex",),
                primary_function="Elbow extension",
                fiber_type="fast",
                notes="Provides counter-torque for quick pointing motions.",
            ),
            MuscleGroup(
                name="forearm_flexors_R",
                actuators=("CTRL_R_WristPitch", "CTRL_R_HandCurl"),
                primary_function="Finger flexion and grip shaping",
                fiber_type="slow",
                notes="Integrates tactile metadata for stylus grip adjustments.",
            ),
            MuscleGroup(
                name="forearm_extensors_R",
                actuators=("CTRL_R_WristPitch", "CTRL_R_WristYaw"),
                primary_function="Wrist extension and radial deviation",
                fiber_type="slow",
                notes="Stabilizes wrist with crossed extensor reflex metadata.",
            ),
        ]

        self._sensors = [
            SensorCluster(
                name="cutaneous_ulnar_R",
                sensor_type="cutaneous",
                afferents=("sensory_cutaneous.ulnar_R", "sensory_cutaneous.palm_R"),
                rig_notes="Triggers micro splay adjustments when grip slips.",
            ),
            SensorCluster(
                name="muscle_spindle_R",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.biceps_spindle_R",),
                rig_notes="Feeds stretch reflex metadata into elbow compensation curves.",
            ),
            SensorCluster(
                name="golgi_tendon_R",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.triceps_gto_R",),
                rig_notes="Enables load release cues for fast bracing.",
            ),
        ]

        self._rig_channels = [
            RigChannel(
                name="CTRL_R_ShoulderPitch",
                channel_type="control",
                limits=(-90.0, 120.0),
                units="deg",
                description="Right arm elevation control.",
            ),
            RigChannel(
                name="CTRL_R_ShoulderYaw",
                channel_type="control",
                limits=(-80.0, 80.0),
                units="deg",
                description="Horizontal reach sweep.",
            ),
            RigChannel(
                name="CTRL_R_ElbowFlex",
                channel_type="control",
                limits=(0.0, 145.0),
                units="deg",
                description="Elbow hinge for right arm.",
            ),
            RigChannel(
                name="CTRL_R_ForearmTwist",
                channel_type="control",
                limits=(-85.0, 85.0),
                units="deg",
                description="Forearm pronation/supination twist.",
            ),
            RigChannel(
                name="CTRL_R_WristPitch",
                channel_type="control",
                limits=(-70.0, 80.0),
                units="deg",
                description="Wrist flexion curve output.",
            ),
            RigChannel(
                name="CTRL_R_WristYaw",
                channel_type="control",
                limits=(-45.0, 45.0),
                units="deg",
                description="Wrist deviation mapping.",
            ),
            RigChannel(
                name="CTRL_R_HandCurl",
                channel_type="blendshape",
                limits=(0.0, 1.0),
                description="Finger curl blendshape weight.",
            ),
            RigChannel(
                name="CTRL_R_PalmSplay",
                channel_type="blendshape",
                limits=(0.0, 1.0),
                description="Finger spread amount for expressive gestures.",
            ),
        ]

        self._micromovements = [
            MicroMovementProfile(
                name="breath_scaffold",
                target="CTRL_R_Clavicle",
                axis="elevate",
                amplitude=0.65,
                frequency_hz=0.34,
                baseline=1.5,
                breathing_scale=0.6,
                description="Clavicle rise synced with breathing but slightly offset.",
            ),
            MicroMovementProfile(
                name="radial_pulse",
                target="CTRL_R_WristPitch",
                axis="pulse",
                amplitude=0.42,
                frequency_hz=1.13,
                phase=0.7,
                tension_scale=0.35,
                description="Subtle artery beat modulated by arousal/tension.",
            ),
            MicroMovementProfile(
                name="precision_jitter",
                target="CTRL_R_ForearmTwist",
                axis="twist",
                amplitude=0.9,
                frequency_hz=0.95,
                phase=0.3,
                tension_scale=0.55,
                description="Handwriting-style micro jitter when idle.",
            ),
            MicroMovementProfile(
                name="finger_fidgets",
                target="CTRL_R_HandCurl",
                axis="curl",
                amplitude=0.06,
                frequency_hz=0.82,
                phase=1.6,
                tension_scale=0.7,
                description="Idle finger flex pulses, more active under tension.",
            ),
        ]

        super().__init__(audit_factory=audit_factory)
        self.log_structure_summary()

    def compose_frame(
        self,
        time_s: float,
        *,
        reach: float = 0.0,
        lateral: float = 0.0,
        elbow: float = 0.0,
        twist: float = 0.0,
        grip: float = 0.0,
        spread: float = 0.0,
        tension: float = 0.1,
        breathing: float = 0.1,
        overrides: Optional[Mapping[str, float]] = None,
    ) -> Mapping[str, float]:
        """Compose a rig-ready channel dictionary for the given frame."""

        idle_packet = self.generate_idle_packet(time_s, tension=tension, breathing=breathing, overrides=overrides)
        frame = dict(idle_packet["channels"])
        frame.update(
            {
                "CTRL_R_ShoulderPitch": max(-90.0, min(120.0, reach)),
                "CTRL_R_ShoulderYaw": max(-80.0, min(80.0, lateral)),
                "CTRL_R_ElbowFlex": max(0.0, min(145.0, elbow)),
                "CTRL_R_ForearmTwist": max(-85.0, min(85.0, twist)),
                "CTRL_R_HandCurl": max(0.0, min(1.0, grip)),
                "CTRL_R_PalmSplay": max(0.0, min(1.0, spread)),
            }
        )

        self.audit.log_event(
            "frame_composed",
            {
                "time": time_s,
                "reach": reach,
                "lateral": lateral,
                "elbow": elbow,
                "twist": twist,
                "grip": grip,
                "spread": spread,
                "tension": tension,
                "breathing": breathing,
            },
        )
        return frame


__all__ = ["RightArmModule"]