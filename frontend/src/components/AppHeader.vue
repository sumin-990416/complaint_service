<script setup>
defineProps({
  title: { type: String, required: true },
  showBack: { type: Boolean, default: false },
})
defineEmits(['back'])
</script>

<template>
  <header class="sticky top-0 z-50 h-14 bg-primary flex items-center justify-between px-2 shadow-md">
    <button
      v-if="showBack"
      class="w-10 h-10 flex items-center justify-center rounded-full text-primary-foreground text-2xl hover:bg-white/20 active:bg-white/30 transition-colors flex-shrink-0"
      @click="$emit('back')"
    >
      ‹
    </button>
    <span v-else class="w-10 flex-shrink-0" />

    <span class="flex-1 text-center text-primary-foreground font-semibold text-base truncate px-2">
      {{ title }}
    </span>

    <div class="w-10 flex justify-end items-center flex-shrink-0">
      <slot name="right" />
    </div>
  </header>
</template>
