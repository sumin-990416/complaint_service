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
  free: {
    label: '여유',
    badge: 'bg-emerald-100 text-emerald-700',
    icon: 'bg-emerald-50 text-emerald-500',
    bar: 'bg-emerald-400',
    count: 'text-emerald-500',
    border: 'border-emerald-100',
  },
  mild: {
    label: '보통',
    badge: 'bg-amber-100 text-amber-700',
    icon: 'bg-amber-50 text-amber-500',
    bar: 'bg-amber-400',
    count: 'text-amber-500',
    border: 'border-amber-100',
  },
  busy: {
    label: '혼잡',
    badge: 'bg-red-100 text-red-600',
    icon: 'bg-red-50 text-red-400',
    bar: 'bg-red-400',
    count: 'text-red-500',
    border: 'border-red-100',
  },
}
</script>

<template>
  <div
    class="rounded-[20px] border bg-white p-4 shadow-[0_8px_24px_rgba(15,23,42,0.07)]"
    :class="levelConfig[waitLevel(item.wtng_cnt)].border"
  >
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-xl flex items-center justify-center" :class="levelConfig[waitLevel(item.wtng_cnt)].icon">
          <Users class="w-4 h-4" />
        </div>
        <span class="font-semibold text-sm text-foreground">{{ item.task_nm }}</span>
      </div>
      <span class="text-[11px] font-bold px-2.5 py-1 rounded-full" :class="levelConfig[waitLevel(item.wtng_cnt)].badge">
        {{ levelConfig[waitLevel(item.wtng_cnt)].label }}
      </span>
    </div>

    <div class="flex items-end justify-between">
      <div class="flex flex-col gap-0.5">
        <span class="text-[10px] font-medium text-muted-foreground uppercase tracking-widest">창구</span>
        <span class="text-lg font-black text-foreground">{{ item.clot_no || '—' }}</span>
      </div>
      <div class="flex items-baseline gap-1">
        <span class="text-4xl font-black leading-none" :class="levelConfig[waitLevel(item.wtng_cnt)].count">
          {{ item.wtng_cnt }}
        </span>
        <span class="text-sm text-muted-foreground font-medium mb-0.5">명 대기</span>
      </div>
    </div>

    <!-- 혼잡도 바 -->
    <div class="mt-3 h-1 rounded-full bg-slate-100 overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-500"
        :class="levelConfig[waitLevel(item.wtng_cnt)].bar"
        :style="{ width: `${Math.min(Number(item.wtng_cnt) * 8, 100)}%` }"
      ></div>
    </div>
  </div>
</template>
