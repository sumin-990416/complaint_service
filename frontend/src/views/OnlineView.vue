<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

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

// 카테고리별 SVG path
const CATEGORY_ICON = {
  '주민등록/등본': '<path stroke-linecap="round" stroke-linejoin="round" d="M15 9h3.75M15 12h3.75M15 15h3.75M4.5 19.5h15a2.25 2.25 0 002.25-2.25V6.75A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25v10.5A2.25 2.25 0 004.5 19.5zm6-10.125a1.875 1.875 0 11-3.75 0 1.875 1.875 0 013.75 0zm1.294 6.336a6.721 6.721 0 01-3.17.789 6.721 6.721 0 01-3.168-.789 3.376 3.376 0 016.338 0z"/>',
  '전입/가족관계': '<path stroke-linecap="round" stroke-linejoin="round" d="M3 9.75L12 3l9 6.75V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.75z"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 21V12h6v9"/>',
  '여권': '<path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"/>',
  '인감/증명': '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/>',
  '운전면허': '<path stroke-linecap="round" stroke-linejoin="round" d="M5 17H3v-5l2.5-5h11L19 12v5h-2m-1 0a2 2 0 11-4 0 2 2 0 014 0zm-8 0a2 2 0 11-4 0 2 2 0 014 0z"/>',
  '토지/부동산': '<path stroke-linecap="round" stroke-linejoin="round" d="M2.25 21h19.5m-18-18v18m10.5-18v18m6-13.5V21M6.75 6.75h.75m-.75 3h.75m-.75 3h.75m3-6h.75m-.75 3h.75m-.75 3h.75M6.75 21v-3.375c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21M3 3h12m-.75 4.5H21m-3.75 3.75h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008zm0 3h.008v.008h-.008v-.008z"/>',
  '세금/납세': '<path stroke-linecap="round" stroke-linejoin="round" d="M9 14.25l6-6m4.5-3.493V21.75l-3.75-1.5-3.75 1.5-3.75-1.5-3.75 1.5V4.757c0-1.108.806-2.057 1.907-2.185a48.507 48.507 0 0111.186 0c1.1.128 1.907 1.077 1.907 2.185zM9.75 9h.008v.008H9.75V9zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm4.125 4.5h.008v.008h-.008V13.5zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/>',
  '병역': '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3c-4.418 0-8 3.134-8 7v5l-1 2h18l-1-2v-5c0-3.866-3.582-7-8-7zm0 18a2 2 0 002-2h-4a2 2 0 002 2z"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 10l1.5 1.5L13 8"/>',
  '기타': '<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/>',
}

onMounted(loadCatalog)
</script>

<template>
  <div class="flex flex-col bg-background">
    <!-- 헤더 -->
    <section class="relative overflow-hidden bg-[#0f172a] text-white flex-shrink-0">
      <div class="absolute inset-0 " />
      <div class="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent to-background pointer-events-none"></div>

      <div class="relative page-gutter pt-3 pb-8">
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
            @keyup.enter="$event.target.blur()"
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
        <!-- SVG 아이콘 -->
        <div class="w-12 h-12 flex-shrink-0 rounded-2xl bg-slate-100 flex items-center justify-center group-hover:bg-primary/10 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.6" v-html="CATEGORY_ICON[item.category] ?? CATEGORY_ICON['기타']" />
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
