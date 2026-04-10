<script setup>
import { computed } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const isMainTab = computed(() => ['home', 'online', 'chat'].includes(route.name))

const headerGradient = computed(() => {
  switch (route.name) {
    case 'online':
      return 'radial-gradient(circle at top left, rgba(14,165,233,0.32), transparent 34%), radial-gradient(circle at top right, rgba(59,110,248,0.16), transparent 18%)'
    case 'chat':
      return 'radial-gradient(circle at top left, rgba(59,110,248,0.34), transparent 34%), radial-gradient(circle at top right, rgba(14,165,233,0.18), transparent 18%)'
    case 'office-detail':
      return 'radial-gradient(circle at top left, rgba(59,110,248,0.34), transparent 34%), radial-gradient(circle at top right, rgba(14,165,233,0.18), transparent 18%)'
    default:
      return 'radial-gradient(circle at top left, rgba(59,110,248,0.38), transparent 38%), radial-gradient(circle at top right, rgba(16,185,129,0.16), transparent 22%)'
  }
})
</script>

<template>
  <div class="app-shell relative">
    <div class="page-frame shadow-xl flex flex-col h-dvh">

      <!-- ── Persistent dark header ── -->
      <div class="flex-shrink-0 relative z-50 bg-[#0f172a] overflow-hidden">
        <div class="absolute inset-0" :style="{ background: headerGradient, transition: 'background 0.5s ease' }" />

        <!-- Status-bar row: back button for detail, empty spacer otherwise -->
        <div class="relative flex h-14 items-center px-3">
          <button
            v-if="route.name === 'office-detail'"
            class="w-9 h-9 flex items-center justify-center rounded-full text-white/70 hover:text-white hover:bg-white/10 active:bg-white/20 transition-colors"
            @click="router.back()"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        </div>

        <!-- Tab toggle (main tabs only) -->
        <div v-if="isMainTab" class="relative flex justify-center pb-2">
          <div class="inline-flex items-center rounded-full bg-white/10 p-1 gap-1">
            <button
              class="rounded-full px-4 py-1.5 text-xs font-semibold transition-colors flex items-center gap-1.5"
              :class="route.name === 'home' ? 'bg-white text-slate-900 shadow-sm' : 'text-white/60 hover:text-white/80'"
              @click="route.name !== 'home' && router.push('/')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9.75L12 3l9 6.75V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.75z"/><path stroke-linecap="round" stroke-linejoin="round" d="M9 21V12h6v9"/></svg>
              방문 민원
            </button>
            <button
              class="rounded-full px-4 py-1.5 text-xs font-semibold transition-colors flex items-center gap-1.5"
              :class="route.name === 'online' ? 'bg-white text-slate-900 shadow-sm' : 'text-white/60 hover:text-white/80'"
              @click="route.name !== 'online' && router.push('/online')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path stroke-linecap="round" d="M2 12h20M12 2a15.3 15.3 0 010 20M12 2a15.3 15.3 0 000 20"/></svg>
              온라인 민원
            </button>
            <button
              class="rounded-full px-4 py-1.5 text-xs font-semibold transition-colors flex items-center gap-1.5"
              :class="route.name === 'chat' ? 'bg-white text-slate-900 shadow-sm' : 'text-white/60 hover:text-white/80'"
              @click="route.name !== 'chat' && router.push('/chat')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
              AI 챗봇
            </button>
          </div>
        </div>
      </div>

      <!-- ── Page content (scrollable) ── -->
      <div class="app-scroll-container flex-1 overflow-y-auto bg-background safe-bottom">
        <RouterView v-slot="{ Component }">
          <Transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </Transition>
        </RouterView>
      </div>

    </div>
  </div>
</template>
