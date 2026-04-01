<script setup>
import { ref } from 'vue'
import UiButton from './ui/Button.vue'
import UiInput from './ui/Input.vue'
import { Search } from 'lucide-vue-next'

defineProps({
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: '' },
})

const emit = defineEmits(['search'])
const query = ref('')

function onSearch() {
  if (!query.value.trim()) return
  emit('search', query.value)
}
</script>

<template>
  <div class="px-4 py-3 bg-muted/50 border-b border-border">
    <div class="flex gap-2">
      <UiInput
        v-model="query"
        placeholder="지역 입력 (예: 강남구, 광주시)"
        class="flex-1"
        @keyup.enter="onSearch"
      />
      <UiButton :disabled="loading" size="default" @click="onSearch">
        <Search v-if="!loading" class="w-4 h-4 mr-1" />
        <span>{{ loading ? '검색 중…' : '검색' }}</span>
      </UiButton>
    </div>
    <p v-if="error" class="mt-2 text-xs text-destructive flex items-center gap-1">
      <span>⚠</span> {{ error }}
    </p>
  </div>
</template>
