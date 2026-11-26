<template>
  <div class="product-detail-page">
    <div class="container">
      <!-- Breadcrumb -->
      <nav v-if="product" class="breadcrumb">
        <router-link to="/" class="breadcrumb-item">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
          </svg>
          Главная
        </router-link>
        <span class="breadcrumb-separator">›</span>
        <router-link to="/catalog" class="breadcrumb-item">Каталог</router-link>
        <template v-for="crumb in product.breadcrumbs ?? []" :key="crumb.slug">
          <span class="breadcrumb-separator">›</span>
          <router-link :to="`/catalog/${crumb.slug}`" class="breadcrumb-item">
            {{ crumb.name }}
          </router-link>
        </template>
        <span class="breadcrumb-separator">›</span>
        <span class="breadcrumb-current">{{ product.name }}</span>
      </nav>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка товара...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="error-state">
        <svg
          width="64"
          height="64"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="8" x2="12" y2="12" />
          <line x1="12" y1="16" x2="12.01" y2="16" />
        </svg>
        <h3>{{ error }}</h3>
        <router-link to="/catalog" class="btn btn-primary"> Вернуться в каталог </router-link>
      </div>

      <!-- Product Content: 3-zone layout -->
      <div v-else-if="product" class="pd-grid">
        <!-- Zone 1: Gallery -->
        <div class="pd-gallery">
          <ImageGalleryComponent :images="product.images" :alt="product.name" />
        </div>

        <!-- Zone 2: Product Info (center) -->
        <div class="pd-info">
          <h1 class="pd-title">{{ product.name }}</h1>

          <!-- Meta table -->
          <div class="pd-meta">
            <div v-if="product.brand" class="pd-meta-item">
              <span class="pd-meta-label">Бренд</span>
              <router-link
                v-if="(product.brand as any)?.slug"
                :to="`/brands/${(product.brand as any).slug}`"
                class="pd-meta-value pd-meta-link"
              >
                {{ (product.brand as any).name || (product.brand as any) }}
              </router-link>
              <span v-else class="pd-meta-value">
                {{ (product.brand as any).name || product.brand }}
              </span>
            </div>
            <div v-if="product.manufacturer_sku || product.internal_sku" class="pd-meta-item">
              <span class="pd-meta-label">Артикул</span>
              <span class="pd-meta-value pd-sku-value">
                <code>{{ product.manufacturer_sku || product.internal_sku }}</code>
                <button
                  class="pd-copy-btn"
                  :class="{ copied: isCopied }"
                  title="Копировать"
                  @click="copySku(product.manufacturer_sku || product.internal_sku)"
                >
                  <svg
                    v-if="!isCopied"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                  <svg
                    v-else
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                  >
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </button>
              </span>
            </div>
            <div class="pd-meta-item">
              <span class="pd-meta-label">Код товара</span>
              <span class="pd-meta-value">{{ productCode }}</span>
            </div>
            <div v-if="product.category" class="pd-meta-item">
              <span class="pd-meta-label">Каталог</span>
              <router-link
                :to="`/catalog/${(product.category as any)?.slug}`"
                class="pd-meta-value pd-meta-link"
              >
                {{ (product.category as any)?.name }}
              </router-link>
            </div>
          </div>

          <!-- Characteristics preview (first 5) -->
          <div v-if="featureRows.length > 0" class="pd-features-preview">
            <h3 class="pd-section-title">Характеристики</h3>
            <div class="pd-features-list">
              <div v-for="(feature, i) in featureRows.slice(0, 2)" :key="i" class="pd-feat-row">
                <span class="pd-feat-name">{{ feature.name }}</span>
                <span class="pd-feat-dots"></span>
                <span class="pd-feat-val">{{ feature.values.join(", ") }}</span>
              </div>
            </div>
            <button
              v-if="featureRows.length > 2"
              class="pd-all-chars-link"
              @click="
                activeTab = 'characteristics';
                scrollToTabs();
              "
            >
              Читать далее
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M9 18l6-6-6-6" />
              </svg>
            </button>
          </div>

          <!-- Description preview -->
          <div v-if="product.description" class="pd-desc-preview">
            <h3 class="pd-section-title">Описание</h3>
            <div class="pd-desc-text" v-html="truncatedDescription"></div>
            <button
              v-if="product.description.length > 100"
              class="pd-all-chars-link"
              @click="
                activeTab = 'description';
                scrollToTabs();
              "
            >
              Читать далее
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M9 18l6-6-6-6" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Zone 3: Price & Actions sidebar -->
        <div class="pd-sidebar">
          <div class="pd-price-card">
            <!-- Price -->
            <div v-if="product.price != null" class="pd-price-block">
              <span class="pd-price-hint">Цена:</span>
              <div class="pd-price-amount">{{ price.price }}</div>
              <div v-if="price.old" class="pd-price-old">
                <s>{{ price.old }}</s>
                <span class="pd-discount">{{ price.discount }}</span>
              </div>
            </div>
            <div v-else class="pd-price-block">
              <span class="pd-price-request">Цена по запросу</span>
            </div>
            <p class="pd-stock" :class="`is-${stock.tone}`">{{ stock.text }}</p>

            <!-- Cart button -->
            <div class="pd-cart-actions">
              <template v-if="cartStore.isInCart(product.id)">
                <div class="pd-qty-control">
                  <button class="pd-qty-btn" @click="decrementQty">−</button>
                  <span class="pd-qty-value">{{ cartQty }}</span>
                  <button class="pd-qty-btn" @click="incrementQty">+</button>
                </div>
                <router-link to="/cart" class="pd-go-cart-btn">
                  <svg
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <circle cx="9" cy="21" r="1" />
                    <circle cx="20" cy="21" r="1" />
                    <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                  </svg>
                  Перейти в корзину
                </router-link>
              </template>
              <button v-else class="pd-add-cart-btn" @click="cartStore.add(product, 1)">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="9" cy="21" r="1" />
                  <circle cx="20" cy="21" r="1" />
                  <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6" />
                </svg>
                В корзину
              </button>
            </div>

            <!-- Quick actions -->
            <div class="pd-quick-actions">
              <button
                class="pd-action-btn"
                :class="{ active: favStore.isFavorite(product.id) }"
                :title="favStore.isFavorite(product.id) ? 'Убрать из избранного' : 'В избранное'"
                @click="favStore.toggle(product)"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  :fill="favStore.isFavorite(product.id) ? 'currentColor' : 'none'"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"
                  />
                </svg>
              </button>
              <button
                class="pd-action-btn"
                :class="{
                  active: compareStore.isInCompare(product.id),
                  disabled: compareStore.isFull && !compareStore.isInCompare(product.id),
                }"
                title="Сравнить"
                @click="toggleCompare"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <line x1="18" y1="20" x2="18" y2="10" />
                  <line x1="12" y1="20" x2="12" y2="4" />
                  <line x1="6" y1="20" x2="6" y2="14" />
                </svg>
              </button>
            </div>

            <!-- Info items -->
            <div class="pd-info-items">
              <div class="pd-info-item" :class="product.is_available ? 'available' : 'unavailable'">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path v-if="product.is_available" d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                  <polyline v-if="product.is_available" points="22 4 12 14.01 9 11.01" />
                  <circle v-if="!product.is_available" cx="12" cy="12" r="10" />
                  <line v-if="!product.is_available" x1="15" y1="9" x2="9" y2="15" />
                  <line v-if="!product.is_available" x1="9" y1="9" x2="15" y2="15" />
                </svg>
                <span>{{ stock.text }}</span>
              </div>
              <div class="pd-info-item">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <rect x="1" y="3" width="15" height="13" rx="2" ry="2" />
                  <path d="M16 8h4l3 3v5a2 2 0 0 1-2 2h-1" />
                  <circle cx="5.5" cy="18.5" r="2.5" />
                  <circle cx="18.5" cy="18.5" r="2.5" />
                </svg>
                <span>Доставка по Узбекистану</span>
              </div>
              <div class="pd-info-item">
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                <span>Гарантия качества</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Product Tabs Section -->
      <div v-if="product" ref="tabsRef" class="product-tabs-layout">
        <div class="tabs-navigation">
          <button
            class="tab-button"
            :class="{ active: activeTab === 'description' }"
            @click="activeTab = 'description'"
          >
            Описание
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'characteristics' }"
            @click="activeTab = 'characteristics'"
          >
            Характеристики
          </button>
          <button
            v-if="product.related?.length"
            class="tab-button"
            :class="{ active: activeTab === 'related' }"
            @click="activeTab = 'related'"
          >
            Сопутствующие товары
          </button>
          <button
            v-if="product.documents?.length"
            class="tab-button"
            :class="{ active: activeTab === 'documents' }"
            @click="activeTab = 'documents'"
          >
            Документация
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'reviews' }"
            @click="activeTab = 'reviews'"
          >
            Отзывы
            <span v-if="reviewsTotal" class="tab-badge">{{ reviewsTotal }}</span>
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'questions' }"
            @click="activeTab = 'questions'"
          >
            Вопросы
            <span v-if="questionsTotal" class="tab-badge">{{ questionsTotal }}</span>
          </button>
        </div>

        <div class="tabs-content">
          <!-- Description Tab -->
          <div
            v-show="activeTab === 'description'"
            class="tab-panel"
            :class="{ active: activeTab === 'description' }"
          >
            <div v-if="product.description" class="description-content">
              <div v-html="formatContent(product.description)"></div>
            </div>
            <div v-else class="empty-state">
              <p>Описание отсутствует</p>
            </div>
          </div>

          <!-- Characteristics Tab -->
          <div
            v-show="activeTab === 'characteristics'"
            class="tab-panel"
            :class="{ active: activeTab === 'characteristics' }"
          >
            <div v-if="featureRows.length > 0" class="characteristics-table">
              <table>
                <tbody v-for="group in product.feature_groups" :key="group.group">
                  <tr class="characteristic-group">
                    <th colspan="2">{{ group.group }}</th>
                  </tr>
                  <tr v-for="row in group.items" :key="row.name" class="characteristic-row">
                    <td class="characteristic-name">{{ row.name }}</td>
                    <td class="characteristic-value">
                      <span v-for="value in row.values" :key="value" class="value-item">
                        {{ value }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else class="empty-state">
              <p>Характеристики отсутствуют</p>
            </div>
          </div>

          <!-- Related products Tab -->
          <div
            v-show="activeTab === 'related'"
            class="tab-panel"
            :class="{ active: activeTab === 'related' }"
          >
            <div class="products-grid">
              <ProductCard v-for="item in product.related ?? []" :key="item.id" :product="item" />
            </div>
          </div>

          <!-- Documents Tab -->
          <div
            v-show="activeTab === 'documents'"
            class="tab-panel"
            :class="{ active: activeTab === 'documents' }"
          >
            <ul class="pd-documents">
              <li v-for="doc in product.documents ?? []" :key="doc.id">
                <a :href="doc.url ?? undefined" target="_blank" rel="noopener" download>
                  {{ doc.title }}
                </a>
                <span class="pd-doc-meta"
                  >{{ doc.ext.toUpperCase() }} {{ fileSize(doc.size) }}</span
                >
              </li>
            </ul>
          </div>

          <!-- Reviews Tab -->
          <div
            v-show="activeTab === 'reviews'"
            class="tab-panel"
            :class="{ active: activeTab === 'reviews' }"
          >
            <div class="reviews-header">
              <div v-if="reviews.length" class="avg-rating">
                <div class="avg-stars">
                  <svg
                    v-for="s in 5"
                    :key="s"
                    width="20"
                    height="20"
                    viewBox="0 0 24 24"
                    :fill="s <= Math.round(avgRating) ? '#f59e0b' : 'none'"
                    :stroke="s <= Math.round(avgRating) ? '#f59e0b' : '#d1d5db'"
                    stroke-width="2"
                  >
                    <polygon
                      points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                    />
                  </svg>
                </div>
                <span class="avg-value">{{ avgRating.toFixed(1) }}</span>
              </div>
              <button
                class="rw-add-btn"
                @click="
                  showReviewForm = !showReviewForm;
                  reviewNotice = '';
                  reviewError = '';
                "
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="16" />
                  <line x1="8" y1="12" x2="16" y2="12" />
                </svg>
                Добавить отзыв
              </button>
            </div>

            <!-- Review form -->
            <p v-if="reviewNotice" class="rw-notice">{{ reviewNotice }}</p>
            <p v-if="reviewError" class="rw-notice rw-notice--error">{{ reviewError }}</p>
            <div v-if="showReviewForm" class="rw-form">
              <h4 class="rw-form-title">Ваш отзыв</h4>
              <div class="rw-form-field">
                <label>Ваше имя</label>
                <input
                  v-model="reviewForm.author_name"
                  type="text"
                  placeholder="Имя"
                  maxlength="150"
                />
              </div>
              <div class="rw-form-field">
                <label>Оценка</label>
                <div class="rw-star-select">
                  <button
                    v-for="s in 5"
                    :key="s"
                    type="button"
                    class="rw-star-btn"
                    :class="{ active: s <= reviewForm.rating }"
                    @click="reviewForm.rating = s"
                  >
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      :fill="s <= reviewForm.rating ? '#f59e0b' : 'none'"
                      :stroke="s <= reviewForm.rating ? '#f59e0b' : '#d1d5db'"
                      stroke-width="2"
                    >
                      <polygon
                        points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                      />
                    </svg>
                  </button>
                </div>
              </div>
              <div class="rw-form-field">
                <label>Текст отзыва</label>
                <textarea
                  v-model="reviewForm.text"
                  maxlength="2000"
                  rows="4"
                  placeholder="Напишите ваш отзыв..."
                ></textarea>
              </div>
              <div class="rw-form-actions">
                <button
                  class="rw-submit-btn"
                  :disabled="!reviewForm.author_name || !reviewForm.text || reviewForm.rating === 0"
                  @click="submitReview"
                >
                  Отправить
                </button>
                <button class="rw-cancel-btn" @click="showReviewForm = false">Отмена</button>
              </div>
            </div>

            <!-- Reviews list -->
            <div v-if="reviews.length" class="rw-list">
              <div v-for="review in reviews" :key="review.id" class="rw-item">
                <div class="rw-item-header">
                  <div class="rw-author">{{ review.author_name }}</div>
                  <div class="rw-stars">
                    <svg
                      v-for="s in 5"
                      :key="s"
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      :fill="s <= review.rating ? '#f59e0b' : 'none'"
                      :stroke="s <= review.rating ? '#f59e0b' : '#d1d5db'"
                      stroke-width="2"
                    >
                      <polygon
                        points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"
                      />
                    </svg>
                  </div>
                  <div class="rw-date">{{ formatDate(review.created_at) }}</div>
                </div>
                <div class="rw-text">{{ review.text }}</div>
                <div v-if="review.admin_reply" class="rw-reply">
                  <div class="rw-reply-header">
                    <span class="rw-reply-author">Nargiza</span>
                    <span class="rw-reply-date">{{ formatDate(review.admin_reply_date) }}</span>
                  </div>
                  <div class="rw-reply-text">{{ review.admin_reply }}</div>
                </div>
              </div>
            </div>
            <div v-else-if="!showReviewForm" class="empty-state">
              <p>Отзывов пока нет. Будьте первым!</p>
            </div>
          </div>

          <!-- Questions Tab -->
          <div
            v-show="activeTab === 'questions'"
            class="tab-panel"
            :class="{ active: activeTab === 'questions' }"
          >
            <div class="reviews-header">
              <span></span>
              <button
                class="rw-add-btn"
                @click="
                  showQuestionForm = !showQuestionForm;
                  questionNotice = '';
                  questionError = '';
                "
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="16" />
                  <line x1="8" y1="12" x2="16" y2="12" />
                </svg>
                Задать вопрос
              </button>
            </div>

            <!-- Question form -->
            <p v-if="questionNotice" class="rw-notice">{{ questionNotice }}</p>
            <p v-if="questionError" class="rw-notice rw-notice--error">{{ questionError }}</p>
            <div v-if="showQuestionForm" class="rw-form">
              <h4 class="rw-form-title">Ваш вопрос</h4>
              <div class="rw-form-field">
                <label>Ваше имя</label>
                <input
                  v-model="questionForm.author_name"
                  type="text"
                  placeholder="Имя"
                  maxlength="150"
                />
              </div>
              <div class="rw-form-field">
                <label>Текст вопроса</label>
                <textarea
                  v-model="questionForm.text"
                  maxlength="1000"
                  rows="4"
                  placeholder="Напишите ваш вопрос..."
                ></textarea>
              </div>
              <div class="rw-form-actions">
                <button
                  class="rw-submit-btn"
                  :disabled="!questionForm.author_name || !questionForm.text"
                  @click="submitQuestion"
                >
                  Отправить
                </button>
                <button class="rw-cancel-btn" @click="showQuestionForm = false">Отмена</button>
              </div>
            </div>

            <!-- Questions list -->
            <div v-if="questions.length" class="rw-list">
              <div v-for="q in questions" :key="q.id" class="rw-item">
                <div class="rw-item-header">
                  <div class="rw-author">{{ q.author_name }}</div>
                  <div class="rw-date">{{ formatDate(q.created_at) }}</div>
                </div>
                <div class="rw-text">{{ q.text }}</div>
                <div v-if="q.admin_reply" class="rw-reply">
                  <div class="rw-reply-header">
                    <span class="rw-reply-author">Nargiza</span>
                    <span class="rw-reply-date">{{ formatDate(q.admin_reply_date) }}</span>
                  </div>
                  <div class="rw-reply-text">{{ q.admin_reply }}</div>
                </div>
              </div>
            </div>
            <div v-else-if="!showQuestionForm" class="empty-state">
              <p>Вопросов пока нет. Задайте первый!</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Similar Products -->
      <div v-if="similarProducts.length > 0" class="similar-section">
        <h2 class="similar-title">Похожие товары</h2>
        <div class="similar-grid">
          <ProductCard v-for="p in similarProducts" :key="p.id" :product="p" />
        </div>
      </div>

      <!-- Contact Modal -->
      <transition name="modal">
        <div v-if="showContactModal" class="modal-overlay" @click="closeModal">
          <div class="modal-content" @click.stop>
            <button class="modal-close" @click="closeModal">
              <svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>

            <h2 class="modal-title">Оформить заказ</h2>
            <p class="modal-subtitle">
              Товар: <strong>{{ product?.name }}</strong>
            </p>

            <div v-if="contactInfo" class="contact-details">
              <div class="contact-item">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
                  />
                </svg>
                <div>
                  <span class="contact-label">Телефон</span>
                  <a :href="`tel:${contactInfo.phone}`" class="contact-value">{{
                    contactInfo.phone
                  }}</a>
                </div>
              </div>

              <div class="contact-item">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"
                  />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                <div>
                  <span class="contact-label">Email</span>
                  <a :href="`mailto:${contactInfo.email}`" class="contact-value">{{
                    contactInfo.email
                  }}</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { describeSubmitError } from "@/utils/apiError";
import { ref, onMounted, computed, watch } from "vue";
import { textToHtml, truncateText } from "@/utils/richText";
import { fileSize, priceView, stockLabel } from "@/utils/productView";
import { useRoute } from "vue-router";
import { productsAPI, contactAPI, reviewsAPI, questionsAPI, similarProductsAPI } from "@/api";
import ImageGalleryComponent from "@/components/ImageGalleryComponent.vue";
import ProductCard from "@/components/ProductCard.vue";
import { useCartStore } from "@/stores/useCartStore";
import { useFavoritesStore } from "@/stores/useFavoritesStore";
import { useCompareStore } from "@/stores/useCompareStore";
import type { Product, ContactInfo, Review, ProductQuestion } from "@/types";

const route = useRoute();
const cartStore = useCartStore();
const favStore = useFavoritesStore();
const compareStore = useCompareStore();

const product = ref<Product | null>(null);
const contactInfo = ref<ContactInfo | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);
const showContactModal = ref(false);
const isCopied = ref(false);
const activeTab = ref<
  "description" | "characteristics" | "related" | "documents" | "reviews" | "questions"
