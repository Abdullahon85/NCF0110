<template>
  <div class="home-page" ref="pageRef">
    <!-- ═══════════════════════════════════════════════════ -->
    <!-- HERO SECTION — Three.js 3D + GSAP                  -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="hero-section" ref="heroRef">
      <canvas class="hero-canvas" ref="canvasRef"></canvas>

      <div class="hero-inner">
        <div class="hero-badge" ref="heroBadgeRef">
          <span class="badge-dot"></span>
          <span>Оборудование безопасности</span>
        </div>

        <h1 class="hero-title" ref="heroTitleRef">
          <span class="title-line" ref="titleLine1">Защита нового</span>
          <span class="title-line title-accent" ref="titleLine2">поколения</span>
        </h1>

        <p class="hero-sub" ref="heroSubRef">
          Системы видеонаблюдения, IP-камеры и оборудование безопасности от ведущих мировых брендов
        </p>

        <div class="hero-actions" ref="heroActionsRef">
          <router-link to="/catalog" class="btn-primary-3d">
            <span class="btn-text">Смотреть каталог</span>
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
            </svg>
            <div class="btn-glow"></div>
          </router-link>
          <router-link to="/about" class="btn-ghost-3d">О компании</router-link>
        </div>

        <div class="hero-stats" ref="heroStatsRef">
          <div class="stat-item" v-for="stat in heroStats" :key="stat.label">
            <div class="stat-number" :data-target="stat.value">0{{ stat.suffix }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>

      <div class="hero-scroll-hint" ref="scrollHintRef">
        <div class="scroll-line"></div>
        <span>Прокрутите вниз</span>
      </div>

      <!-- Floating orbs -->
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
    </section>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- MARQUEE — Brand strip                              -->
    <!-- ═══════════════════════════════════════════════════ -->
    <div class="marquee-wrap" v-if="brands.length">
      <div class="marquee-track">
        <div class="marquee-inner">
          <template v-for="i in 3" :key="i">
            <div v-for="brand in brands" :key="`${i}-${brand.id}`" class="marquee-item">
              <img v-if="brand.image" :src="getImageUrl(brand.image)" :alt="brand.name" />
              <span v-else>{{ brand.name }}</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- BANNER SECTION — 3D Parallax                       -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="banner-section" v-if="banners.length" ref="bannerSectionRef">
      <div class="banner-3d-wrapper" ref="banner3dRef">
        <div class="banner-container-inner">
          <BannerSlider :banners="banners" :loading="bannersLoading" :autoplay-interval="5000" />
        </div>
        <div class="banner-reflection"></div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- CATEGORIES — 3D Grid                               -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="categories-section" ref="categoriesRef">
      <div class="section-container">
        <div class="section-header" ref="catHeaderRef">
          <div class="section-label">Продукции</div>
          <h2 class="section-title">Каталог товаров</h2>
          <p class="section-desc">Широкий ассортимент оборудования для любых задач безопасности</p>
        </div>

        <div v-if="loading" class="cat-grid">
          <div v-for="n in 6" :key="n" class="cat-card-skeleton skeleton"></div>
        </div>

        <div v-else-if="categories.length" class="cat-grid" ref="catGridRef">
          <div
            v-for="(cat, i) in categories"
            :key="cat.id"
            class="cat-card-3d"
            :ref="el => catCards[i] = el as HTMLElement"
            @mousemove="tiltCard($event, i)"
            @mouseleave="resetCard(i)"
            @click="$router.push(`/catalog/${cat.slug}`)"
          >
            <div class="card-inner">
              <div class="card-image-wrap">
                <img
                  v-if="cat.image"
                  :src="getImageUrl(cat.image)"
                  :alt="cat.name"
                  class="card-img"
                  loading="lazy"
                />
                <div v-else class="card-img-placeholder">
                  <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                    <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
                  </svg>
                </div>
                <div class="card-shimmer"></div>
              </div>
              <div class="card-body">
                <h3 class="card-title">{{ cat.name }}</h3>
                <div class="card-arrow">
                  <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                  </svg>
                </div>
              </div>
              <div class="card-glow"></div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- FEATURES — Scroll Reveal Bento                     -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="features-section" ref="featuresRef">
      <div class="section-container">
        <div class="section-header" ref="featHeaderRef">
          <div class="section-label">Преимущества</div>
          <h2 class="section-title">Почему выбирают нас</h2>
        </div>

        <div class="bento-grid" ref="bentoRef">
          <div v-for="(feat, i) in features" :key="i"
               class="bento-card"
               :class="`bento-${feat.size}`"
               :ref="el => bentoCards[i] = el as HTMLElement">
            <div class="bento-icon">
              <div class="icon-ring" v-html="feat.icon"></div>
            </div>
            <h3 class="bento-title">{{ feat.title }}</h3>
            <p class="bento-desc">{{ feat.desc }}</p>
            <div class="bento-bg-shape"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- BRANDS — 3D Hover Logos                            -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="brands-section" v-if="brands.length" ref="brandsRef">
      <div class="section-container">
        <div class="section-header" ref="brandHeaderRef">
          <div class="section-label">Партнёры</div>
          <h2 class="section-title">Наши бренды</h2>
          <p class="section-desc">Работаем только с проверенными мировыми производителями</p>
        </div>

        <div class="brands-scroll-stage" ref="brandsGridRef">
          <!-- Row 1 — scrolls left -->
          <div class="brands-scroll-row">
            <div class="brands-scroll-inner brands-scroll-ltr">
              <div
                v-for="brand in brands"
                :key="'r1a-' + brand.id"
                class="brand-card-3d"
                @click="$router.push(`/brands/${brand.slug}`)"
              >
                <div class="brand-inner">
                  <img v-if="brand.image" :src="getImageUrl(brand.image)" :alt="brand.name" class="brand-logo" />
                  <span v-else class="brand-name-text">{{ brand.name }}</span>
                </div>
              </div>
            </div>
            <!-- duplicate for seamless loop -->
            <div class="brands-scroll-inner brands-scroll-ltr" aria-hidden="true">
              <div
                v-for="brand in brands"
                :key="'r1b-' + brand.id"
                class="brand-card-3d"
                @click="$router.push(`/brands/${brand.slug}`)"
              >
                <div class="brand-inner">
                  <img v-if="brand.image" :src="getImageUrl(brand.image)" :alt="brand.name" class="brand-logo" />
                  <span v-else class="brand-name-text">{{ brand.name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Row 2 — scrolls right (reverse) -->
          <div class="brands-scroll-row">
            <div class="brands-scroll-inner brands-scroll-rtl">
              <div
                v-for="brand in [...brands].reverse()"
                :key="'r2a-' + brand.id"
                class="brand-card-3d"
                @click="$router.push(`/brands/${brand.slug}`)"
              >
                <div class="brand-inner">
                  <img v-if="brand.image" :src="getImageUrl(brand.image)" :alt="brand.name" class="brand-logo" />
                  <span v-else class="brand-name-text">{{ brand.name }}</span>
                </div>
              </div>
            </div>
            <div class="brands-scroll-inner brands-scroll-rtl" aria-hidden="true">
              <div
                v-for="brand in [...brands].reverse()"
                :key="'r2b-' + brand.id"
                class="brand-card-3d"
                @click="$router.push(`/brands/${brand.slug}`)"
              >
                <div class="brand-inner">
                  <img v-if="brand.image" :src="getImageUrl(brand.image)" :alt="brand.name" class="brand-logo" />
                  <span v-else class="brand-name-text">{{ brand.name }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="brands-cta" ref="brandCtaRef">
          <router-link to="/brands" class="btn-outline-gold">
            Все бренды
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
            </svg>
          </router-link>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════════════════════ -->
    <!-- CTA — Dark Glow Section                            -->
    <!-- ═══════════════════════════════════════════════════ -->
    <section class="cta-section" ref="ctaRef">
      <div class="cta-bg-canvas" ref="ctaBgRef"></div>
      <div class="cta-inner" ref="ctaInnerRef">
        <div class="cta-badge">Готовы начать?</div>
        <h2 class="cta-title">Оставьте заявку —<br><span class="cta-accent">свяжемся сегодня</span></h2>
        <p class="cta-sub">Бесплатная консультация по подбору оборудования для вашего объекта</p>
        <router-link to="/contact" class="btn-gold-3d">
          <span>Получить консультацию</span>
          <div class="btn-shine"></div>
        </router-link>
      </div>
      <div class="cta-orb cta-orb-1"></div>
      <div class="cta-orb cta-orb-2"></div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { categoriesAPI, brandsAPI, bannersAPI, getImageUrl } from '@/api'
import BannerSlider from '@/components/BannerSlider.vue'
import type { Category, Brand, Banner } from '@/types'

gsap.registerPlugin(ScrollTrigger)

const router = useRouter()

// ─── Data ───────────────────────────────────────────────────────────────────
const categories = ref<Category[]>([])
const brands     = ref<Brand[]>([])
const banners    = ref<Banner[]>([])
const loading        = ref(true)
const bannersLoading = ref(true)

const heroStats = [
  { value: 500,  suffix: '+', label: 'Товаров в наличии' },
  { value: 50,   suffix: '+', label: 'Брендов партнёров' },
  { value: 5,    suffix: 'лет', label: 'На рынке' },
  { value: 1000, suffix: '+', label: 'Клиентов' },
]

const features = [
  {
    size: 'tall',
    icon: `<svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>`,
    title: 'Гарантия качества',
    desc: 'Все товары проходят строгий контроль качества перед поступлением на склад. Официальные гарантийные обязательства производителей.',
  },
  {
    size: 'wide',
    icon: `<svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>`,
    title: 'Быстрая доставка',
    desc: 'Доставка по всей стране в кратчайшие сроки.',
  },
  {
    size: 'small',
    icon: `<svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
    title: 'Экспертная поддержка',
    desc: 'Команда специалистов готова помочь с выбором и установкой.',
  },
  {
    size: 'small',
    icon: `<svg width="32" height="32" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>`,
    title: 'Лучшие цены',
    desc: 'Прямые поставки от производителей обеспечивают конкурентные цены.',
  },
]

// ─── Refs ───────────────────────────────────────────────────────────────────
const pageRef        = ref<HTMLElement>()
const heroRef        = ref<HTMLElement>()
const canvasRef      = ref<HTMLCanvasElement>()
const heroBadgeRef   = ref<HTMLElement>()
const heroTitleRef   = ref<HTMLElement>()
const titleLine1     = ref<HTMLElement>()
const titleLine2     = ref<HTMLElement>()
const heroSubRef     = ref<HTMLElement>()
const heroActionsRef = ref<HTMLElement>()
const heroStatsRef   = ref<HTMLElement>()
const scrollHintRef  = ref<HTMLElement>()
const bannerSectionRef = ref<HTMLElement>()
const banner3dRef    = ref<HTMLElement>()
const categoriesRef  = ref<HTMLElement>()
const catHeaderRef   = ref<HTMLElement>()
const catGridRef     = ref<HTMLElement>()
const catCards       = ref<HTMLElement[]>([])
const featuresRef    = ref<HTMLElement>()
const featHeaderRef  = ref<HTMLElement>()
const bentoRef       = ref<HTMLElement>()
const bentoCards     = ref<HTMLElement[]>([])
const brandsRef      = ref<HTMLElement>()
const brandHeaderRef = ref<HTMLElement>()
const brandsGridRef  = ref<HTMLElement>()
const brandCtaRef    = ref<HTMLElement>()
const ctaRef         = ref<HTMLElement>()
const ctaInnerRef    = ref<HTMLElement>()

// ─── Canvas 2D Particle Field ───────────────────────────────────────────────
let animFrameId = 0
let mouseX = 0, mouseY = 0

interface Particle {
  x: number; y: number; z: number
  vx: number; vy: number
  r: number
  color: string
  alpha: number
}

interface WireShape {
  cx: number; cy: number
  size: number
  angle: number
  rotSpeed: number
  sides: number
  color: string
  alpha: number
  floatOffset: number
}

function initThree() {
  const canvas = canvasRef.value
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const resize = () => {
    canvas.width  = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()

  // ── Particles ──────────────────────────────────────────
  const COLORS = ['#2d6a4f', '#1b4332', '#d4a574', '#3a8463', '#b8956a', '#52a77c']
  const particles: Particle[] = Array.from({ length: 260 }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    z: Math.random(),
    vx: (Math.random() - 0.5) * 0.25,
    vy: (Math.random() - 0.5) * 0.25,
    r: Math.random() * 2.2 + 0.4,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    alpha: Math.random() * 0.55 + 0.15,
  }))

  // ── Wireframe Shapes ───────────────────────────────────
  const shapes: WireShape[] = [
    { cx: 0.82, cy: 0.18, size: 80, angle: 0, rotSpeed: 0.004, sides: 8, color: '#d4a574', alpha: 0.22, floatOffset: 0 },
    { cx: 0.12, cy: 0.75, size: 60, angle: 1, rotSpeed: 0.006, sides: 6, color: '#2d6a4f', alpha: 0.28, floatOffset: 2 },
    { cx: 0.70, cy: 0.65, size: 45, angle: 2, rotSpeed: 0.003, sides: 4, color: '#d4a574', alpha: 0.18, floatOffset: 4 },
    { cx: 0.25, cy: 0.25, size: 35, angle: 0.5, rotSpeed: 0.008, sides: 3, color: '#3a8463', alpha: 0.2, floatOffset: 1 },
    { cx: 0.55, cy: 0.85, size: 50, angle: 0.8, rotSpeed: 0.005, sides: 6, color: '#b8956a', alpha: 0.15, floatOffset: 3 },
  ]

  // ── Connection lines ───────────────────────────────────
  const drawConnections = (ps: Particle[], ctx: CanvasRenderingContext2D) => {
    const maxDist = 110
    for (let i = 0; i < ps.length; i++) {
      for (let j = i + 1; j < ps.length; j++) {
        const dx = ps[i].x - ps[j].x
        const dy = ps[i].y - ps[j].y
        const d  = Math.sqrt(dx * dx + dy * dy)
        if (d < maxDist) {
          ctx.save()
          ctx.globalAlpha = (1 - d / maxDist) * 0.12
          ctx.strokeStyle = '#2d6a4f'
          ctx.lineWidth = 0.6
          ctx.beginPath()
          ctx.moveTo(ps[i].x, ps[i].y)
          ctx.lineTo(ps[j].x, ps[j].y)
          ctx.stroke()
          ctx.restore()
        }
      }
    }
  }

  // ── Draw polygon wireframe ─────────────────────────────
  const drawShape = (s: WireShape, t: number, ctx: CanvasRenderingContext2D) => {
    const W = canvas.width, H = canvas.height
    const cx = s.cx * W + mouseX * 15
    const cy = s.cy * H + mouseY * 10 + Math.sin(t * 0.6 + s.floatOffset) * 18
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(s.angle)
    ctx.globalAlpha = s.alpha
    ctx.strokeStyle = s.color
    ctx.lineWidth = 1.2
    ctx.beginPath()
    for (let i = 0; i <= s.sides; i++) {
      const a = (i / s.sides) * Math.PI * 2 - Math.PI / 2
      const x = Math.cos(a) * s.size
      const y = Math.sin(a) * s.size
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.closePath()
    ctx.stroke()
    // inner ring
    ctx.beginPath()
    for (let i = 0; i <= s.sides; i++) {
      const a = (i / s.sides) * Math.PI * 2 - Math.PI / 2
      const x = Math.cos(a) * s.size * 0.55
      const y = Math.sin(a) * s.size * 0.55
      i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
    }
    ctx.stroke()
    // spokes
    for (let i = 0; i < s.sides; i++) {
      const a = (i / s.sides) * Math.PI * 2 - Math.PI / 2
      ctx.beginPath()
      ctx.moveTo(Math.cos(a) * s.size * 0.55, Math.sin(a) * s.size * 0.55)
      ctx.lineTo(Math.cos(a) * s.size, Math.sin(a) * s.size)
      ctx.stroke()
    }
    ctx.restore()
  }

  let t = 0
  const tick = () => {
    animFrameId = requestAnimationFrame(tick)
    t += 0.016

    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Move & draw particles
    particles.forEach(p => {
      p.x += p.vx + mouseX * 0.008 * p.z
      p.y += p.vy + mouseY * 0.008 * p.z
      if (p.x < -10) p.x = canvas.width + 10
      if (p.x > canvas.width + 10) p.x = -10
      if (p.y < -10) p.y = canvas.height + 10
      if (p.y > canvas.height + 10) p.y = -10

      ctx.save()
      ctx.globalAlpha = p.alpha
      ctx.fillStyle = p.color
      ctx.shadowColor = p.color
      ctx.shadowBlur = p.r * 3
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2)
      ctx.fill()
      ctx.restore()
    })

    drawConnections(particles, ctx)

    // Draw shapes
    shapes.forEach(s => {
      s.angle += s.rotSpeed
      drawShape(s, t, ctx)
    })
  }
  tick()

  window.addEventListener('mousemove', onMouseMove)
  window.addEventListener('resize', () => { resize(); })
}

function onMouseMove(e: MouseEvent) {
  mouseX = (e.clientX / window.innerWidth - 0.5) * 2
  mouseY = (e.clientY / window.innerHeight - 0.5) * 2
}

function onResize() {}

// ─── 3D Card Tilt ───────────────────────────────────────────────────────────
function tiltCard(e: MouseEvent, i: number) {
  const card = catCards.value[i]
  if (!card) return
  const rect = card.getBoundingClientRect()
  const cx = rect.left + rect.width / 2
  const cy = rect.top + rect.height / 2
  const rx = ((e.clientY - cy) / (rect.height / 2)) * -12
  const ry = ((e.clientX - cx) / (rect.width / 2)) * 12
  gsap.to(card, { rotateX: rx, rotateY: ry, scale: 1.04, duration: 0.3, ease: 'power2.out', transformPerspective: 800 })
}
function resetCard(i: number) {
  const card = catCards.value[i]
  if (!card) return
  gsap.to(card, { rotateX: 0, rotateY: 0, scale: 1, duration: 0.5, ease: 'power2.out' })
}

// ─── GSAP Scroll Animations ──────────────────────────────────────────────────
function initAnimations() {
  // On mobile skip all scroll-triggered GSAP animations —
  // gsap.from() immediately sets opacity:0 and ScrollTrigger
  // often doesn't fire on iOS Safari, leaving content invisible.
  if (window.innerWidth < 768) {
    ScrollTrigger.getAll().forEach(t => t.kill())
    return
  }

  // Hero uses CSS animations — no GSAP needed for initial reveal

  // Counter animation for stats (runs after CSS animation shows elements)
  setTimeout(() => {
    document.querySelectorAll('.stat-number').forEach(el => {
      const target = parseInt(el.getAttribute('data-target') || '0')
      const suffix = (el.textContent || '').replace(/\d/g, '').trim()
      const obj = { val: 0 }
      gsap.to(obj, {
        val: target,
        duration: 2,
        ease: 'power2.out',
        onUpdate() { el.textContent = Math.floor(obj.val) + suffix },
      })
    })
  }, 1200)

  // Banner 3D parallax
  ScrollTrigger.create({
    trigger: bannerSectionRef.value,
    start: 'top bottom',
    end: 'bottom top',
    onUpdate: (self) => {
      if (banner3dRef.value) {
        gsap.set(banner3dRef.value, {
          rotateX: (self.progress - 0.5) * 6,
          y: (self.progress - 0.5) * -30,
        })
      }
    },
  })

  // Categories header
  gsap.from(catHeaderRef.value, {
    y: 60, opacity: 0, duration: 0.9,
    scrollTrigger: { trigger: catHeaderRef.value, start: 'top 85%', end: 'bottom 60%', toggleActions: 'play none none reverse' },
  })

  // Category cards stagger
  if (catGridRef.value) {
    gsap.from(catGridRef.value.children, {
      y: 80, opacity: 0, scale: 0.92, stagger: 0.08, duration: 0.8, ease: 'power3.out',
      scrollTrigger: { trigger: catGridRef.value, start: 'top 80%', toggleActions: 'play none none reverse' },
    })
  }

  // Features header
  gsap.from(featHeaderRef.value, {
    y: 60, opacity: 0, duration: 0.9,
    scrollTrigger: { trigger: featHeaderRef.value, start: 'top 85%', toggleActions: 'play none none reverse' },
  })

  // Bento cards
  if (bentoRef.value) {
    gsap.from(bentoRef.value.children, {
      y: 100, opacity: 0, scale: 0.9, stagger: 0.12, duration: 0.9, ease: 'power3.out',
      scrollTrigger: { trigger: bentoRef.value, start: 'top 80%', toggleActions: 'play none none reverse' },
    })
  }

  // Brands section
  gsap.from(brandHeaderRef.value, {
    y: 60, opacity: 0, duration: 0.9,
    scrollTrigger: { trigger: brandHeaderRef.value, start: 'top 85%', toggleActions: 'play none none reverse' },
  })
  if (brandsGridRef.value) {
    gsap.from(brandsGridRef.value.children, {
      scale: 0.8, opacity: 0, stagger: 0.06, duration: 0.6, ease: 'back.out(1.7)',
      scrollTrigger: { trigger: brandsGridRef.value, start: 'top 80%', toggleActions: 'play none none reverse' },
    })
  }
  gsap.from(brandCtaRef.value, {
    y: 30, opacity: 0, duration: 0.7,
    scrollTrigger: { trigger: brandCtaRef.value, start: 'top 90%', toggleActions: 'play none none reverse' },
  })

  // CTA section
  gsap.from(ctaInnerRef.value?.children ? Array.from(ctaInnerRef.value.children) : [], {
    y: 60, opacity: 0, stagger: 0.15, duration: 0.9, ease: 'power3.out',
    scrollTrigger: { trigger: ctaRef.value, start: 'top 75%', toggleActions: 'play none none reverse' },
  })

  // CTA parallax orbs
  ScrollTrigger.create({
    trigger: ctaRef.value,
    start: 'top bottom', end: 'bottom top',
    onUpdate: self => {
      document.querySelectorAll('.cta-orb').forEach((orb, i) => {
        gsap.set(orb, { y: (self.progress - 0.5) * (i % 2 === 0 ? -60 : 60) })
      })
    },
  })
}

// ─── Data Fetch ───────────────────────────────────────────────────────────────
const cache = {
  get(k: string) {
    try {
      const s = sessionStorage.getItem(k)
      if (!s) return null
      const { data, expiry } = JSON.parse(s)
      if (Date.now() > expiry) { sessionStorage.removeItem(k); return null }
      return data
    } catch { return null }
  },
  set(k: string, data: any, ttl = 300000) {
    try { sessionStorage.setItem(k, JSON.stringify({ data, expiry: Date.now() + ttl })) } catch {}
  },
}

onMounted(async () => {
  initThree()

  bannersAPI.getAll()
    .then(r => { banners.value = r.data; bannersLoading.value = false })
    .catch(() => { bannersLoading.value = false })

  const cc = cache.get('home_categories')
  const bc = cache.get('home_brands')
  if (cc && bc) {
    categories.value = cc; brands.value = bc; loading.value = false
  } else {
    try {
      const [cr, br] = await Promise.all([categoriesAPI.getAll(), brandsAPI.getAll()])
      categories.value = cr.data.results ?? cr.data
      brands.value     = br.data.results ?? br.data
      cache.set('home_categories', categories.value, 120000)
      cache.set('home_brands',     brands.value,     120000)
    } catch (e) { console.error(e) }
    finally { loading.value = false }
  }

  // Init animations after DOM is fully ready
  await nextTick()
  await new Promise(r => setTimeout(r, 80))
  try { initAnimations() } catch(e) { console.warn('Anim init:', e) }
})

onUnmounted(() => {
  cancelAnimationFrame(animFrameId)
  window.removeEventListener('mousemove', onMouseMove)
  window.removeEventListener('resize', onResize)
  ScrollTrigger.getAll().forEach(t => t.kill())
})
</script>

<style scoped>
/* ════════════════════════════════════════════════════════
   BASE
════════════════════════════════════════════════════════ */
.home-page { overflow-x: hidden; background: var(--light); }

/* ════════════════════════════════════════════════════════
   HERO
════════════════════════════════════════════════════════ */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #081c15 0%, #0a0a0b 50%, #0d1f18 100%);
  overflow: hidden;
}

.hero-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.hero-inner {
  position: relative;
  z-index: 2;
  max-width: 1200px;
  margin: 0 auto;
  padding: 120px 40px 80px;
  width: 100%;
}

/* Hero CSS entrance animations */
.hero-badge   { animation: heroUp 0.8s cubic-bezier(0.19,1,0.22,1) 0.2s both; }
.hero-title   { animation: heroUp 0.9s cubic-bezier(0.19,1,0.22,1) 0.4s both; }
.hero-sub     { animation: heroUp 0.8s cubic-bezier(0.19,1,0.22,1) 0.6s both; }
.hero-actions { animation: heroUp 0.8s cubic-bezier(0.19,1,0.22,1) 0.75s both; }
.hero-stats   { animation: heroUp 0.8s cubic-bezier(0.19,1,0.22,1) 0.9s both; }
.hero-scroll-hint { animation: heroFade 1s ease 1.2s both; }

@keyframes heroUp {
  from { opacity: 0; transform: translateY(50px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes heroFade {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Badge */
.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 18px;
  background: rgba(212, 165, 116, 0.1);
  border: 1px solid rgba(212, 165, 116, 0.3);
  border-radius: 999px;
  color: var(--accent);
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-bottom: 28px;
  backdrop-filter: blur(8px);
}

.badge-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--accent);
  box-shadow: 0 0 8px var(--accent);
  animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
  0%,100% { box-shadow: 0 0 8px var(--accent); }
  50%      { box-shadow: 0 0 18px var(--accent), 0 0 30px rgba(212,165,116,0.4); }
}

/* Title */
.hero-title {
  display: flex;
  flex-direction: column;
  font-size: clamp(3rem, 8vw, 6.5rem);
  font-weight: 900;
  line-height: 1.02;
  letter-spacing: -0.03em;
  color: #fff;
  margin-bottom: 28px;
}

.title-accent {
  background: linear-gradient(135deg, #e5b889, #d4a574, #b8956a);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-sub {
  font-size: clamp(1rem, 2vw, 1.2rem);
  color: rgba(255,255,255,0.6);
  max-width: 520px;
  line-height: 1.7;
  margin-bottom: 40px;
}

/* Buttons */
.hero-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-bottom: 60px;
}

.btn-primary-3d {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 36px;
  background: linear-gradient(135deg, #e5b889, #d4a574, #b8956a);
  color: #081c15;
  font-weight: 700;
  font-size: 1rem;
  border-radius: 14px;
  text-decoration: none;
  overflow: hidden;
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.3s ease;
  box-shadow: 0 4px 24px rgba(212,165,116,0.35), 0 2px 8px rgba(0,0,0,0.3);
}
.btn-primary-3d:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 0 12px 40px rgba(212,165,116,0.5), 0 4px 16px rgba(0,0,0,0.3);
  color: #081c15;
}
.btn-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}
.btn-primary-3d:hover .btn-glow { opacity: 1; }

.btn-ghost-3d {
  padding: 16px 32px;
  border: 1.5px solid rgba(255,255,255,0.2);
  border-radius: 14px;
  color: rgba(255,255,255,0.8);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  backdrop-filter: blur(8px);
}
.btn-ghost-3d:hover {
  border-color: rgba(212,165,116,0.5);
  color: var(--accent);
  background: rgba(212,165,116,0.05);
}

/* Stats */
.hero-stats {
  display: flex;
  gap: 48px;
  flex-wrap: wrap;
}
.stat-item {
  position: relative;
}
.stat-item::after {
  content: '';
  position: absolute;
  right: -24px;
  top: 20%;
  height: 60%;
  width: 1px;
  background: rgba(255,255,255,0.1);
}
.stat-item:last-child::after { display: none; }

.stat-number {
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 800;
  color: var(--accent);
  letter-spacing: -0.02em;
  line-height: 1;
  margin-bottom: 4px;
}
.stat-label {
  font-size: 0.78rem;
  color: rgba(255,255,255,0.45);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 500;
}

/* Scroll hint */
.hero-scroll-hint {
  position: absolute;
  bottom: 36px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: rgba(255,255,255,0.3);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  z-index: 2;
}
.scroll-line {
  width: 1px;
  height: 48px;
  background: linear-gradient(to bottom, rgba(212,165,116,0.7), transparent);
  animation: scroll-line 2s infinite;
}
@keyframes scroll-line {
  0%   { transform: scaleY(0); transform-origin: top; opacity: 1; }
  50%  { transform: scaleY(1); transform-origin: top; opacity: 1; }
  100% { transform: scaleY(1); transform-origin: bottom; opacity: 0; }
}

/* Orbs */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 1;
}
.orb-1 {
  width: 600px; height: 600px;
  background: radial-gradient(circle, rgba(27,67,50,0.5) 0%, transparent 70%);
  top: -200px; right: -150px;
  animation: orb-float 12s ease-in-out infinite;
}
.orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(212,165,116,0.15) 0%, transparent 70%);
  bottom: 0; left: -100px;
  animation: orb-float 9s ease-in-out infinite reverse;
}
.orb-3 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(45,106,79,0.3) 0%, transparent 70%);
  top: 40%; right: 20%;
  animation: orb-float 15s ease-in-out infinite;
}
@keyframes orb-float {
  0%,100% { transform: translate(0,0) scale(1); }
  33%      { transform: translate(30px,-20px) scale(1.05); }
  66%      { transform: translate(-20px,15px) scale(0.95); }
}

/* ════════════════════════════════════════════════════════
   MARQUEE
════════════════════════════════════════════════════════ */
@keyframes marquee-scroll {
  from { transform: translateX(0); }
  to   { transform: translateX(-33.333%); }
}
.marquee-wrap {
  background: var(--dark);
  border-top: 1px solid rgba(212,165,116,0.1);
  border-bottom: 1px solid rgba(212,165,116,0.1);
  padding: 12px 0;
  overflow: hidden;
}
.marquee-track { overflow: hidden; }
.marquee-inner {
  display: flex;
  gap: 48px;
  width: max-content;
  animation: marquee-scroll 20s linear infinite;
}
.marquee-wrap:hover .marquee-inner { animation-play-state: paused; }
.marquee-item {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  height: 50px;
  min-width: 130px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
  border: 1px solid rgba(255,255,255,0.06);
  transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
              box-shadow 0.3s ease;
}
.marquee-item:hover {
  transform: translateY(-4px) scale(1.06);
  box-shadow: 0 12px 32px rgba(0,0,0,0.3), 0 0 0 1px rgba(212,165,116,0.35);
}
.marquee-item img {
  height: 36px;
  width: auto;
  max-width: 110px;
  object-fit: contain;
  /* Full color — no filter */
  filter: none;
  opacity: 1;
  display: block;
}
.marquee-item span {
  color: var(--gray-700);
  font-size: 0.95rem;
  font-weight: 800;
  white-space: nowrap;
  letter-spacing: -0.01em;
}

/* ════════════════════════════════════════════════════════
   BANNER
════════════════════════════════════════════════════════ */
.banner-section {
  padding: 60px 40px;
  background: linear-gradient(180deg, #0a0a0b 0%, var(--light) 100%);
  perspective: 1200px;
}
.banner-3d-wrapper {
  max-width: 1320px;
  margin: 0 auto;
  transform-style: preserve-3d;
  will-change: transform;
}
.banner-container-inner {
  border-radius: 24px;
  overflow: hidden;
  box-shadow:
    0 32px 80px rgba(0,0,0,0.35),
    0 0 0 1px rgba(212,165,116,0.12),
    inset 0 1px 0 rgba(255,255,255,0.08);
}
.banner-reflection {
  margin: 0 8% -20px;
  height: 60px;
  background: inherit;
  filter: blur(20px);
  opacity: 0.25;
  border-radius: 50%;
  transform: scaleY(0.3);
}

/* ════════════════════════════════════════════════════════
   SHARED SECTION STYLES
════════════════════════════════════════════════════════ */
.section-container {
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 40px;
}
.section-header {
  text-align: center;
  margin-bottom: 56px;
}
.section-label {
  display: inline-block;
  padding: 5px 16px;
  background: var(--accent-light);
  border: 1px solid rgba(212,165,116,0.25);
  border-radius: 999px;
  color: var(--accent-dark);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.section-title {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 800;
  color: var(--gray-900);
  letter-spacing: -0.03em;
  margin-bottom: 16px;
}
.section-desc {
  font-size: 1.05rem;
  color: var(--gray-500);
  max-width: 520px;
  margin: 0 auto;
  line-height: 1.7;
}

/* ════════════════════════════════════════════════════════
   CATEGORIES 3D GRID
════════════════════════════════════════════════════════ */
.categories-section {
  padding: 100px 0;
  background: var(--light);
}

.cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}

.cat-card-3d {
  cursor: pointer;
  transform-style: preserve-3d;
  perspective: 800px;
  will-change: transform;
}

.card-inner {
  position: relative;
  background: var(--white);
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: var(--shadow-card);
  transition: box-shadow 0.4s ease;
}
.cat-card-3d:hover .card-inner {
  box-shadow: 0 20px 60px rgba(27,67,50,0.12), 0 8px 24px rgba(0,0,0,0.08);
}

.card-image-wrap {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: var(--gray-100);
}
.card-img {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.19,1,0.22,1);
}
.cat-card-3d:hover .card-img { transform: scale(1.08); }

.card-img-placeholder {
  width: 100%; height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gray-400);
  background: linear-gradient(135deg, var(--gray-100), var(--gray-50));
}

.card-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.4) 50%, transparent 60%);
  transform: translateX(-100%);
  transition: transform 0s;
}
.cat-card-3d:hover .card-shimmer {
  transform: translateX(100%);
  transition: transform 0.6s ease;
}

.card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
}
.card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--gray-900);
  letter-spacing: -0.01em;
  margin: 0;
}
.card-arrow {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: var(--primary-light);
  display: flex; align-items: center; justify-content: center;
  color: var(--primary);
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  flex-shrink: 0;
}
.cat-card-3d:hover .card-arrow {
  background: var(--primary);
  color: white;
  transform: rotate(45deg);
}

.card-glow {
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 80px;
  background: radial-gradient(circle, rgba(27,67,50,0.15) 0%, transparent 70%);
  filter: blur(12px);
  transition: opacity 0.3s;
  opacity: 0;
  pointer-events: none;
}
.cat-card-3d:hover .card-glow { opacity: 1; }

.cat-card-skeleton {
  border-radius: 20px;
  aspect-ratio: 3/2.4;
  background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* ════════════════════════════════════════════════════════
   FEATURES BENTO
════════════════════════════════════════════════════════ */
.features-section {
  padding: 100px 0;
  background: linear-gradient(180deg, var(--light) 0%, var(--gray-50) 100%);
}

.bento-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: auto auto;
  gap: 20px;
}

.bento-card {
  position: relative;
  background: var(--white);
  border-radius: 24px;
  padding: 36px 32px;
  border: 1px solid rgba(0,0,0,0.06);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.4s ease;
}
.bento-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 24px 64px rgba(27,67,50,0.1), 0 8px 24px rgba(0,0,0,0.06);
}

.bento-tall  { grid-column: span 5; grid-row: span 2; }
.bento-wide  { grid-column: span 7; }
.bento-small { grid-column: span 3; }

.bento-icon {
  margin-bottom: 24px;
}
.icon-ring {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary-light), rgba(27,67,50,0.04));
  border: 1.5px solid rgba(27,67,50,0.12);
  display: flex; align-items: center; justify-content: center;
  color: var(--primary);
  transition: all 0.3s ease;
}
.bento-card:hover .icon-ring {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
  transform: rotate(-6deg) scale(1.1);
}

.bento-title {
  font-size: 1.2rem;
  font-weight: 800;
  color: var(--gray-900);
  margin-bottom: 12px;
  letter-spacing: -0.02em;
}
.bento-desc {
  font-size: 0.9rem;
  color: var(--gray-500);
  line-height: 1.7;
  margin: 0;
}

.bento-bg-shape {
  position: absolute;
  bottom: -60px; right: -60px;
  width: 200px; height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(27,67,50,0.04) 0%, transparent 70%);
  transition: transform 0.6s ease;
  pointer-events: none;
}
.bento-card:hover .bento-bg-shape { transform: scale(1.4); }

/* ════════════════════════════════════════════════════════
   BRANDS — infinite two-row scroll
════════════════════════════════════════════════════════ */
@keyframes brands-ltr {
  from { transform: translateX(0); }
  to   { transform: translateX(-50%); }
}
@keyframes brands-rtl {
  from { transform: translateX(-50%); }
  to   { transform: translateX(0); }
}

.brands-section {
  padding: 100px 0;
  background: linear-gradient(180deg, #fff 0%, #f8faf8 100%);
  overflow: hidden;
}

.brands-scroll-stage {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 52px;
  overflow: hidden;
  position: relative;
}

/* edge fade */
.brands-scroll-stage::before,
.brands-scroll-stage::after {
  content: "";
  position: absolute;
  top: 0; bottom: 0;
  width: 140px;
  z-index: 2;
  pointer-events: none;
}
.brands-scroll-stage::before {
  left: 0;
  background: linear-gradient(to right, #f8faf8, transparent);
}
.brands-scroll-stage::after {
  right: 0;
  background: linear-gradient(to left, #f8faf8, transparent);
}

.brands-scroll-row {
  display: flex;
  width: max-content;
}

.brands-scroll-inner {
  display: flex;
  gap: 16px;
  flex-shrink: 0;
}

.brands-scroll-ltr { animation: brands-ltr 22s linear infinite; padding: 10px}
.brands-scroll-rtl { animation: brands-rtl 22s linear infinite; padding: 10px}

/* Pause whole row on hover */
.brands-scroll-stage:hover .brands-scroll-inner {
  animation-play-state: paused;
}

.brand-card-3d {
  cursor: pointer;
  border-radius: 18px;
  border: 1.5px solid rgba(27,67,50,0.12);
  padding: 20px 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100px;
  min-width: 168px;
  background: #fff;
  box-shadow: 0 2px 16px rgba(0,0,0,0.07);
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  flex-shrink: 0;
}
.brand-card-3d:hover {
  border-color: rgba(212,165,116,0.5);
  transform: translateY(-6px) scale(1.05);
  box-shadow: 0 20px 48px rgba(27,67,50,0.16), 0 0 0 1px rgba(212,165,116,0.2);
}
.brand-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}
.brand-logo {
  max-height: 85px;
  max-width: 130px;
  width: auto;
  height: auto;
  object-fit: contain;
  /* Full color, full opacity — always visible */
  filter: none;
  opacity: 1;
  transition: transform 0.3s ease, filter 0.3s ease;
}
.brand-card-3d:hover .brand-logo {
  transform: scale(1.08);
  filter: drop-shadow(0 4px 12px rgba(27,67,50,0.2));
}
.brand-name-text {
  font-weight: 400;
  font-size: 1rem;
  color: var(--gray-700);
  transition: color 0.3s;
  letter-spacing: -0.01em;
}
.brand-card-3d:hover .brand-name-text { color: var(--primary); }

.brands-cta { text-align: center; }
.btn-outline-gold {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 14px 32px;
  border: 2px solid var(--accent);
  border-radius: 12px;
  color: var(--accent-dark);
  font-weight: 700;
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
}
.btn-outline-gold:hover {
  background: var(--accent);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(212,165,116,0.35);
}

/* ════════════════════════════════════════════════════════
   CTA
════════════════════════════════════════════════════════ */
.cta-section {
  position: relative;
  padding: 140px 40px;
  background: linear-gradient(135deg, #081c15 0%, #0a0a0b 60%, #0d1f18 100%);
  text-align: center;
  overflow: hidden;
}
.cta-inner {
  position: relative;
  z-index: 2;
  max-width: 700px;
  margin: 0 auto;
}
.cta-badge {
  display: inline-block;
  padding: 6px 18px;
  border: 1px solid rgba(212,165,116,0.3);
  border-radius: 999px;
  color: var(--accent);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 28px;
  background: rgba(212,165,116,0.05);
}
.cta-title {
  font-size: clamp(2rem, 5vw, 3.8rem);
  font-weight: 900;
  color: white;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin-bottom: 20px;
}
.cta-accent {
  background: linear-gradient(135deg, #e5b889, #d4a574);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.cta-sub {
  font-size: 1.05rem;
  color: rgba(255,255,255,0.5);
  margin-bottom: 44px;
  line-height: 1.7;
}
.btn-gold-3d {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 18px 48px;
  background: linear-gradient(135deg, #e5b889, #d4a574, #b8956a);
  color: #081c15;
  font-weight: 800;
  font-size: 1.05rem;
  border-radius: 16px;
  text-decoration: none;
  overflow: hidden;
  transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
  box-shadow: 0 6px 32px rgba(212,165,116,0.4), 0 2px 8px rgba(0,0,0,0.3);
}
.btn-gold-3d:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 16px 60px rgba(212,165,116,0.55), 0 4px 16px rgba(0,0,0,0.3);
  color: #081c15;
}
.btn-shine {
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.35) 50%, transparent 60%);
  transform: translateX(-100%);
  transition: transform 0s;
}
.btn-gold-3d:hover .btn-shine {
  transform: translateX(100%);
  transition: transform 0.55s ease;
}

.cta-orb {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  filter: blur(90px);
}
.cta-orb-1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(27,67,50,0.45) 0%, transparent 70%);
  top: -150px; left: -100px;
}
.cta-orb-2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(212,165,116,0.12) 0%, transparent 70%);
  bottom: -100px; right: -80px;
}

/* ════════════════════════════════════════════════════════
   RESPONSIVE
════════════════════════════════════════════════════════ */
@media (max-width: 1024px) {
  .bento-tall  { grid-column: span 6; }
  .bento-wide  { grid-column: span 6; }
  .bento-small { grid-column: span 6; }
}

@media (max-width: 768px) {
  .hero-inner { padding: 100px 20px 60px; }
  .hero-stats { gap: 28px; }
  .stat-item::after { display: none; }
  .banner-section { padding: 32px 16px; }
  .section-container { padding: 0 20px; }
  .categories-section, .features-section, .brands-section { padding: 72px 0; }
  .bento-tall, .bento-wide, .bento-small { grid-column: span 12; }
  .cat-grid { grid-template-columns: repeat(2, 1fr); gap: 14px; }
  .brands-3d-grid { grid-template-columns: repeat(3, 1fr); }
  .cta-section { padding: 90px 20px; }
}

@media (max-width: 480px) {
  .cat-grid { grid-template-columns: 1fr 1fr; gap: 10px; }
  .brands-3d-grid { grid-template-columns: repeat(2, 1fr); }
  .hero-actions { flex-direction: column; align-items: flex-start; }
}

@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
