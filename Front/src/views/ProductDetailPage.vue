<template>
  <div class="product-detail-page">
    <div class="container">
      <!-- Breadcrumb -->
      <nav class="breadcrumb" v-if="product">
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
        <span v-if="product.category" class="breadcrumb-separator">›</span>
        <router-link
          v-if="product.category"
          :to="`/catalog/${(product.category as any)?.slug}`"
          class="breadcrumb-item"
        >
          {{ (product.category as any)?.name }}
        </router-link>
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
        <router-link to="/catalog" class="btn btn-primary">
          Вернуться в каталог
        </router-link>
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
            <div
              v-if="product.manufacturer_sku || product.internal_sku"
              class="pd-meta-item"
            >
              <span class="pd-meta-label">Артикул</span>
              <span class="pd-meta-value pd-sku-value">
                <code>{{
                  product.manufacturer_sku || product.internal_sku
                }}</code>
                <button
                  @click="
                    copySku(product.manufacturer_sku || product.internal_sku)
                  "
                  class="pd-copy-btn"
                  :class="{ copied: isCopied }"
                  title="Копировать"
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
                    <path
                      d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"
                    />
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
          <div v-if="groupedFeatures.length > 0" class="pd-features-preview">
            <h3 class="pd-section-title">Характеристики</h3>
            <div class="pd-features-list">
              <div
                v-for="(feature, i) in groupedFeatures.slice(0, 2)"
                :key="i"
                class="pd-feat-row"
              >
                <span class="pd-feat-name">{{ feature.feature_name }}</span>
                <span class="pd-feat-dots"></span>
                <span class="pd-feat-val">{{ feature.values.join(", ") }}</span>
              </div>
            </div>
            <button
              v-if="groupedFeatures.length > 2"
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
            <div v-if="product.price" class="pd-price-block">
              <span class="pd-price-hint">Цена:</span>
              <div class="pd-price-amount">
                {{ formatPrice(product.price) }}
              </div>
            </div>
            <div v-else class="pd-price-block">
              <span class="pd-price-request">Цена по запросу</span>
            </div>

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
                    <path
                      d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                    />
                  </svg>
                  Перейти в корзину
                </router-link>
              </template>
              <button
                v-else
                class="pd-add-cart-btn"
                :disabled="!product.is_available"
                @click="cartStore.add(product, 1)"
              >
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
                  <path
                    d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"
                  />
                </svg>
                В корзину
              </button>
            </div>

            <!-- Quick actions -->
            <div class="pd-quick-actions">
              <button
                class="pd-action-btn"
                :class="{ active: favStore.isFavorite(product.id) }"
                @click="favStore.toggle(product)"
                :title="
                  favStore.isFavorite(product.id)
                    ? 'Убрать из избранного'
                    : 'В избранное'
                "
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  :fill="
                    favStore.isFavorite(product.id) ? 'currentColor' : 'none'
                  "
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
                  disabled:
                    compareStore.isFull &&
                    !compareStore.isInCompare(product.id),
                }"
                @click="toggleCompare"
                title="Сравнить"
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
              <div
                class="pd-info-item"
                :class="product.is_available ? 'available' : 'unavailable'"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    v-if="product.is_available"
                    d="M22 11.08V12a10 10 0 1 1-5.93-9.14"
                  />
                  <polyline
                    v-if="product.is_available"
                    points="22 4 12 14.01 9 11.01"
                  />
                  <circle v-if="!product.is_available" cx="12" cy="12" r="10" />
                  <line
                    v-if="!product.is_available"
                    x1="15"
                    y1="9"
                    x2="9"
                    y2="15"
                  />
                  <line
                    v-if="!product.is_available"
                    x1="9"
                    y1="9"
                    x2="15"
                    y2="15"
                  />
                </svg>
                <span>{{
                  product.is_available ? "В наличии" : "Нет в наличии"
                }}</span>
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
            class="tab-button"
            :class="{ active: activeTab === 'reviews' }"
            @click="activeTab = 'reviews'"
          >
            Отзывы
            <span v-if="reviews.length" class="tab-badge">{{
              reviews.length
            }}</span>
          </button>
          <button
            class="tab-button"
            :class="{ active: activeTab === 'questions' }"
            @click="activeTab = 'questions'"
          >
            Вопросы
            <span v-if="questions.length" class="tab-badge">{{
              questions.length
            }}</span>
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
            <div
              v-if="groupedFeatures.length > 0"
              class="characteristics-table"
            >
              <table>
                <tbody>
                  <tr
                    v-for="(feature, index) in groupedFeatures"
                    :key="index"
                    class="characteristic-row"
                  >
                    <td class="characteristic-name">
                      {{ feature.feature_name }}
                    </td>
                    <td class="characteristic-value">
                      <span
                        v-for="(value, vIndex) in feature.values"
                        :key="vIndex"
                        class="value-item"
                      >
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
                @click="showReviewForm = !showReviewForm"
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
                    @click="reviewForm.rating = s"
                    class="rw-star-btn"
                    :class="{ active: s <= reviewForm.rating }"
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
                  @click="submitReview"
                  :disabled="
                    !reviewForm.author_name ||
                    !reviewForm.text ||
                    reviewForm.rating === 0
                  "
                >
                  Отправить
                </button>
                <button class="rw-cancel-btn" @click="showReviewForm = false">
                  Отмена
                </button>
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
                    <span class="rw-reply-date">{{
                      formatDate(review.admin_reply_date)
                    }}</span>
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
                @click="showQuestionForm = !showQuestionForm"
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
                  @click="submitQuestion"
                  :disabled="!questionForm.author_name || !questionForm.text"
                >
                  Отправить
                </button>
                <button class="rw-cancel-btn" @click="showQuestionForm = false">
                  Отмена
                </button>
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
                    <span class="rw-reply-date">{{
                      formatDate(q.admin_reply_date)
                    }}</span>
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
            <button @click="closeModal" class="modal-close">
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
                  <a
                    :href="`mailto:${contactInfo.email}`"
                    class="contact-value"
                    >{{ contactInfo.email }}</a
                  >
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
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";
import {
  productsAPI,
  contactAPI,
  reviewsAPI,
  questionsAPI,
  similarProductsAPI,
} from "@/api";
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
  "description" | "characteristics" | "reviews" | "questions"
