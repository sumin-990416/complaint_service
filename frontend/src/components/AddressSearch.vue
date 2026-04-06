<script setup>
import { ref, computed } from 'vue'
import { LocateFixed } from 'lucide-vue-next'

defineProps({
  loading: { type: Boolean, default: false },
  error:   { type: String,  default: '' },
})

const emit = defineEmits(['search', 'locate'])

const REGIONS = {
  '서울특별시': ['종로구','중구','용산구','성동구','광진구','동대문구','중랑구','성북구','강북구','도봉구','노원구','은평구','서대문구','마포구','양천구','강서구','구로구','금천구','영등포구','동작구','관악구','서초구','강남구','송파구','강동구'],
  '부산광역시': ['중구','서구','동구','영도구','부산진구','동래구','남구','북구','해운대구','사하구','금정구','강서구','연제구','수영구','사상구','기장군'],
  '대구광역시': ['중구','동구','서구','남구','북구','수성구','달서구','달성군','군위군'],
  '인천광역시': ['중구','동구','미추홀구','연수구','남동구','부평구','계양구','서구','강화군','옹진군'],
  '광주광역시': ['동구','서구','남구','북구','광산구'],
  '대전광역시': ['동구','중구','서구','유성구','대덕구'],
  '울산광역시': ['중구','남구','동구','북구','울주군'],
  '세종특별자치시': [],
  '경기도': ['수원시','성남시','의정부시','안양시','부천시','광명시','평택시','동두천시','안산시','고양시','과천시','구리시','남양주시','오산시','시흥시','군포시','의왕시','하남시','용인시','파주시','이천시','안성시','김포시','화성시','광주시','양주시','포천시','여주시','연천군','가평군','양평군'],
  '강원특별자치도': ['춘천시','원주시','강릉시','동해시','태백시','속초시','삼척시','홍천군','횡성군','영월군','평창군','정선군','철원군','화천군','양구군','인제군','고성군','양양군'],
  '충청북도': ['청주시','충주시','제천시','보은군','옥천군','영동군','증평군','진천군','괴산군','음성군','단양군'],
  '충청남도': ['천안시','공주시','보령시','아산시','서산시','논산시','계룡시','당진시','금산군','부여군','서천군','청양군','홍성군','예산군','태안군'],
  '전북특별자치도': ['전주시','군산시','익산시','정읍시','남원시','김제시','완주군','진안군','무주군','장수군','임실군','순창군','고창군','부안군'],
  '전라남도': ['목포시','여수시','순천시','나주시','광양시','담양군','곡성군','구례군','고흥군','보성군','화순군','장흥군','강진군','해남군','영암군','무안군','함평군','영광군','장성군','완도군','진도군','신안군'],
  '경상북도': ['포항시','경주시','김천시','안동시','구미시','영주시','영천시','상주시','문경시','경산시','의성군','청송군','영양군','영덕군','청도군','고령군','성주군','칠곡군','예천군','봉화군','울진군','울릉군'],
  '경상남도': ['창원시','진주시','통영시','사천시','김해시','밀양시','거제시','양산시','의령군','함안군','창녕군','고성군','남해군','하동군','산청군','함양군','거창군','합천군'],
  '제주특별자치도': ['제주시','서귀포시'],
}

const sidoList = Object.keys(REGIONS)
const showModal = ref(false)
const step = ref('sido')
const selectedSido = ref('')
const selectedSigungu = ref('')
let bodyLockScrollY = 0

const sigunguList = computed(() => REGIONS[selectedSido.value] ?? [])

const displayLabel = computed(() => {
  if (selectedSigungu.value) return `${selectedSido.value} ${selectedSigungu.value}`
  if (selectedSido.value && sigunguList.value.length === 0) return selectedSido.value
  return ''
})

function openModal() {
  step.value = 'sido'
  showModal.value = true
  bodyLockScrollY = window.scrollY || window.pageYOffset || 0
  document.body.style.position = 'fixed'
  document.body.style.top = `-${bodyLockScrollY}px`
  document.body.style.left = '0'
  document.body.style.right = '0'
  document.body.style.width = '100%'
  document.body.style.overflow = 'hidden'
}

