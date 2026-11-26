<template>
  <section class="bs" aria-label="Игра «Соберите систему»">
    <div ref="stageRef" class="bs-stage" :class="{ 'is-dragging': dragging }">
      <img
        class="bs-scene"
        src="/builder/scene.webp"
        width="1586"
        height="992"
        alt="Схема объекта: двор, вход, торговый зал, касса, служебное помещение с серверным шкафом и парковка"
      />
      <div
        v-for="s in SLOTS"
        :key="s.id"
        class="bs-slot"
        :class="slotClass(s)"
        :style="{ left: `${s.x}%`, top: `${s.y}%` }"
      >
        <template v-if="placement[s.id]">
          <img
            :src="pieceOf(placement[s.id]).img"
            alt=""
            class="bs-placed"
            :class="{ 'is-new': justPlaced === s.id }"
            draggable="false"
          />
          <button
            type="button"
            class="bs-remove"
            :aria-label="`Убрать: ${pieceOf(placement[s.id]).label}, ${s.label}`"
            @click="remove(s.id)"
          >
            <svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
              <path
                d="M2 2l8 8M10 2l-8 8"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </template>
        <span v-else-if="dragging && fits(s)" class="bs-slot-label">{{ s.label }}</span>
      </div>
    </div>

    <div class="bs-side">
      <div class="bs-box">
        <p id="bs-tray-title" class="bs-box-title">Оборудование</p>
        <ul class="bs-tray" aria-labelledby="bs-tray-title">
          <li v-for="p in PIECES" :key="p.id">
            <button
              type="button"
              class="bs-piece"
              :data-piece="p.id"
              :aria-label="`${p.label}: поставить на схему`"
              @pointerdown="onPointerDown($event, p.id)"
              @click="onPieceClick(p.id)"
            >
              <img :src="p.img" alt="" draggable="false" />
              <span>{{ trayLabel(p.label) }}</span>
            </button>
          </li>
        </ul>
      </div>

      <aside class="bs-panel" aria-labelledby="bs-title">
        <h2 id="bs-title" class="bs-panel-title">Ваша система</h2>
        <p v-if="!rows.length" class="bs-empty">
          Пока пусто. Перетащите оборудование на схему или просто нажмите на него.
        </p>
        <ul v-else class="bs-list">
          <li v-for="r in rows" :key="r.id">
            <span class="bs-list-name">{{ r.label }}</span>
            <span class="bs-list-count">× {{ r.count }}</span>
            <router-link
              :to="{ path: '/catalog', query: { search: pieceOf(r.id).search } }"
              class="bs-list-link"
            >
              в каталоге
            </router-link>
          </li>
        </ul>
        <ul v-if="tips.length" class="bs-hints">
          <li v-for="t in tips" :key="t">{{ t }}</li>
        </ul>
        <div class="bs-actions">
          <button
            type="button"
            class="btn btn-primary bs-send"
            :disabled="!rows.length"
            @click="send"
          >
            Отправить на расчёт
          </button>
          <button v-if="rows.length" type="button" class="btn btn-ghost bs-reset" @click="reset">
            Очистить
          </button>
        </div>
        <p class="sr-only" aria-live="polite">{{ status }}</p>
      </aside>
    </div>

    <img
      v-if="drag && dragging"
      class="bs-ghost"
      :src="pieceOf(drag.pieceId).img"
      alt=""
      :style="{ transform: `translate(${drag.x}px, ${drag.y}px)` }"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref } from "vue";
import { useRouter } from "vue-router";
import {
  PIECES,
  SLOTS,
  firstFreeSlot,
  hints,
  place,
  removeAt,
  requestText,
  summary,
  type PieceId,
  type Placement,
  type Slot,
} from "./model";

const router = useRouter();

const placement = ref<Placement>({});
const stageRef = ref<HTMLElement>();
const justPlaced = ref<string | null>(null);
const status = ref("");

const pieceMap = new Map(PIECES.map((p) => [p.id, p]));
const pieceOf = (id: PieceId) => pieceMap.get(id)!;
const slotMap = new Map(SLOTS.map((s) => [s.id, s]));

const rows = computed(() => summary(placement.value));

// Tray cells are ~70 px wide: let the one long word break where a reader expects it.
const trayLabel = (label: string) => label.replace("Видеорегистратор", "Видео\u00ADрегистратор");
const tips = computed(() => hints(placement.value));

// ── Dragging (Pointer Events: mouse, pen and finger alike) ─────────────────
interface Drag {
  pieceId: PieceId;
  pointerId: number;
  startX: number;
  startY: number;
  x: number;
  y: number;
  moved: boolean;
  target: string | null;
}

const GHOST = 76; // px, size of the piece that follows the pointer
const START = 6; // px of movement before a press becomes a drag

const drag = ref<Drag | null>(null);
const dragging = computed(() => !!drag.value?.moved);
let suppressClick = false;