>("description");
const tabsRef = ref<HTMLElement | null>(null);

// Reviews & Questions
const reviews = ref<Review[]>([]);
const questions = ref<ProductQuestion[]>([]);
const similarProducts = ref<Product[]>([]);
const showReviewForm = ref(false);
const showQuestionForm = ref(false);
const reviewForm = ref({ author_name: "", rating: 0, text: "" });
const questionForm = ref({ author_name: "", text: "" });
// New reviews/questions are hidden until a moderator publishes them.
const reviewNotice = ref("");
const questionNotice = ref("");

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
  }
};

const submitQuestion = async () => {
  if (
    !product.value ||
    !questionForm.value.author_name ||
    !questionForm.value.text
  )
    return;
  try {
    const res = await questionsAPI.create(
      product.value.slug,
      questionForm.value,
    );
    if (res.data.is_published) {
      questions.value.unshift(res.data);
    } else {
      questionNotice.value = "Спасибо! Вопрос появится после проверки модератором.";
    }
    questionForm.value = { author_name: "", text: "" };
    showQuestionForm.value = false;
  } catch (err) {
    console.error("Failed to submit question:", err);
  }
};

const loadReviews = async () => {
  if (!product.value) return;
  try {
    const res = await reviewsAPI.listByProduct(product.value.slug);
    reviews.value = res.data.results || [];
  } catch (err) {
    console.error("Failed to load reviews:", err);
  }
};

