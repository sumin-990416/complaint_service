<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { fetchOffice, fetchRealtime } from '../api/index.js'
import AppHeader from '../components/AppHeader.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import OfficeInfoCard from '../components/OfficeInfoCard.vue'
import OfficeMap from '../components/OfficeMap.vue'
import QueueCard from '../components/QueueCard.vue'

const props = defineProps({ csoSn: String })
const router = useRouter()

const office = ref(null)
const realtime = ref([])
const loading = ref(true)
const realtimeLoading = ref(false)
const error = ref(null)
const userPos = ref(null)

if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    ({ coords: { latitude: lat, longitude: lng } }) => { userPos.value = { lat, lng } },
    () => {},
    { timeout: 6000 },
  )
}

function formatUpdatedAt(dt) {
  if (!dt || dt.length < 12) return ''
  return `${dt.slice(8, 10)}:${dt.slice(10, 12)} 기준`
}

const lastUpdated = computed(() =>
  realtime.value.length ? formatUpdatedAt(realtime.value[0].tot_dt) : ''
)

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
  realtimeLoading.value = true
  try {
    const data = await fetchRealtime(office.value.stdg_cd)
    realtime.value = data.items
  } catch { /* silent */ } finally {
    realtimeLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="flex flex-col min-h-dvh bg-muted/30">
    <AppHeader
      :title="office?.cso_nm ?? '민원실'"
      :show-back="true"
      @back="router.back()"
    />

    <LoadingSpinner v-if="loading" />
    <p v-else-if="error" class="text-center py-12 text-destructive text-sm">⚠ {{ error }}</p>

    <template v-else-if="office">
      <!-- 지도: 민원실 위치 -->
      <OfficeMap
        :offices="[office]"
        :user-pos="userPos"
        height="35vh"
      />

      <OfficeInfoCard :office="office" :user-pos="userPos" />

      <!-- 섹션 헤더 -->
      <div class="flex items-center justify-between px-4 pt-6 pb-3">
        <h3 class="font-bold text-base text-foreground">⏱ 실시간 창구 대기현황</h3>
        <span v-if="lastUpdated" class="text-xs text-muted-foreground">{{ lastUpdated }}</span>
      </div>

      <LoadingSpinner v-if="realtimeLoading" text="대기현황 조회 중…" />

      <div v-else-if="!realtime.length" class="flex flex-col items-center gap-2 py-10 text-muted-foreground">
        <span class="text-3xl">🗂</span>
        <p class="text-sm">현재 대기 데이터가 없습니다</p>
      </div>

      <div v-else class="px-4 pb-20 flex flex-col gap-3">
        <QueueCard v-for="item in realtime" :key="item.task_no" :item="item" />
      </div>
    </template>
  </div>
</template>
