# Claude Production Prompt: Hope Wellness Center 60 Second Reel

Build and render the reel. Do not stop at a treatment, storyboard, or code sketch.

Work from this folder and inspect every supplied asset before editing. The delivered PDF and `source/extracted-analysis.md` are the source of truth. Use all eleven illustrations and the exact supplied logo.

## Creative objective

Create a premium 60 second Instagram Reel or TikTok style vertical brand film for The Hope Wellness Center. The piece should feel like one continuous breath: calm, dimensional, emotionally reassuring, and intentionally designed. It should turn the flat illustrations into a living visual world through subtle 2.5D depth, organic appearing and disappearing masks, controlled camera motion, elegant typography, and seamless object motivated transitions.

The emotional movement is:

`overwhelm -> breath -> reflection -> balance -> gentle forward motion -> confidence -> hope`

This is not a hard sell. It is a soothing invitation to take a first step.

## Required deliverable

- Exactly 60.00 seconds, acceptable tolerance plus or minus 0.10 seconds
- 1080 by 1920, 9:16 vertical
- 30 fps, 1,800 frames
- H.264 MP4, high quality, web optimized
- AAC audio, 48 kHz
- Safe margins: 90 px left and right, 140 px top, 250 px bottom
- Final filename: `hope-wellness-60s-reel-final.mp4`
- Also preserve the editable project and render source in this folder

## Brand system

- Exact logo: `assets/00-hope-wellness-logo.png`
- Never redraw, regenerate, stretch, recolor, crop, retype, or distort the logo
- Typography: Poppins for primary copy; Lora Italic only for a restrained emotional accent
- Palette sampled from the delivered logo and kit: deep navy around `#204090`, leaf green around `#70C050`, soft blue around `#DCEAFE`, and warm white around `#F7FAF8`
- Preserve the native colors of every illustration
- Use white space, layered botanical shapes, curved paths, breath rings, and restrained depth
- Avoid generic glass cards, neon, purple gradients, loud glitch effects, kinetic type overload, or busy stock transitions

## Motion language

Every shot should have three depth planes where practical:

1. A softly enlarged and slightly blurred environmental plane
2. The original illustration as the stable full fidelity base
3. A carefully masked foreground subject or botanical plane with subtle independent movement

Use 3D camera motion sparingly: 2 to 5 degrees of perspective, 3 to 7 percent scale travel, and slow ease in or ease out. Do not warp faces, hands, limbs, the dog, or volleyballs. If automated segmentation is imperfect, choose a clean geometric mask or keep the original flat image rather than accepting visible artifacts.

The disappearing motif should feel organic. Subjects or scene edges can resolve into soft leaf shapes, breath rings, ink strokes, or pale particles, then reassemble into the next scene. Keep the opacity and motion soft enough that the person never feels erased in a disturbing way.

Transition vocabulary:

- Logo brain and leaf form revealed by two interlocking curved masks
- Breath rings and drifting leaves
- Ink line from the journal becoming the edge of the yoga mat
- Mat edge becoming a walking or running path
- Plant leaves creating foreground wipes
- Volleyball match cuts linking the final three active scenes
- Final particles and leaves gathering back into the exact logo

Do not repeat one transition mechanically. Let the visual object in the current scene motivate the next transition.

## Frame accurate scene plan

Follow `timeline.json`. Use every image in the specified order unless a technically stronger transition needs a brief overlap. No illustration may be omitted.

### On-screen copy

Keep copy minimal, readable, and off the subject's face. Use one strong phrase at a time.

- 00:00 to 00:03: `A gentler way forward`
- 00:03 to 00:13: `Breathe. Begin where you are.`
- 00:13 to 00:23: `Care that makes room for you.`
- 00:23 to 00:33: `Balance. Rest. Reconnect.`
- 00:33 to 00:43: `Small steps still move you forward.`
- 00:43 to 00:53: `Personalized mental health care`
- 00:53 to 00:56: `Telehealth across MA • RI • NY • CO • AZ`
- 00:56 to 01:00: `Helping you find comfort, peace of mind, and hope.` plus `thehopewellnesscenter.com`

Animate type with masked reveals, line by line timing, and gentle tracking shifts. Do not bounce text or place all copy in rounded rectangles.

## Voiceover

Use a warm, grounded, reassuring adult voice with natural pauses. Avoid an overly polished announcer delivery.

> When life feels heavy, care should feel human. A moment to breathe. A place to reflect. Gentle support that meets you where you are. At The Hope Wellness Center, personalized mental health care is built around compassion, trust, and real clinical expertise. Through telehealth, our team supports patients across Massachusetts, Rhode Island, New York, Colorado, and Arizona. Whether you are seeking medication management, therapy, or a thoughtful psychiatric evaluation, you do not have to take the next step alone. Find comfort. Find peace of mind. Find hope. The Hope Wellness Center.

If a licensed voice is not available, produce a polished music and text version rather than using a noticeably artificial placeholder voice in the final export.

## Sound design

- Music: 70 to 76 BPM, airy piano, warm pads, very light organic percussion, no lyrics
- Keep music emotionally uplifting without becoming corporate or cinematic trailer music
- Add subtle breath swells, soft leaf movement, a quiet journal pencil or page sound, gentle fabric or mat movement, soft footsteps, and restrained volleyball taps
- Transitions may use low volume airy whooshes, never sharp impacts
- Duck music 5 to 7 dB under voiceover
- End with a clean, warm resolve and 8 to 12 frames of natural tail

## Editorial guardrails

- This practice is telehealth only and serves Massachusetts, Rhode Island, New York, Colorado, and Arizona
- Supported service language includes psychiatric care, therapy, medication management, and psychiatric evaluation
- Do not claim a cure, guaranteed result, immediate access, or universal insurance acceptance
- Do not add patient testimonials, star ratings, before and after claims, medication imagery, or crisis imagery
- Do not add new people or generated illustrations that could drift away from the approved kit
- Keep any call to action invitational, not urgent or fear based

## Implementation guidance

Use the strongest reliable video stack available in the repository or environment. Remotion is preferred for a reproducible programmatic build, but a clean FFmpeg, After Effects, or equivalent implementation is acceptable. Keep all source references relative to this folder. Do not hotlink assets.

For each scene, design the settled frame first, then animate into it. Motion should complete within its scene duration. Use overlaps only to create the planned transition, not to hide timing errors.

If the render system supports depth maps or masks, generate them locally from the supplied images and retain those derivative files. Do not replace the original illustrations. If depth generation introduces artifacts, fall back to clean parallax using duplicated full frames and geometric masks.

## Required QA before completion

1. Confirm the export is 1080 by 1920, 30 fps, and exactly 1,800 frames.
2. Confirm every file from `assets/01` through `assets/11` appears visibly for at least 2.5 seconds.
3. Confirm the exact `assets/00-hope-wellness-logo.png` appears at the end and remains readable for at least 2.5 seconds.
4. Confirm no face, hand, limb, dog, or volleyball is visibly warped by segmentation or depth effects.
5. Confirm all text is inside safe margins and readable on a phone.
6. Confirm the five state abbreviations are correct: MA, RI, NY, CO, AZ.
7. Confirm the URL is exactly `thehopewellnesscenter.com`.
8. Confirm audio does not clip and voiceover remains intelligible.
9. Watch the full render once at normal speed and once muted.
10. Save a final contact sheet or six frame review strip beside the MP4.

When complete, report the final MP4 path, exact duration, resolution, fps, file size, and any deliberate deviations from this brief.
