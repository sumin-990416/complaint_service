<script setup>
defineProps({
  text: { type: String, default: '불러오는 중…' },
})
</script>

<template>
  <div class="flex flex-col items-center gap-3 py-12 text-muted-foreground text-sm">
    <div class="w-7 h-7 rounded-full border-[3px] border-muted border-t-primary animate-spin"></div>
    <p>{{ text }}</p>
  </div>
</template>
