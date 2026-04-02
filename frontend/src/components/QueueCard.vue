<script setup>
import { Users } from 'lucide-vue-next'

defineProps({ item: { type: Object, required: true } })

function waitLevel(cnt) {
  const n = Number(cnt)
  if (n === 0) return 'free'
  if (n <= 3) return 'mild'
  return 'busy'
}

const levelConfig = {
  free: { label: '여유', color: 'bg-emerald-50 text-emerald-600', countClass: 'text-emerald-500' },
  mild: { label: '보통', color: 'bg-amber-50 text-amber-600', countClass: 'text-amber-500' },
  busy: { label: '혼잡', color: 'bg-red-50 text-red-500', countClass: 'text-red-500' },
}
</script>

<template>
  <div class="rounded-[22px] border border-white/70 bg-white p-4 shadow-[0_14px_40px_rgba(15,23,42,0.08)]">
    <div class="flex items-start justify-between mb-3">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 rounded-xl bg-primary-light flex items-center justify-center">
          <Users class="w-4 h-4 text-primary" />
        </div>
        <span class="font-semibold text-sm text-foreground">{{ item.task_nm }}</span>
      </div>
      <span class="text-[11px] font-bold px-2.5 py-1 rounded-full" :class="levelConfig[waitLevel(item.wtng_cnt)].color">
        {{ levelConfig[waitLevel(item.wtng_cnt)].label }}
      </span>
    </div>

    <div class="flex items-end justify-between">
      <div class="flex flex-col gap-0.5">
        <span class="text-[0.7rem] text-muted-foreground uppercase tracking-wide">창구 번호</span>
        <span class="text-base font-bold text-foreground">{{ item.clot_no || '—' }}</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-4xl font-black leading-none" :class="levelConfig[waitLevel(item.wtng_cnt)].countClass">
          {{ item.wtng_cnt }}
        </span>
        <span class="text-sm text-muted-foreground font-medium">명 대기</span>
      </div>
    </div>
  </div>
</template>
