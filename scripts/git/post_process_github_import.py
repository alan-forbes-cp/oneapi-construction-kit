#!/usr/bin/env python

import re
import shlex # does this handle corresponding windows command lines ??
import yaml

def verbose(str):
    if True: # replace with cl option
       print(str)

def print_preamble():
    print("""
env:
  CXXCompiler: llvm_install/bin/clang++
steps:
# checkout to code directory
- name: Checkout repo
  uses: actions/checkout@v4.1.0
  with:
    path: code
# copy .github to workspace top level
- run: cp -R code/.github .github
# setup ubuntu now includes vulcan sdk
- name: setup-ubuntu
  # installs tools, ninja, installs llvm and sets up sccache
  uses:  ./.github/actions/setup_ubuntu_build
  with:
    llvm_version: 17
    llvm_build_type: RelAssert
 - run: pwd && ls -al""")

def ignore(substring):
    ignore_list = [ re.compile("python"),
                    re.compile("-u"),
                    re.compile(".*scripts/build.py"),
                    re.compile("-GNinja"), # hard-wired in Github build action  
                    re.compile("--verbose"),
                    re.compile("--clean"),
                    re.compile("-Bbuild"), # build dir is explicity set below
                  ]
    return any(ignore_regex.match(substring) for ignore_regex in ignore_list)

def split_define(dsetting):
    dsplit = dsetting.split('=', 1)
    return dsplit[0], dsplit[1]

