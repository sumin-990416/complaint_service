<script setup>
defineProps({
  title: { type: String, required: true },
  showBack: { type: Boolean, default: false },
})
defineEmits(['back'])
</script>

<template>
  <header class="sticky top-0 z-50 h-14 bg-transparent flex items-center justify-between px-3">
    <button
      v-if="showBack"
      class="w-9 h-9 flex items-center justify-center rounded-full text-white/70 hover:text-white hover:bg-white/10 active:bg-white/20 transition-colors flex-shrink-0"
      @click="$emit('back')"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
      </svg>
    </button>
    <span v-else class="w-9 flex-shrink-0" />

    <span class="flex-1 text-center text-white font-semibold text-[15px] tracking-[0.01em] truncate px-1">
      {{ title }}
    </span>

    <div class="flex items-center gap-2 flex-shrink-0">
      <slot name="right" />
    </div>
  </header>
</template>
