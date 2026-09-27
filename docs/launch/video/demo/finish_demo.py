"""Finish the rendered demo: put the lossless mix back in, pick the poster, attach it, cut the stage version.

Input : build/demo_render.mp4 (from `npx hyperframes@0.8.79 render --quality delivery --output ../build/demo_render.mp4`
        in composition/) and build/demo_mix.wav (from build_demo.py)
Output: demo.mp4        full walkthrough, poster attached as cover art (no poster flash in frame 0)
        demo_stage.mp4  stage cut: hook + approval-to-end (about 109 s), same poster
        demo.jpg        poster (also use it as <video poster> in the deck)
Usage : python finish_demo.py [poster_time_seconds]
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "build", "demo_render.mp4")
OUT = os.path.join(HERE, "demo.mp4")
STAGE = os.path.join(HERE, "demo_stage.mp4")
JPG = os.path.join(HERE, "demo.jpg")
MIX = os.path.join(HERE, "build", "demo_mix.wav")
POSTER_T = float(sys.argv[1]) if len(sys.argv) > 1 else 70.0
# stage cut: hook until HOOK_END, then from APPROVAL_START (just before "Before anything happens") to the end
HOOK_END = 7.3
APPROVAL_START = 47.7
PAPER = "0xF7F4EC"


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def check(r):
    if r.returncode:
        print(r.stderr[-3000:])
        sys.exit(1)


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
    I = TP = None
    sect = None
    for line in r.stderr.splitlines():
        s = line.strip()
        if s.startswith("Integrated loudness"):
            sect = "I"
        elif s.startswith("True peak"):
            sect = "TP"
        elif s.startswith("I:") and sect == "I":
            I = float(s.split()[1])
        elif s.startswith("Peak:") and sect == "TP":
            TP = float(s.split()[1])
    return I, TP


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def attach_poster(src, dst):
    check(run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", JPG, "-map", "0:v:0", "-map", "0:a:0", "-map", "1:v:0",
               "-c", "copy", "-disposition:v:0", "default", "-disposition:v:1", "attached_pic",
               "-movflags", "+faststart", dst]))


def main():
    I, TP = loudness(RAW)
    print(f"raw render: {duration(RAW):.2f}s, {I} LUFS, true peak {TP} dBTP")
    # always use the lossless mix from build_demo.py (the renderer may resample or re-level it); video stream copied
    fixed = os.path.join(HERE, "build", "demo_remux.mp4")
    check(run(["ffmpeg", "-y", "-v", "error", "-i", RAW, "-i", MIX, "-map", "0:v:0", "-map", "1:a:0",
               "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", fixed]))
    print("remuxed with build/demo_mix.wav:", loudness(fixed))
    check(run(["ffmpeg", "-y", "-v", "error", "-ss", f"{POSTER_T}", "-i", fixed, "-frames:v", "1", "-q:v", "2", JPG]))
    attach_poster(fixed, OUT)
    I, TP = loudness(OUT)
    print(f"final demo.mp4: {duration(OUT):.2f}s, {I} LUFS, true peak {TP} dBTP, {os.path.getsize(OUT)/1e6:.1f} MB")

    # stage cut (re-encoded once, from the remux, not from the poster file)
    end = duration(fixed)
    fc = (f"[0:v:0]trim=0:{HOOK_END},setpts=PTS-STARTPTS,fade=t=out:st={HOOK_END - 0.25:.2f}:d=0.25:color={PAPER}[v0];"
          f"[0:a:0]atrim=0:{HOOK_END},asetpts=PTS-STARTPTS,afade=t=out:st={HOOK_END - 0.4:.2f}:d=0.35[a0];"
          f"[0:v:0]trim={APPROVAL_START}:{end:.3f},setpts=PTS-STARTPTS[v1];"
          f"[0:a:0]atrim={APPROVAL_START}:{end:.3f},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.08[a1];"
          f"[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    tmp = os.path.join(HERE, "build", "demo_stage_noposter.mp4")
    check(run(["ffmpeg", "-y", "-v", "error", "-i", fixed, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "192k", tmp]))
    attach_poster(tmp, STAGE)
    I, TP = loudness(STAGE)
    print(f"stage cut demo_stage.mp4: {duration(STAGE):.2f}s, {I} LUFS, true peak {TP} dBTP, {os.path.getsize(STAGE)/1e6:.1f} MB")


if __name__ == "__main__":
    main()
