#!/usr/bin/env python

import re
import shlex # does this handle corresponding windows command lines ??
import yaml

def verbose(str):
    if True:
       print(str)

def ignore(substring):
    ignore_list = [ "python",
                    "-u",
                    "scripts/build.py",
                    "-GNinja", # hard-wired in Github build action  
                    "--verbose",
                    "--clean",
                  ]
    return substring in ignore_list

def translate(command):
    ignore_arg = False
    command_buffer_is_set = False # should only be set once

    print("""
# call build ock action - overwriting any defaults
- name: build ock
  uses: ./.github/actions/do_build_ock
  with: 
    build_dir: $GITHUB_WORKSPACE/build
    path: $GITHUB_WORKSPACE/code
    install_dir: $GITHUB_WORKSPACE/install
    llvm_install_dir: $GITHUB_WORKSPACE/llvm_install""")

    for substr in shlex.split(command):
       if ignore(substr):
          verbose("     # Ignoring string '" + substr + "'")
       elif ignore_arg:
          verbose("     # - Ignoring arg '" + substr + "'")
          ignore_arg = False
       elif substr.startswith('-D'):
          #print(substr)
          #print("  # -D option")
          if substr.startswith('-DCA_CL_ENABLE_ICD_LOADER='):
             verbose("     # Ignoring option '" + substr + "'") # hard-wired "ON" in Github build action 
          elif substr.startswith('-DCA_ENABLE_HOST_IMAGE_SUPPORT='):
             verbose("     # Translating '" + substr)
             print("    host_image: $Image")
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTIN_KERNEL=ON'):
             verbose("     # Translating '" + substr) # hard-wire to "ON" (for now?)
             print("    debug_support: ON")
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTINS_EXTENSION=ON'):
             verbose("     # Translating '" + substr) # hard-wire to "ON" (for now?)
             print("    host_enable_builtins: ON")
          elif substr.startswith('-DCA_HOST_ENABLE_FP16='):
             verbose("     # Translating '" + substr)
             print("    host_fp16: $FP16")
          elif substr.startswith('-DCA_ASSEMBLE_SPIRV_LL_LIT_TESTS_OFFLINE=OFF'):
             verbose("     # Translating '" + substr)
             print("    assemble_spirv_ll_lit_test_offline:: OFF")
          elif substr.startswith('-DOCL_EXTENSION_cl_intel_unified_shared_memory='):
             verbose("     # Translating '" + substr)
             print("    usm: $USM")
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr)
                print("    command_buffer: $CommandBuffer")
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer_mutable_dispatch='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr)
                print("    command_buffer: $CommandBuffer")
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DCA_USE_LINKER='):
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action 
          else:
             print("     # ERROR: '" + substr + " IS UNKNOWN'")
       elif substr.startswith('-'):
          #print(substr)
          #print("  # - option")
          if substr == "--build_type":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    build_type: ", end='')
          elif substr == "--arch":
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action
             ignore_arg = True
          elif substr == "--compiler":
             verbose("     # Translating '" + substr + "'")
             print("    c_compiler: $GITHUB_WORKSPACE/$Compiler")
             print("    cxx_compiler: $GITHUB_WORKSPACE/$CXXCompiler")  # this needs added as a new Github env var
             ignore_arg = True
          elif substr == "--artefact_name":
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action
             ignore_arg = True
          elif substr == "--target":
             verbose("     # Translating '" + substr + " <ARG>'")
             print("    build_targets: ", end='')
          elif substr == "--binary_dir":
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action
             ignore_arg = True
          elif substr == "--offline_only":
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action
          elif substr == "--external_clc":
             verbose("     # Ignoring option '" + substr + "'") # not yet supported in Github build action
             ignore_arg = True
          else:
             print("     # ERROR: '" + substr + " IS UNKNOWN'")
       else: # its an arg to a previous option
          print(substr)

def main():
    with open('ci-github-mrexport.yml', 'r') as file:
       try:
          content = yaml.safe_load(file)
       except yaml.YAMLError as e:
          print(e)
    #print(yaml.dump(content))
    for jobname in content['jobs']:
       print("\n======== " + jobname + " ========")
       job = content['jobs'][jobname]
       for step in job['steps']:
          if command := step.get('run'):
             if re.search(".*python.*build\.py.*", command):
                print("\n-------- build.py --------")
                #print(command)
                #print(shlex.split(command))
                translate(command)
       
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
