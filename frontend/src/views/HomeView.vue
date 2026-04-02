<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOffices, geocodeAddress } from '../api/index.js'
import AppHeader from '../components/AppHeader.vue'
import AddressSearch from '../components/AddressSearch.vue'
import OfficeMap from '../components/OfficeMap.vue'
import OfficeCard from '../components/OfficeCard.vue'

const router = useRouter()
const mapRef = ref(null)
const showNearbyModal = ref(false)
const LOCATION_STORAGE_KEY = 'minwon_now_user_pos'
const CATEGORY_STORAGE_KEY = 'minwon_now_category'
const selectedCategory = ref('전체')
const CATEGORIES = [
  '전체',
  '주민등록/등본',
  '전입/가족관계',
  '여권',
  '인감/증명',
  '건축/인허가',
  '사업/세무',
]

const offices = ref([])
const userPos = ref(null)
const userLocationLabel = ref('')
const locationStatus = ref('loading') // 'loading' | 'granted' | 'denied'
const searchLoading = ref(false)
const searchError = ref('')
const NEARBY_RADIUS_KM = 20

function saveUserPos(pos) {
  if (!pos) return
  sessionStorage.setItem(LOCATION_STORAGE_KEY, JSON.stringify(pos))
}

function restoreUserPos() {
  const raw = sessionStorage.getItem(LOCATION_STORAGE_KEY)
  if (!raw) return false
  try {
    const parsed = JSON.parse(raw)
    if (typeof parsed?.lat !== 'number' || typeof parsed?.lng !== 'number') return false
    userPos.value = parsed
    locationStatus.value = 'granted'
    return true
  } catch {
    return false
  }
}

function saveCategory(category) {
  selectedCategory.value = category
  sessionStorage.setItem(CATEGORY_STORAGE_KEY, category)
}

function restoreCategory() {
  const stored = sessionStorage.getItem(CATEGORY_STORAGE_KEY)
  if (stored && CATEGORIES.includes(stored)) selectedCategory.value = stored
}

