# Sanitized distribution readiness

Status: ready for the parent publisher's independent verification as an EXPERIMENTAL DEBUG PRE-RELEASE, not a production or legally guaranteed release. No repository, release or artifact was uploaded.

## Final artifact

- Separate release attachment: `minicpm-v47-android-debug.apk`.
- Exact size: 23,738,393 bytes.
- SHA-256: `824b73e62a2f5b994a092444f33b4c073eeab69545d80ea24859eb56a363e445`.
- Package `com.tianchi.minicpmv.v47debug`, version `2.5-v47-1b-debug`, code 17, minimum API 24, target API 36, arm64-v8a, debuggable=true.
- Generic Android Debug certificate; apksigner passes with v2=true. v1/v3/v3.1/v4=false, as explicitly recorded in VERIFICATION.json. No production signing.

## Actually executed

- Incremental Gradle assembleDebug and testDebugUnitTest: PASS. Three JVM tests, zero failures/errors/skips.
- Compiled native-prefix execution plus text/one-image lifetime/bounds/projector/backend and asset-exclusion/UI static regression contracts: PASS.
- Both text-only patches checked AND applied to freshly extracted archives at the documented exact upstream pins. Integration check executed in the reconstructed combined source tree: PASS.
- Both default voice files absent from APK; no *.wav/ref_audios member or RIFF/WAVE file payload. Neither patch contains a Git binary patch. Existing upstream recordings are not part of the public source set.
- All packaged license/NOTICE bytes match the distribution texts and reconstructed source: PASS.
- All 17 native libraries AArch64; PT_LOAD alignment at least 16 KB, native dependency closure and zipalign -P 16: PASS. Native bytes matched the prior canonical APK before replacement; no clean or forced native rebuild was requested.
- Entire final APK scanned: raw container plus all 951 decompressed files, 952 records and 53,331,029 inspected bytes. Zero configured local-path/credential-pattern matches, including null-interleaved strings. Full public source set scanned separately. These are heuristic scans, not proof that every possible secret is absent.
- lintDebug executed: FAIL, nine existing upstream errors and 71 warnings. No baseline or suppression introduced.

## Blockers resolved within scope

1. Unestablished WAV provenance: remove from distribution rather than claim ownership. Android packaging excludes *.wav and ref_audios in all patched variants. TTS default-reference buttons are disabled and an explicit warning appears; the shared loader guards before clearing a user's reference. Permitted user recording/no-reference synthesis remains separate and untested. The 1B text/one-image integration is unchanged.
2. Source-only attribution: exact official source JARs for all 64 resolved runtime artifacts reviewed, supplemented by versioned upstream repository material where feasible. Added coroutines 1.6.4 NOTICE and Kotlin 2.2.10 ThreeTenBP BSD-3-Clause text; retained additional conservative attributions and notices. Existing native license/NDK notice coverage retained. No known required attribution remains missing within this bounded review. See third-party-notices.txt and licenses/android-upstream-source-review.json for exact evidence and limitations.

## Remaining limitations and publisher gate

- Device install, native initialization, model download/load, text/one-image inference, TTS, POCO performance and runtime stability: NOT TESTED. Do not advertise runtime support as verified.
- Nine upstream lint errors, debug signing/debuggable mode, and incomplete device QA prevent a production-ready claim. Publisher must knowingly accept them for an experimental pre-release.
- This is a practical dependency license/attribution review, not an exhaustive historical source/ownership audit or legal guarantee. No new specific missing attribution blocker was identified. Model weights have separate terms and are not included or downloaded.
- Parent must independently verify the final artifact and distribution before upload. Publish only this selected source set and the verified APK, not the upstream/development workspace or private reports.

## Checksum verification

Run `sha256sum -c SHA256SUMS` inside this source distribution. Place the APK in its parent directory and run `sha256sum -c minicpm-public-dist/APK-SHA256SUMS` from that parent (adjust only the distribution directory name if renamed). SHA256SUMS covers every other file in this source set. APK-SHA256SUMS covers the separate APK attachment. Rebuilding reproduces source/configuration, not a guaranteed identical debug-signed APK.
