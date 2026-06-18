# PROMPT — Video Editing Notes

Write me new notes on Video Editing in a new directory such that it explains each of the term below in beginner friendly language.

For each term:
- Write real world editing example
- ASCII diagram if applicable
- Add gotchas and practical context
- Add production scenario based FAQ

Additionally, after the glossary, write **2 full project case studies** (described at the bottom) with workflow, tool settings, export configs, and lessons learned.

Write me a markdown file with index at the starting, create it by yourself after analysing the content. If required divide the notes generation into batches and maintain a batch file to continue from next batch if context window is finished.

Also make the notes as short as possible without degrading quality and without degrading beginner friendly language.

---

## PART 1 — Complete Video Editing Glossary

### Batch 1 — Fundamentals & Formats
Video Editing Overview
Non-Linear Editing (NLE)
Timeline
Tracks (Video, Audio, Adjustment)
Playhead / Scrubber
In Point / Out Point
Frame
Frame Rate (24, 25, 30, 60, 120 fps)
Resolution (720p, 1080p, 1440p, 4K, 8K)
Aspect Ratio (16:9, 9:16, 4:3, 1:1, 21:9)
Pixel Aspect Ratio (PAR) vs Display Aspect Ratio (DAR)
Interlaced vs Progressive (1080i vs 1080p)
Codec (H.264, H.265/HEVC, ProRes, DNxHR, VP9, AV1)
Container (MP4, MOV, MKV, AVI, WebM)
Bitrate (CBR vs VBR)
Bit Depth (8-bit vs 10-bit vs 12-bit)
Chroma Subsampling (4:4:4, 4:2:2, 4:2:0)
Color Space (Rec.709, Rec.2020, sRGB, DCI-P3)
HDR vs SDR
RAW Video

### Batch 2 — Editing Software & Workspace
DaVinci Resolve (Free vs Studio)
Adobe Premiere Pro
Final Cut Pro
CapCut (Desktop & Mobile)
Kdenlive / Shotcut (Open Source)
Media Pool / Project Panel
Source Monitor / Program Monitor
Timeline Panel
Inspector / Effect Controls
Bins / Folders (Organizing Media)
Proxy Workflow (Editing Large Files Smoothly)
Project Settings (Timeline Resolution, FPS)
Auto-Save & Project Versioning
Keyboard Shortcuts (Essential Editing Shortcuts)
Workspace Customization

### Batch 3 — Cuts & Transitions
Cut (Hard Cut)
J-Cut (Audio leads video)
L-Cut (Video leads audio)
Jump Cut
Match Cut
Smash Cut
Cross Dissolve / Fade
Dip to Black / Dip to White
Wipe
Slide / Push
Whip Pan Transition
Zoom Transition
Morph Cut (Premiere Pro)
Speed Ramp Transition
Invisible Cut
Luma / Stinger Transition
When to Use vs When NOT to Use Transitions

### Batch 4 — Audio Editing
Audio Waveform
Sample Rate (44.1 kHz, 48 kHz, 96 kHz)
Audio Bit Depth (16-bit, 24-bit)
Mono vs Stereo vs Surround (5.1, 7.1)
Audio Levels (dB, LUFS, Peak vs RMS)
Loudness Standards (YouTube: -14 LUFS, Broadcast: -24 LUFS)
Gain / Volume
Normalization (Peak vs Loudness)
Compression (Audio Compressor)
EQ (Equalization — Low, Mid, High)
Noise Reduction / Noise Gate
De-Esser
Reverb & Delay
Audio Ducking (Lower music during speech)
Audio Sync (Waveform Matching, Timecode)
ADR (Automated Dialogue Replacement)
Foley & Sound Effects
Music Licensing (Royalty-Free, Creative Commons, Sync License)
Audio Formats (WAV, FLAC, MP3, AAC, OGG)

