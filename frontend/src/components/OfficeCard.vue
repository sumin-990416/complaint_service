<script setup>
import { MapPin } from 'lucide-vue-next'

defineProps({ office: { type: Object, required: true } })
defineEmits(['select'])

function extractRegion(addr) {
  if (!addr) return ''
  const parts = addr.split(' ')
  const first = parts[0] ?? ''
  if (first.endsWith('광역시') || first.endsWith('특별시') || first.endsWith('특별자치시') || first.endsWith('특별자치도')) {
    const second = parts[1] ?? ''
    if (second.endsWith('구') || second.endsWith('군') || second.endsWith('시')) return `${first} ${second}`
    return first
  }
  return first
}

function displayName(office) {
  const region = extractRegion(office.road_nm_addr)
  const name = office.cso_nm
  if (!region || name.replace(/\s/g, '').includes(region.replace(/\s/g, ''))) return name
  return `${region} · ${name}`
}

function formatDist(d) {
  if (d == null) return null
  return d < 1 ? `${Math.round(d * 1000)}m` : `${d.toFixed(1)}km`
}
</script>

<template>
  <li class="list-none">
    <div
      class="group relative overflow-hidden rounded-[22px] border border-white/70 bg-white/92 shadow-[0_14px_40px_rgba(15,23,42,0.08)] backdrop-blur hover:-translate-y-0.5 hover:shadow-[0_18px_48px_rgba(15,23,42,0.12)] active:scale-[0.985] transition-all duration-150 cursor-pointer"
      @click="$emit('select', office)"
    >
      <div class="absolute inset-y-3 left-0 w-1 rounded-r-full bg-gradient-to-b from-primary via-sky-400 to-emerald-300 opacity-85"></div>
      <div class="flex items-center gap-3 px-4 py-3 pl-5">
        <div class="w-10 h-10 rounded-2xl bg-[linear-gradient(135deg,#eef2ff_0%,#dbeafe_100%)] flex items-center justify-center flex-shrink-0 shadow-[inset_0_1px_0_rgba(255,255,255,0.9)]">
          <MapPin class="w-4.5 h-4.5 text-primary" />
        </div>

        <div class="flex-1 min-w-0">
          <p class="text-[11px] font-semibold uppercase tracking-[0.16em] text-primary/60">Civil Office</p>
          <p class="mt-0.5 font-bold text-[0.95rem] text-foreground leading-snug break-keep">{{ displayName(office) }}</p>
          <p class="text-[11px] text-muted-foreground truncate mt-0.5">{{ office.road_nm_addr }}</p>
          <div class="flex gap-1.5 mt-1.5 flex-wrap">
            <span v-if="office.nght_oper_yn === 'Y'" class="inline-flex items-center text-[10px] font-semibold bg-violet-50 text-violet-700 px-2 py-0.5 rounded-full">🌙 야간</span>
            <span v-if="office.wknd_oper_yn === 'Y'" class="inline-flex items-center text-[10px] font-semibold bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full">📅 주말</span>
          </div>
        </div>

        <div class="flex flex-col items-end gap-1.5 flex-shrink-0">
          <span v-if="formatDist(office.dist)" class="inline-flex items-center rounded-full bg-slate-950 px-2 py-0.5 text-[10px] font-semibold text-white shadow-sm">
            {{ formatDist(office.dist) }}
          </span>
          <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-400 group-hover:text-primary transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  </li>
</template>