function fits(s: Slot): boolean {
  return !!drag.value && !placement.value[s.id] && s.accepts.includes(drag.value.pieceId);
}

function slotClass(s: Slot) {
  return {
    "is-filled": !!placement.value[s.id],
    "is-target": dragging.value && fits(s),
    "is-over": dragging.value && drag.value?.target === s.id,
  };
}

/** Nearest free slot that takes the dragged piece, if the pointer is close enough to it. */
function slotUnder(clientX: number, clientY: number): string | null {
  const stage = stageRef.value;
  if (!stage || !drag.value) return null;
  const r = stage.getBoundingClientRect();
  if (clientX < r.left || clientX > r.right || clientY < r.top || clientY > r.bottom) return null;
  const reach = Math.max(44, r.width * 0.09);
  let best: string | null = null;
  let bestDist = Infinity;
  for (const s of SLOTS) {
    if (!fits(s)) continue;
    const d = Math.hypot(
      r.left + (r.width * s.x) / 100 - clientX,
      r.top + (r.height * s.y) / 100 - clientY,
    );
    if (d < bestDist) {
      bestDist = d;
      best = s.id;
    }
  }
  return bestDist <= reach ? best : null;
}

function onPointerDown(e: PointerEvent, pieceId: PieceId) {
  if (e.button !== 0 || drag.value) return;
  suppressClick = false;
  const el = e.currentTarget as HTMLElement;
  el.setPointerCapture(e.pointerId);
  drag.value = {
    pieceId,
    pointerId: e.pointerId,
    startX: e.clientX,
    startY: e.clientY,
    x: e.clientX - GHOST / 2,
    y: e.clientY - GHOST / 2,
    moved: false,
    target: null,
  };

  const move = (ev: PointerEvent) => {
    const d = drag.value;
    if (!d || ev.pointerId !== d.pointerId) return;
    if (!d.moved && Math.hypot(ev.clientX - d.startX, ev.clientY - d.startY) < START) return;
    d.moved = true;
    d.x = ev.clientX - GHOST / 2;
    d.y = ev.clientY - GHOST / 2;
    d.target = slotUnder(ev.clientX, ev.clientY);
  };

  const end = (ev: PointerEvent) => {
    const d = drag.value;
    if (!d || ev.pointerId !== d.pointerId) return;
    el.removeEventListener("pointermove", move);
    el.removeEventListener("pointerup", end);
    el.removeEventListener("pointercancel", end);
    el.removeEventListener("lostpointercapture", end);
    drag.value = null;
    if (!d.moved) return; // a plain press: the click handler places the piece
    if (ev.type === "pointerup") {
      suppressClick = true; // the browser fires a click right after this pointerup
      const target = slotUnder(ev.clientX, ev.clientY) ?? d.target;
      if (target) commit(target, d.pieceId);
      else
        status.value = `${pieceOf(d.pieceId).label}: сюда не подходит, попробуйте подсвеченное место.`;
    }
  };

  el.addEventListener("pointermove", move);
  el.addEventListener("pointerup", end);
  el.addEventListener("pointercancel", end);
  // capture can be lost without pointerup/cancel (element hidden, window switch) — never stay stuck mid-drag
  el.addEventListener("lostpointercapture", end);
}

function onPieceClick(pieceId: PieceId) {
  if (suppressClick) {
    suppressClick = false;
    return;
  }
  const slot = firstFreeSlot(placement.value, pieceId);
  if (slot) commit(slot, pieceId);
  else status.value = `${pieceOf(pieceId).label}: свободных мест для неё на схеме больше нет.`;
}

let newTimer = 0;
onBeforeUnmount(() => window.clearTimeout(newTimer));
function commit(slotId: string, pieceId: PieceId) {
  const next = place(placement.value, slotId, pieceId);
  if (next === placement.value) return;
  placement.value = next;
  justPlaced.value = slotId;
  window.clearTimeout(newTimer);
  newTimer = window.setTimeout(() => (justPlaced.value = null), 400);
  status.value = `${pieceOf(pieceId).label} — ${slotMap.get(slotId)!.label}. ${totalText()}`;
}

async function remove(slotId: string) {
  const pieceId = placement.value[slotId];
  if (!pieceId) return;
  placement.value = removeAt(placement.value, slotId);
  status.value = `Убрано: ${pieceOf(pieceId).label}. ${totalText()}`;
  // the button that had focus is gone — return focus to the same piece in the tray
  await nextTick();
  document.querySelector<HTMLElement>(`.bs-piece[data-piece="${pieceId}"]`)?.focus();
}

function reset() {
  placement.value = {};
  status.value = "Схема очищена.";
}

function totalText(): string {
  const n = Object.keys(placement.value).length;
  return n ? `На схеме устройств: ${n}.` : "Схема пуста.";
}

function send() {
  const message = requestText(placement.value);
  if (!message) return;
  router.push({ path: "/contact", state: { message } });
}
</script>

<style scoped src="@/styles/components/BuildSystem.css"></style>