### Batch 5 — Color Correction & Grading
Color Correction vs Color Grading
Primary Correction (Lift, Gamma, Gain)
Secondary Correction (Qualifier / Mask)
Color Wheels / Color Bars
Scopes (Waveform, Vectorscope, Histogram, Parade)
White Balance / Color Temperature
Exposure (Highlights, Shadows, Midtones)
Contrast & Curves
Saturation vs Vibrance
Hue vs Saturation vs Luminance (HSL)
LUT (Look-Up Table) — Technical vs Creative
Log Footage (S-Log, C-Log, V-Log, BRAW)
ACES (Academy Color Encoding System)
Color Management (DaVinci Wide Gamut)
Node-Based Grading (DaVinci Resolve)
Power Windows / Masks
Tracking (Color Correction Tracking)
Skin Tone Correction
Color Matching Between Clips
Legal Levels (Broadcast Safe)

### Batch 6 — Effects & Motion Graphics
Keyframing (Position, Scale, Rotation, Opacity)
Bezier Curves / Ease In / Ease Out
Speed Ramping / Time Remapping
Slow Motion & Fast Motion
Reverse Clip
Freeze Frame
Ken Burns Effect (Pan & Zoom on Still Image)
Picture-in-Picture (PiP)
Split Screen
Green Screen / Chroma Key
Rotoscoping
Masking (Shape, Pen, Luminance)
Motion Tracking
Stabilization (Warp Stabilizer)
Text & Titles (Lower Thirds, End Cards)
Animated Typography
Blur (Gaussian, Directional, Radial)
Lens Flare / Light Leaks / Film Grain
Particle Effects
3D Text & Logo Animation

### Batch 7 — Export & Delivery
Export Settings (Resolution, FPS, Codec, Bitrate)
Render vs Export
Encoding (Single Pass vs Two Pass)
YouTube Export Settings (Recommended)
Instagram / TikTok / Shorts Export (9:16, 1080×1920)
Broadcast Delivery (ProRes, DNxHR)
Streaming Delivery (H.264, H.265)
Web Delivery (WebM, VP9, AV1)
Render Queue / Batch Export
Chapter Markers
Subtitles (SRT, VTT, Burnt-In vs Soft Subs)
Thumbnail Creation
Metadata (Title, Description, Tags)
Upload Optimization (Bitrate vs File Size)
Archival Format (Lossless Master)

---

## PART 2 — Project Case Studies

### Case Study 1: YouTube Video Production (10-Minute Tech Tutorial)

Create a complete YouTube tutorial video covering:
- Screen recording + face cam overlay
- B-roll integration
- Animated text callouts and lower thirds
- Background music with audio ducking
- Color correction for face cam
- Custom thumbnail creation
- Chapters and subtitles
- Optimized export for YouTube

**Cover in the case study:**
- Complete workflow diagram (ASCII): Shoot → Import → Rough Cut → Fine Cut → Audio Mix → Color → Graphics → Export
- Software: DaVinci Resolve (free), OBS for screen recording
- Timeline structure breakdown (intro, content, outro)
- Audio workflow: noise reduction, EQ, compression, ducking
- Color workflow: correction first, then creative grade
- Export settings: exact YouTube recommended settings
- Thumbnail workflow: screenshot + Photoshop/Canva
- File organization strategy
- Lessons learned & common beginner mistakes

### Case Study 2: Short-Form Content Pipeline (30 Instagram Reels in a Week)

Create a batch production pipeline for short-form content:
- Film 5 long-form clips → cut into 30 short clips
- Vertical format (9:16) with captions
- Hook text in first 3 seconds
- Trending audio integration
- Consistent brand template (colors, fonts, lower thirds)
- Batch export with correct settings per platform

**Cover in the case study:**
- Pipeline diagram (ASCII): Film → Selects → Cut → Caption → Brand → Export → Schedule
- Software: CapCut (batch) + DaVinci Resolve (hero edits)
- Batch editing workflow: template-based editing, preset effects
- Auto-captions: tools comparison (CapCut, Descript, Premiere)
- Platform-specific export: Instagram, TikTok, YouTube Shorts
- Scheduling: Buffer, Later, Meta Business Suite
- Content repurposing strategy
- Lessons learned & production efficiency tips
