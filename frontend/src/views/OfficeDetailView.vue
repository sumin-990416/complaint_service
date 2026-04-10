<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOffice, fetchRealtime } from '../api/index.js'

import LoadingSpinner from '../components/LoadingSpinner.vue'
import OfficeInfoCard from '../components/OfficeInfoCard.vue'
import OfficeMap from '../components/OfficeMap.vue'
import QueueCard from '../components/QueueCard.vue'

const props = defineProps({ csoSn: String })
const router = useRouter()

/** KST(Asia/Seoul) 기준 현재 시각 정보 */
function nowKST() {
  const now = new Date()
  const kst = new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    hour: 'numeric', minute: 'numeric',
    weekday: 'short',
    hour12: false,
  }).formatToParts(now)
  const get = (type) => kst.find(p => p.type === type)?.value ?? ''
  const hour = parseInt(get('hour'), 10)
  const minute = parseInt(get('minute'), 10)
  const weekdayMap = { '일': 0, '월': 1, '화': 2, '수': 3, '목': 4, '금': 5, '토': 6 }
  const dayOfWeek = weekdayMap[get('weekday')] ?? new Date().getDay()
  return { hour, minute, dayOfWeek }
}

const office = ref(null)
const realtime = ref([])
const loading = ref(true)
const realtimeLoading = ref(false)
const error = ref(null)
const userPos = ref(null)
const prediction = ref(null)
const gov24Links = ref([])

function parseTimeToMinutes(value) {
  if (!value || value.length < 4) return null
  const hours = Number(value.slice(0, 2))
  const minutes = Number(value.slice(2, 4))
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return null
  return hours * 60 + minutes
}

const isWithinOperatingHours = computed(() => {
  if (!office.value) return false

  const { hour, minute, dayOfWeek } = nowKST()
  const currentMinutes = hour * 60 + minute
  const startMinutes = parseTimeToMinutes(office.value.wkdy_oper_bgng_tm)
  const endMinutes = parseTimeToMinutes(office.value.wkdy_oper_end_tm)
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6

  if (isWeekend) {
    return office.value.wknd_oper_yn === 'Y'
  }

  if (startMinutes == null || endMinutes == null) return false
  return currentMinutes >= startMinutes && currentMinutes <= endMinutes
})

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => { userPos.value = { lat, lng } },
    () => {},
    { timeout: 30000 },
  )
}

// "서울 강동구 성내로 25" → "서울" / "부산광역시 남구 ..." → "부산광역시 남구"
function extractRegion(addr) {
  if (!addr) return ''
  const parts = addr.split(' ')
  // 첫 번째 토큰이 광역시/특별시/특별자치시 이면 두 번째까지 합침
  const first = parts[0] ?? ''
  if (first.endsWith('광역시') || first.endsWith('특별시') || first.endsWith('특별자치시') || first.endsWith('특별자치도')) {
    const second = parts[1] ?? ''
    // 두 번째가 구/군/시 면 같이 표시
    if (second.endsWith('구') || second.endsWith('군') || second.endsWith('시')) {
      return `${first} ${second}`
    }
    return first
  }
  return first
}

const headerTitle = computed(() => {
  if (!office.value) return '민원실'
  const region = extractRegion(office.value.road_nm_addr)
  const name = office.value.cso_nm
  // 이름이 이미 지역명을 포함하면 지역 접두사 생략 (공백 제거 후 비교)
  const regionNoSpace = region.replace(/\s/g, '')
  const nameNoSpace = name.replace(/\s/g, '')
  if (!region || nameNoSpace.includes(regionNoSpace)) return name
  return `${region} · ${name}`
})

function formatUpdatedAt(dt) {
  if (!dt || dt.length < 12) return ''
  return `${dt.slice(8, 10)}:${dt.slice(10, 12)} 기준`
}

const lastUpdated = computed(() =>
  realtime.value.length ? formatUpdatedAt(realtime.value[0].tot_dt) : ''
)

async function loadPrediction(csoSn) {
  const { hour, dayOfWeek } = nowKST()
  // JS 요일(0=일…6=토) → Python(0=월…6=일)
  const dow = dayOfWeek === 0 ? 6 : dayOfWeek - 1
  try {
    const res = await fetch(`/api/prediction/${csoSn}?dow=${dow}&hour=${hour}`)
    prediction.value = await res.json()
  } catch { /* silent */ }
}

