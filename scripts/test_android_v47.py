#!/usr/bin/env python3
"""Static integration contracts; does not claim inference or download weights."""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'MiniCPM-V-demo-Android/app'
JNI = (APP / 'src/main/cpp/llama_jni.cpp').read_text()
IOS = (ROOT / 'MiniCPM-V-demo/MTMDWrapper/Bridge/MBMtmd.mm').read_text()
# Compile and exercise the actual native prefix function, not a rewritten copy.
prefix_match = re.search(r'static const char \* assistant_turn_prefix\(\) \{.*?\n\}', JNI, re.S)
expected_match = re.search(r'static const char \* chatml_nothink_header\(\) \{\s*return (.*?);', IOS, re.S)
assert prefix_match and expected_match
prefix = prefix_match[0]
expected = expected_match[1]
with tempfile.TemporaryDirectory() as tmp:
    source = Path(tmp) / 'prefix.cpp'
    binary = Path(tmp) / 'prefix'
    source.write_text('#include <cassert>\n#include <string>\nstatic int g_minicpmv_version;\nstatic bool g_enable_thinking;\n' + prefix + '\nint main() {\n'
        + 'for (bool thinking : {false, true}) { g_enable_thinking=thinking; g_minicpmv_version=47; assert(std::string(assistant_turn_prefix())==' + expected + '); }\n'
        + 'for (int version : {46,460,461}) { g_minicpmv_version=version; g_enable_thinking=false; assert(std::string(assistant_turn_prefix())==' + expected + '); g_enable_thinking=true; assert(std::string(assistant_turn_prefix())=="<|im_start|>assistant\\n<think>\\n"); }\n'
        + 'g_minicpmv_version=5; assert(std::string(assistant_turn_prefix())=="<|im_start|>assistant\\n");\n}\n')
    subprocess.run(['c++', '-std=c++17', '-Wall', '-Werror', str(source), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
image = JNI.split('LlamaEngine_prefillImage(', 1)[1].split('LlamaEngine_fullReset', 1)[0]
assert image.index('if (g_minicpmv_version == 47)') < image.index('mtmd_tokenize(')
assert 'g_pending_image.reset(bitmap)' in image
assert image.index('if (g_pending_image)') < image.index('g_pending_image.reset()')
assert 'jimage_size > env->GetArrayLength(jimage_data)' in image
user = JNI.split('LlamaEngine_processUserPrompt(', 1)[1].split('static bool is_valid_utf8', 1)[0]
assert user.index('"<|im_start|>user\\n"') < user.index('mtmd_default_marker()') < user.index('"<|im_end|>\\n"')
assert 'g_pending_image ? bitmaps : nullptr' in user
assert 'g_pending_image ? 1 : 0' in user
assert user.index('mtmd_tokenize(') < user.index('g_pending_image.reset()')
reset = JNI.split('static void reset_long_term_states', 1)[1].split('static const char * assistant_turn_prefix', 1)[0]
assert 'g_pending_image.reset()' in reset
unload = JNI.split('LlamaEngine_unload(', 1)[1]
assert 'g_minicpmv_version = 0' in unload
engine = (APP / 'src/main/java/com/example/minicpm_v_demo/LlamaEngine.kt').read_text()
assert 'MiniCPM-V 4.7 1B requires its vision projector' in engine
assert 'Failed to load MiniCPM-V 4.7 1B projector' in engine
load_error = engine.split('Error loading model', 1)[1].split('val isVisionSupported', 1)[0]
assert load_error.index('unload()') < load_error.index('LlamaState.Error(e)')
assert 'throw RuntimeException("Failed to process user prompt (code: $result)")' in engine
build = (APP / 'build.gradle.kts').read_text()
assert build.count('-DANDROID_SUPPORT_FLEXIBLE_PAGE_SIZES=ON') == 2
assert 'inputs.property("flexiblePageSizes", true)' in build
assert build.count('-DCMAKE_C_FLAGS=$nativePrivacyFlags') == 2
assert build.count('-DCMAKE_CXX_FLAGS=$nativePrivacyFlags') == 2
assert build.count('-DCMAKE_ASM_FLAGS=$nativePrivacyFlags') == 2
assert '-ffile-prefix-map=' in build and '-fdebug-prefix-map=' in build
assert 'postfix = " -g0"' in build
assert 'inputs.property("nativePrivacyFlags", nativePrivacyFlags)' in build
assert ':*.wav:ref_audios"' in build
tts = (APP / 'src/main/java/com/example/minicpm_v_demo/TtsActivity.kt').read_text()
assert 'btnPresetFemale.isEnabled = false' in tts and 'btnPresetMale.isEnabled = false' in tts
assert '.setMessage(R.string.tts_presets_unavailable)' in tts
preset = tts.split('private fun selectPresetRefAudio(assetName: String)', 1)[1]
assert preset.index('assets.list("ref_audios").isNullOrEmpty()') < preset.index('referenceWavFile?.delete()')
native = ROOT / 'llama.cpp-omni'
assert 'llama_model_qwen35::build_arch_graph' in (native / 'src/models/qwen35.cpp').read_text()
assert 'PROJECTOR_TYPE_MINICPMV4_7' in (native / 'tools/mtmd/clip.cpp').read_text()
print('PASS: native prefix execution + deferred image/lifetime/bounds/projector/backend contracts')
