<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: { type: String, default: 'default' },
  class:   { type: String, default: '' },
})

const base = 'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors'

const variants = {
  default:     'bg-primary/10 text-primary',
  secondary:   'bg-secondary text-secondary-foreground',
  outline:     'border border-input text-foreground',
  destructive: 'bg-destructive/10 text-destructive',
  success:     'bg-emerald-50 text-emerald-700',
  warning:     'bg-amber-50 text-amber-700',
  night:       'bg-blue-50 text-blue-700',
  weekend:     'bg-green-50 text-green-700',
}

const classes = computed(() =>
  cn(base, variants[props.variant] ?? variants.default, props.class)
)
</script>

<template>
  <span :class="classes"><slot /></span>
</template>