def translate(command):
    ignore_arg = False
    got_option = False
    unknown_option = False
    set_build_dir = False
    command_buffer_is_set = False # should only be set once

    print("""
# call build ock action - overwriting any defaults
- name: build ock
  uses: ./.github/actions/do_build_ock
  with: 
    path: $GITHUB_WORKSPACE/code
    install_dir: $GITHUB_WORKSPACE/install
    llvm_install_dir: $GITHUB_WORKSPACE/llvm_install""")

    for substr in shlex.split(command):
       if ignore(substr):
          verbose("     # Ignoring string '" + substr + "'")
       elif ignore_arg:
          verbose("     # - Ignoring arg '" + substr + "'")
          ignore_arg = False
          got_option = False
       elif substr.startswith('-D'):
          #print(substr)
          #print("  # -D option")
          dvar, darg = split_define(substr)
          if substr.startswith('-DCA_CL_ENABLE_ICD_LOADER='):
             verbose("     # Ignoring option '" + substr + "'") # hard-wired "ON" in Github build action 
          elif substr.startswith('-DCA_CL_DISABLE_UNITCL_VECZ_CHECKS='):
             verbose("     # Translating '" + substr + "'")
             print("    disable_unitcl_vecz_checks: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_OFFLINE_KERNEL_TESTS='):
             verbose("     # Translating '" + substr + "'")
             print("    offline_kernel_tests: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_RVV_SCALABLE_VECZ_CHECK='):
             verbose("     # Translating '" + substr + "'")
             print("    enable_rvv_scalable_vecz_check: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_RVV_SCALABLE_VP_VECZ_CHECK='):
             verbose("     # Translating '" + substr + "'")
             print("    enable_rvv_scalable_vp_vecz_check: " + darg)
          elif substr.startswith('-DCA_ENABLE_API='):
             verbose("     # Translating '" + substr + "'")
             print("    enable_api: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_MUX_COMPILER_DIRS='):
             verbose("     # Translating '" + substr + "'")
             print("    external_compiler_dirs: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_ONEAPI_CON_KIT_DIR='):
             verbose("     # Translating '" + substr + "'")
             print("    oneapi_con_kit_dir: " + darg)
          elif substr.startswith('-DCA_MUX_COMPILERS_TO_ENABLE='):
             verbose("     # Translating '" + substr + "'")
             print("    mux_compilers_enable: " + darg)
          elif substr.startswith('-DCA_MUX_TARGETS_TO_ENABLE='):
             verbose("     # Translating '" + substr + "'")
             print("    mux_targets_enable: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_REFSI_TUTORIAL_HAL_DIR='):
             verbose("     # Translating '" + substr + "'")
             print("    refsi_tutorial_hal_dir: " + darg)
          elif substr.startswith('-DCA_REFSI_TUTORIAL_ENABLED='):
             verbose("     # Translating '" + substr + "'")
             print("    refsi_tutorial_enabled: " + darg)
          elif substr.startswith('-DCA_RISCV_ENABLED='):
             verbose("     # Translating '" + substr + "'")
             print("    riscv_enabled: " + darg)
          elif substr.startswith('-DHAL_DESCRIPTION='):
             verbose("     # Translating '" + substr + "'")
             print("    hal_description: " + darg)
          elif substr.startswith('-DHAL_REFSI_SOC='):
             verbose("     # Translating '" + substr + "'")
             print("    hal_refsi_soc: " + darg)
          elif substr.startswith('-DHAL_REFSI_THREAD_MODE='):
             verbose("     # Translating '" + substr + "'")
             print("    hal_refsi_thread_mode: " + darg)
          elif substr.startswith('-DCA_ENABLE_HOST_IMAGE_SUPPORT='):
             verbose("     # Translating '" + substr + "'")
             print("    host_image: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTIN_KERNEL='):
             verbose("     # Translating '" + substr + "'")
             print("    debug_support: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTINS_EXTENSION='):
             verbose("     # Translating '" + substr + "'")
             print("    host_enable_builtins: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_FP16='):
             verbose("     # Translating '" + substr + "'")
             print("    host_fp16: " + darg)
          elif substr.startswith('-DCA_ASSEMBLE_SPIRV_LL_LIT_TESTS_OFFLINE='):
             verbose("     # Translating '" + substr + "'")
             print("    assemble_spirv_ll_lit_test_offline: " + darg)
          elif substr.startswith('-DOCL_EXTENSION_cl_intel_unified_shared_memory='):
             verbose("     # Translating '" + substr + "'")
             print("    usm: " + darg)
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr + "'")
                print("    command_buffer: " + darg)
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer_mutable_dispatch='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr + "'")
                print("    command_buffer: " + darg)
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DCA_USE_LINKER='):
             verbose("     # Translating '" + substr + "'")
             print("    use_linker: " + darg)
          else:
             print("     # ERROR: '" + substr + "' IS UNKNOWN'")
             unknown_option = True
          if not unknown_option:
             got_option = True
          unknown_option = False
       elif substr.startswith('-'):
          #print(substr)
          #print("  # - option")
          if substr == "--build_type":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    build_type: ", end='')
          elif substr == "--arch":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    arch: ", end='')
          elif substr == "--compiler":
             verbose("     # Translating '" + substr + "'")
             # $CXXCompiler needs added as a new Github env var
             print("    extra_flags: $GITHUB_WORKSPACE/$Compiler $GITHUB_WORKSPACE/$CXXCompiler")  
             ignore_arg = True
          elif substr == "--artefact_name":
             verbose("     # Ignoring option '" + substr + "'") # needed?
             ignore_arg = True
          elif substr == "--target":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    build_targets: ", end='')
          elif substr == "--binary_dir":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    build_dir: $GITHUB_WORKSPACE/", end='')
             set_build_dir = True
          elif substr == "--offline_only":
             verbose("     # Translating '" + substr + "'")
             print("    runtime_compiler_enabled: OFF")
             print("    enable_api: cl")
             print("    assemble_spirv_ll_lit_test_offline: ON")
          elif substr == "--external_clc":
             verbose("     # Translating '" + substr + "'")
             print("    external_clc: ", end='')
          elif substr == "--source_dir":
             verbose("     # Ignoring option '" + substr + "'") # needed?
             ignore_arg = True
          else:
             print("     # ERROR: '" + substr + "' IS UNKNOWN'")
             unknown_option = True
          if not unknown_option:
             got_option = True
          unknown_option = False
       else: # its an arg to a previous option else orphaned arg (likely 'import' tool added whitespace)
          if got_option:
             print(substr)
          else:
             print("ERROR: '" + substr + "' IS AN ORPHANED ARG")
          got_option = False

    if not set_build_dir:
       print("""    build_dir: $GITHUB_WORKSPACE/build""")

def check_for_build_py(command):
    if re.search(".*python.*build\.py.*", command):
       print("\n# -------- build.py --------")
       #print(command)
       #print(shlex.split(command))
       translate(command)
    
def main():
    with open('/home/alan/github/oneapi-construction-kit-alan/.github/workflows/ci-github-mrexport.yml', 'r') as file:
       try:
          content = yaml.safe_load(file)
       except yaml.YAMLError as e:
          print(e)
    #print(yaml.dump(content))
    for jobname in content['jobs']:
       print("\n# ======== " + jobname + " ========")
       print("\n# -------- preamble --------")
       print_preamble()
       job = content['jobs'][jobname]
       for step in job['steps']:
          if command := step.get('run'):
             if type(command) is str:
                check_for_build_py(command)
             elif type(command) is list:
                for subcommand in command:
                   check_for_build_py(subcommand)
             else:
                print("ERROR: UNKNOWN 'run' TYPE: ", type(command))
       
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