const loadQuestions = async () => {
  if (!product.value) return;
  try {
    const res = await questionsAPI.listByProduct(product.value.slug);
    questions.value = res.data.results || [];
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
  if (text.length <= 100) return formatContent(text);
  return formatContent(text.substring(0, 100) + "...");
});

// Группировка характеристик по feature_name
const groupedFeatures = computed(() => {
  if (!product.value?.features || product.value.features.length === 0) {
    return [];
  }

  const featuresMap = new Map<string, string[]>();

  product.value.features.forEach((feature) => {
    const featureName = feature.feature_name;
    const valueName = feature.value_name;

    if (!featureName || !valueName) return;

    if (!featuresMap.has(featureName)) {
      featuresMap.set(featureName, []);
    }

    const values = featuresMap.get(featureName)!;
    if (!values.includes(valueName)) {
      values.push(valueName);
    }
  });

  return Array.from(featuresMap.entries()).map(([feature_name, values]) => ({
    feature_name,
    values,
  }));
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

const formatPrice = (price: number) => {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "UZS",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

const formatContent = (content: string) => {
  if (!content) return "";
  return content.replace(/\n/g, "<br>");
};

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
    similarProducts.value = [];
    error.value = null;
    loading.value = true;
    activeTab.value = "description";

    window.scrollTo({ top: 0, behavior: "smooth" });

    await Promise.all([loadProduct(), loadContactInfo()]);
    if (product.value) {
      await Promise.all([loadReviews(), loadQuestions(), loadSimilarProducts()]);
    }
  }
);

/* --- brand helpers --- */
/* product.brand может быть объектом Brand, строкой или id */
</script>

<style scoped>
/* ==================== 3-ZONE PRODUCT LAYOUT ==================== */
.pd-grid {
  display: grid;
  grid-template-columns: 1fr 1.1fr 320px;
  gap: 32px;
  align-items: start;
}

/* Zone 1: Gallery */
.pd-gallery {
  position: sticky;
  top: 24px;
}

/* Zone 2: Product Info */
.pd-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.pd-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--gray-900);
  line-height: 1.3;
  margin: 0;
  letter-spacing: -0.01em;
}

/* Meta table */
.pd-meta {
  display: flex;
  flex-direction: column;
  gap: 0;
  border: 1px solid var(--gray-100);
  border-radius: 10px;
  overflow: hidden;
}

.pd-meta-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 16px;
  border-bottom: 1px solid var(--gray-100);
  font-size: 14px;
}

.pd-meta-item:last-child {
  border-bottom: none;
}

.pd-meta-label {
  color: var(--gray-500);
  font-weight: 500;
  flex-shrink: 0;
}

.pd-meta-value {
  color: var(--gray-800);
  font-weight: 600;
  text-align: right;
}

.pd-meta-link {
  color: var(--primary);
  text-decoration: none;
  transition: color 0.2s;
}

.pd-meta-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.pd-sku-value {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.pd-sku-value code {
  font-family: "SF Mono", Monaco, monospace;
  background: var(--gray-100);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-800);
}

.pd-copy-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: 1px solid var(--gray-200);
  border-radius: 6px;
  cursor: pointer;
  color: var(--gray-400);
  transition: all 0.2s;
  min-height: auto;
}

.pd-copy-btn:hover {
  background: var(--primary-light);
  color: var(--primary);
  border-color: var(--primary);
}

.pd-copy-btn.copied {
  color: var(--success);
  border-color: var(--success);
}

/* Features preview */
.pd-section-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-800);
  margin: 0 0 12px;
}

.pd-features-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.pd-feat-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 7px 0;
  font-size: 14px;
  border-bottom: 1px solid var(--gray-50);
}

.pd-feat-row:last-child {
  border-bottom: none;
}

.pd-feat-name {
  color: var(--gray-500);
  flex-shrink: 0;
  white-space: nowrap;
}

.pd-feat-dots {
  flex: 1;
  border-bottom: 1px dotted var(--gray-300);
  min-width: 20px;
  align-self: center;
  margin-bottom: 3px;
}