>("description");
const tabsRef = ref<HTMLElement | null>(null);

// Reviews & Questions
const reviews = ref<Review[]>([]);
const questions = ref<ProductQuestion[]>([]);
// Totals from the server: the lists are paginated, the tab badges show all of them.
const reviewsTotal = ref(0);
const questionsTotal = ref(0);
// The API returns 12 per page by default; the average rating needs them all (max 100).
const LIST_PAGE_SIZE = 100;
const similarProducts = ref<Product[]>([]);
const showReviewForm = ref(false);
const showQuestionForm = ref(false);
const reviewForm = ref({ author_name: "", rating: 0, text: "" });
const questionForm = ref({ author_name: "", text: "" });
// New reviews/questions are hidden until a moderator publishes them.
const reviewNotice = ref("");
const questionNotice = ref("");
const reviewError = ref("");
const questionError = ref("");

// Cart quantity for current product
const cartQty = computed(() => {
  if (!product.value) return 0;
  const item = cartStore.items.find((i: any) => i.product.id === product.value!.id);
  return item ? item.quantity : 0;
});

const incrementQty = () => {
  if (!product.value) return;
  cartStore.setQty(product.value.id, cartQty.value + 1);
};

const decrementQty = () => {
  if (!product.value) return;
  if (cartQty.value <= 1) {
    cartStore.remove(product.value.id);
  } else {
    cartStore.setQty(product.value.id, cartQty.value - 1);
  }
};

