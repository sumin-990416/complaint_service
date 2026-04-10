<script setup>
import { ref, nextTick, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const CATEGORY_STORAGE_KEY = 'minwon_now_category'
const messages = ref([
  {
    role: 'assistant',
    content: '안녕하세요! 민원실 이용 관련 궁금한 점을 물어보세요.\n예) "출생신고는 어디서 하나요?" "여권 발급에 필요한 서류가 뭐예요?"',
  },
])
const input = ref('')
const loading = ref(false)
const scrollEl = ref(null)
const selectedCategory = ref('전체')

const CATEGORIES = [
  '전체',
  '주민등록/등본',
  '전입/가족관계',
  '여권',
  '인감/증명',
  '건축/인허가',
  '사업/세무',
]

async function scrollToBottom() {
  await nextTick()
  if (scrollEl.value) scrollEl.value.scrollTop = scrollEl.value.scrollHeight
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  await scrollToBottom()

  messages.value.push({ role: 'assistant', content: '', links: [] })
  const lastIdx = messages.value.length - 1

  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        messages: messages.value.slice(1, -1).map(m => ({ role: m.role, content: m.content })),
        category: selectedCategory.value === '전체' ? null : selectedCategory.value,
      }),
    })

    const reader = res.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value)
      for (const line of chunk.split('\n')) {
        if (!line.startsWith('data: ')) continue
        const data = line.slice(6).trim()
        if (data === '[DONE]') break
        try {
          const json = JSON.parse(data)
          const delta = json.choices?.[0]?.delta?.content
          if (delta) {
            messages.value[lastIdx].content += delta
            await scrollToBottom()
          }
        } catch { /* skip malformed */ }
      }
    }

    try {
      const reqCategory = selectedCategory.value
      const q = encodeURIComponent(
        reqCategory && reqCategory !== '전체' ? `${reqCategory} ${text}` : text
      )
      const linksRes = await fetch(`/api/chat/gov24-links?q=${q}`)
      const links = await linksRes.json()
      if (links.length) messages.value[lastIdx].links = links
    } catch { /* silent */ }
  } catch {
    messages.value[lastIdx].content = '오류가 발생했어요. 잠시 후 다시 시도해 주세요.'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

const SUGGESTIONS = [
  '출생신고는 어디서 하나요?',
  '여권 발급 필요 서류가 뭐예요?',
  '주민등록등본 발급 방법 알려주세요',
  '야간에도 운영하는 민원실이 있나요?',
]

onMounted(scrollToBottom)
onMounted(() => {
  const stored = sessionStorage.getItem(CATEGORY_STORAGE_KEY)
  if (stored && CATEGORIES.includes(stored)) selectedCategory.value = stored
  scrollToBottom()
})
</script>

<template>
  <div class="flex flex-col h-full bg-background">
    <section class="relative overflow-hidden bg-[#0f172a] text-white flex-shrink-0">
      <div class="absolute inset-0 bg-gradient-to-b from-blue-600/20 to-transparent"></div>
      <div class="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-b from-transparent to-background pointer-events-none"></div>

      <div class="relative page-gutter pt-3 pb-8">
        <p class="text-[11px] uppercase tracking-[0.24em] text-blue-600 font-bold">AI Assistant</p>
        <h1 class="hero-copy mt-2 font-bold tracking-tight text-slate-900">민원 절차를 바로 물어보세요</h1>
        <p class="mt-3 max-w-[22rem] text-sm leading-6 text-slate-700">
          출생신고, 여권, 전입신고, 야간 운영 여부처럼 실제 방문 전에 필요한 정보를 빠르게 정리해 드립니다.
        </p>
      </div>
    </section>

    <div ref="scrollEl" class="touch-scroll flex-1 px-4 py-4 -mt-2 space-y-3">
      <div class="rounded-[22px] border border-white/70 bg-white px-4 py-3 shadow-[0_12px_30px_rgba(15,23,42,0.08)]">
        <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">Category Filter</p>
        <div class="mt-2 flex flex-wrap gap-2">
          <button
            v-for="category in CATEGORIES"
            :key="category"
            class="rounded-full px-3 py-1.5 text-[11px] font-semibold transition-colors"
            :class="selectedCategory === category
              ? 'bg-slate-950 text-white shadow-sm'
              : 'bg-slate-100 text-slate-700 hover:bg-primary-light hover:text-primary'"
            @click="selectedCategory = category"
          >
            {{ category }}
          </button>
        </div>
        <p class="mt-2 text-[11px] text-muted-foreground">
          선택한 카테고리 기준으로만 기관/민원실 추천을 안내합니다.
        </p>
      </div>

      <div v-if="messages.length === 1" class="flex flex-wrap gap-2 mt-1">
        <button
          v-for="s in SUGGESTIONS"
          :key="s"
          class="text-xs px-3 py-1.5 rounded-full border border-white/70 bg-white text-foreground shadow-sm hover:bg-primary-light transition-colors"
          @click="input = s; send()"
        >
          {{ s }}
        </button>
      </div>

      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
      >
        <div v-if="msg.role === 'assistant'" class="w-8 h-8 rounded-2xl bg-slate-950 flex items-center justify-center text-[11px] font-semibold text-white flex-shrink-0 mt-1 mr-2 shadow-sm">
          AI
        </div>

        <div
          :class="[
            'max-w-[78%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap',
            msg.role === 'user'
              ? 'bg-slate-950 text-white rounded-br-sm shadow-sm'
              : 'bg-white border border-white/70 text-foreground rounded-bl-sm shadow-[0_12px_30px_rgba(15,23,42,0.08)]',
          ]"
        >
          <span v-if="msg.role === 'assistant' && msg.content === '' && loading" class="flex gap-1 items-center py-1">
            <span class="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:0ms]" />
            <span class="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:150ms]" />
            <span class="w-1.5 h-1.5 bg-muted-foreground rounded-full animate-bounce [animation-delay:300ms]" />
          </span>
          <span v-else>{{ msg.content }}</span>
        </div>

        <div
          v-if="msg.role === 'assistant' && msg.links?.length"
          class="mt-2 ml-10 flex flex-wrap gap-2"
        >
          <a
            v-for="link in msg.links"
            :key="link.url"
            :href="link.url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/5 px-3 py-1.5 text-[11px] font-semibold text-primary hover:bg-primary/10 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
            </svg>
            {{ link.label }} — 정부24 신청
          </a>
        </div>
      </div>
    </div>

    <div class="border-t border-slate-200/80 bg-white/90 backdrop-blur px-4 py-3 flex gap-2 items-end">
      <textarea
        v-model="input"
        rows="1"
        placeholder="민원 관련 질문을 입력하세요…"
        class="flex-1 resize-none rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm outline-none focus:border-primary focus:bg-white transition-colors max-h-32"
        :disabled="loading"
        @keydown="onKeydown"
        @input="e => { e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px' }"
      />
      <button
        class="w-11 h-11 flex-shrink-0 rounded-2xl bg-slate-950 text-white flex items-center justify-center disabled:opacity-40 active:scale-95 transition-all shadow-sm"
        :disabled="!input.trim() || loading"
        @click="send"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>
    </div>
  </div>
</template>