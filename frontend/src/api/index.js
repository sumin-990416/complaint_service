const BASE = '/api'

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
  // services 로드 대기 (최대 3초)
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
        return
      }
      // addressSearch 실패 시 keywordSearch 폴백 (세종특별자치시 등 행정구역명)
      const places = new window.kakao.maps.services.Places()
      places.keywordSearch(query, (placeResult, placeStatus) => {
        if (placeStatus === window.kakao.maps.services.Status.OK && placeResult.length) {
          resolve({ lat: parseFloat(placeResult[0].y), lng: parseFloat(placeResult[0].x) })
        } else {
          reject(new Error('정확한 지역명(주소)을 입력해주세요'))
        }
      })
    })
  })
}