const toggleCompare = () => {
  if (!product.value) return;
  if (compareStore.isInCompare(product.value.id)) {
    compareStore.remove(product.value.id);
  } else {
    compareStore.add(product.value);
  }
};

const scrollToTabs = () => {
  tabsRef.value?.scrollIntoView({ behavior: "smooth", block: "start" });
};

// Average rating
const avgRating = computed(() => {
  if (!reviews.value.length) return 0;
  const sum = reviews.value.reduce((acc, r) => acc + r.rating, 0);
  return sum / reviews.value.length;
});

const formatDate = (dateStr?: string) => {
  if (!dateStr) return "";
  const d = new Date(dateStr);
  return (
    d.toLocaleDateString("ru-RU", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    }) +
    ", " +
    d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
  );
};

const submitReview = async () => {
  if (
    !product.value ||
    !reviewForm.value.author_name ||
    !reviewForm.value.text ||
    reviewForm.value.rating === 0
  )
    return;
  try {
    reviewError.value = "";
    const res = await reviewsAPI.create(product.value.slug, reviewForm.value);
    if (res.data.is_published) {
      reviews.value.unshift(res.data);
    } else {
      reviewNotice.value = "Спасибо! Отзыв появится после проверки модератором.";
    }
    reviewForm.value = { author_name: "", rating: 0, text: "" };
    showReviewForm.value = false;
  } catch (err) {
    console.error("Failed to submit review:", err);
    reviewError.value = describeSubmitError(err, "Не удалось отправить отзыв. Попробуйте ещё раз.");
  }
};

