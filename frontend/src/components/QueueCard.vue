<script setup>
import UiCard from './ui/Card.vue'
import UiBadge from './ui/Badge.vue'
import { Users } from 'lucide-vue-next'

defineProps({ item: { type: Object, required: true } })

function waitLevel(cnt) {
  const n = Number(cnt)
  if (n === 0) return 'free'
  if (n <= 3) return 'mild'
  return 'busy'
}

const levelConfig = {
  free: { variant: 'success', label: '여유', countClass: 'text-emerald-600' },
  mild: { variant: 'warning', label: '보통', countClass: 'text-amber-600' },
  busy: { variant: 'destructive', label: '혼잡', countClass: 'text-red-500' },
}
</script>

<template>
  <UiCard class="p-4">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
          <Users class="w-4 h-4 text-primary" />
        </div>
        <span class="font-semibold text-sm text-foreground">{{ item.task_nm }}</span>
      </div>
      <UiBadge :variant="levelConfig[waitLevel(item.wtng_cnt)].variant">
        {{ levelConfig[waitLevel(item.wtng_cnt)].label }}
      </UiBadge>
    </div>

    <div class="flex items-end justify-between">
      <div class="flex flex-col gap-0.5">
        <span class="text-[0.7rem] text-muted-foreground uppercase tracking-wide">창구 번호</span>
        <span class="text-base font-bold text-foreground">{{ item.clot_no || '—' }}</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span
          class="text-4xl font-black leading-none"
          :class="levelConfig[waitLevel(item.wtng_cnt)].countClass"
        >{{ item.wtng_cnt }}</span>
        <span class="text-sm text-muted-foreground font-medium">명 대기</span>
      </div>
    </div>
  </UiCard>
</template>
