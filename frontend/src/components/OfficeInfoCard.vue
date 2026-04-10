<script setup>
import { ref, watch } from 'vue'
import { MapPin, Clock, Moon, Calendar, Phone } from 'lucide-vue-next'

const props = defineProps({
  office: { type: Object, required: true },
  userPos: { type: Object, default: null }, // { lat, lng }
})

const phoneNumber = ref('')
const phoneLookupDone = ref(false)

function normalizeSpacing(text) {
  return String(text ?? '')
    .replace(/\s+/g, ' ')
    .replace(/\s*([,·~])\s*/g, ' $1 ')
    .replace(/\s*([()])/g, '$1')
    .trim()
}

async function waitForKakaoServices() {
  for (let i = 0; i < 30; i += 1) {
    if (window.kakao?.maps?.services) return true
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  return false
}

function searchPlacePhone(keyword) {
  return new Promise(resolve => {
    const places = new window.kakao.maps.services.Places()
    places.keywordSearch(keyword, (result, status) => {
      if (status !== window.kakao.maps.services.Status.OK || !result.length) {
        resolve('')
        return
      }
      const exact = result.find(place => place.place_name?.includes(props.office.cso_nm))
      resolve(exact?.phone || result[0]?.phone || '')
    })
  })
}

async function loadPhoneNumber() {
  phoneNumber.value = ''
  phoneLookupDone.value = false

  if (!props.office?.cso_nm) {
    phoneLookupDone.value = true
    return
  }

  const ready = await waitForKakaoServices()
  if (!ready) {
    phoneLookupDone.value = true
    return
  }

  const keywords = [
    [props.office.cso_nm, props.office.road_nm_addr].filter(Boolean).join(' '),
    props.office.cso_nm,
  ]

  for (const keyword of keywords) {
    const found = await searchPlacePhone(keyword)
    if (found) {
      phoneNumber.value = found
      break
    }
  }

  phoneLookupDone.value = true
}

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

function telHref(phone) {
  return `tel:${String(phone).replace(/[^\d+]/g, '')}`
}

const NAV_MODES = [
  { mode: 'walk', label: '도보', svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M13 4a1 1 0 11-2 0 1 1 0 012 0zm-1 3l-3 4h2v6h2v-6h2l-3-4z"/>' },
  { mode: 'car',  label: '자차', svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M5 17H3v-5l2.5-5h11L19 12v5h-2m-1 0a2 2 0 11-4 0 2 2 0 014 0zm-8 0a2 2 0 11-4 0 2 2 0 014 0z"/>' },
  { mode: 'bus',  label: '대중교통', svgPath: '<path stroke-linecap="round" stroke-linejoin="round" d="M8 6v6m0 0v6m0-6h8m0 0V6m0 6v6M5 6h14a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2z"/>' },
]

watch(() => props.office?.cso_sn, loadPhoneNumber, { immediate: true })
</script>

<template>
  <div class="mx-4 mt-4 rounded-[22px] border border-white/70 bg-white px-5 py-5 shadow-[0_14px_40px_rgba(15,23,42,0.08)] space-y-5">
    <div>
      <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Office Overview</p>
      <h2 class="mt-2 text-xl font-bold text-foreground break-keep">{{ office.cso_nm }}</h2>
    </div>

    <div class="space-y-3.5">
      <div class="flex items-start gap-3">
        <MapPin class="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
        <span class="text-[15px] text-muted-foreground leading-relaxed">{{ office.road_nm_addr }}</span>
      </div>
      <div class="flex items-center gap-3">
        <Phone class="w-5 h-5 text-primary flex-shrink-0" />
        <a
          v-if="phoneNumber"
          :href="telHref(phoneNumber)"
          class="text-[15px] font-medium text-primary underline-offset-2 hover:underline"
        >
          {{ phoneNumber }}
        </a>
        <span v-else class="text-[15px] text-muted-foreground">
          {{ phoneLookupDone ? '전화번호 확인 불가' : '전화번호 조회 중' }}
        </span>
      </div>
      <div class="flex items-center gap-3">
        <Clock class="w-5 h-5 text-primary flex-shrink-0" />
        <span class="text-[15px] text-muted-foreground">
          평일 {{ formatTime(office.wkdy_oper_bgng_tm) }} ~ {{ formatTime(office.wkdy_oper_end_tm) }}
        </span>
      </div>
    </div>

    <div class="flex gap-2 flex-wrap pt-1">
      <span class="inline-flex items-center text-sm font-semibold px-3.5 py-2 rounded-full"
        :class="office.nght_oper_yn === 'Y' ? 'bg-violet-50 text-violet-600' : 'bg-muted text-muted-foreground'">
        <Moon class="w-3.5 h-3.5 mr-1.5" />
        {{ office.nght_oper_yn === 'Y' ? '야간 여권 운영' : '야간 미운영' }}
      </span>
      <span class="inline-flex items-center text-sm font-semibold px-3.5 py-2 rounded-full"
        :class="office.wknd_oper_yn === 'Y' ? 'bg-emerald-50 text-emerald-600' : 'bg-muted text-muted-foreground'">
        <Calendar class="w-3.5 h-3.5 mr-1.5" />
        {{ office.wknd_oper_yn === 'Y' ? '주말 운영' : '주말 미운영' }}
      </span>
    </div>

    <p v-if="office.nght_dow_expln" class="rounded-2xl bg-slate-50 px-4 py-3.5 text-sm leading-relaxed text-muted-foreground">
      {{ normalizeSpacing(office.nght_dow_expln) }}
    </p>

    <div class="pt-1">
      <p class="text-sm font-semibold text-foreground mb-3">길찾기</p>
      <div class="grid grid-cols-3 gap-2.5">
        <a
          v-for="{ mode, label, svgPath } in NAV_MODES"
          :key="mode"
          :href="kakaoNavUrl(mode)"
          target="_blank"
          rel="noopener noreferrer"
          class="flex flex-col items-center gap-2 py-4 rounded-2xl bg-slate-50 hover:bg-primary-light hover:shadow-sm active:scale-95 transition-all cursor-pointer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" v-html="svgPath" />
          <span class="text-sm font-semibold text-foreground">{{ label }}</span>
        </a>
      </div>
      <p v-if="!userPos" class="text-xs text-muted-foreground mt-2.5 text-center">
        위치를 허용하면 현재 위치에서 출발합니다
      </p>
    </div>
  </div>
</template>
