const BASE = '/api'
import { lookupCentroid } from '../lib/regionCentroids.js'

export async function fetchOffices() {
  const res = await fetch(`${BASE}/offices`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchOffice(csoSn) {
  const res = await fetch(`${BASE}/offices/${csoSn}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchRealtime(stdgCd) {
  const res = await fetch(`${BASE}/realtime?stdg_cd=${stdgCd}`)
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function geocodeAddress(query) {
  // 1순위: 정적 행정구역 좌표표 (즉시)
  const centroid = lookupCentroid(query)
  if (centroid) return centroid

  // 2순위: 백엔드 /api/geocode 프록시 (카카오 로컬 REST API)
  try {
    const res = await fetch(`${BASE}/geocode?q=${encodeURIComponent(query)}`)
    if (res.ok) {
      const data = await res.json()
      if (data.lat && data.lng) return data
    }
  } catch {
    // 백엔드 실패 시 SDK 폴백
  }

  // 3순위: 카카오 Maps JS SDK 폴백
  for (let i = 0; i < 30; i++) {
    if (window.kakao?.maps?.services) break
    await new Promise(r => setTimeout(r, 100))
  }
  if (!window.kakao?.maps?.services) {
    throw new Error('카카오 지도 SDK가 아직 로드되지 않았습니다. 페이지를 새로고침 해주세요.')
  }
  return new Promise((resolve, reject) => {
    const geocoder = new window.kakao.maps.services.Geocoder()
    geocoder.addressSearch(query, (result, status) => {
      if (status === window.kakao.maps.services.Status.OK && result.length) {
        resolve({ lat: parseFloat(result[0].y), lng: parseFloat(result[0].x) })
      } else {
        reject(new Error('정확한 지역명(주소)을 입력해주세요'))
      }
    })
  })
}
