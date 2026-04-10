<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { ref } from 'vue'

const route = useRoute()
const router = useRouter()

const transitionName = ref('page-fade')

router.beforeEach((to, from) => {
  const toDepth = to.meta?.depth ?? 0
  const fromDepth = from.meta?.depth ?? 0

  if (toDepth !== fromDepth) {
    transitionName.value = toDepth > fromDepth ? 'page-slide-up' : 'page-slide-down'
  } else {
    const toIndex = to.meta?.index ?? 0
    const fromIndex = from.meta?.index ?? 0
    transitionName.value = toIndex > fromIndex ? 'page-slide-left' : 'page-slide-right'
  }
})
</script>

<template>
  <div class="app-shell relative">
    <div class="page-frame shadow-xl overflow-hidden">
      <RouterView v-slot="{ Component }">
        <Transition :name="transitionName" mode="out-in">
          <component :is="Component" :key="route.fullPath" />
        </Transition>
      </RouterView>
    </div>

  </div>
</template>
