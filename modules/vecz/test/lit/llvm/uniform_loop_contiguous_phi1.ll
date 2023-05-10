; Copyright (C) Codeplay Software Limited. All Rights Reserved.

; RUN: %veczc -k test -w 4 -S < %s | %filecheck %s

target datalayout = "e-p:32:32:32-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v16:16:16-v24:32:32-v32:32:32-v48:64:64-v64:64:64-v96:128:128-v128:128:128-v192:256:256-v256:256:256-v512:512:512-v1024:1024:1024"
target triple = "spir-unknown-unknown"

define spir_kernel void @test(i32 addrspace(1)* %in) {
entry:
  %id = call spir_func i64 @_Z13get_global_idj(i64 0) #2
  %init_addr = getelementptr inbounds i32, i32 addrspace(1)* %in, i64 %id
  %load = load i32, i32 addrspace(1)* %init_addr
  br label %loop

loop:
  %index = phi i64 [0, %entry], [%inc, %loop]
  %slot = phi i32 addrspace(1)* [%init_addr, %entry], [%inc_addr, %loop]
  store i32 %load, i32 addrspace(1)* %slot
  %inc_addr = getelementptr inbounds i32, i32 addrspace(1)* %slot, i64 16
  %inc = add i64 %index, 1
  %cmp = icmp ne i64 %inc, 16
  br i1 %cmp, label %loop, label %merge

merge:
  ret void
}

declare spir_func i64 @_Z13get_global_idj(i64)

; It checks that the stride analysis can tell the store is contiguous through the PHI node.

; CHECK: define spir_kernel void @__vecz_v4_test
; CHECK: %[[LD:.+]] = load <4 x i32>, ptr addrspace(1) %init_addr
; CHECK: loop:
; CHECK: store <4 x i32> %[[LD]], ptr addrspace(1) %slot