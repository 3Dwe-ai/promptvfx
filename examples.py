from animation import Animation


# Example Explosion

EXPLOSION_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()

    if t <= 0.3:
        scale_factor = 1.1  # 10% scale increase
        new_centers *= scale_factor
    elif t <= 0.7:
        # Recursive call to get the centers from the last second of Phase 1
        new_centers = compute_centers(0.3, centers)
        scale_factor = 4.0  # 300% increase
        direction = np.random.uniform(-1, 1, new_centers.shape)  # random direction for explosion
        direction /= np.linalg.norm(direction, axis=1, keepdims=True)  # normalize
        new_centers += direction * scale_factor * (t - 0.3) / 0.4  # disperse based on time
    else:
        # Phase 3: Keep the centers from Phase 2
        new_centers = compute_centers(0.7, centers)

    return new_centers
'''.strip()

EXPLOSION_RGBS_CODE = '''
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()

    # Define constants for color transformations
    BRIGHTNESS_FACTOR = 1.5  # Factor to brighten colors

    # Phase 1: Initial Build-Up (0.0 - 0.3 seconds)
    if t <= 0.3:
        new_rgbs = np.clip(new_rgbs * BRIGHTNESS_FACTOR, 0.0, 1.0)

    # Phase 2: Outwards Explosion (0.3 - 0.7 seconds)
    elif t <= 0.7:
        new_rgbs = compute_rgbs(0.3, rgbs)  # Get colors from Phase 1

    # Phase 3: Further Explosion and Gravity Fall Down (0.7 - 1.0 seconds)
    else:
        new_rgbs = compute_rgbs(0.7, rgbs)  # Get colors from Phase 2

    return new_rgbs
'''.strip()

EXPLOSION_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    # Define constants for opacity transformations
    phase_1_end = 0.3
    phase_2_end = 0.7
    
    if t <= phase_1_end:
        # Phase 1: Initial Build-Up
        new_opacities = new_opacities * (t / phase_1_end)
    elif t <= phase_2_end:
        # Phase 2: Outwards Explosion
        # Maintain the same opacities as the end of Phase 1
        new_opacities = opacities * (1.0)  # No change, keep max opacities from Phase 1
    else:
        # Phase 3: Further Explosion and Gravity Fall Down
        # Recursively get opacities at the end of Phase 2
        new_opacities = compute_opacities(phase_2_end, opacities)
        # Decrease opacities to create a fading effect
        new_opacities = new_opacities * (1 - (t - phase_2_end) / (1.0 - phase_2_end))

    return new_opacities.reshape(N, 1)
'''.strip()

EXAMPLE_EXPLOSION = Animation(
    title="Example Explosion",
    duration=1,
    centers_code=EXPLOSION_CENTERS_CODE,
    rgbs_code=EXPLOSION_RGBS_CODE,
    opacities_code=EXPLOSION_OPACITIES_CODE,
)

# Example Color Shift

COLOR_SHIFT_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()

    if t <= 0.5:
        return new_centers  # Phase 1

    elif t <= 1.5:
        return new_centers  # Phase 2

    elif t <= 2.5:
        return new_centers  # Phase 3

    elif t <= 3.5:
        return new_centers  # Phase 4

    elif t <= 4.0:
        return new_centers  # Phase 5

    return new_centers
