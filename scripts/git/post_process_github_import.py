#!/usr/bin/env python

import re
import shlex # does this handle corresponding windows command lines ??
import yaml
from yaml.resolver import Resolver

def verbose(str):
    if True: # replace with cl option
       add_to_translation(str)

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

translation_str = ""

def add_to_translation(string, newline=True):
    global translation_str
    if newline:
       translation_str += string + "\n"
    else:
       translation_str += string

def translate(command, build_type):
    ignore_arg = False
    got_option = False
    unknown_option = False
    set_build_dir = False
    command_buffer_is_set = False # should only be set once
    add_to_translation("""
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
             add_to_translation("    disable_unitcl_vecz_checks: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_OFFLINE_KERNEL_TESTS='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    offline_kernel_tests: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_RVV_SCALABLE_VECZ_CHECK='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    enable_rvv_scalable_vecz_check: " + darg)
          elif substr.startswith('-DCA_CL_ENABLE_RVV_SCALABLE_VP_VECZ_CHECK='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    enable_rvv_scalable_vp_vecz_check: " + darg)
          elif substr.startswith('-DCA_ENABLE_API='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    enable_api: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_MUX_COMPILER_DIRS='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    external_compiler_dirs: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_ONEAPI_CON_KIT_DIR='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    oneapi_con_kit_dir: " + darg)
          elif substr.startswith('-DCA_MUX_COMPILERS_TO_ENABLE='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    mux_compilers_enable: " + darg)
          elif substr.startswith('-DCA_MUX_TARGETS_TO_ENABLE='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    mux_targets_enable: " + darg)
          elif substr.startswith('-DCA_EXTERNAL_REFSI_TUTORIAL_HAL_DIR='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    refsi_tutorial_hal_dir: " + darg)
          elif substr.startswith('-DCA_REFSI_TUTORIAL_ENABLED='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    refsi_tutorial_enabled: " + darg)
          elif substr.startswith('-DCA_RISCV_ENABLED='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    riscv_enabled: " + darg)
          elif substr.startswith('-DHAL_DESCRIPTION='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    hal_description: " + darg)
          elif substr.startswith('-DHAL_REFSI_SOC='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    hal_refsi_soc: " + darg)
          elif substr.startswith('-DHAL_REFSI_THREAD_MODE='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    hal_refsi_thread_mode: " + darg)
          elif substr.startswith('-DCA_ENABLE_HOST_IMAGE_SUPPORT='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    host_image: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTIN_KERNEL='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    debug_support: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_BUILTINS_EXTENSION='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    host_enable_builtins: " + darg)
          elif substr.startswith('-DCA_HOST_ENABLE_FP16='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    host_fp16: " + darg)
          elif substr.startswith('-DCA_ASSEMBLE_SPIRV_LL_LIT_TESTS_OFFLINE='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    assemble_spirv_ll_lit_test_offline: " + darg)
          elif substr.startswith('-DOCL_EXTENSION_cl_intel_unified_shared_memory='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    usm: " + darg)
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr + "'")
                add_to_translation("    command_buffer: " + darg)
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DOCL_EXTENSION_cl_khr_command_buffer_mutable_dispatch='):
             if not command_buffer_is_set:
                verbose("     # Translating '" + substr + "'")
                add_to_translation("    command_buffer: " + darg)
                command_buffer_is_set = True # should only be set once
             else:
                verbose("     # Ignoring option '" + substr + "'")
          elif substr.startswith('-DCA_USE_LINKER='):
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    use_linker: " + darg)
          else:
             add_to_translation("     # ERROR: '" + substr + "' IS UNKNOWN'")
             unknown_option = True
          if not unknown_option:
             got_option = True
          unknown_option = False
       elif substr.startswith('-'):
          #print(substr)
          #print("  # - option")
          if substr == "--build_type":
             verbose("     # Translating '" + substr + " <ARG>'")
             # build_type is derived from job name suffix
             add_to_translation("    build_type: " + build_type, False)
             ignore_arg = True
          elif substr == "--arch":
             verbose("     # Translating '" + substr + " <ARG>'")
             add_to_translation("    arch: ", False)
          elif substr == "--compiler":
             verbose("     # Translating '" + substr + "'")
             # $CXXCompiler needs added as a new Github env var
             add_to_translation("    extra_flags: $GITHUB_WORKSPACE/$Compiler $GITHUB_WORKSPACE/$CXXCompiler")  
             ignore_arg = True
          elif substr == "--artefact_name":
             verbose("     # Ignoring option '" + substr + "'") # needed?
             ignore_arg = True
          elif substr == "--target":
             verbose("     # Translating '" + substr + " <ARG>'")
             add_to_translation("    build_targets: ", False)
          elif substr == "--binary_dir":
             verbose("     # Translating '" + substr + " <ARG>'")
             add_to_translation("    build_dir: $GITHUB_WORKSPACE/", False)
             set_build_dir = True
          elif substr == "--offline_only":
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    runtime_compiler_enabled: OFF")
             add_to_translation("    enable_api: cl")
             add_to_translation("    assemble_spirv_ll_lit_test_offline: ON")
          elif substr == "--external_clc":
             verbose("     # Translating '" + substr + "'")
             add_to_translation("    external_clc: ", False)
          elif substr == "--source_dir":
             verbose("     # Ignoring option '" + substr + "'") # needed?
             ignore_arg = True
          else:
             add_to_translation("     # ERROR: '" + substr + "' IS UNKNOWN'")
             unknown_option = True
          if not unknown_option:
             got_option = True
          unknown_option = False
       else: # its an arg to a previous option else orphaned arg (likely 'import' tool added whitespace)
          if got_option:
             add_to_translation(substr)
          else:
             print("ERROR: '" + substr + "' IS AN ORPHANED ARG")
          got_option = False

    if not set_build_dir:
       add_to_translation("""    build_dir: $GITHUB_WORKSPACE/build""")

def check_for_build_py(command, build_type):
    global translation_str
    translation_str = ""
    #if re.search(".*python.*build\.py.*", command):
    if re.search(".*scripts/build\.py.*", command):
       #print("\n# -------- build.py --------")
       #print(command)
       #print(shlex.split(command))
       translate(command, build_type)
       return translation_str
    return None
    
def lookup_key(sk, d, path=[]):
   # ...thank you Google ...
   # lookup the values for key(s) sk return as list the tuple (path with key, value, path)
   if isinstance(d, dict):
       for k, v in d.items():
           if k == sk:
               yield (d, v, path)
           for res in lookup_key(sk, v, path + [k]):
               yield res
   elif isinstance(d, list):
       for item in d:
           for res in lookup_key(sk, item, path + [item]):
               yield res

def main():
    # remove Yaml resolver entries for On/Off/Yes/No - treat as str not bool
    # ...thank you Google (again) ...
    for ch in "OoYyNn":
        if len(Resolver.yaml_implicit_resolvers[ch]) == 1:
            del Resolver.yaml_implicit_resolvers[ch]
        else:
            Resolver.yaml_implicit_resolvers[ch] = [x for x in
                    Resolver.yaml_implicit_resolvers[ch] if x[0] != 'tag:yaml.org,2002:bool']

    with open('/home/alan/github/oneapi-construction-kit-alan/.github/workflows/ci-github-mrexport.yml', 'r') as file:
       try:
          content = yaml.safe_load(file)
       except yaml.YAMLError as e:
          print(e)
    #print(yaml.safe_dump(content, sort_keys=False, width=float("inf")))

    # ADDITIONS / REPLACEMENTS / DELETIONS VIA YAML

    # all jobs with names ending "-" can go - delete key
    found_jobs_keys = []
    for job in content["jobs"]:
       if re.search(".*-$", job):
          found_jobs_keys.append(job)

    for job in found_jobs_keys:
       del(content["jobs"][job])

    # all top-level envs can go - delete key
    #print("### " + str(content["env"]))
    del(content["env"])

    # new "on" key setting - note workflow_dispatch is None
    content["on"] = [ { "pull_request": { "paths": [ 'source/**',
                                                     'clik/**',
                                                     'modules/**',
                                                     'examples/**',
                                                     'cmake/**',
                                                     'hal/**',
                                                     '.github/actions/do_build_ock/**',
                                                     '.github/actions/setup_ubuntu_build/**',
                                                     '.github/workflows/run_pr_tests.yml',
                                                     'CMakeLists.txt',
                                                   ]
                                        },
                      },
                      { "workflow_dispatch": None,
                      }
                    ]

    # update PR group
    content["concurrency"]["group"] = "${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}"

    found_steps_keys = []
    for key, value, path in lookup_key("steps", content): # value needed?
       # save found items to list here - avoids in-situ update issues
       found_steps_keys.append((key, path))

    for steps_key, path in found_steps_keys:
       # set llvm_build_type from job name suffix
       llvm_build_type =  "RelAssert"
       for jobname in path:
         if re.search("mr-.*-release", jobname):
           llvm_build_type =  "Release"
           break

       # import tool adds its own checkout boilerplate in step[0] - delete prior to adding our own
       del(steps_key["steps"][0])

       # append boilerplate steps in reverse order
       steps_key["steps"] = [ { "run": "pwd && ls -al",
                              } ] + steps_key["steps"]
       steps_key["steps"] = [ { "name": "setup-ubuntu",
                                "uses":  "./.github/actions/setup_ubuntu_build",
                                "with": { "llvm_version": "17",
                                          "llvm_build_type": llvm_build_type,
                                        },
                              } ] + steps_key["steps"]
       steps_key["steps"] = [ { "run": "cp -R code/.github .github", 
                              } ] + steps_key["steps"]
       steps_key["steps"] = [ { "name": "Checkout repo", 
                                "uses": "actions/checkout@v4.1.0", 
                                "with": { "path": "code", } 
                              } ] + steps_key["steps"]

       # "env" keys are found at two levels - take advantage of the "steps" keys 
       # being at the same level as "jobs env" keys to update any job env vars here too
       steps_key["env"].update({ "CXXCompiler": "llvm_install/bin/clang++", })

       # ...similarly ... ubuntu version ...
       if re.search("ubuntu.*", steps_key["runs-on"]):
          steps_key["runs-on"] = "ubuntu-22.04"

    found_run_keys = []
    for key, value, path in lookup_key("run", content): # value needed?
       # save found items to list here - avoids in-situ update issues
       found_run_keys.append((key, path))

    for run_key, steps_path in found_run_keys:
       # set build_type from job name suffix
       build_type =  "ReleaseAssert"
       for jobname in steps_path:
         if re.search("mr-.*-release", str(jobname)):
           build_type =  "Release"
           break
       if type(run_key["run"]) is list:
          True
          #print("LIST: ", run_key["run"])
          # Placeholder for edge case:
          # "run"s can be str or list. Currently the only "run" entry using list 
          # format is (by happy accident) removed entirely by regex deletion below.
          # However if we ever want to support list processing in this context we'll 
          # need to revisit with a view to transfoming any significant string in the 
          # "run" list (e.g. build.py call or similar) in-situ while honouring any 
          # remaining list content before and/or after the transformed string.
       else: # str
          # find every "run" key with a build.py string value and
          # replace its key:value with a yaml 'build action' call
          if yaml_str := check_for_build_py(run_key['run'], build_type):
             # convert (plain text) build action yaml_str to yaml ...
             build_action = yaml.safe_load(yaml_str)
# get the path to the "steps" list containing the key we want to replace
#             path_to_key = 'content'
#             for i in range(len(steps_path[:-1])):
#                 path_to_key += '["' + str(steps_path[i]) + '"]'
#             # find the offending "run" key and replace with the action yaml
#             for i, step_entry in enumerate(eval(path_to_key)):
#                 if step_entry == run_key:
#                    eval(path_to_key)[i].clear() 
#                    eval(path_to_key)[i].update(build_action[0])
#                    break 
             # find the offending "run" key and replace with the action yaml
             for i, step_entry in enumerate(steps_path):
                 if step_entry == run_key:
                    steps_path[i].clear() 
                    steps_path[i].update(build_action[0])
                    break 

    # DELETIONS VIA PLAIN TEXT REGEX

    regex_list = [ " container:",
                   " image:",
                   " GITHUB_USER: codeplaysoftware",
                   " GIT_STRATEGY: clone",
                   "[:-] echo cloning.*oneapi-construction-kit.*",
                   "[:-] git clone.*oneapi-construction-kit.*",
                   "[:-] cd oneapi-construction-kit",
                   "[:-] echo adding",
                   "[:-] git remote",
                   "[:-] git config user",
                   "[:-] git fetch",
                   "[:-] echo merging",
                   "[:-] git merge",
                   "[:-] git log",
                   "[:-] cp -r",
                   "- run: *$",  # no "run" lists now so delete key
                   'if: .*== "merge_request_event"',
                   "RUN_BUILD_TEST:",
                   "RUN_DOC:",
                   "needs: ",
                   "BuildType:", # now taken from job name suffix
                   "LLVMBranch",
    ]
    only_job = "mr-ubuntu-gcc-x86_64-riscv-fp16-cl3-0-unitcl_vecz"
    found_only_job = True
    #found_only_job = False
    for line in yaml.safe_dump(content, sort_keys=False, width=float("inf")).splitlines():
       if re.search("^ *mr-.*: *$", line):
          #if found_only_job := re.search(only_job, line):
             print("\n############### JOB " + line + "\n")
       if found_only_job:
          if any(re.search(regex, line) for regex in regex_list ):
             True #print("###", end='')
          else:
             print(line)

    #print(yaml.safe_dump(content, sort_keys=False, width=float("inf")))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
