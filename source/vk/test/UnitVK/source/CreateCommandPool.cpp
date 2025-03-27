// Copyright (C) Codeplay Software Limited
//
// Licensed under the Apache License, Version 2.0 (the "License") with LLVM
// Exceptions; you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://github.com/codeplaysoftware/oneapi-construction-kit/blob/main/LICENSE.txt
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
// WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
// License for the specific language governing permissions and limitations
// under the License.
//
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

#include <UnitVK.h>

// https://www.khronos.org/registry/vulkan/specs/1.0/xhtml/vkspec.html#vkCreateCommandPool

class CreateCommandPool : public uvk::DeviceTest {
 public:
  CreateCommandPool() : createInfo(), commandPool() {}

  void SetUp() override {
    RETURN_ON_FATAL_FAILURE(DeviceTest::SetUp());
    createInfo.sType = VK_STRUCTURE_TYPE_COMMAND_POOL_CREATE_INFO;
  }

  void TearDown() override {
    if (commandPool) {
      vkDestroyCommandPool(device, commandPool, nullptr);
    }
    DeviceTest::TearDown();
  }

  VkCommandPoolCreateInfo createInfo;
  VkCommandPool commandPool;
};

TEST_F(CreateCommandPool, Default) {
  ASSERT_EQ_RESULT(VK_SUCCESS, vkCreateCommandPool(device, &createInfo, nullptr,
                                                   &commandPool));
}

TEST_F(CreateCommandPool, DefaultAllocator) {
  ASSERT_EQ_RESULT(VK_SUCCESS,
                   vkCreateCommandPool(device, &createInfo,
                                       uvk::defaultAllocator(), &commandPool));
  vkDestroyCommandPool(device, commandPool, uvk::defaultAllocator());
  commandPool = VK_NULL_HANDLE;
}

TEST_F(CreateCommandPool, DefaultFlagsTransient) {
  // Create with the transient flag enabled
  createInfo.flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT;
  ASSERT_EQ_RESULT(VK_SUCCESS, vkCreateCommandPool(device, &createInfo, nullptr,
                                                   &commandPool));
}

TEST_F(CreateCommandPool, DefaultFlagsResetCommandBuffer) {
  // Create with the reset command buffer flag enabled
  createInfo.flags = VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
  ASSERT_EQ_RESULT(VK_SUCCESS, vkCreateCommandPool(device, &createInfo, nullptr,
                                                   &commandPool));
}

TEST_F(CreateCommandPool, DefaultFlagsAll) {
  // Create with both flags enabled
  createInfo.flags = VK_COMMAND_POOL_CREATE_TRANSIENT_BIT |
                     VK_COMMAND_POOL_CREATE_RESET_COMMAND_BUFFER_BIT;
  ASSERT_EQ_RESULT(VK_SUCCESS, vkCreateCommandPool(device, &createInfo, nullptr,
                                                   &commandPool));
}

TEST_F(CreateCommandPool, ErrorOutOfHostMemory) {
  ASSERT_EQ_RESULT(VK_ERROR_OUT_OF_HOST_MEMORY,
                   vkCreateCommandPool(device, &createInfo,
                                       uvk::nullAllocator(), &commandPool));
}

// VK_ERROR_OUT_OF_DEVICE_MEMORY
// Is a possible return from this function, but is untestable
// due to the fact that we can't currently access device memory
// allocators to mess with