'''.strip()

COLOR_SHIFT_RGBS_CODE = '''
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()

    # Define color transformation constants
    def transition(t, start_color, end_color, start_time, end_time):
        if start_time <= t <= end_time:
            fraction = (t - start_time) / (end_time - start_time)
            return start_color + fraction * (end_color - start_color)
        return None

    # Phase 1: Keep colors unchanged
    if t <= 0.5:
        return new_rgbs

    # Phase 2: Color Transition Begins
    if t <= 1.5:
        if t <= 0.75:
            color_transform = transition(t, np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.0, 0.0]), 0.5, 0.75)
        elif t <= 1.0:
            color_transform = transition(t, np.array([1.0, 0.0, 0.0]), np.array([1.0, 0.5, 0.0]), 0.75, 1.0)
        elif t <= 1.25:
            color_transform = transition(t, np.array([1.0, 0.5, 0.0]), np.array([1.0, 1.0, 0.0]), 1.0, 1.25)
        else:  # t <= 1.5
            color_transform = transition(t, np.array([1.0, 1.0, 0.0]), np.array([0.0, 1.0, 0.0]), 1.25, 1.5)

        if color_transform is not None:
            new_rgbs = new_rgbs * (1 - (t % 0.5) / 0.5) + color_transform * (t % 0.5 / 0.5)

    # Phase 3: Continued Color Transition
    elif t <= 2.5:
        if t <= 1.75:
            color_transform = transition(t, np.array([0.0, 1.0, 0.0]), np.array([0.0, 0.0, 1.0]), 1.5, 1.75)
        elif t <= 2.0:
            color_transform = transition(t, np.array([0.0, 0.0, 1.0]), np.array([0.29, 0.0, 0.51]), 1.75, 2.0)
        elif t <= 2.25:
            color_transform = transition(t, np.array([0.29, 0.0, 0.51]), np.array([0.56, 0.0, 1.0]), 2.0, 2.25)
        else:  # t <= 2.5
            color_transform = transition(t, np.array([0.56, 0.0, 1.0]), np.array([0.4, 0.0, 0.56]), 2.25, 2.5)

        if color_transform is not None:
            new_rgbs = new_rgbs * (1 - (t % 0.5) / 0.5) + color_transform * (t % 0.5 / 0.5)

    # Phase 4: Reverse Color Transition
    elif t <= 3.5:
        if t <= 2.75:
            color_transform = transition(t, np.array([0.4, 0.0, 0.56]), np.array([0.29, 0.0, 0.51]), 2.5, 2.75)
        elif t <= 3.0:
            color_transform = transition(t, np.array([0.29, 0.0, 0.51]), np.array([0.0, 0.0, 1.0]), 2.75, 3.0)
        elif t <= 3.25:
            color_transform = transition(t, np.array([0.0, 0.0, 1.0]), np.array([0.0, 1.0, 0.0]), 3.0, 3.25)
        else:  # t <= 3.5
            color_transform = transition(t, np.array([0.0, 1.0, 0.0]), np.array([1.0, 1.0, 0.0]), 3.25, 3.5)

        if color_transform is not None:
            new_rgbs = new_rgbs * (1 - (t % 0.5) / 0.5) + color_transform * (t % 0.5 / 0.5)

    # Phase 5: Return to Original State
    elif t <= 4.0:
        if t <= 3.75:
            color_transform = transition(t, np.array([1.0, 1.0, 0.0]), np.array([1.0, 0.5, 0.0]), 3.5, 3.75)
        else:  # t <= 4.0
            color_transform = transition(t, np.array([1.0, 0.5, 0.0]), np.array([1.0, 0.0, 0.0]), 3.75, 4.0)

        if color_transform is not None:
            new_rgbs = new_rgbs * (1 - (t % 0.25) / 0.25) + color_transform * (t % 0.25 / 0.25)

    return new_rgbs
'''.strip()

COLOR_SHIFT_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    if t <= 0.5:
        return new_opacities  # Phase 1
    elif t <= 1.5:
        return new_opacities  # Phase 2
    elif t <= 2.5:
        return new_opacities  # Phase 3
    elif t <= 3.5:
        return new_opacities  # Phase 4
    else:
        return new_opacities  # Phase 5
'''.strip()

EXAMPLE_COLOR_SHIFT = Animation(
    title="Example Color Shift",
    duration=4,
    centers_code=COLOR_SHIFT_CENTERS_CODE,
    rgbs_code=COLOR_SHIFT_RGBS_CODE,
    opacities_code=COLOR_SHIFT_OPACITIES_CODE,
)

# Example LSD

LSD_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()

    if t <= 0.5:
        # Phase 1: Static centers
        return new_centers
    elif t <= 1.5:
        # Phase 2: Static centers
        return new_centers
    elif t <= 2.5:
        # Phase 3: Static centers
        return new_centers
    elif t <= 3.0:
        # Phase 4: Static centers
        return new_centers
    else:
        # Beyond the defined phases
        return new_centers
'''.strip()

LSD_RGBS_CODE = '''
import numpy as np

