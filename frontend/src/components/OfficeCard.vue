<script setup>
import UiCard from './ui/Card.vue'
import UiBadge from './ui/Badge.vue'
import { MapPin, ChevronRight } from 'lucide-vue-next'

defineProps({ office: { type: Object, required: true } })
defineEmits(['select'])

function formatDist(d) {
  if (d == null) return ''
  return d < 1 ? `${Math.round(d * 1000)}m` : `${d.toFixed(1)}km`
}
</script>

<template>
  <li class="list-none">
    <UiCard
      class="flex items-center gap-3 p-4 cursor-pointer border border-transparent hover:border-primary/30 hover:shadow-md active:scale-[0.99] transition-all duration-150"
      @click="$emit('select', office)"
    >
      <!-- 아이콘 -->
      <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
        <MapPin class="w-5 h-5 text-primary" />
      </div>

      <!-- 본문 -->
      <div class="flex-1 min-w-0">
        <p class="font-semibold text-[0.97rem] text-foreground truncate">{{ office.cso_nm }}</p>
        <p class="text-xs text-muted-foreground truncate mt-0.5">{{ office.road_nm_addr }}</p>
        <div class="flex gap-1.5 mt-1.5 flex-wrap">
          <UiBadge v-if="office.nght_oper_yn === 'Y'" variant="night">🌙 야간</UiBadge>
          <UiBadge v-if="office.wknd_oper_yn === 'Y'" variant="weekend">📅 주말</UiBadge>
        </div>
      </div>

      <!-- 우측 -->
      <div class="flex flex-col items-end gap-1 flex-shrink-0">
        <UiBadge v-if="office.dist != null" variant="default" class="text-[0.75rem]">
          {{ formatDist(office.dist) }}
        </UiBadge>
        <ChevronRight class="w-4 h-4 text-muted-foreground" />
      </div>
    </UiCard>
  </li>
</template>