function haversine(lat1, lon1, lat2, lon2) {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

async function waitForKakaoServices() {
  for (let i = 0; i < 30; i += 1) {
    if (window.kakao?.maps?.services) return true
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  return false
}

function reverseGeocode(lat, lng) {
  return new Promise(resolve => {
    const geocoder = new window.kakao.maps.services.Geocoder()
    geocoder.coord2Address(lng, lat, (result, status) => {
      if (status !== window.kakao.maps.services.Status.OK || !result.length) {
        resolve('')
        return
      }

      const road = result[0]?.road_address?.address_name
      const jibun = result[0]?.address
      resolve(
        road
          || [jibun?.region_1depth_name, jibun?.region_2depth_name, jibun?.region_3depth_name].filter(Boolean).join(' ')
          || ''
      )
    })
  })
}

async function updateUserLocationLabel(pos) {
  if (!pos) {
    userLocationLabel.value = ''
    return
  }

  const ready = await waitForKakaoServices()
  if (!ready) {
    userLocationLabel.value = ''
    return
  }

  userLocationLabel.value = await reverseGeocode(pos.lat, pos.lng)
}

const nearbyOffices = computed(() => {
  if (!offices.value.length) return []
  const mapped = offices.value
    .filter(o => o.lat && o.lot)
    .map(o => ({
      ...o,
      dist: userPos.value
        ? haversine(userPos.value.lat, userPos.value.lng, o.lat, o.lot)
        : null,
    }))

  if (!userPos.value) return []

  return mapped
    .filter(o => o.dist != null && o.dist <= NEARBY_RADIUS_KM)
    .sort((a, b) => (a.dist ?? Infinity) - (b.dist ?? Infinity))
})

const mapOffices = computed(() => {
  if (userPos.value) return nearbyOffices.value
  return offices.value.filter(o => o.lat && o.lot)
})

const officeCountLabel = computed(() => {
  if (userPos.value) return `${nearbyOffices.value.length}곳`
  return `${offices.value.length}곳`
})

const sortedOffices = computed(() => {
  if (!offices.value.length) return []
  return offices.value
    .filter(o => o.lat && o.lot)
    .map(o => ({
      ...o,
      dist: userPos.value
        ? haversine(userPos.value.lat, userPos.value.lng, o.lat, o.lot)
        : null,
    }))
    .sort((a, b) => (a.dist ?? Infinity) - (b.dist ?? Infinity))
})

const heroStatus = computed(() => {
  if (locationStatus.value === 'loading') {
    return {
      dot: 'bg-amber-400',
      text: '현재 위치를 확인하는 중입니다',
    }
  }
  if (userPos.value) {
    return {
      dot: 'bg-emerald-400',
      text: `현재 위치 기준 ${NEARBY_RADIUS_KM}km 이내 민원실만 보여줘요`,
    }
  }
  return {
    dot: 'bg-rose-400',
    text: '지역을 검색하면 가까운 민원실을 바로 찾아드려요',
  }
})

const topOffice = computed(() => nearbyOffices.value[0] ?? null)

const currentLocationText = computed(() => {
  if (!userPos.value) return '현재 위치 정보 없음'
  if (userLocationLabel.value) return `현재 위치 ${userLocationLabel.value}`
  return '현재 위치 확인 중'
})

async function handleSearch(query) {
  searchLoading.value = true
  searchError.value = ''
  try {
    const pos = await geocodeAddress(query)
    userPos.value = pos
    locationStatus.value = 'granted'
    saveUserPos(pos)
    await updateUserLocationLabel(pos)
  } catch (e) {
    searchError.value = e.message
  } finally {
    searchLoading.value = false
  }
}

function handleOfficeSelect(office) {
  showNearbyModal.value = false
  mapRef.value?.flyTo(office.lat, office.lot, 3)
  router.push(`/office/${office.cso_sn}`)
}

function openChatRecommendation() {
  router.push('/chat')
}

function requestGeolocation() {
  locationStatus.value = 'loading'
  navigator.geolocation.getCurrentPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => {
      userPos.value = { lat, lng }
      locationStatus.value = 'granted'
      saveUserPos(userPos.value)
      updateUserLocationLabel(userPos.value)
    },
    () => {
      if (!restoreUserPos()) locationStatus.value = 'denied'
      else updateUserLocationLabel(userPos.value)
    },
    { timeout: 8000 }
  )
}

onMounted(async () => {
  offices.value = await fetchOffices()
  restoreCategory()
  const restored = restoreUserPos()
  if (restored) updateUserLocationLabel(userPos.value)
  if (!restored && navigator.geolocation) requestGeolocation()
  else if (!restored) locationStatus.value = 'denied'
})
</script>

<template>
  <div class="relative min-h-dvh w-full bg-background safe-bottom pb-32">
    <section class="relative overflow-hidden bg-[#0f172a] text-white">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,110,248,0.38),_transparent_38%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.16),_transparent_22%)]"></div>
      <div class="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-b from-transparent to-background"></div>

      <AppHeader title="민원나우" />

      <div class="relative page-gutter pt-2 pb-10">
        <div class="mt-1 flex items-end gap-2.5">
          <h1 class="brand-display hero-brand text-white drop-shadow-[0_10px_30px_rgba(15,23,42,0.45)]">
            민원나우
          </h1>
          <span class="mb-1 inline-flex items-center rounded-full bg-[#7dd3fc]/18 px-2.5 py-1 text-[11px] font-semibold text-sky-200 ring-1 ring-inset ring-white/10">
            Beta
          </span>
        </div>

        <div class="mt-3 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur-sm">
            <span class="w-2 h-2 rounded-full" :class="heroStatus.dot"></span>
            {{ heroStatus.text }}
          </span>
          <span class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur-sm">
            <span class="text-white/55">민원실</span>
            {{ officeCountLabel }}
          </span>
        </div>

        <div class="mt-4 space-y-3">
          <div class="rounded-[24px] border border-white/12 bg-white/10 p-2 shadow-[0_24px_60px_rgba(15,23,42,0.35)] backdrop-blur-xl">
            <div class="rounded-[18px] border border-white/10 bg-white/8 px-4 py-3 text-white/90">
              <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/55">Step 1</p>
              <div class="mt-2 flex flex-wrap gap-2">
                <button
                  v-for="category in CATEGORIES"
                  :key="category"
                  class="tap-feedback rounded-full px-3 py-1.5 text-[11px] font-semibold transition-colors"
                  :class="selectedCategory === category
                    ? 'bg-white text-slate-950 shadow-[0_6px_18px_rgba(255,255,255,0.16)]'
                    : 'bg-white/10 text-white/78 hover:bg-white/18 active:bg-white/20'"
                  @click="saveCategory(category)"
                >
                  {{ category }}
                </button>
              </div>
              <p class="mt-2 text-xs text-white/62">
                먼저 민원 종류를 고르면, 이후 AI 안내와 추천이 그 기준을 이어받습니다.
              </p>
            </div>
          </div>

          <div class="rounded-[24px] border border-white/12 bg-white/10 p-2 shadow-[0_24px_60px_rgba(15,23,42,0.35)] backdrop-blur-xl">
            <div class="rounded-[18px] bg-white/96 p-1.5">
              <AddressSearch
                :loading="searchLoading"
                :error="searchError"
                @search="handleSearch"
                @locate="requestGeolocation"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="relative -mt-6 page-gutter z-10">
      <div class="mb-3 rounded-[20px] border border-slate-200/70 bg-white/90 px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.08)]">
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Step 2</p>
        <p class="mt-1 text-sm font-semibold text-foreground">현재 위치 기준으로 가까운 민원실을 확인하세요</p>
        <p class="mt-1 text-xs leading-5 text-muted-foreground">
          지도에서 주변 민원실을 보고, 추천 시작점에서 가장 먼저 확인할 곳을 바로 찾을 수 있습니다.
        </p>
      </div>

      <div class="overflow-hidden rounded-[26px] border border-white/70 bg-white shadow-[0_20px_70px_rgba(15,23,42,0.16)]">
        <div v-if="userPos" class="relative">
          <OfficeMap
            ref="mapRef"
            :offices="mapOffices"
            :user-pos="userPos"
            height="var(--home-map-height)"
            :zoom-level="4"
            @office-click="handleOfficeSelect"
          />
          <div class="pointer-events-none absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-black/18 to-transparent"></div>
          <button
            class="tap-feedback absolute bottom-4 right-4 inline-flex items-center rounded-full bg-white/95 px-4 py-2 text-sm font-semibold text-slate-950 shadow-[0_12px_28px_rgba(15,23,42,0.24)] backdrop-blur"
            @click="showNearbyModal = true"
          >
            가까운 민원실
          </button>
        </div>
        <div v-else class="px-5 py-4 bg-[linear-gradient(135deg,#eef4ff_0%,#f8fafc_60%,#ffffff_100%)]">
          <p class="text-xs font-semibold tracking-[0.18em] text-primary/70 uppercase">Location Setup</p>
          <h2 class="mt-2 text-base font-bold text-foreground">위치를 찾거나 지역을 검색하세요</h2>
          <p class="mt-1 text-sm leading-5 text-muted-foreground">
            위치 권한을 허용하거나 원하는 지역을 검색하면 주변 민원실을 지도와 리스트에 함께 보여드립니다.
          </p>
        </div>

        <div class="border-t border-slate-100 px-4 py-3 bg-white">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="pt-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">추천 시작점</p>
              <p class="mt-1 text-[11px] leading-5 text-muted-foreground break-keep">
                {{ currentLocationText }}
              </p>
            </div>
            <div class="flex shrink-0 flex-wrap justify-end gap-2">
              <button
                class="tap-feedback inline-flex min-h-9 items-center rounded-full bg-primary-light px-3.5 py-2 text-[12px] font-semibold text-primary"
                @click="showNearbyModal = true"
              >
                가까운 민원실 보기
              </button>
            </div>
          </div>
          <div class="mt-2 min-w-0">
            <p class="mt-1 text-sm font-semibold leading-6 text-foreground break-keep">
              {{ selectedCategory === '전체' ? '통합으로 안내 준비됨' : `${selectedCategory} 기준으로 안내 준비됨` }}
            </p>
            <p v-if="selectedCategory !== '전체'" class="mt-1 text-[11px] leading-5 text-muted-foreground break-keep">
              위치 추천 전 선택한 민원 기준을 먼저 반영합니다.
            </p>
          </div>
        </div>
      </div>
    </section>

    <div
      v-if="showNearbyModal"
      class="absolute inset-0 z-[80] flex items-end bg-slate-950/38 backdrop-blur-[2px]"
      @click.self="showNearbyModal = false"
    >
      <section class="w-full rounded-t-[30px] bg-white shadow-[0_-20px_60px_rgba(15,23,42,0.18)] max-h-[72dvh] pb-[max(16px,env(safe-area-inset-bottom))]">
        <div class="flex justify-center pt-3 pb-2">
          <div class="h-1.5 w-14 rounded-full bg-slate-200"></div>
        </div>

        <div class="flex items-center justify-between px-5 pb-3">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Nearby Offices</p>
            <h3 class="mt-1 text-lg font-bold text-foreground">반경 {{ NEARBY_RADIUS_KM }}km 이내 민원실</h3>
          </div>
          <button
            class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1.5 text-[11px] font-semibold text-slate-700"
            @click="showNearbyModal = false"
          >
            닫기
          </button>
        </div>

        <div v-if="!userPos" class="px-5 py-8 text-center text-sm text-muted-foreground">
          위치를 찾거나 지역을 검색하면 가까운 민원실 목록이 나타납니다.
        </div>

        <div v-else-if="!nearbyOffices.length" class="px-5 py-8 text-center text-sm text-muted-foreground">
          현재 위치 기준 {{ NEARBY_RADIUS_KM }}km 이내에 표시할 민원실이 없습니다.
        </div>

        <ul v-else class="touch-scroll max-h-[54dvh] px-4 pb-2 flex flex-col gap-2.5">
          <OfficeCard
            v-for="o in nearbyOffices"
            :key="o.cso_sn"
            :office="o"
            @select="handleOfficeSelect"
          />
        </ul>
      </section>
    </div>
  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }
</style>


