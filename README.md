# MiniCPM-V 4.7 1B Android — EXPERIMENTAL PRE-RELEASE

This distribution proposal adds the small dense MiniCPM-V 4.7 1B model to the existing Android demo. It is not an official upstream release, a production-signed application, or proof of on-device inference.

- Debug application ID: `com.tianchi.minicpmv.v47debug` (separate from the upstream release app).
- Version: `2.5-v47-1b-debug`, version code 17; arm64-v8a, Android API 24+.
- Generic Android Debug signing; debug mode is intentional. No production keys are included.
- Actual build, three JVM tests, native-prefix regression, signature, ZIP/ELF 16 KB alignment and complete APK privacy scans passed.
- POCO runtime/model inference: NOT TESTED. No model weights are bundled or downloaded during the build.
- Lint is NOT green: nine existing upstream errors and 71 warnings remain. Do not interpret this as production readiness.

## Contents

`android-integration.patch` contains tracked integration changes and relevant new source, tests and license assets. `native-compatibility.patch` applies inside the pinned native submodule. `scripts/` contains runnable integration, APK and privacy checks. `licenses/` and `third-party-notices.txt` contain the runtime license inventory and actual texts.

See BUILD.md for reproducible source commands. Local build paths are mapped during compilation; NDK r27 OpenMP debug-location strings additionally require native `-g0`. The debug app identity and inference code remain unchanged. No binary string patching is used.

## Publication review and TTS limitations

Both upstream default reference WAV files are excluded during packaging with Android's asset ignore pattern (`*.wav:ref_audios`); this setting also applies to any other build variant made from this patched source. No voice WAV bytes or binary voice patches are included in this distribution. TTS displays an explicit unavailable warning and disables both default-reference buttons when those assets are absent; its shared preset loader also guards before clearing a user reference. Recording a permitted reference and no-reference synthesis remain separate, untested upstream TTS features. MiniCPM-V 4.7 1B text/one-image inference does not use those TTS assets. Do not publish a full upstream checkout containing the excluded recordings.

The practical review covers 64 resolved runtime artifacts, their exact official source JARs, matching versioned upstream license directories/trees where feasible, and the existing compiled native inventory. Required source-only coroutines NOTICE and Kotlin ThreeTenBP copyright/BSD terms are now included, along with conservative source attributions and supplemental texts. No known missing attribution remains within that scope. Evidence and limitations (including historical AndroidX repository coverage and non-exhaustive Kotlin trees) are in `licenses/android-upstream-source-review.json` and `third-party-notices.txt`. This is not a legal guarantee or exhaustive ownership audit.

The previous WAV-distribution and unperformed source-NOTICE review blockers are resolved for this sanitized experimental distribution only. Device runtime/inference and production readiness remain unverified; parent verification and explicit publisher acceptance of debug signing and lint failures are still required. Nothing has been published.

Root application and native submodule declare MIT. Runtime and supplemental licenses include Apache-2.0, BSD-2-Clause/BSD-3-Clause, Boost-1.0, MIT/MIT-0, and LLVM Apache-2.0 exceptions with legacy runtime notices. The full component-by-component evidence, resolved artifact hashes and limitations are in third-party-notices.txt and licenses/runtime-license-inventory.json. Model weights have separate publisher terms and are outside these notices.

See READINESS.md and VERIFICATION.json for the final factual checks and remaining publisher gate. SHA256SUMS covers this source set; APK-SHA256SUMS covers the separate APK attachment. These hashes identify the delivered files, not a guarantee of byte-identical builds.

## Device smoke test (not yet executed)

Install as a separate debug app without uninstalling the existing release. Select `MiniCPM-V-4.7 1B (Q4_K_M)` explicitly (the original default is unchanged), then download its model and projector on the device. Test text, one image inside the user turn, clear/cancel, model switching, failed-projector cleanup and offline restart. Video remains limited to the existing 4.6 path. Record native initialization, crashes, page size, RAM and performance before claiming runtime support.

No repository, release or artifact has been uploaded by the builder. Publish only this reviewed distribution set and the verified APK, not a complete development workspace, caches, signing material or private build reports.
