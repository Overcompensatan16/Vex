"""Left arm routing and rig metadata module."""

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


class LeftArmModule(LimbModuleBase):
    """Aggregate structural metadata and micromotion for the left arm."""

    module_name = "left_arm"
    reflex_subsystem = "limbs_upper"

    def __init__(self, *, audit_factory=None) -> None:
        self._bones = [
            BoneSegment(
                name="clavicle_L",
                rig_target="CTRL_L_Clavicle",
                length_cm=14.0,
                parent="sternum",
                degrees_of_freedom=("elevate", "protract", "roll"),
                notes="Bridges torso posture data into shoulder positioning.",
            ),
            BoneSegment(
                name="scapula_L",
                rig_target="CTRL_L_Scapula",
                length_cm=17.5,
                parent="clavicle_L",
                degrees_of_freedom=("up_down", "tilt", "slide"),
                notes="Carries scapular glide and upward rotation curves.",
            ),
            BoneSegment(
                name="humerus_L",
                rig_target="CTRL_L_UpperArm",
                length_cm=32.0,
                parent="scapula_L",
                degrees_of_freedom=("pitch", "yaw", "roll"),
                notes="Primary lever for reach and flexor withdrawal reflexes.",
            ),
            BoneSegment(
                name="ulna_L",
                rig_target="CTRL_L_Forearm",
                length_cm=26.5,
                parent="humerus_L",
                degrees_of_freedom=("flex", "pronate"),
                notes="Tracks ulnar deviation metadata for wrist stabilization.",
            ),
            BoneSegment(
                name="radius_L",
                rig_target="CTRL_L_Radius",
                length_cm=25.5,
                parent="humerus_L",
                degrees_of_freedom=("supinate", "twist"),
                notes="Feeds pronation-supination arcs for tool handling.",
            ),
            BoneSegment(
                name="hand_L",
                rig_target="CTRL_L_Hand",
                length_cm=18.0,
                parent="ulna_L",
                degrees_of_freedom=("cup", "spread", "twist"),
                notes="Publishes hand pose blendshape group metadata.",
            ),
        ]

        self._joints = [
            Joint(
                name="sternoclavicular_L",
                bones=("sternum", "clavicle_L"),
                rig_controls=("CTRL_L_Clavicle" ,),
                limits_deg=(-25.0, 35.0),
                default_pose=5.0,
                notes="Transfers torso micro sway into clavicle elevation.",
            ),
            Joint(
                name="glenohumeral_L",
                bones=("scapula_L", "humerus_L"),
                rig_controls=("CTRL_L_ShoulderPitch", "CTRL_L_ShoulderYaw", "CTRL_L_ShoulderRoll"),
                limits_deg=(-90.0, 120.0),
                default_pose=12.0,
                notes="Primary multi-axis shoulder joint controlling reach envelopes.",
            ),
            Joint(
                name="elbow_L",
                bones=("humerus_L", "ulna_L"),
                rig_controls=("CTRL_L_ElbowFlex",),
                limits_deg=(0.0, 145.0),
                default_pose=15.0,
                notes="Routes stretch and Golgi tendon reflex data to elbow control.",
            ),
            Joint(
                name="radioulnar_L",
                bones=("radius_L", "ulna_L"),
                rig_controls=("CTRL_L_ForearmTwist",),
                limits_deg=(-85.0, 85.0),
                notes="Handles pronation/supination coupling metadata.",
            ),
            Joint(
                name="wrist_L",
                bones=("radius_L", "hand_L"),
                rig_controls=("CTRL_L_WristPitch", "CTRL_L_WristYaw"),
                limits_deg=(-70.0, 80.0),
                default_pose=0.0,
                notes="Feeds micromotion pulses for radial artery beat and hand poise.",
            ),
        ]

        self._muscles = [
            MuscleGroup(
                name="deltoid_L",
                actuators=("CTRL_L_ShoulderPitch", "CTRL_L_ShoulderYaw"),
                primary_function="Arm elevation and abduction",
                fiber_type="mixed",
                notes="Coupled to flexor withdrawal reflex to accelerate lift.",
            ),
            MuscleGroup(
                name="biceps_brachii_L",
                actuators=("CTRL_L_ElbowFlex", "CTRL_L_ForearmTwist"),
                primary_function="Elbow flexion and forearm supination",
                fiber_type="fast",
                notes="Consumes stretch reflex metadata for load compensation.",
            ),
            MuscleGroup(
                name="triceps_brachii_L",
                actuators=("CTRL_L_ElbowFlex",),
                primary_function="Elbow extension",
                fiber_type="fast",
                notes="Antagonist group modulated by Golgi tendon reflex arcs.",
            ),
            MuscleGroup(
                name="forearm_flexors_L",
                actuators=("CTRL_L_WristPitch", "CTRL_L_HandCurl"),
                primary_function="Finger flexion and wrist stabilization",
                fiber_type="slow",
                notes="Mapped to grasp curves and tactile withdrawal metadata.",
            ),
            MuscleGroup(
                name="forearm_extensors_L",
                actuators=("CTRL_L_WristPitch", "CTRL_L_WristYaw"),
                primary_function="Wrist extension and radial deviation",
                fiber_type="slow",
                notes="Stabilizes hand during reach with micro jitter suppression.",
            ),
        ]

        self._sensors = [
            SensorCluster(
                name="cutaneous_radial_L",
                sensor_type="cutaneous",
                afferents=("sensory_cutaneous.radial_L", "sensory_cutaneous.palm_L"),
                rig_notes="Triggers protective flexor micromotion and grip tightening.",
            ),
            SensorCluster(
                name="muscle_spindle_L",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.biceps_spindle_L",),
                rig_notes="Feeds stretch reflex metadata into elbow compensation curves.",
            ),
            SensorCluster(
                name="golgi_tendon_L",
                sensor_type="proprioceptor",
                afferents=("sensory_proprioceptive.triceps_gto_L",),
                rig_notes="Provides load shedding cues for rig-driven bracing motions.",
            ),
        ]

        self._rig_channels = [
            RigChannel(
                name="CTRL_L_ShoulderPitch",
                channel_type="control",
                limits=(-90.0, 120.0),
                units="deg",
                description="Primary arm elevation control.",
            ),
            RigChannel(
                name="CTRL_L_ShoulderYaw",
                channel_type="control",
                limits=(-80.0, 80.0),
                units="deg",
                description="Horizontal reach sweep.",
            ),
            RigChannel(
                name="CTRL_L_ElbowFlex",
                channel_type="control",
                limits=(0.0, 145.0),
                units="deg",
                description="Elbow hinge for reach and withdrawal.",
            ),
            RigChannel(
                name="CTRL_L_ForearmTwist",
                channel_type="control",
                limits=(-85.0, 85.0),
                units="deg",
                description="Forearm pronation/supination twist.",
            ),
            RigChannel(
                name="CTRL_L_WristPitch",
                channel_type="control",
                limits=(-70.0, 80.0),
                units="deg",
                description="Wrist flexion curve output.",
            ),
            RigChannel(
                name="CTRL_L_WristYaw",
                channel_type="control",
                limits=(-45.0, 45.0),
                units="deg",
                description="Wrist deviation mapping.",
            ),
            RigChannel(
                name="CTRL_L_HandCurl",
                channel_type="blendshape",
                limits=(0.0, 1.0),
                description="Finger curl blendshape weight.",
            ),
            RigChannel(
                name="CTRL_L_PalmSplay",
                channel_type="blendshape",
                limits=(0.0, 1.0),
                description="Finger spread amount for expressive gestures.",
            ),
        ]

        self._micromovements = [
            MicroMovementProfile(
                name="breath_scaffold",
                target="CTRL_L_Clavicle",
                axis="elevate",
                amplitude=0.8,
                frequency_hz=0.32,
                baseline=2.0,
                breathing_scale=0.6,
                description="Slow clavicle lift tracking respiratory phase.",
            ),
            MicroMovementProfile(
                name="radial_pulse",
                target="CTRL_L_WristPitch",
                axis="pulse",
                amplitude=0.45,
                frequency_hz=1.15,
                phase=0.4,
                tension_scale=0.35,
                description="Subtle radial artery beat modulated by tension.",
            ),
            MicroMovementProfile(
                name="finger_fidgets",
                target="CTRL_L_HandCurl",
                axis="curl",
                amplitude=0.05,
                frequency_hz=0.8,
                phase=1.2,
                tension_scale=0.75,
                description="Stochastic-like finger curl ripple for idle nuance.",
            ),
            MicroMovementProfile(
                name="ulnar_adjust",
                target="CTRL_L_WristYaw",
                axis="yaw",
                amplitude=0.6,
                frequency_hz=0.22,
                baseline=0.2,
                breathing_scale=0.25,
                description="Keeps wrist subtly cycling with gait sway metadata.",
            ),
        ]

        super().__init__(audit_factory=audit_factory)
        self.log_structure_summary()

    # ------------------------------------------------------------------
    # Frame composition helpers
    # ------------------------------------------------------------------
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
                "CTRL_L_ShoulderPitch": max(-90.0, min(120.0, reach)),
                "CTRL_L_ShoulderYaw": max(-80.0, min(80.0, lateral)),
                "CTRL_L_ElbowFlex": max(0.0, min(145.0, elbow)),
                "CTRL_L_ForearmTwist": max(-85.0, min(85.0, twist)),
                "CTRL_L_HandCurl": max(0.0, min(1.0, grip)),
                "CTRL_L_PalmSplay": max(0.0, min(1.0, spread)),
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


__all__ = ["LeftArmModule"]