// Copyright (C) Codeplay Software Limited. All Rights Reserved.
// CL_STD: 3.0
__kernel void exchange_global_int(volatile __global atomic_int *in_out_buffer,
                              __global int *desired_buffer,
                              __global int *output_buffer) {
  uint gid = get_global_id(0);
  output_buffer[gid] =
      atomic_exchange_explicit(in_out_buffer + gid, desired_buffer[gid],
                               memory_order_relaxed, memory_scope_work_item);
}