def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()
    
    phase_1_duration = 0.5
    phase_2_duration = 1.0
    phase_3_duration = 1.0
    phase_4_duration = 0.5

    def phase_1(t):
        colors = np.array([(np.abs(np.sin(t * np.pi * 2 + i * 2*np.pi/3)), 
                             np.abs(np.sin(t * np.pi * 2 + (i + 1) * 2*np.pi/3)), 
                             np.abs(np.sin(t * np.pi * 2 + (i + 2) * 2*np.pi/3)) ) for i in range(N)])
        return colors

    if t <= phase_1_duration:
        new_rgbs = phase_1(t)

    elif t <= phase_1_duration + phase_2_duration:
        normalized_t = t - phase_1_duration  # Use time even during phase 2
        new_rgbs = phase_1(normalized_t)

    elif t <= phase_1_duration + phase_2_duration + phase_3_duration:
        normalized_t = t - (phase_1_duration + phase_2_duration)  # Normalize for phase 3
        new_rgbs = phase_1(normalized_t)

    elif t <= phase_1_duration + phase_2_duration + phase_3_duration + phase_4_duration:
        explosion_color = np.array([1.0, 1.0, 0.0])  # Bright explosion color
        new_rgbs = np.clip(new_rgbs * (1 - (t - 2.5) / 0.5) + explosion_color * ((t - 2.5) / 0.5), 0, 1)

    return new_rgbs
'''.strip()

LSD_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    # Define constants for phases
    phase_1_end = 0.5
    phase_2_end = 1.5
    phase_3_end = 2.5
    phase_4_end = 3.0

    # Modifications to RGB based on 't' instead of static phase durations
    if t <= phase_1_end:  # Phase 1: Initial Visuals
        return new_opacities  # Opacities remain the same

    elif t <= phase_2_end:  # Phase 2: Expansion and Pulse
        sin_effect = np.sin((t - 0.5) * (np.pi))
        pulse_effect = 0.1 * sin_effect + 1.0
        new_opacities *= pulse_effect
        # Integrate color dynamics based on time: new_rgbs definition necessary here
        return new_opacities

    elif t <= phase_3_end:  # Phase 3: Rotation and Spiraling 
        # Further transformations based on new positioning in color if needed
        return new_opacities

    else:  # Phase 4: Final Transformation and Compression
        fade_out_time = t - 2.5  # Time since start of phase 4
        if fade_out_time < 0.2:
            new_opacities *= (1.0 - fade_out_time * 5)  # Fast decrease
        else:
            new_opacities *= 0.0  # Fully dissipated

        if fade_out_time >= 0.15 and fade_out_time < 0.2: 
            new_opacities += np.clip((fade_out_time - 0.15) * 50, 0, 1)

        return new_opacities
'''.strip()

EXAMPLE_LSD = Animation(
    title="Example LSD",
    duration=1,
    centers_code=LSD_CENTERS_CODE,
    rgbs_code=LSD_RGBS_CODE,
    opacities_code=LSD_OPACITIES_CODE,
)

# Example Lava Melting

LAVA_MELTING_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()

    lowest_z = np.min(centers[:, 2])
    outer_slice = np.where(centers[:, 2] > lowest_z + 1)[0]  # Assuming outer Gaussians are above the lowest z + 1
    inner_slice = np.where(centers[:, 2] <= lowest_z + 1)[0] # Assuming inner Gaussians are at or below the lowest z + 1

    if t <= 0.5:
        # Phase 1: No movement
        return new_centers

    elif t <= 2.0:
        # Phase 2: Outer shell melting
        dt = (t - 0.5) / (2.0 - 0.5)
        melt_amount = dt * 2.0 # Arbitrary downward movement up to 2.0 Z units
        new_centers[outer_slice, 2] = np.maximum(new_centers[outer_slice, 2] - melt_amount, lowest_z)

    elif t <= 4.0:
        # Phase 3: Core melting
        new_centers = compute_centers(2.0, centers)  # recurse to getting end of Phase 2
        dt = (t - 2.0) / (4.0 - 2.0)
        melt_amount = dt * 1.0 # Slower downward movement (up to 1.0 Z units)
        new_centers[inner_slice, 2] = np.maximum(new_centers[inner_slice, 2] - melt_amount, lowest_z)

    else:
        # Phase 4: Final melting and settling
        new_centers = compute_centers(4.0, centers)  # recurse to getting end of Phase 3
        melt_amount_outer = 2.0 # Complete outer melting
        melt_amount_inner = 1.0 # Complete inner melting
        new_centers[outer_slice, 2] = np.maximum(new_centers[outer_slice, 2] - melt_amount_outer, lowest_z)
        new_centers[inner_slice, 2] = np.maximum(new_centers[inner_slice, 2] - melt_amount_inner, lowest_z)

    return new_centers
