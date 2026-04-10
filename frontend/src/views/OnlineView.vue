<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '../components/AppHeader.vue'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const router = useRouter()

const catalog = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('전체')

const CATEGORIES = ['전체', '주민등록/등본', '전입/가족관계', '여권', '인감/증명', '운전면허', '토지/부동산', '세금/납세', '병역']

async function loadCatalog() {
  try {
    const res = await fetch('/api/chat/gov24-catalog')
    catalog.value = await res.json()
  } catch {
    catalog.value = []
  } finally {
    loading.value = false
  }
}

const filtered = computed(() => {
  return catalog.value.filter(item => {
    const matchCategory = selectedCategory.value === '전체' || item.category === selectedCategory.value
    const q = searchQuery.value.trim()
    const matchSearch = !q || item.label.includes(q) || item.category.includes(q)
    return matchCategory && matchSearch
  })
})

// 카테고리별 이모지
const CATEGORY_EMOJI = {
  '주민등록/등본': '🪪',
  '전입/가족관계': '🏠',
  '여권': '✈️',
  '인감/증명': '🔏',
  '운전면허': '🚗',
  '토지/부동산': '🏗️',
  '세금/납세': '💰',
  '병역': '🪖',
  '기타': '📄',
}

onMounted(loadCatalog)
</script>

<template>
  <div class="flex flex-col min-h-dvh bg-background safe-bottom">
    <!-- 헤더 -->
    <section class="relative overflow-hidden bg-[#0f172a] text-white flex-shrink-0">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.32),_transparent_34%),radial-gradient(circle_at_top_right,_rgba(59,110,248,0.16),_transparent_18%)]" />
      <AppHeader title="" />

      <!-- 모드 토글 -->
      <div class="relative page-gutter pt-2 pb-2">
        <div class="inline-flex items-center rounded-full bg-white/10 p-1 gap-1">
          <button
            class="rounded-full px-4 py-1.5 text-xs font-semibold transition-colors text-white/60 hover:text-white/80"
            @click="router.push('/')"
          >
            🏢 방문 민원
          </button>
          <button
            class="rounded-full px-4 py-1.5 text-xs font-semibold transition-colors bg-white text-slate-900 shadow-sm"
          >
            🌐 온라인 민원
          </button>
        </div>
      </div>

      <div class="relative page-gutter pt-1 pb-8">
        <p class="text-[11px] uppercase tracking-[0.24em] text-white/45">Online Application</p>
        <h1 class="hero-copy mt-2 font-bold tracking-tight">민원을 집에서 처리하세요</h1>
        <p class="mt-3 text-sm leading-7 text-white/70">
          정부24에서 <span class="font-semibold text-sky-300">본인인증</span> 후 신청할 수 있습니다.<br>
          일부 민원은 방문이 필요합니다.
        </p>
      </div>
    </section>

    <!-- 검색 + 카테고리 필터 -->
    <div class="relative -mt-5 mx-4 z-10">
      <div class="rounded-[22px] border border-white/70 bg-white shadow-[0_20px_60px_rgba(15,23,42,0.14)] px-4 py-4">
        <!-- 검색 입력 -->
        <div class="relative">
          <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="민원 이름 검색…"
            class="w-full pl-9 pr-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-sm outline-none focus:border-primary focus:bg-white transition-colors"
          />
        </div>

        <!-- 카테고리 필터 -->
        <div class="mt-3 flex flex-wrap gap-1.5">
          <button
            v-for="cat in CATEGORIES"
            :key="cat"
            class="rounded-full px-3 py-1 text-[11px] font-semibold transition-colors"
            :class="selectedCategory === cat
              ? 'bg-slate-950 text-white shadow-sm'
              : 'bg-slate-100 text-slate-600 hover:bg-slate-200'"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
      </div>
    </div>

    <!-- 서비스 카드 목록 -->
    <LoadingSpinner v-if="loading" text="서비스 목록 불러오는 중…" />

    <div v-else-if="!filtered.length" class="flex-1 flex flex-col items-center justify-center py-16 text-muted-foreground">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-12 h-12 mb-3 opacity-30" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <p class="text-sm">검색 결과가 없습니다</p>
    </div>

    <div v-else class="px-4 pt-4 pb-8 grid grid-cols-1 gap-3">
      <a
        v-for="item in filtered"
        :key="item.code"
        :href="item.url"
        target="_blank"
        rel="noopener noreferrer"
        class="flex items-center gap-4 rounded-[20px] border border-slate-200 bg-white px-4 py-4 shadow-[0_4px_16px_rgba(15,23,42,0.06)] hover:shadow-[0_8px_24px_rgba(15,23,42,0.12)] hover:border-primary/30 active:scale-[0.99] transition-all group"
      >
        <!-- 이모지 아이콘 -->
        <div class="w-12 h-12 flex-shrink-0 rounded-2xl bg-slate-100 flex items-center justify-center text-2xl group-hover:bg-primary/10 transition-colors">
          {{ CATEGORY_EMOJI[item.category] ?? '📄' }}
        </div>

        <!-- 내용 -->
        <div class="flex-1 min-w-0">
          <p class="font-semibold text-[15px] text-foreground leading-snug truncate">{{ item.label }}</p>
          <p class="mt-0.5 text-xs text-muted-foreground">{{ item.category }}</p>
          <div class="mt-1.5 flex items-center gap-1.5">
            <span class="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              인터넷 신청 가능
            </span>
          </div>
        </div>

        <!-- 화살표 -->
        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-muted-foreground/40 group-hover:text-primary flex-shrink-0 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 18l6-6-6-6"/>
        </svg>
      </a>
    </div>


  </div>
</template>
