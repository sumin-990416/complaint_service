<script setup>
import { ref } from 'vue'
import { LocateFixed } from 'lucide-vue-next'

defineProps({
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: '' },
})

const emit = defineEmits(['search', 'locate'])
const query = ref('')

function onSearch() {
  if (!query.value.trim()) return
  emit('search', query.value)
}
</script>

<template>
  <div class="rounded-[20px] bg-white px-4 py-4 text-foreground shadow-[inset_0_1px_0_rgba(255,255,255,0.4)]">
    <div class="flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 transition-all focus-within:border-primary focus-within:bg-white focus-within:shadow-[0_0_0_4px_rgba(59,110,248,0.08)]">
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"/>
      </svg>
      <input
        v-model="query"
        placeholder="지역, 구청, 시청을 입력해 보세요"
        class="flex-1 bg-transparent text-[15px] text-foreground placeholder-slate-400 outline-none"
        :disabled="loading"
        @keyup.enter="onSearch"
      />
      <button
        class="tap-feedback inline-flex items-center justify-center rounded-xl bg-slate-950 px-4 py-2 text-xs font-semibold text-white disabled:opacity-50 transition-opacity flex-shrink-0"
        :disabled="loading || !query.trim()"
        @click="onSearch"
      >
        {{ loading ? '검색 중' : '검색' }}
      </button>
    </div>
    <div class="mt-3 flex items-center justify-between gap-3 px-1">
      <p class="text-xs text-slate-500">예: 강남구, 부산 남구, 광주시청</p>
      <button
        class="tap-feedback inline-flex items-center gap-1.5 rounded-full bg-primary-light px-3 py-1.5 text-[11px] font-semibold text-primary hover:bg-primary/15 transition-all"
        type="button"
        @click="emit('locate')"
      >
        <LocateFixed class="w-3.5 h-3.5" />
        내 위치 찾기
      </button>
    </div>
    <p v-if="error" class="mt-2 text-xs text-rose-500 flex items-center gap-1 px-1">
      <span>⚠</span> {{ error }}
    </p>
  </div>
</template>