const submitQuestion = async () => {
  if (!product.value || !questionForm.value.author_name || !questionForm.value.text) return;
  try {
    questionError.value = "";
    const res = await questionsAPI.create(product.value.slug, questionForm.value);
    if (res.data.is_published) {
      questions.value.unshift(res.data);
    } else {
      questionNotice.value = "Спасибо! Вопрос появится после проверки модератором.";
    }
    questionForm.value = { author_name: "", text: "" };
    showQuestionForm.value = false;
  } catch (err) {
    console.error("Failed to submit question:", err);
    questionError.value = describeSubmitError(
      err,
      "Не удалось отправить вопрос. Попробуйте ещё раз.",
    );
  }
};

const loadReviews = async () => {
  if (!product.value) return;
  try {
    const res = await reviewsAPI.listByProduct(product.value.slug, { page_size: LIST_PAGE_SIZE });
    reviews.value = res.data.results || [];
    reviewsTotal.value = Number(res.data.count ?? reviews.value.length);
  } catch (err) {
    console.error("Failed to load reviews:", err);
  }
};

const loadQuestions = async () => {
  if (!product.value) return;
  try {
    const res = await questionsAPI.listByProduct(product.value.slug, { page_size: LIST_PAGE_SIZE });
    questions.value = res.data.results || [];
    questionsTotal.value = Number(res.data.count ?? questions.value.length);
  } catch (err) {
    console.error("Failed to load questions:", err);
  }
};

