# Copyright (C) Codeplay Software Limited
#
# Licensed under the Apache License, Version 2.0 (the "License") with LLVM
# Exceptions; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://github.com/codeplaysoftware/oneapi-construction-kit/blob/main/LICENSE.txt
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

add_ca_library(compiler-binary-metadata STATIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include/compiler/utils/add_metadata_pass.h
  ${CMAKE_CURRENT_SOURCE_DIR}/include/compiler/utils/metadata_analysis.h
  ${CMAKE_CURRENT_SOURCE_DIR}/include/compiler/utils/metadata_hooks.h
  ${CMAKE_CURRENT_SOURCE_DIR}/source/metadata_analysis.cpp
  ${CMAKE_CURRENT_SOURCE_DIR}/source/metadata_hooks.cpp)

target_include_directories(compiler-binary-metadata PUBLIC
$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)

target_compile_definitions(compiler-binary-metadata PRIVATE
  $<$<BOOL:${CA_PLATFORM_LINUX}>:CA_PLATFORM_LINUX>
  $<$<BOOL:${CA_PLATFORM_WINDOWS}>:CA_PLATFORM_WINDOWS>
  $<$<BOOL:${CA_PLATFORM_MAC}>:CA_PLATFORM_MAC>
  $<$<BOOL:${CA_PLATFORM_ANDROID}>:CA_PLATFORM_ANDROID>
  $<$<BOOL:${CA_PLATFORM_QNX}>:CA_PLATFORM_QNX>)

target_link_libraries(compiler-binary-metadata PUBLIC
  compiler-pipeline md_handler multi_llvm LLVMPasses LLVMTransformUtils)
if(TARGET LLVMCore)
  target_link_libraries(compiler-binary-metadata PUBLIC LLVMCore)
endif()


# Determine whether LLVM was built with LLD, in which case add a support
# library that exposes lld to ComputeMux compiler targets.
find_package(LLD CONFIG HINTS ${CA_LLVM_INSTALL_DIR})
if(LLD_FOUND)
  add_ca_library(compiler-linker-utils STATIC
    ${CMAKE_CURRENT_SOURCE_DIR}/include/compiler/utils/lld_linker.h
    ${CMAKE_CURRENT_SOURCE_DIR}/source/lld_linker.cpp
  )

  target_include_directories(compiler-linker-utils PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  )

  # Explicitly link against the individual static versions of the lld
  # libraries, see modules/compiler/source/base/CMakeLists.txt for details.
  # LLD initializes all targets, even the ones we will not use, requiring
  # us to also add their corresponding libraries.
  set(LLVM_LIBS)
  foreach(target IN LISTS LLVM_TARGETS_TO_BUILD)
    foreach(lib IN LISTS LLVM_AVAILABLE_LIBS)
      # If LLVM is built with SPIRV-LLVM-Translator as an external project, in
      # addition to LLVM's own LLVMSPIRVCodeGen, LLVMSPIRVDesc, etc. libraries,
      # we will also have SPIRV-LLVM-Translator's LLVMSPIRVLib. This is not
      # required by LLD and may result in linker errors depending on the exact
      # configuration, so take care to leave it out.
      if(lib MATCHES "^LLVM${target}" AND NOT lib STREQUAL "LLVMSPIRVLib")
        list(APPEND LLVM_LIBS "${lib}")
      endif()
    endforeach()
  endforeach()
  list(APPEND LLVM_LIBS LLVMGlobalISel LLVMMCDisassembler LLVMMIRParser
    LLVMSelectionDAG LLVMipo LLVMAsmPrinter LLVMCodeGen)
  set(LLD_LIBS lldELF lldCommon ${LLVM_LIBS})

  if(NOT OCK_IN_LLVM_TREE)
    list(TRANSFORM LLD_LIBS PREPEND "${LLVM_LIBRARY_DIR}/${CMAKE_STATIC_LIBRARY_PREFIX}")
    list(TRANSFORM LLD_LIBS APPEND "${CMAKE_STATIC_LIBRARY_SUFFIX}")
  endif()

  target_link_libraries(compiler-linker-utils PUBLIC
    cargo multi_llvm ${LLD_LIBS}
  )
endif()