'''.strip()

LAVA_MELTING_RGBS_CODE = '''
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()

    # Phase Constants
    phase1_end = 0.5
    phase2_end = 2.0
    phase3_end = 4.0
    phase4_end = 5.0

    def transition_to_lava_color(colors, t_current):
        # Define transformation constants for blending towards lava colors
        warm_lava_colors = np.array([[1.0, 0.5, 0.0], [1.0, 0.0, 0.0], [1.0, 0.8, 0.2]])  # some sample warm colors
        # Compute blending factor based on time progressing in the phases
        blend_factor = (t_current - phase2_end) / (phase3_end - phase2_end)
        blend_factor = np.clip(blend_factor, 0.0, 1.0)
        # Blend the original colors towards warm lava colors
        return (1 - blend_factor) * colors + blend_factor * warm_lava_colors[np.mod(np.arange(N), 3)]

    if t <= phase1_end:
        return new_rgbs
    elif t <= phase2_end:
        # Transition to warm lava colors for outer melting
        return transition_to_lava_color(new_rgbs, t)
    elif t <= phase3_end:
        # Recursively call the previous phase
        new_rgbs = compute_rgbs(phase2_end, rgbs)
        # Continue transitioning inner sections 
        return transition_to_lava_color(new_rgbs, t)
    elif t <= phase4_end:
        # Final phase, set all Gaussians to a uniform lava color
        return transition_to_lava_color(new_rgbs, phase3_end)

    return new_rgbs
'''.strip()

LAVA_MELTING_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    if t <= 0.5:
        # Phase 1: Initialization
        return new_opacities
    elif t <= 2.0:
        # Phase 2: Outer Shell Melting
        return new_opacities
    elif t <= 4.0:
        # Phase 3: Core Melting
        return new_opacities
    elif t <= 5.0:
        # Phase 4: Final Melting and Settling
        return new_opacities

    return new_opacities
'''.strip()

EXAMPLE_LAVA_MELTING = Animation(
    title="Example Lava Melting",
    duration=5,
    centers_code=LAVA_MELTING_CENTERS_CODE,
    rgbs_code=LAVA_MELTING_RGBS_CODE,
    opacities_code=LAVA_MELTING_OPACITIES_CODE,
)

# Example Acceleration

ACCELERATION_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()

    # Phase 1: Initialization (0.0 - 0.5 seconds)
    if t <= 0.5:
        return new_centers

    # Phase 2: Acceleration (0.5 - 1.5 seconds)
    elif t <= 1.5:
        acceleration_time = t - 0.5
        distance = 2 * acceleration_time ** 2  # Quadratic for acceleration
        new_centers += np.array([distance, 0, 0])  # Moving forward in X-axis

    # Phase 3: Mid-Acceleration (1.5 - 1.8 seconds)
    elif t <= 1.8:
        new_centers = compute_centers(1.5, centers)  # Getting the final centers from previous phase
        speed = 1  # Constant speed
        new_centers += np.array([speed * (t - 1.5), 0, 0])  # Continue moving forward

    # Phase 4: Deceleration and Stopping (1.8 - 2.0 seconds)
    elif t <= 2.0:
        new_centers = compute_centers(1.8, centers)  # Getting the final centers from previous phase

    return new_centers
'''.strip()

ACCELERATION_RGBS_CODE = '''
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()

    # Phase constants
    increase_factor = 1.5
    saturation_shift = 0.25

    if t <= 0.5:
        # Phase 1: Initialization
        return new_rgbs
    elif t <= 1.5:
        # Phase 2: Acceleration
        return new_rgbs
    elif t <= 1.8:
        # Phase 3: Mid-Acceleration
        return new_rgbs
    elif t <= 2.0:
        # Phase 4: Deceleration and Stopping
        return new_rgbs

    return new_rgbs
