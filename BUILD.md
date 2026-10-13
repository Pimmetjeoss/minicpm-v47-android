# Reproducible source build

These commands reproduce the source/configuration, not necessarily a byte-identical signed APK: debug certificates, ZIP timestamps and build metadata can differ. Use Linux, Python 3, a C++17 host compiler and existing Android tools. Do not run release signing tasks.

## Pinned inputs

- Application: https://github.com/OpenBMB/MiniCPM-V-Apps.git at `68f53d67a418dd6444659c39005dd5cc4097071c`.
- Native submodule: https://github.com/tc-mb/llama.cpp-omni.git at `96bbf61710d44421ea54e63f5194f9b17c20d877`.
- Temurin JDK 21.0.12.1+1; Gradle wrapper 9.3.1, AGP 9.1.1.
- Android SDK platform `android-36.1`, build-tools `36.0.0`, NDK `27.0.12077973`, CMake `4.1.2`; command-line tools providing apkanalyzer.
- KleidiAI 1.24.0 is resolved by pinned upstream CMake FetchContent; runtime artifact coordinates/hashes are inventoried in licenses/runtime-license-inventory.json.
- Wrapper checksum: `b266d5ff6b90eada6dc3b20cb090e3731302e553a27c5d3e4df1f0d76beaff06`.

## Checkout and apply

Run from a directory containing this distribution proposal. Set DIST to its absolute path using `pwd`, not a machine-specific path.

```sh
DIST="$PWD"
git clone https://github.com/OpenBMB/MiniCPM-V-Apps.git source
cd source
git checkout --detach 68f53d67a418dd6444659c39005dd5cc4097071c
git submodule update --init --recursive
test "$(git -C llama.cpp-omni rev-parse HEAD)" = 96bbf61710d44421ea54e63f5194f9b17c20d877
git apply --check "$DIST/android-integration.patch"
git apply "$DIST/android-integration.patch"
git -C llama.cpp-omni apply --check "$DIST/native-compatibility.patch"
git -C llama.cpp-omni apply "$DIST/native-compatibility.patch"
git diff --check
git -C llama.cpp-omni diff --check
```

## Build and checks

Set JAVA_HOME and ANDROID_HOME to your installed tools before running. Gradle's isolated user home prevents reading personal release-signing properties. Only generic debug signing is allowed for this experiment. A fresh checkout builds its own native outputs; compiler mappings apply to C, C++ and assembly in both normal and ARMv8.6 custom configurations. Incremental packaging updates do not require clean or forced native rebuilds.

```sh
: "${JAVA_HOME:?Set JAVA_HOME to JDK 21}"
: "${ANDROID_HOME:?Set ANDROID_HOME to the Android SDK}"
export JAVA_HOME ANDROID_HOME
export PATH="$JAVA_HOME/bin:$PATH"
export GRADLE_USER_HOME="$PWD/.gradle-user"
export CMAKE_BUILD_PARALLEL_LEVEL=2
python3 scripts/test_android_v47.py
cd MiniCPM-V-demo-Android
./gradlew :app:assembleDebug :app:testDebugUnitTest --no-daemon --max-workers=2 '-Dorg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8'
# Expected nonzero: nine existing lint errors, 71 warnings; no suppression.
./gradlew :app:lintDebug --no-daemon --max-workers=2 '-Dorg.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8'
cd ..
APK=MiniCPM-V-demo-Android/app/build/outputs/apk/debug/app-debug.apk
python3 scripts/verify_android_apk.py "$APK" --sdk "$ANDROID_HOME" --output apk-verification.json
python3 scripts/scan_public_artifact.py "$APK" --output apk-privacy-scan.json
"$ANDROID_HOME/build-tools/36.0.0/apksigner" verify --verbose --print-certs "$APK"
sha256sum "$APK"
```

Keep generated JSON reports, caches, `.cxx`, jniLibs, logs, local.properties and debug keystores out of public source trees. The scanner checks raw APK bytes and every decompressed ZIP member for local path and credential patterns, including null-interleaved strings. Heuristics cannot prove the absence of all possible secrets. ELF checks cover all 17 native libraries, dependencies, AArch64 and 16 KB PT_LOAD plus ZIP alignment; the DEX check covers the model ID and both download paths.

The inherited native Release optimization is used inside the debug APK. Prefix mapping preserves source checks/assertions. Native `-g0` removes NDK r27 OpenMP source-location strings that bypass prefix maps; no inference component or backend is disabled. libomp is the NDK's supplied runtime, not locally rebuilt source; every application-built native library is recompiled, with its prebuilt runtime dependency separately inspected.

The Android asset ignore pattern excludes both upstream reference voices and all WAV assets at packaging time; it applies to all variants from this patch. The verifier rejects *.wav/ref_audios entries and renamed RIFF/WAVE payloads. TTS shows an unavailable warning and disables default-reference buttons; recorded/no-reference TTS is retained but untested and separate from the 1B model. No upstream WAV is present in either patch. See README.md for review scope and limitations.

Runtime on POCO remains NOT TESTED. The prior WAV and unperformed source-NOTICE review blockers are resolved within this bounded scope, not a legal guarantee. Nine upstream lint errors and debug signing remain disclosed experimental limitations.