.pd-feat-val {
  color: var(--gray-800);
  font-weight: 600;
  text-align: right;
  flex-shrink: 0;
  max-width: 50%;
}

.pd-all-chars-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 10px;
  padding: 0;
  background: none;
  border: none;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
  cursor: pointer;
  transition: color 0.2s;
  min-height: auto;
}

.pd-all-chars-link:hover {
  color: var(--primary-hover);
}

/* Description preview */
.pd-desc-preview {
  padding-top: 4px;
}

.pd-desc-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--gray-600);
}

/* Zone 3: Price sidebar */
.pd-sidebar {
  position: sticky;
  top: 24px;
}

.pd-price-card {
  background: var(--white);
  border: 1px solid var(--gray-100);
  border-radius: 14px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.pd-price-block {
  text-align: left;
}

.pd-price-hint {
  display: block;
  font-size: 13px;
  color: var(--gray-500);
  font-weight: 500;
  margin-bottom: 4px;
}

.pd-price-amount {
  font-size: 1.75rem;
  font-weight: 800;
  color: var(--gray-900);
  line-height: 1.2;
}

.pd-price-request {
  font-size: 16px;
  color: var(--gray-600);
  font-weight: 600;
}

/* Cart actions */
.pd-cart-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.pd-add-cart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: var(--primary);
  color: var(--white);
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  min-height: 52px;
}

.pd-add-cart-btn:hover:not(:disabled) {
  background: var(--primary-hover);
  box-shadow: 0 4px 16px rgba(27, 67, 50, 0.25);
}

.pd-add-cart-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pd-qty-control {
  display: flex;
  align-items: center;
  border: 2px solid var(--primary);
  border-radius: 10px;
  overflow: hidden;
}

.pd-qty-btn {
  width: 48px;
  height: 48px;
  background: transparent;
  border: none;
  font-size: 20px;
  font-weight: 600;
  color: var(--primary);
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  min-height: auto;
}

.pd-qty-btn:hover {
  background: var(--primary-light);
}

.pd-qty-value {
  flex: 1;
  text-align: center;
  font-size: 17px;
  font-weight: 700;
  color: var(--gray-900);
  min-width: 40px;
}

.pd-go-cart-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid var(--primary);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  min-height: 44px;
}

.pd-go-cart-btn:hover {
  background: var(--primary);
  color: var(--white);
}

/* Quick actions */
.pd-quick-actions {
  display: flex;
  gap: 8px;
  justify-content: center;
  padding-top: 4px;
  border-top: 1px solid var(--gray-100);
}

.pd-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  padding: 0;
  background: var(--gray-50);
  border: 1px solid var(--gray-200);
  border-radius: 10px;
  cursor: pointer;
  color: var(--gray-400);
  transition: all 0.2s;
  min-height: auto;
}

.pd-action-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: var(--primary-light);
}

.pd-action-btn.active {
  background: var(--primary-light);
  border-color: var(--primary);
  color: var(--primary);
}

.pd-action-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Info items */
.pd-info-items {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.pd-info-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid var(--gray-50);
  font-size: 13px;
  color: var(--gray-600);
}

.pd-info-item:last-child {
  border-bottom: none;
}

.pd-info-item.available svg {
  color: var(--success);
}

.pd-info-item.unavailable svg {
  color: var(--error);
}

.pd-info-item.available span {
  color: var(--success);
  font-weight: 600;
}

.pd-info-item.unavailable span {
  color: var(--error);
  font-weight: 600;
}

