<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { Bot } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
</script>

<template>
  <div class="app-shell relative">
    <div class="page-frame shadow-xl">
      <RouterView />
    </div>

    <div
      v-if="route.name !== 'chat'"
      class="pointer-events-none fixed inset-x-0 bottom-0 z-[110] flex justify-center pb-[calc(var(--safe-bottom)+16px)]"
    >
      <div class="flex w-full max-w-[480px] justify-end px-[var(--page-gutter)]">
        <button
          class="pointer-events-auto inline-flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/95 px-4 py-3 text-white shadow-[0_18px_40px_rgba(15,23,42,0.34)] backdrop-blur hover:bg-slate-900 active:scale-95 transition-all"
          @click="router.push('/chat')"
          title="AI 민원 안내"
          aria-label="AI 민원 안내"
        >
          <Bot class="w-5 h-5 shrink-0" />
          <span class="text-sm font-semibold tracking-tight">AI 챗봇</span>
        </button>
      </div>
    </div>
  </div>
</template>
