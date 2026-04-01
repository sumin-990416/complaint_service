<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'

const props = defineProps({
  offices: { type: Array, default: () => [] },
  userPos: { type: Object, default: null }, // { lat, lng }
  height: { type: String, default: '45vh' },
})

const emit = defineEmits(['officeClick'])

const mapEl = ref(null)
const mapError = ref('')
let map = null
let userOverlay = null
const officeOverlays = []

const KAKAO_KEY = import.meta.env.VITE_KAKAO_MAPS_KEY

// SVG dot 마커 이미지 팩토리
function makeDotImage(color, size = 18, stroke = '#fff') {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}">
    <circle cx="${size/2}" cy="${size/2}" r="${size/2 - 2}" fill="${color}" stroke="${stroke}" stroke-width="2.5"/>
  </svg>`
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`
}

function loadKakaoScript() {
  return new Promise((resolve, reject) => {
    if (window.kakao?.maps?.services) { resolve(); return }
    if (window.kakao?.maps) {
      // SDK는 있지만 services 없으면 services만 추가 로드
      const s = document.createElement('script')
      s.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_KEY}&libraries=services&autoload=false`
      s.onload = () => window.kakao.maps.load(resolve)
      s.onerror = () => reject(new Error('카카오 services 라이브러리 로드 실패'))
      document.head.appendChild(s)
      return
    }
    if (!KAKAO_KEY) { reject(new Error('VITE_KAKAO_MAPS_KEY 환경변수가 없습니다')); return }
    const s = document.createElement('script')
    s.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${KAKAO_KEY}&libraries=services&autoload=false`
    s.onload = () => window.kakao.maps.load(resolve)
    s.onerror = () => reject(new Error('카카오 SDK 로드 실패 (도메인 미등록 또는 키 오류)'))
    document.head.appendChild(s)
  })
}

function initMap(lat, lng, level) {
  if (map) return
  map = new window.kakao.maps.Map(mapEl.value, {
    center: new window.kakao.maps.LatLng(lat, lng),
    level,
  })
}

function renderMarkers() {
  officeOverlays.forEach(m => m.setMap(null))
  officeOverlays.length = 0

  const imgSrc = makeDotImage('#1a73e8', 18)
  const imgSize = new window.kakao.maps.Size(18, 18)
  const imgOpts = { offset: new window.kakao.maps.Point(9, 9) }
  const markerImg = new window.kakao.maps.MarkerImage(imgSrc, imgSize, imgOpts)

  for (const o of props.offices) {
    if (!o.lat || !o.lot) continue
    const pos = new window.kakao.maps.LatLng(o.lat, o.lot)
    const marker = new window.kakao.maps.Marker({ position: pos, image: markerImg })
    marker.setMap(map)

    // 인포윈도우 (팝업)
    const iw = new window.kakao.maps.InfoWindow({
      content: `<div style="padding:8px 12px;font-size:13px;font-weight:600;color:#111;max-width:180px;line-height:1.5;">`
        + `${o.cso_nm}`
        + `<br><span style="font-size:11px;color:#777;font-weight:400">${o.road_nm_addr ?? ''}</span></div>`,
      removable: true,
    })

    window.kakao.maps.event.addListener(marker, 'click', () => {
      iw.open(map, marker)
      emit('officeClick', o)
    })

    officeOverlays.push(marker)
  }
}

function placeUserMarker(lat, lng) {
  if (userOverlay) userOverlay.setMap(null)
  const imgSrc = makeDotImage('#22c55e', 22, '#fff')
  const imgSize = new window.kakao.maps.Size(22, 22)
  const imgOpts = { offset: new window.kakao.maps.Point(11, 11) }
  const markerImg = new window.kakao.maps.MarkerImage(imgSrc, imgSize, imgOpts)
  userOverlay = new window.kakao.maps.Marker({
    position: new window.kakao.maps.LatLng(lat, lng),
    image: markerImg,
  })
  userOverlay.setMap(map)
}

function flyTo(lat, lng, level = 4) {
  map?.setCenter(new window.kakao.maps.LatLng(lat, lng))
  map?.setLevel(level)
}

defineExpose({ flyTo })

watch(() => props.offices, () => { if (map) renderMarkers() }, { deep: true })

watch(() => props.userPos, (pos) => {
  if (!map) return
  if (pos) {
    map.setCenter(new window.kakao.maps.LatLng(pos.lat, pos.lng))
    map.setLevel(5)
    placeUserMarker(pos.lat, pos.lng)
  } else if (userOverlay) {
    userOverlay.setMap(null)
    userOverlay = null
  }
})

function fitToMarkers() {
  if (!map || !props.offices.length) return
  const bounds = new window.kakao.maps.LatLngBounds()
  let count = 0
  for (const o of props.offices) {
    if (!o.lat || !o.lot) continue
    bounds.extend(new window.kakao.maps.LatLng(o.lat, o.lot))
    count++
  }
  if (props.userPos) {
    bounds.extend(new window.kakao.maps.LatLng(props.userPos.lat, props.userPos.lng))
  }
  if (count > 0) map.setBounds(bounds)
}

onMounted(async () => {
  try {
    await loadKakaoScript()
    await nextTick()
    const lat = props.userPos?.lat ?? 36.5
    const lng = props.userPos?.lng ?? 127.5
    const level = props.userPos ? 5 : 8
    initMap(lat, lng, level)
    renderMarkers()
    if (props.userPos) {
      placeUserMarker(props.userPos.lat, props.userPos.lng)
    } else {
      fitToMarkers()
    }
  } catch (e) {
    mapError.value = e.message
    console.error('[OfficeMap]', e)
  }
})
</script>

<template>
  <div class="w-full relative" :style="{ height: height }">
    <div ref="mapEl" class="w-full h-full"></div>
    <div
      v-if="mapError"
      class="absolute inset-0 flex items-center justify-center bg-muted text-sm text-destructive p-4 text-center"
    >
      ⚠️ {{ mapError }}
    </div>
  </div>
</template>