/* ==================== TABS LAYOUT ==================== */
.product-tabs-layout {
  margin-top: 40px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.tabs-navigation {
  display: flex;
  gap: 0;
  background: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
}

.tab-button {
  flex: 1;
  padding: 16px 24px;
  background: transparent;
  border: none;
  font-size: 15px;
  font-weight: 500;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tab-button:hover {
  background: rgba(52, 58, 64, 0.05);
  color: #343a40;
}

.tab-button.active {
  color: var(--primary);
  background: #ffffff;
  border-bottom-color: var(--primary);
  font-weight: 600;
}

.tabs-content {
  padding: 28px;
  min-height: 200px;
}

.tab-panel {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 48px 20px;
  color: #adb5bd;
}

.empty-state p {
  margin: 0;
  font-size: 15px;
}

/* Description Content */
.description-content {
  font-size: 15px;
  line-height: 1.8;
  color: var(--gray-700);
}

/* ==================== CHARACTERISTICS TABLE ==================== */
.characteristics-table {
  width: 100%;
  overflow-x: auto;
}

.characteristics-table table {
  width: 100%;
  border-collapse: collapse;
}

.characteristic-row {
  border-bottom: 1px solid #e9ecef;
  transition: background-color 0.15s ease;
}

.characteristic-row:hover {
  background: #f8f9fa;
}

.characteristic-row:last-child {
  border-bottom: none;
}

.characteristic-name {
  padding: 14px 16px;
  font-weight: 600;
  color: #343a40;
  font-size: 14px;
  width: 35%;
  background: #fafbfc;
}

.characteristic-value {
  padding: 14px 16px;
  color: var(--gray-700);
  font-size: 14px;
  line-height: 1.7;
}

.value-item {
  display: block;
}

/* ==================== RESPONSIVE ==================== */

/* Tablet: 2 columns (gallery+info | sidebar) */
@media (max-width: 1100px) {
  .pd-grid {
    grid-template-columns: 1fr 280px;
    gap: 24px;
  }

  .pd-gallery {
    grid-column: 1;
    position: static;
  }

  .pd-info {
    grid-column: 1;
  }

  .pd-sidebar {
    grid-column: 2;
    grid-row: 1 / 3;
  }

  .pd-title {
    font-size: 1.35rem;
  }
}

/* Mobile: single column */
@media (max-width: 768px) {
  .pd-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .pd-gallery {
    position: static;
  }

  .pd-sidebar {
    grid-column: 1;
    grid-row: auto;
    position: static;
  }

  .pd-title {
    font-size: 1.2rem;
  }

  .pd-meta-item {
    padding: 8px 12px;
    font-size: 13px;
  }

  .pd-feat-row {
    font-size: 13px;
  }

  .pd-price-card {
    padding: 16px;
    gap: 14px;
    border-radius: 12px;
  }

  .pd-price-amount {
    font-size: 1.4rem;
  }

  .pd-add-cart-btn {
    padding: 12px;
    font-size: 14px;
    min-height: 48px;
  }

  .pd-qty-btn {
    width: 42px;
    height: 42px;
  }

  .pd-action-btn {
    width: 40px;
    height: 40px;
  }

  .pd-section-title {
    font-size: 14px;
  }

  .pd-desc-text {
    font-size: 13px;
  }

  .pd-info-item {
    font-size: 12px;
    padding: 8px 0;
  }

  /* Tabs */
  .product-tabs-layout {
    margin-top: 20px;
    border-radius: 0;
    box-shadow: none;
    border-top: 1px solid #e9ecef;
  }

  .tab-button {
    padding: 12px 8px;
    font-size: 13px;
  }

  .tabs-content {
    padding: 16px;
    min-height: 100px;
  }

  .description-content {
    font-size: 14px;
  }

  .characteristic-name {
    padding: 10px 12px;
    font-size: 13px;
    width: 40%;
  }

  .characteristic-value {
    padding: 10px 12px;
    font-size: 13px;
  }

  .empty-state {
    padding: 30px 16px;
  }

  .empty-state p {
    font-size: 14px;
  }
}

@media (max-width: 390px) {
  .pd-title {
    font-size: 1.1rem;
  }

  .pd-price-amount {
    font-size: 1.25rem;
  }

  .pd-meta-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
}

/* ==================== TAB BADGE ==================== */
.tab-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  background: var(--primary);
  color: #fff;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  margin-left: 6px;
  line-height: 1;
}

/* ==================== REVIEWS & QUESTIONS ==================== */
.reviews-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.avg-rating {
  display: flex;
  align-items: center;
  gap: 10px;
}

.avg-stars {
  display: flex;
  gap: 2px;
}

.avg-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--gray-900);
}