const loadSimilarProducts = async () => {
  if (!product.value) return;
  try {
    const res = await similarProductsAPI.get(product.value.slug);
    similarProducts.value = res.data;
  } catch (err) {
    console.error("Failed to load similar products:", err);
  }
};

// Truncated description for preview
const truncatedDescription = computed(() => {
  if (!product.value?.description) return "";
  const text = product.value.description;
  return textToHtml(truncateText(text, 100));
});

const copySku = async (sku: string | number | undefined) => {
  if (!sku) return;
  try {
    await navigator.clipboard.writeText(String(sku));
    isCopied.value = true;
    setTimeout(() => {
      isCopied.value = false;
    }, 2000);
  } catch (err) {
    console.error("Copy failed", err);
  }
};

const featureRows = computed(() => (product.value?.feature_groups ?? []).flatMap((g) => g.items));
const price = computed(() => priceView(product.value ?? { price: null }));
const stock = computed(() =>
  stockLabel(product.value ?? { is_available: false, stock_quantity: null }),
);
// "Код товара" like shop.nag.uz: the product number with leading zeros.
const productCode = computed(() => String(product.value?.id ?? "").padStart(6, "0"));

const formatContent = textToHtml; // escapes HTML, keeps line breaks

const closeModal = () => {
  showContactModal.value = false;
};

