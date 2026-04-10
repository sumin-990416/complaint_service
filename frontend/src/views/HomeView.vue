<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOffices, geocodeAddress } from '../api/index.js'

import AddressSearch from '../components/AddressSearch.vue'
import OfficeMap from '../components/OfficeMap.vue'
import OfficeCard from '../components/OfficeCard.vue'
import { useDragToClose } from '../composables/useDragToClose.js'

const KAKAO_KEY = import.meta.env.VITE_KAKAO_MAPS_KEY

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
const locationStatus = ref('loading')
const searchLoading = ref(false)
const searchError = ref('')
const RADIUS_OPTIONS = [1, 5, 10, 20]
const NEARBY_RADIUS_KM = ref(5)
const showRadiusModal = ref(false)
const pendingRadius = ref(5)
const RADIUS_TONE = {
  active: 'bg-primary text-white shadow-[0_6px_18px_rgba(59,110,248,0.35)]',
  label: 'text-primary',
  line: 'bg-primary',
}
let bodyLockScrollY = 0
const CATEGORY_RULES = {
  '주민등록/등본': ['주민센터', '행정복지센터', '동사무소', '읍사무소', '면사무소', '출장소', '구청', '시청', '군청'],
  '전입/가족관계': ['주민센터', '행정복지센터', '동사무소', '읍사무소', '면사무소', '출장소', '구청', '시청', '군청'],
  '여권': ['여권', '구청', '시청', '군청'],
  '인감/증명': ['주민센터', '행정복지센터', '동사무소', '읍사무소', '면사무소', '출장소', '구청', '시청', '군청'],
  '건축/인허가': ['시청', '구청', '군청', '도청'],
  '사업/세무': ['세무서', '시청', '구청', '군청'],
}
const CATEGORY_EXCLUDES = {
  '여권': ['주민센터', '행정복지센터', '동사무소', '읍사무소', '면사무소'],
  '건축/인허가': ['주민센터', '행정복지센터', '동사무소', '읍사무소', '면사무소'],
}

function getRadiusTone(radius) {
  return RADIUS_TONE
}

function lockBodyScroll() {
  const container = document.querySelector('.app-scroll-container')
  if (!container) return
  bodyLockScrollY = container.scrollTop
  container.style.overflow = 'hidden'
}

function unlockBodyScroll() {
  const container = document.querySelector('.app-scroll-container')
  if (!container) return
  container.style.overflow = ''
  container.scrollTop = bodyLockScrollY
}

function officeSearchText(office) {
  return [office.cso_nm, office.road_nm_addr, office.lotno_addr]
    .filter(Boolean)
    .join(' ')
}

function matchesCategory(office, category) {
  if (category === '전체') return true

  const searchText = officeSearchText(office)
  const includes = CATEGORY_RULES[category] ?? []
  const excludes = CATEGORY_EXCLUDES[category] ?? []
  const included = includes.some(keyword => searchText.includes(keyword))
  const excluded = excludes.some(keyword => searchText.includes(keyword))

  return included && !excluded
}

function openNearbyModal() {
  nearbyResetDrag()
  showNearbyModal.value = true
  lockBodyScroll()
}

function closeNearbyModal() {
  showNearbyModal.value = false
  unlockBodyScroll()
}

function openRadiusModal() {
  pendingRadius.value = NEARBY_RADIUS_KM.value
  radiusResetDrag()
  showRadiusModal.value = true
  lockBodyScroll()
}

function closeRadiusModal() {
  showRadiusModal.value = false
  unlockBodyScroll()
}

function applyRadius() {
  NEARBY_RADIUS_KM.value = pendingRadius.value
  closeRadiusModal()
}

const {
  sheetStyle: nearbySheetStyle,
  onTouchStart: nearbyTouchStart,
  onTouchMove: nearbyTouchMove,
  onTouchEnd: nearbyTouchEnd,
  resetDrag: nearbyResetDrag,
} = useDragToClose(closeNearbyModal)