'''.strip()

ACCELERATION_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    # Phase constants
    PHASE_1_END = 0.5
    PHASE_2_END = 1.5
    PHASE_3_END = 1.8
    PHASE_4_END = 2.0

    # Phase 1: Initialization
    if t <= PHASE_1_END:
        return new_opacities

    # Phase 2: Acceleration
    if t <= PHASE_2_END:
        return new_opacities

    # Phase 3: Mid-Acceleration
    if t <= PHASE_3_END:
        return new_opacities

    # Phase 4: Deceleration and Stopping
    if t <= PHASE_4_END:
        return new_opacities

    return new_opacities
'''.strip()

EXAMPLE_ACCELERATION = Animation(
    title="Example Acceleration",
    duration=2,
    centers_code=ACCELERATION_CENTERS_CODE,
    rgbs_code=ACCELERATION_RGBS_CODE,
    opacities_code=ACCELERATION_OPACITIES_CODE,
)

# Example Breathing

BREATHING_CENTERS_CODE = '''
def compute_centers(t: float, centers: np.ndarray) -> np.ndarray:
    N = centers.shape[0]
    new_centers = centers.copy()
    amplitude = 0.2  # The maximum change in position - reduced 

    if 0.0 <= t <= 1.0:
        # Phase 1: Expansion (0 to 1)
        new_centers += (np.sin((t / 1.0) * np.pi) * amplitude) * (new_centers / np.linalg.norm(new_centers, axis=1, keepdims=True))

    elif 1.0 < t <= 2.0:
        # Phase 2: Holding Maximum (1 to 2)
        new_centers = new_centers  # maintain maximum size.

    elif 2.0 < t <= 3.0:
        # Phase 3: Contraction (2 to 3)
        new_centers += (np.sin((t - 2.0) / 1.0 * np.pi) * amplitude) * (new_centers / np.linalg.norm(new_centers, axis=1, keepdims=True))

    return new_centers
'''.strip()

BREATHING_RGBS_CODE = '''
def compute_rgbs(t: float, rgbs: np.ndarray) -> np.ndarray:
    N = rgbs.shape[0]
    new_rgbs = rgbs.copy()

    if 0.0 <= t <= 1.0:
        # Phase 1: Expansion
        return new_rgbs

    elif 1.0 < t <= 1.2:
        # Phase 2: Holding Maximum with slight variations
        return new_rgbs

    elif 1.2 < t <= 2.2:
        # Phase 3: Contraction
        return new_rgbs

    elif 2.2 < t <= 3.0:
        # Phase 4: Holding Rest Position
        return new_rgbs

    return new_rgbs
'''.strip()

BREATHING_OPACITIES_CODE = '''
def compute_opacities(t: float, opacities: np.ndarray) -> np.ndarray:
    N = opacities.shape[0]
    new_opacities = opacities.copy()

    # Define constants for opacity transformations
    max_increase_factor = 1.05  # Reduced to create a softer expansion
    min_variation = 0.05

    if 0.0 <= t <= 1.0:
        # Phase 1: Expansion
        new_opacities = np.clip(opacities * (1 + (max_increase_factor - 1) * (t / 1.0)), 0, 1)

    elif 1.0 < t <= 1.2:
        # Phase 2: Holding Maximum with slight variations
        previous_opacities = compute_opacities(1.0, opacities)
        variation = min_variation * np.sin(10 * np.pi * (t - 1.0))  # slight oscillation effect
        new_opacities = np.clip(previous_opacities + variation, 0, 1)

    elif 1.2 < t <= 2.2:
        # Phase 3: Contraction
        # progress = (t - 1.2) / (2.2 - 1.2)
        # contraction_factor = np.sin(np.pi * progress)
        # new_opacities = np.clip(new_opacities * contraction_factor, 0, 1)
        new_opacities = opacities

    elif 2.2 < t <= 3.0:
        # Phase 4: Holding Rest Position
        new_opacities = opacities  # No change during this phase

    return new_opacities.reshape(N, 1)
'''.strip()

EXAMPLE_BREATHING = Animation(
    title="Example Breathing",
    duration=3,
    centers_code=BREATHING_CENTERS_CODE,
    rgbs_code=BREATHING_RGBS_CODE,
    opacities_code=BREATHING_OPACITIES_CODE,
)
