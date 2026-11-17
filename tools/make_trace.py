#!/usr/bin/env python3
"""Rebuild the home-page seismogram (content/data/trace.yml) from real data.

    pip install obspy scipy
    python tools/make_trace.py

Downloads 80 minutes of IU.MAJO.10.BHZ (40 samples/s) recorded after the
2023-02-06 Mw 7.8 Kahramanmaras earthquake from the EarthScope FDSN service,
band-passes it, and reduces it to time-ordered min/max pairs per column.
Change the station or window with the constants below.
"""

import io
import urllib.request
from pathlib import Path

import numpy as np
import obspy
from scipy.signal import butter, sosfiltfilt

NET, STA, LOC, CHA = "IU", "MAJO", "10", "BHZ"
START, END = "2023-02-06T01:27:00", "2023-02-06T02:47:00"
BAND = (0.05, 8.0)      # Hz
POWER = 0.7             # amplitude compression, keeps the P wave visible
W, H, COLUMNS = 6000, 200, 3000

url = (
    "https://service.earthscope.org/fdsnws/dataselect/1/query"
    f"?net={NET}&sta={STA}&loc={LOC}&cha={CHA}&starttime={START}&endtime={END}"
)
with urllib.request.urlopen(url, timeout=60) as r:
    st = obspy.read(io.BytesIO(r.read()))
st.merge(fill_value=0)
tr = st[0]
fs = tr.stats.sampling_rate

x = tr.data.astype(float)
x -= x.mean()
n = int(0.01 * len(x))
taper = np.ones_like(x)
taper[:n] = np.hanning(2 * n)[:n]
taper[-n:] = np.hanning(2 * n)[n:]
x = sosfiltfilt(butter(2, BAND, btype="band", fs=fs, output="sos"), x * taper)
x /= np.abs(x).max()
y = np.sign(x) * np.abs(x) ** POWER

edges = np.linspace(0, len(y), COLUMNS + 1).astype(int)
pts = []
for i in range(COLUMNS):
    c = y[edges[i]:edges[i + 1]]
    lo, hi = int(np.argmin(c)), int(np.argmax(c))
    for k, j in enumerate(sorted((lo, hi))):
        pts.append((2 * i + k, round(H / 2 - c[j] * H / 2 * 0.95)))

steps = [f"{qx - px} {qy - py}" for (px, py), (qx, qy) in zip(pts, pts[1:])]
path = f"M{pts[0][0]} {pts[0][1]}l" + " ".join(steps)

out = Path(__file__).resolve().parent.parent / "content" / "data" / "trace.yml"
out.write_text(
    f"# Hero seismogram: {NET}.{STA}.{LOC}.{CHA} at {fs:g} samples/s, {START} to {END} UTC,\n"
    f"# band-passed {BAND[0]}-{BAND[1]} Hz, amplitude compressed as |x|^{POWER}, reduced to\n"
    f"# time-ordered min/max pairs in {COLUMNS} columns. Rebuild with tools/make_trace.py.\n"
    f'viewbox: "0 0 {W} {H}"\n'
    f'path: "{path}"\n',
    encoding="utf-8",
)
print(f"wrote {out} ({len(pts)} points, {len(path)} characters)")