const {
  sheetStyle: radiusSheetStyle,
  onTouchStart: radiusTouchStart,
  onTouchMove: radiusTouchMove,
  onTouchEnd: radiusTouchEnd,
  resetDrag: radiusResetDrag,
} = useDragToClose(closeRadiusModal)

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

function loadKakaoSdk() {
  if (window.kakao?.maps?.services) return Promise.resolve()
  return new Promise((resolve) => {
    if (!KAKAO_KEY) {
      resolve()
      return
    }
    if (document.querySelector('script[src*="dapi.kakao.com"]')) {
      const timer = setInterval(() => {
        if (window.kakao?.maps?.services) {
          clearInterval(timer)
          resolve()
        }
      }, 100)
      setTimeout(() => {
        clearInterval(timer)
        resolve()
      }, 5000)
      return
    }

    const script = document.createElement('script')
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_KEY}&libraries=services&autoload=false`
    script.onload = () => window.kakao.maps.load(resolve)
    script.onerror = resolve
    document.head.appendChild(script)
  })
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
  if (!offices.value.length || !userPos.value) return []

  return offices.value
    .filter(office => matchesCategory(office, selectedCategory.value))
    .filter(office => office.lat && office.lot)
    .map(office => ({
      ...office,
      dist: haversine(userPos.value.lat, userPos.value.lng, office.lat, office.lot),
    }))
    .filter(office => office.dist <= NEARBY_RADIUS_KM.value)
    .sort((a, b) => (a.dist ?? Infinity) - (b.dist ?? Infinity))
})

const mapOffices = computed(() => {
  if (userPos.value) return nearbyOffices.value
  return offices.value
    .filter(office => matchesCategory(office, selectedCategory.value))
    .filter(office => office.lat && office.lot)
})

const officeCountLabel = computed(() => {
  if (userPos.value) return `${nearbyOffices.value.length}곳`
  return `${mapOffices.value.length}곳`
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
      text: `현재 위치 기준 ${NEARBY_RADIUS_KM.value}km 이내 민원실만 보여줘요`,
    }
  }
  return {
    dot: 'bg-rose-400',
    text: '지역을 검색하면 가까운 민원실을 바로 찾아드려요',
  }
})

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
    if (!userLocationLabel.value) userLocationLabel.value = query
  } catch (error) {
    searchError.value = error.message
  } finally {
    searchLoading.value = false
  }
}

function handleOfficeSelect(office) {
  closeNearbyModal()
  mapRef.value?.flyTo(office.lat, office.lot, 3)
  router.push(`/office/${office.cso_sn}`)
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
    (err) => {
      // TIMEOUT(3)은 무시 — Safari는 권한 대화상자 표시 중에도 timeout이 흐름
      if (err.code === err.TIMEOUT) return
      if (!restoreUserPos()) locationStatus.value = 'denied'
      else updateUserLocationLabel(userPos.value)
    },
    { timeout: 30000 }
  )
}

onMounted(async () => {
  loadKakaoSdk()
  offices.value = await fetchOffices()
  restoreCategory()
  const restored = restoreUserPos()
  if (restored) updateUserLocationLabel(userPos.value)
  if (navigator.geolocation) requestGeolocation()
  else if (!restored) locationStatus.value = 'denied'
})
</script>

<template>
  <div class="relative w-full bg-background pb-16">
    <section class="relative overflow-hidden bg-[#0f172a] text-white">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(59,110,248,0.38),_transparent_38%),radial-gradient(circle_at_top_right,_rgba(16,185,129,0.16),_transparent_22%)]"></div>
      <div class="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-[#0f172a] to-background"></div>

      <div class="relative page-gutter pt-4 pb-12">
        <div class="mt-1 flex items-center gap-2.5">
          <h1 class="hero-brand text-white font-bold drop-shadow-[0_10px_30px_rgba(15,23,42,0.5)] tracking-tight">민원새길</h1>
        </div>

        <div class="mt-3 flex items-center gap-2 flex-wrap">
          <span class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur-sm">
            <span class="h-2 w-2 rounded-full" :class="heroStatus.dot"></span>
            {{ heroStatus.text }}
          </span>
          <span class="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-medium backdrop-blur-sm">
            <span class="text-white/55">민원실</span>
            {{ officeCountLabel }}
          </span>
        </div>

        <div class="mt-5 rounded-[22px] border border-white/12 bg-white/10 p-2 shadow-[0_24px_60px_rgba(15,23,42,0.35)] backdrop-blur-xl">
          <div class="rounded-[16px] border border-white/10 bg-white/8 px-4 py-3 text-white/90">
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/50 text-left">Step 1 · 민원 종류</p>
            <div class="mt-2.5 flex flex-wrap gap-2">
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
          </div>
        </div>

        <div class="mt-3 rounded-[22px] border border-white/12 bg-white/10 p-2 shadow-[0_24px_60px_rgba(15,23,42,0.35)] backdrop-blur-xl">
          <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-white/50 px-3 pb-1.5 text-left">Step 2 · 시/도/군 선택 (위치 미허용시)</p>
          <div class="rounded-[16px] bg-white/96 p-1.5">
            <AddressSearch
              :loading="searchLoading"
              :error="searchError"
              @search="handleSearch"
              @locate="requestGeolocation"
            />
          </div>
        </div>
      </div>
    </section>

    <section class="relative z-10 -mt-6 page-gutter space-y-3">
      <div class="rounded-[20px] border border-slate-200/70 bg-white/90 px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.08)]">
        <div class="flex items-center justify-between gap-3">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Step 3 · 민원실 찾기</p>
            <p class="mt-0.5 text-sm font-semibold text-foreground">주변 민원실을 지도에서 확인하세요</p>
          </div>
          <div v-if="userPos" class="flex shrink-0 items-center gap-2">
            <span class="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-[11px] font-semibold text-slate-700">
              반경 {{ NEARBY_RADIUS_KM }}km
            </span>
            <button
              class="tap-feedback inline-flex items-center rounded-full border border-primary/20 bg-primary-light px-3 py-1.5 text-[11px] font-semibold text-primary"
              @click="openRadiusModal"
            >
              변경하기
            </button>
          </div>
        </div>
      </div>

      <div class="overflow-hidden rounded-[26px] border border-white/70 bg-white shadow-[0_20px_70px_rgba(15,23,42,0.16)]">
        <div v-if="userPos" class="relative">
          <OfficeMap
            ref="mapRef"
            :offices="mapOffices"
            :user-pos="userPos"
            height="var(--home-map-height)"
            :zoom-level="6"
            @office-click="handleOfficeSelect"
          />
          <div class="pointer-events-none absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-black/18 to-transparent"></div>
        </div>

        <div v-else-if="locationStatus === 'denied'" class="bg-[linear-gradient(135deg,#fff7ed_0%,#fef3c7_60%,#ffffff_100%)] px-5 py-6">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-amber-600">위치 권한 필요</p>
          <h2 class="mt-1.5 text-base font-bold text-foreground">위치 권한을 허용해주세요!</h2>
          <p class="mt-1 text-sm leading-5 text-muted-foreground">
            주소창 옆 <strong>자물쇠(<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 inline-block align-text-bottom" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>)</strong>를 탭해 <strong>위치 → 허용</strong>으로 바꾼 뒤 다시 시도해 주세요.
          </p>
          <button
            class="tap-feedback mt-3 inline-flex items-center gap-2 rounded-full bg-amber-500 px-4 py-2 text-xs font-semibold text-white shadow-sm"
            @click="requestGeolocation"
          >다시 위치 요청하기</button>
        </div>

        <div v-else class="bg-[linear-gradient(135deg,#eef4ff_0%,#f8fafc_60%,#ffffff_100%)] px-5 py-6">
          <p class="text-xs font-semibold uppercase tracking-[0.18em] text-primary/70">위치 미설정</p>
          <h2 class="mt-1.5 text-base font-bold text-foreground">위치 권한을 허용해주세요!</h2>
          <p class="mt-1 text-sm leading-5 text-muted-foreground">
            위치 권한을 허용하면 주변 민원실을 바로 찾고, 검색한 지역도 즉시 지도에 반영합니다.
          </p>
        </div>

        <div v-if="userPos && !mapOffices.length" class="border-t border-slate-100 bg-slate-50 px-4 py-3 text-sm text-muted-foreground">
          {{ selectedCategory === '전체'
            ? '현재 반경 안에 표시할 민원실이 없습니다.'
            : `${selectedCategory} 업무로 추정되는 민원실이 현재 반경 안에 없습니다.` }}
        </div>

        <div class="flex items-center justify-between gap-3 border-t border-slate-100 bg-white px-4 py-3">
          <div class="min-w-0">
            <p class="text-[11px] font-semibold text-muted-foreground">
              {{ selectedCategory === '전체' ? '통합 기준' : `${selectedCategory} 기준` }}
            </p>
            <p class="mt-0.5 truncate text-[11px] leading-5 text-muted-foreground">
              {{ currentLocationText }}
            </p>
          </div>
          <button
            class="tap-feedback inline-flex min-h-9 shrink-0 items-center rounded-full bg-primary px-4 py-2 text-[12px] font-semibold text-white shadow-sm"
            @click="openNearbyModal"
          >민원실 목록</button>
        </div>
      </div>
    </section>

    <div
      v-if="showNearbyModal"
      class="fixed inset-0 z-[80] flex items-end justify-center bg-slate-950/38 backdrop-blur-[2px]"
      @click.self="closeNearbyModal"
    >
      <section
        class="max-h-[72dvh] w-full max-w-[var(--app-max-width)] rounded-t-[30px] bg-white pb-[max(16px,env(safe-area-inset-bottom))] shadow-[0_-20px_60px_rgba(15,23,42,0.18)]"
        :style="nearbySheetStyle"
        style="transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1)"
      >
        <div
          class="flex justify-center pb-2 pt-3 cursor-grab active:cursor-grabbing touch-none"
          @touchstart.passive="nearbyTouchStart"
          @touchmove="nearbyTouchMove"
          @touchend="nearbyTouchEnd"
        >
          <div class="h-1.5 w-14 rounded-full bg-slate-200"></div>
        </div>
        <div class="flex items-center justify-between px-5 pb-3">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Nearby Offices</p>
            <h3 class="mt-1 text-lg font-bold text-foreground">반경 {{ NEARBY_RADIUS_KM }}km 이내 민원실</h3>
          </div>
          <button
            class="inline-flex items-center rounded-full bg-slate-100 px-3 py-1.5 text-[11px] font-semibold text-slate-700"
            @click="closeNearbyModal"
          >닫기</button>
        </div>

        <div v-if="!userPos" class="px-5 py-8 text-center text-sm text-muted-foreground">
          위치를 찾거나 지역을 검색하면 가까운 민원실 목록이 나타납니다.
        </div>
        <div v-else-if="!nearbyOffices.length" class="px-5 py-8 text-center text-sm text-muted-foreground">
          {{ selectedCategory === '전체'
            ? `현재 위치 기준 ${NEARBY_RADIUS_KM}km 이내에 표시할 민원실이 없습니다. 반경을 넓혀보세요.`
            : `${selectedCategory} 업무로 추정되는 민원실이 현재 위치 기준 ${NEARBY_RADIUS_KM}km 이내에 없습니다. 반경을 넓히거나 다른 민원 종류를 선택해보세요.` }}
        </div>
        <ul v-else class="touch-scroll flex max-h-[54dvh] flex-col gap-2.5 px-4 pb-2">
          <OfficeCard
            v-for="office in nearbyOffices"
            :key="office.cso_sn"
            :office="office"
            @select="handleOfficeSelect"
          />
        </ul>
      </section>
    </div>

    <Teleport to="body">
      <Transition name="radius-backdrop">
        <div
          v-if="showRadiusModal"
          class="fixed inset-0 z-[200] flex items-end justify-center bg-slate-950/40 backdrop-blur-[2px]"
          @click.self="closeRadiusModal"
        >
          <Transition name="radius-sheet" appear>
            <div
              class="w-full max-w-[var(--app-max-width)] rounded-t-[28px] bg-white pb-[max(24px,env(safe-area-inset-bottom))] shadow-[0_-20px_60px_rgba(15,23,42,0.18)]"
              :style="radiusSheetStyle"
              style="transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1)"
            >
              <div
                class="flex justify-center pb-1 pt-3 cursor-grab active:cursor-grabbing touch-none"
                @touchstart.passive="radiusTouchStart"
                @touchmove="radiusTouchMove"
                @touchend="radiusTouchEnd"
              >
                <div class="h-1.5 w-14 rounded-full bg-slate-200"></div>
              </div>
              <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
                <h3 class="text-base font-bold text-foreground">반경 설정</h3>
                <button
                  class="tap-feedback rounded-full bg-slate-100 px-3 py-1.5 text-[11px] font-semibold text-slate-700"
                  @click="closeRadiusModal"
                >닫기</button>
              </div>

              <div class="px-6 pb-4 pt-8">
                <div class="relative flex items-center justify-between">
                  <div class="absolute left-5 right-5 h-1.5 rounded-full bg-slate-200"></div>
                  <div
                    class="absolute left-5 h-1.5 rounded-full"
                    :class="getRadiusTone(pendingRadius).line"
                    style="transition: width 0.35s cubic-bezier(0.34,1.56,0.64,1)"
                    :style="{ width: `calc(${(RADIUS_OPTIONS.indexOf(pendingRadius) / (RADIUS_OPTIONS.length - 1)) * 100}% - ${RADIUS_OPTIONS.indexOf(pendingRadius) === 0 ? 0 : RADIUS_OPTIONS.indexOf(pendingRadius) === RADIUS_OPTIONS.length - 1 ? 40 : 20}px)` }"
                  ></div>
                  <button
                    v-for="radius in RADIUS_OPTIONS"
                    :key="radius"
                    class="relative z-10 flex flex-col items-center"
                    @click="pendingRadius = radius"
                  >
                    <span
                      class="flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold shadow"
                      style="transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1)"
                      :class="pendingRadius === radius
                        ? `scale-125 ${getRadiusTone(radius).active}`
                        : 'scale-100 border-2 border-slate-200 bg-white text-slate-500'"
                    >
                      {{ RADIUS_OPTIONS.indexOf(radius) + 1 }}
                    </span>
                  </button>
                </div>

                <div class="mt-3 flex items-center justify-between">
                  <span
                    v-for="radius in RADIUS_OPTIONS"
                    :key="radius"
                    class="w-11 text-center text-[12px] font-semibold"
                    style="transition: color 0.2s"
                    :class="pendingRadius === radius ? getRadiusTone(radius).label : 'text-slate-400'"
                  >{{ radius }}km</span>
                </div>
              </div>

              <div class="px-5 pb-1">
                <p class="mb-4 text-center text-sm text-muted-foreground">
                  선택한 반경: <strong :class="getRadiusTone(pendingRadius).label">{{ pendingRadius }}km</strong> 이내 민원실을 표시합니다
                </p>
                <button
                  class="tap-feedback w-full rounded-2xl py-3.5 text-sm font-bold text-white transition-transform active:scale-[0.98]"
                  :class="getRadiusTone(pendingRadius).active"
                  @click="applyRadius"
                >이 반경으로 적용하기</button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

.radius-backdrop-enter-active, .radius-backdrop-leave-active { transition: opacity 0.25s ease; }
.radius-backdrop-enter-from, .radius-backdrop-leave-to { opacity: 0; }

.radius-sheet-enter-active { transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.radius-sheet-leave-active { transition: transform 0.22s ease-in; }
.radius-sheet-enter-from, .radius-sheet-leave-to { transform: translateY(100%); }
</style>