function closeModal() {
  showModal.value = false
  const scrollY = Math.abs(parseInt(document.body.style.top || '0', 10)) || bodyLockScrollY
  document.body.style.position = ''
  document.body.style.top = ''
  document.body.style.left = ''
  document.body.style.right = ''
  document.body.style.width = ''
  document.body.style.overflow = ''
  window.scrollTo({ top: scrollY, behavior: 'auto' })
}

function selectSido(sido) {
  selectedSido.value = sido
  selectedSigungu.value = ''
  if (REGIONS[sido].length === 0) {
    closeModal()
    emit('search', sido)
  } else {
    step.value = 'sigungu'
  }
}

function selectSigungu(sg) {
  selectedSigungu.value = sg
  closeModal()
  emit('search', `${selectedSido.value} ${sg}`)
}

function goBackToSido() {
  step.value = 'sido'
}
</script>

<template>
  <div class="rounded-[20px] bg-white px-4 py-4 text-foreground shadow-[inset_0_1px_0_rgba(255,255,255,0.4)]">
    <button
      class="tap-feedback w-full flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-[15px] transition-all hover:border-primary hover:bg-white disabled:opacity-50"
      :disabled="loading"
      @click="openModal"
    >
      <span :class="displayLabel ? 'text-foreground font-medium' : 'text-slate-400'">
        {{ displayLabel || '지역을 선택하세요' }}
      </span>
      <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <div class="mt-3 flex items-center justify-between gap-3 px-1">
      <p class="text-xs text-slate-500">시/도 → 시/군/구 순서로 선택하세요</p>
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

  <Teleport to="body">
    <div
      v-if="showModal"
      class="fixed inset-0 z-[200] flex items-end justify-center bg-slate-950/40 backdrop-blur-[2px]"
      @click.self="closeModal"
    >
      <div class="w-full max-w-[var(--app-max-width)] rounded-t-[28px] bg-white shadow-[0_-20px_60px_rgba(15,23,42,0.18)] max-h-[80dvh] flex flex-col pb-[max(16px,env(safe-area-inset-bottom))]">
        <div class="flex justify-center pt-3 pb-1 flex-shrink-0">
          <div class="h-1.5 w-14 rounded-full bg-slate-200"></div>
        </div>
        <div class="flex items-center gap-2 px-5 py-3 border-b border-slate-100 flex-shrink-0">
          <button
            v-if="step === 'sigungu'"
            class="tap-feedback p-1 -ml-1 rounded-full text-slate-500"
            @click="goBackToSido"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/>
            </svg>
          </button>
          <div class="flex-1">
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-primary/60">
              {{ step === 'sido' ? 'Step 2' : 'Step 2' }}
            </p>
            <h3 class="text-base font-bold text-foreground">
              {{ step === 'sido' ? '시/도 선택' : `${selectedSido} › 시/군/구 선택` }}
            </h3>
          </div>
          <button
            class="tap-feedback rounded-full bg-slate-100 px-3 py-1.5 text-[11px] font-semibold text-slate-700"
            @click="closeModal"
          >
            닫기
          </button>
        </div>

        <ul class="overflow-y-auto flex-1 px-4 py-2">
          <template v-if="step === 'sido'">
            <li v-for="sido in sidoList" :key="sido">
              <button
                class="tap-feedback w-full flex items-center justify-between rounded-xl px-4 py-3.5 text-sm font-medium text-foreground hover:bg-slate-50 active:bg-slate-100 transition-colors"
                @click="selectSido(sido)"
              >
                <span>{{ sido }}</span>
                <svg v-if="REGIONS[sido].length > 0" xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
            </li>
          </template>

          <template v-if="step === 'sigungu'">
            <li v-for="sg in sigunguList" :key="sg">
              <button
                class="tap-feedback w-full flex items-center rounded-xl px-4 py-3.5 text-sm font-medium text-foreground hover:bg-slate-50 active:bg-slate-100 transition-colors"
                @click="selectSigungu(sg)"
              >
                {{ sg }}
              </button>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </Teleport>
</template>
