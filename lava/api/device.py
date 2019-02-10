# -*- coding: UTF-8 -*-

import itertools
import logging

import vulkan as vk

from lava.api.constants.vk import DeviceType, MemoryType, QueueType, VALIDATION_LAYERS
from lava.api.memory import Memory


class PhysicalDevice(object):

    def __init__(self, instance, handle):
        self.instance = instance
        self.handle = handle

        # meta data
        properties = vk.vkGetPhysicalDeviceProperties(self.handle)
        self.device_name = properties.deviceName
        self.device_type = DeviceType.from_vulkan(properties.deviceType)

        # queue information
        queue_families = vk.vkGetPhysicalDeviceQueueFamilyProperties(self.handle)
        self.queue_support = {}
        self.queue_idx = {t: [] for t in QueueType.keys()}

        for idx, queue_family in enumerate(queue_families):
            for queue_type in QueueType.keys():
                support = bool(queue_family.queueFlags & QueueType.to_vulkan(queue_type))
                self.queue_support[queue_type] = self.queue_support.get(queue_type, False) or support
                if support:
                    self.queue_idx[queue_type].append(idx)

        # memory properties
        memory_properties = vk.vkGetPhysicalDeviceMemoryProperties(self.handle)
        self.memory_type_idx = {t: [] for t in MemoryType.keys()}
        self.memory_type_idx_to_heap = {}
        self.heap_sizes = {}

        for idx, memory_type in itertools.product(range(memory_properties.memoryTypeCount), MemoryType.keys()):
            support = memory_properties.memoryTypes[idx].propertyFlags & MemoryType.to_vulkan(memory_type)
            if support:
                self.memory_type_idx[memory_type].append(idx)

            heap_idx = memory_properties.memoryTypes[idx].heapIndex
            self.memory_type_idx_to_heap[idx] = heap_idx

            if heap_idx not in self.heap_sizes:
                self.heap_sizes[heap_idx] = memory_properties.memoryHeaps[heap_idx].size

    @classmethod
    def all(cls, instance):
        return [cls(instance, handle) for handle in vk.vkEnumeratePhysicalDevices(instance.handle)]

    def __str__(self):
        return "\n".join(["{}: {}".format(key, self.__dict__[key]) for key in sorted(self.__dict__)])

    def get_name(self):
        return self.device_name

    def get_type(self):
        return self.device_type

    def get_queue_indices(self, queue_type):
        return self.queue_idx[queue_type]

    def supports_queue_type(self, queue_type):
        return self.queue_support[queue_type]

    def get_memory_index(self, *memory_types):
        sets_of_indices = []

        for memory_type in memory_types:
            sets_of_indices.append(set(self.memory_type_idx[memory_type]))

        indices = sets_of_indices[0]
        for other_indices in sets_of_indices[1:]:
            indices.intersection_update(other_indices)

        if len(indices) == 0:
            return None
        else:
            return indices.pop()  # TODO: better way than just picking first/random index?


class Device(object):

    def __init__(self, physical_device, queue_definitions, validation_lvl=None, extensions=()):
        self.validation_lvl = validation_lvl
        self.physical_device = physical_device
        self.memories = []
        queue_create_infos = []

        for queue_idx in set(map(lambda (_, q_idx): q_idx, queue_definitions)):
            queue_create_infos.append(vk.VkDeviceQueueCreateInfo(
                queueFamilyIndex=queue_idx,
                queueCount=1,
                pQueuePriorities=[1.0]
            ))

        features = vk.VkPhysicalDeviceFeatures()

        if validation_lvl:
            create_info = vk.VkDeviceCreateInfo(
                pQueueCreateInfos=queue_create_infos,
                ppEnabledLayerNames=VALIDATION_LAYERS,
                ppEnabledExtensionNames=extensions,
                pEnabledFeatures=features
            )
        else:
            create_info = vk.VkDeviceCreateInfo(
                pQueueCreateInfos=queue_create_infos,
                enabledLayerCount=0,
                ppEnabledExtensionNames=extensions,
                pEnabledFeatures=features,
            )

        self.handle = vk.vkCreateDevice(physical_device.handle, create_info, None)
        self.queue_handles = {}
        self.queue_indices = {}

        for queue_type, queue_idx in queue_definitions:
            self.queue_handles[queue_type] = vk.vkGetDeviceQueue(self.handle, queue_idx, 0)
            self.queue_indices[queue_type] = queue_idx

    def __del__(self):
        del self.memories
        vk.vkDestroyDevice(self.handle, None)  # does also destroy the queues

    def get_physical_device(self):
        return self.physical_device

    def get_queue_handle(self, queue_type):
        return self.queue_handles[queue_type]

    def get_queue_index(self, queue_type):
        return self.queue_indices[queue_type]

    def allocate_memory(self, memory_types, size):
        memory_index = self.physical_device.get_memory_index(*memory_types)

        if memory_index is None:
            raise RuntimeError("Could not find a device memory which supports {}".format(" and ".join(memory_types)))

        memory = Memory(self, memory_index, size)
        self.memories.append(memory)
        return memory

    def free_memory(self, memory):
        pass