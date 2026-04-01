<script setup>
import UiCard from './ui/Card.vue'
import UiBadge from './ui/Badge.vue'
import { MapPin, Clock, Moon, Calendar } from 'lucide-vue-next'

const props = defineProps({
  office: { type: Object, required: true },
  userPos: { type: Object, default: null }, // { lat, lng }
})

function formatTime(t) {
  if (!t || t.length < 4) return '—'
  return `${t.slice(0, 2)}:${t.slice(2, 4)}`
}

function kakaoNavUrl(mode) {
  const { lat, lot: lng, cso_nm: name } = props.office
  // 카카오맵 길찾기 URL (WGS84 좌표)
  if (props.userPos) {
    // 출발지 → 도착지 경로
    const sLat = props.userPos.lat
    const sLng = props.userPos.lng
    return `https://map.kakao.com/link/from/현재위치,${sLat},${sLng}/to/${encodeURIComponent(name)},${lat},${lng}`
  }
  // 출발지 없이 도착지만
  return `https://map.kakao.com/link/to/${encodeURIComponent(name)},${lat},${lng}`
}

const NAV_MODES = [
  { mode: 'walk', label: '도보', emoji: '🚶', color: 'bg-emerald-50 border-emerald-200 text-emerald-700 hover:bg-emerald-100' },
  { mode: 'car',  label: '자차', emoji: '🚗', color: 'bg-blue-50 border-blue-200 text-blue-700 hover:bg-blue-100' },
  { mode: 'bus',  label: '대중교통', emoji: '🚌', color: 'bg-amber-50 border-amber-200 text-amber-700 hover:bg-amber-100' },
]
</script>

<template>
  <UiCard class="mx-4 mt-4 p-5 space-y-4">
    <h2 class="text-lg font-bold text-foreground">{{ office.cso_nm }}</h2>

    <div class="space-y-2.5">
      <div class="flex items-start gap-3">
        <MapPin class="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
        <span class="text-sm text-muted-foreground leading-relaxed">{{ office.road_nm_addr }}</span>
      </div>
      <div class="flex items-center gap-3">
        <Clock class="w-4 h-4 text-primary flex-shrink-0" />
        <span class="text-sm text-muted-foreground">
          평일 {{ formatTime(office.wkdy_oper_bgng_tm) }} ~ {{ formatTime(office.wkdy_oper_end_tm) }}
        </span>
      </div>
    </div>

    <div class="flex gap-2 flex-wrap pt-1">
      <UiBadge
        :variant="office.nght_oper_yn === 'Y' ? 'night' : 'secondary'"
        class="py-1 px-3 text-xs"
      >
        <Moon class="w-3 h-3 mr-1" />
        야간 {{ office.nght_oper_yn === 'Y' ? '운영' : '미운영' }}
      </UiBadge>
      <UiBadge
        :variant="office.wknd_oper_yn === 'Y' ? 'weekend' : 'secondary'"
        class="py-1 px-3 text-xs"
      >
        <Calendar class="w-3 h-3 mr-1" />
        주말 {{ office.wknd_oper_yn === 'Y' ? '운영' : '미운영' }}
      </UiBadge>
    </div>

    <p v-if="office.nght_dow_expln" class="text-xs text-muted-foreground leading-relaxed border-l-2 border-primary pl-3 bg-muted/40 py-2 pr-2 rounded-r-lg">
      {{ office.nght_dow_expln }}
    </p>

    <!-- 길찾기 -->
    <div class="pt-2">
      <p class="text-xs font-semibold text-foreground mb-2.5">🧭 길찾기</p>
      <div class="grid grid-cols-3 gap-2.5">
        <a
          v-for="{ mode, label, emoji, color } in NAV_MODES"
          :key="mode"
          :href="kakaoNavUrl(mode)"
          target="_blank"
          rel="noopener noreferrer"
          :class="[
            'flex flex-col items-center gap-1.5 py-3.5 rounded-xl border transition-all cursor-pointer',
            'hover:shadow-md active:scale-95',
            color,
          ]"
        >
          <span class="text-2xl">{{ emoji }}</span>
          <span class="text-xs font-semibold">{{ label }}</span>
        </a>
      </div>
      <p v-if="!userPos" class="text-[11px] text-muted-foreground mt-2 text-center">
        📍 위치를 허용하면 현재 위치에서 출발합니다
      </p>
    </div>
  </UiCard>
</template>
