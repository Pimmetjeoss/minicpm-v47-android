#!/usr/bin/env python3
"""Verify real debug APK metadata, signature, ELF architecture/alignment and deps."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import tempfile
import zipfile

p = argparse.ArgumentParser()
p.add_argument('apk', type=Path)
p.add_argument('--sdk', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
bt = a.sdk / 'build-tools/36.0.0'
analyzer = a.sdk / 'cmdline-tools/latest/bin/apkanalyzer'
readelf = a.sdk / 'ndk/27.0.12077973/toolchains/llvm/prebuilt/linux-x86_64/bin/llvm-readelf'

def run(*args):
    return subprocess.check_output([str(x) for x in args], text=True, stderr=subprocess.STDOUT)

badging = run(bt / 'aapt', 'dump', 'badging', a.apk)
assert "name='com.tianchi.minicpmv.v47debug'" in badging
assert "versionName='2.5-v47-1b-debug'" in badging
assert "versionCode='17'" in badging
assert "sdkVersion:'24'" in badging
assert "launchable-activity: name='com.example.minicpm_v_demo.MainActivity'" in badging
assert "native-code: 'arm64-v8a'" in badging
assert "application-label:'MiniCPM-V 4.7 1B Debug'" in badging
manifest = run(analyzer, 'manifest', 'print', a.apk)
metadata = {k: run(analyzer, 'manifest', k, a.apk).strip() for k in
            ['application-id', 'version-name', 'version-code', 'min-sdk', 'target-sdk', 'debuggable']}
assert metadata['application-id'] == 'com.tianchi.minicpmv.v47debug'
assert metadata['debuggable'] == 'true'
signature = run(bt / 'apksigner', 'verify', '--verbose', a.apk)
assert 'Verified using v2 scheme (APK Signature Scheme v2): true' in signature
alignment = run(bt / 'zipalign', '-c', '-P', '16', '-v', '4', a.apk)
assert 'Verification successful' in alignment
libraries = []
with zipfile.ZipFile(a.apk) as z, tempfile.TemporaryDirectory() as tmp:
    names = [n for n in z.namelist() if n.startswith('lib/') and n.endswith('.so')]
    assert names and all(n.startswith('lib/arm64-v8a/') for n in names)
    assert not any(n.endswith('.gguf') for n in z.namelist())
    assert not any(n.lower().endswith('.wav') or 'ref_audios' in n.lower() for n in z.namelist()), 'Voice assets must not be packaged'
    assert not any(z.read(n)[:4] == b'RIFF' and z.read(n)[8:12] == b'WAVE' for n in z.namelist() if not n.endswith('/')), 'Renamed WAV payload'
    packaged = {Path(n).name for n in names}
    platform = {'libc.so', 'libm.so', 'libdl.so', 'liblog.so', 'libandroid.so', 'libz.so'}
    for name in names:
        data = z.read(name)
        assert data[:6] == b'\x7fELF\x02\x01', name
        assert struct.unpack_from('<H', data, 18)[0] == 183, name  # AArch64
        offset = struct.unpack_from('<Q', data, 32)[0]
        size, count = struct.unpack_from('<HH', data, 54)
        aligns = [struct.unpack_from('<Q', data, offset+i*size+48)[0]
                  for i in range(count) if struct.unpack_from('<I', data, offset+i*size)[0] == 1]
        assert aligns and all(v >= 16384 for v in aligns), (name, aligns)
        path = Path(tmp) / Path(name).name
        path.write_bytes(data)
        dynamic = run(readelf, '-d', path)
        needed = re.findall(r'Shared library: \[(.*?)\]', dynamic)
        assert set(needed) <= packaged | platform, (name, needed)
        libraries.append({'path': name, 'bytes': len(data), 'load_alignments': aligns, 'needed': needed})
    assert b'qwen35' in z.read('lib/arm64-v8a/libllama.so')
    assert b'minicpmv4_7' in z.read('lib/arm64-v8a/libmtmd.so')
    dex = b''.join(z.read(n) for n in z.namelist() if n.endswith('.dex'))
    for token in [b'minicpm-v-4_7-1b', b'MiniCPM-V-4.7-1B/MiniCPM-V-4_7-1B-Q4_K_M.gguf',
                  b'MiniCPM-V-4.7-1B/mmproj-model-f16.gguf']:
        assert token in dex, token

result = {'apk': str(a.apk.resolve()), 'bytes': a.apk.stat().st_size,
          'sha256': hashlib.sha256(a.apk.read_bytes()).hexdigest(),
          'metadata': metadata, 'launcher': 'com.example.minicpm_v_demo.MainActivity',
          'signature': signature, 'zipalign_16k': 'PASS', 'libraries': libraries,
          'model_catalogue_in_dex': 'PASS', 'gguf_weights_in_apk': False,
          'wav_or_ref_audios_in_apk': False,
          'runtime_model_tested': False, 'manifest': manifest}
a.output.write_text(json.dumps(result, indent=2))
print(json.dumps({k: v for k, v in result.items() if k not in ['libraries', 'manifest']}, indent=2))
print('PASS: all', len(libraries), 'libraries are AArch64, 16KiB aligned, with closed packaged/platform dependencies')
