import { ref, computed } from 'vue'

/**
 * 바텀시트를 아래로 드래그해서 닫는 기능을 제공하는 composable
 * @param {Function} closeFn - 시트를 닫는 함수
 * @param {number} threshold - 닫힘 판정 거리(px), 기본 120
 */
export function useDragToClose(closeFn, threshold = 120) {
  const dragY = ref(0)
  let startY = 0
  let startTime = 0
  let isDragging = false

  const sheetStyle = computed(() => {
    if (dragY.value <= 0) return {}
    return {
      transform: `translateY(${dragY.value}px)`,
      transition: 'none',
    }
  })

  function onTouchStart(e) {
    startY = e.touches[0].clientY
    startTime = Date.now()
    isDragging = true
    dragY.value = 0
  }

  function onTouchMove(e) {
    if (!isDragging) return
    const delta = e.touches[0].clientY - startY
    if (delta > 0) {
      dragY.value = delta
      // 드래그 중에는 시트 내 스크롤 방지
      e.preventDefault()
    }
  }

  function onTouchEnd() {
    if (!isDragging) return
    isDragging = false

    const elapsed = Date.now() - startTime
    const velocity = dragY.value / elapsed // px/ms

    if (dragY.value >= threshold || velocity > 0.5) {
      // 빠르게 튕겨내리기
      dragY.value = window.innerHeight
      setTimeout(() => {
        dragY.value = 0
        closeFn()
      }, 180)
    } else {
      // 원위치로 스프링백
      dragY.value = 0
    }
  }

  function resetDrag() {
    dragY.value = 0
  }

  return { sheetStyle, onTouchStart, onTouchMove, onTouchEnd, resetDrag }
}