async function load() {
  loading.value = true
  error.value = null
  try {
    office.value = await fetchOffice(props.csoSn)
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
  if (!office.value) return
  await loadPrediction(office.value.cso_sn)

  if (!isWithinOperatingHours.value) {
    realtime.value = []
    realtimeLoading.value = false
    return
  }

  realtimeLoading.value = true
  await fetchRealtime(office.value.stdg_cd)
    .then(async data => {
      // 해당 민원실 항목만, 업무명 없는 항목 제외
      realtime.value = data.items.filter(
        item => item.cso_sn === office.value.cso_sn && item.task_nm?.trim()
      )
      // 실시간 업무명을 쿼리로 삼아 정부24 신청 링크 조회
      if (realtime.value.length) {
        const q = encodeURIComponent(realtime.value.map(r => r.task_nm).join(' '))
        try {
          const res = await fetch(`/api/chat/gov24-links?q=${q}`)
          gov24Links.value = await res.json()
        } catch { /* silent */ }
      }
    })
    .catch(() => {})
    .finally(() => { realtimeLoading.value = false })
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col min-h-full bg-background">
    <section class="relative overflow-hidden bg-[#0f172a] text-white flex-shrink-0">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,110,248,0.34),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(14,165,233,0.18),_transparent_18%)]"></div>
      <div class="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-[#0f172a] to-background pointer-events-none"></div>

      <div v-if="office" class="relative page-gutter pt-4 pb-12">
        <p class="text-[11px] uppercase tracking-[0.22em] text-white/45">Office Detail</p>
        <h1 class="hero-copy mt-2 font-bold tracking-tight break-keep">{{ office.cso_nm }}</h1>
        <p class="mt-3 max-w-[22rem] text-sm leading-6 text-white/70">
          운영시간, 길찾기, 실시간 대기현황, AI 방문 예측을 한 화면에서 확인할 수 있습니다.
        </p>
      </div>
    </section>

    <LoadingSpinner v-if="loading" />
    <p v-else-if="error" class="text-center py-12 text-destructive text-sm flex items-center justify-center gap-1.5">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v4m0 4h.01M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/></svg>
      {{ error }}
    </p>

    <template v-else-if="office">
      <section class="relative -mt-8 page-gutter z-10">
        <div class="overflow-hidden rounded-[26px] border border-white/70 bg-white shadow-[0_20px_70px_rgba(15,23,42,0.16)]">
          <OfficeMap
            :offices="[office]"
            :user-pos="userPos"
            height="var(--detail-map-height)"
          />
        </div>
      </section>

      <OfficeInfoCard :office="office" :user-pos="userPos" />

      <div v-if="prediction" class="mx-4 mt-3 overflow-hidden rounded-[22px] border border-slate-200 bg-white shadow-[0_14px_40px_rgba(15,23,42,0.08)]">
        <div class="flex items-center justify-between px-4 py-3.5 border-b border-slate-100">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary/60">AI 방문 예측</p>
          <span
            v-if="prediction.level !== 'unknown'"
            class="text-sm font-bold px-3 py-1.5 rounded-full"
            :class="{
              'bg-emerald-100 text-emerald-700': prediction.level === '여유',
              'bg-amber-100 text-amber-700': prediction.level === '보통',
              'bg-red-100 text-red-600': prediction.level === '혼잡',
            }"
          >{{ prediction.level }}</span>
        </div>
        <div class="px-4 py-4">
          <template v-if="prediction.level === 'unknown'">
            <p class="text-[15px] text-muted-foreground">추후 업데이트 예정입니다</p>
          </template>
          <template v-else>
            <p class="text-[17px] font-bold text-foreground">{{ prediction.message }}</p>
            <div class="mt-2.5 flex items-center gap-3">
              <p v-if="prediction.predicted !== null" class="text-sm text-muted-foreground">
                이 시간대 평균 대기 <span class="font-semibold text-foreground">{{ prediction.predicted }}명</span>
              </p>
              <span v-if="prediction.predicted !== null && prediction.sample_count > 0" class="text-slate-300">·</span>
              <p v-if="prediction.sample_count > 0" class="text-sm text-muted-foreground">
                수집 데이터 {{ prediction.sample_count }}건
              </p>
            </div>
          </template>
        </div>
      </div>

      <template v-if="isWithinOperatingHours">
        <div class="flex items-center justify-between px-4 pt-6 pb-3">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">Realtime Queue</p>
            <h3 class="mt-1 font-bold text-lg text-foreground">실시간 창구 대기현황</h3>
          </div>
          <span v-if="lastUpdated" class="text-xs text-muted-foreground">{{ lastUpdated }}</span>
        </div>

        <LoadingSpinner v-if="realtimeLoading" text="대기현황 조회 중…" />

        <div v-else-if="!realtime.length" class="px-4 pb-6">
          <p class="text-sm text-muted-foreground">추후 업데이트 예정입니다</p>
        </div>

        <div v-else class="px-4 pb-6 flex flex-col gap-3">
          <QueueCard v-for="item in realtime" :key="item.task_no" :item="item" />
        </div>
      </template>

      <!-- 정부24 온라인 신청 링크 -->
      <div v-if="gov24Links.length" class="mx-4 mb-8 mt-1 overflow-hidden rounded-[22px] border border-slate-200 bg-white shadow-[0_14px_40px_rgba(15,23,42,0.08)]">
        <div class="px-4 py-3.5 border-b border-slate-100">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary/60">Online Application</p>
          <h3 class="mt-1 font-bold text-base text-foreground">정부24에서 바로 신청</h3>
          <p class="mt-0.5 text-xs text-muted-foreground">방문 없이 온라인으로도 처리할 수 있는 민원을 확인하세요.</p>
        </div>
        <div class="px-4 py-4 flex flex-col gap-2">
          <a
            v-for="link in gov24Links"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center justify-between rounded-xl border border-primary/20 bg-primary/5 px-4 py-3 hover:bg-primary/10 transition-colors group"
          >
            <span class="text-sm font-semibold text-primary">{{ link.label }}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-primary/50 group-hover:text-primary transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
          </a>
        </div>
      </div>
    </template>
  </div>
</template>
