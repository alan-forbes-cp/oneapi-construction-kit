#!/usr/bin/env python

import re
import shlex # does this handle corresponding windows command lines ??
import yaml

def ignore(substring):
    ignore_list = [ "python",
                    "-u",
                    "scripts/build.py",
                    "-GNinja", # already hard-wired in Github build action  
                    "--verbose",
                    "--clean",
                  ]
    return substring in ignore_list

def translate(command):
    ignore_arg = False
    print("""
- name: build ock
  uses: ./.github/actions/do_build_ock
  with: """)
    for substr in shlex.split(command):
       if ignore(substr) or ignore_arg:
          print("    # Ignoring '" + substr + "'")
          ignore_arg = False
       elif substr.startswith('-D'):
          #print(substr)
          #print("  # -D option")
          if substr.startswith('-DCA_CL_ENABLE_ICD_LOADER='):
             print("    # Ignoring '" + substr + "'") # already hard-wired "ON" in Github build action 
          else:
             print("    # ERROR: '" + substr + " IS UNKNOWN'")
       elif substr.startswith('-'):
          #print(substr)
          #print("  # - option")
          if substr == "--build_type":
             print("    # Translating '" + substr + " <ARG>'")
             print("    build_type: ", end='')
          elif substr == "--arch":
             print("    # Ignoring '" + substr + "'")
             ignore_arg = True
          elif substr == "--compiler":
             print("    # Translating '" + substr + "'")
             print("    c_compiler: $GITHUB_WORKSPACE/$Compiler")
             print("    cxx_compiler: $GITHUB_WORKSPACE/$CXXCompiler")
             ignore_arg = True
          elif substr == "--artefact_name":
             print("    # Ignoring '" + substr + "'")
             ignore_arg = True
          elif substr == "--target":
             print("    # Translating '" + substr + " <ARG>'")
             print("    build_targets: ", end='')
          else:
             print("    # ERROR: '" + substr + " IS UNKNOWN'")
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
       print("======== " + jobname + " ========")
       job = content['jobs'][jobname]
       for step in job['steps']:
          if command := step.get('run'):
             if re.search(".*python.*build\.py.*", command):
                print("-------- build.py --------")
                #print(command)
                #print(shlex.split(command))
                translate(command)
       
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
