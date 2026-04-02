<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: { type: String, default: 'default' },
  class:   { type: String, default: '' },
})

const base = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors'

const variants = {
  default:  'bg-primary/10 text-primary',
  outline:  'border border-primary text-foreground',
}

const classes = computed(() =>
  cn(base, variants[props.variant] ?? variants.default, props.class)
)
</script>

<template>
  <span :class="classes"><slot /></span>
</template>
