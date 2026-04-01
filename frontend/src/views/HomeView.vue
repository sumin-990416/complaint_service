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

const offices = ref([])
const userPos = ref(null)
const locationStatus = ref('loading') // 'loading' | 'granted' | 'denied'
const searchLoading = ref(false)
const searchError = ref('')

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

async function handleSearch(query) {
  searchLoading.value = true
  searchError.value = ''
  try {
    const pos = await geocodeAddress(query)
    userPos.value = pos
    locationStatus.value = 'granted'
  } catch (e) {
    searchError.value = e.message
  } finally {
    searchLoading.value = false
  }
}

function handleOfficeSelect(office) {
  mapRef.value?.flyTo(office.lat, office.lot, 3)
  router.push(`/office/${office.cso_sn}`)
}

function requestGeolocation() {
  locationStatus.value = 'loading'
  navigator.geolocation.getCurrentPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => {
      userPos.value = { lat, lng }
      locationStatus.value = 'granted'
    },
    () => { locationStatus.value = 'denied' },
    { timeout: 8000 }
  )
}

onMounted(async () => {
  offices.value = await fetchOffices()
  if (navigator.geolocation) requestGeolocation()
  else locationStatus.value = 'denied'
})
</script>

<template>
  <div class="flex flex-col h-dvh bg-background overflow-hidden">
    <AppHeader title="🏛 내 주변 민원실">
      <template #right>
        <button
          v-if="locationStatus !== 'loading'"
          class="w-9 h-9 flex items-center justify-center rounded-full text-primary-foreground hover:bg-white/20 active:bg-white/30 transition-colors text-base"
          @click="requestGeolocation"
          title="현재 위치로"
        >📍</button>
      </template>
    </AppHeader>

    <transition name="slide-down">
      <AddressSearch
        v-if="locationStatus === 'denied' || locationStatus === 'loading'"
        :loading="searchLoading"
        :error="searchError"
        @search="handleSearch"
      />
    </transition>

    <!-- 위치가 있을 때만 지도 표시 -->
    <OfficeMap
      v-if="userPos"
      ref="mapRef"
      :offices="offices"
      :user-pos="userPos"
      height="45vh"
      @office-click="handleOfficeSelect"
    />

    <!-- 상태바 -->
    <div class="flex items-center gap-2 px-4 py-2 bg-blue-50 border-b border-blue-100 text-xs text-blue-700 flex-shrink-0">
      <template v-if="locationStatus === 'loading'">
        <span class="w-2 h-2 rounded-full bg-amber-400 animate-pulse flex-shrink-0"></span>
        위치 확인 중… 또는 지역을 검색하세요
      </template>
      <template v-else-if="userPos">
        <span class="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0"></span>
        현재 위치 기준 · <strong class="font-semibold ml-1">{{ sortedOffices.length }}개</strong>&nbsp;민원실 (가까운 순)
      </template>
      <template v-else>
        <span class="w-2 h-2 rounded-full bg-red-400 flex-shrink-0"></span>
        지역을 검색하면 가까운 민원실을 찾아드려요
      </template>
    </div>

    <ul class="flex-1 overflow-y-auto p-3 pb-4 flex flex-col gap-2">
      <OfficeCard
        v-for="o in sortedOffices"
        :key="o.cso_sn"
        :office="o"
        @select="handleOfficeSelect"
      />
    </ul>
  </div>
</template>

<style scoped>
.slide-down-enter-active, .slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }
</style>