const loadContactInfo = async () => {
  try {
    const response = await contactAPI.getInfo();
    contactInfo.value = response.data;
  } catch (err) {
    console.error("Failed to load contact info:", err);
  }
};

const loadProduct = async () => {
  const slug = route.params.slug as string;

  if (!slug) {
    error.value = "Товар не найден";
    loading.value = false;
    return;
  }

  try {
    loading.value = true;
    error.value = null;

    const response = await productsAPI.getBySlug(slug);
    product.value = response.data;
  } catch (err: any) {
    if (err.response?.status === 404) {
      error.value = "Товар не найден";
    } else {
      error.value = "Ошибка загрузки товара";
    }
    console.error("Failed to load product:", err);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await Promise.all([loadProduct(), loadContactInfo()]);
  // Load reviews, questions, similar products after product is loaded
  if (product.value) {
    await Promise.all([loadReviews(), loadQuestions(), loadSimilarProducts()]);
  }
});

// When the slug changes (e.g. clicking a similar product card), reset all
// page state, scroll to top, and re-fetch everything for the new product.
watch(
  () => route.params.slug,
  async (newSlug, oldSlug) => {
    if (!newSlug || newSlug === oldSlug) return;

    // Reset content so stale data is never visible during load
    product.value = null;
    reviews.value = [];
    questions.value = [];
    reviewsTotal.value = 0;
    questionsTotal.value = 0;
    similarProducts.value = [];
    error.value = null;
    loading.value = true;
    activeTab.value = "description";

    window.scrollTo({ top: 0, behavior: "smooth" });

    await Promise.all([loadProduct(), loadContactInfo()]);
    if (product.value) {
      await Promise.all([loadReviews(), loadQuestions(), loadSimilarProducts()]);
    }
  },
);

/* --- brand helpers --- */
/* product.brand может быть объектом Brand, строкой или id */
</script>

<style scoped src="@/styles/views/ProductDetailPage.css"></style>