.rw-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  min-height: auto;
}

.rw-add-btn:hover {
  background: var(--primary-hover);
}

/* Review/Question Form */
.rw-form {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.rw-form-title {
  font-size: 16px;
  font-weight: 700;
  color: var(--gray-800);
  margin: 0 0 16px;
}

.rw-form-field {
  margin-bottom: 14px;
}

.rw-form-field label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--gray-600);
  margin-bottom: 6px;
}

.rw-form-field input,
.rw-form-field textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 14px;
  color: var(--gray-800);
  background: #fff;
  transition: border-color 0.2s;
  box-sizing: border-box;
  font-family: inherit;
}

.rw-form-field input:focus,
.rw-form-field textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(27, 67, 50, 0.1);
}

.rw-star-select {
  display: flex;
  gap: 4px;
}

.rw-star-btn {
  background: none;
  border: none;
  padding: 2px;
  cursor: pointer;
  transition: transform 0.15s;
  min-height: auto;
}

.rw-star-btn:hover {
  transform: scale(1.15);
}

.rw-form-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
}

.rw-submit-btn {
  padding: 10px 24px;
  background: var(--primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
  min-height: auto;
}

.rw-submit-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.rw-submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.rw-cancel-btn {
  padding: 10px 24px;
  background: transparent;
  color: var(--gray-600);
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  min-height: auto;
}

.rw-cancel-btn:hover {
  background: #f8f9fa;
  border-color: var(--gray-400);
}

/* Reviews/Questions List */
.rw-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.rw-item {
  padding: 20px 0;
  border-bottom: 1px solid #e9ecef;
}

.rw-item:last-child {
  border-bottom: none;
}

.rw-item-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.rw-author {
  font-size: 15px;
  font-weight: 700;
  color: var(--gray-800);
}

.rw-stars {
  display: flex;
  gap: 1px;
}

.rw-date {
  font-size: 13px;
  color: var(--gray-400);
  margin-left: auto;
}

.rw-text {
  font-size: 14px;
  line-height: 1.7;
  color: var(--gray-700);
}

/* Admin reply */
.rw-reply {
  margin-top: 14px;
  margin-left: 24px;
  padding: 14px 18px;
  background: #f0fdf4;
  border-left: 3px solid var(--primary);
  border-radius: 0 8px 8px 0;
}

.rw-reply-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.rw-reply-author {
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
}

.rw-reply-date {
  font-size: 12px;
  color: var(--gray-400);
}

.rw-reply-text {
  font-size: 14px;
  line-height: 1.6;
  color: var(--gray-700);
}

/* ==================== SIMILAR PRODUCTS ==================== */
.similar-section {
  margin-top: 48px;
  padding-bottom: 40px;
}

.similar-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--gray-900);
  margin: 0 0 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--primary);
  display: inline-block;
}

.similar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

/* ==================== RESPONSIVE ADDITIONS ==================== */
@media (max-width: 768px) {
  .reviews-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .rw-date {
    margin-left: 0;
  }

  .rw-reply {
    margin-left: 12px;
    padding: 10px 14px;
  }

  .rw-form {
    padding: 16px;
  }

  .similar-section {
    margin-top: 28px;
    padding-bottom: 20px;
  }

  .similar-title {
    font-size: 1.15rem;
  }

  .similar-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }

  .tab-badge {
    min-width: 18px;
    height: 18px;
    font-size: 10px;
    padding: 0 5px;
  }
}


.rw-notice {
  margin: 12px 0;
  padding: 10px 14px;
  border-radius: 8px;
  background: rgba(34, 197, 94, 0.12);
  color: inherit;
  font-size: 14px;
}
</style>
