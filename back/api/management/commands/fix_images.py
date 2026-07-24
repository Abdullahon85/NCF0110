"""
Management command: fix_images
Downloads Unsplash images for categories and products that are missing them.
Use --force to replace ALL existing images.
"""

import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile

from api.models import Category, Product, Image


def fetch(url, name, timeout=20):
    try:
        r = requests.get(
            url, timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (compatible; SecurityShop/1.0)'},
        )
        if r.status_code == 200 and len(r.content) > 5000:
            return ContentFile(r.content, name=name)
    except Exception as e:
        print(f"    ⚠  {url}: {e}")
    return None


def unsplash(photo_id, w=900):
    return f"https://images.unsplash.com/{photo_id}?w={w}&fit=crop"


# ── Relevant Unsplash photo IDs ───────────────────────────────────
# Security / CCTV cameras
_CAM_DOME   = unsplash('photo-1558618666-fcd25c85cd64')   # dome security cam
_CAM_BULLET = unsplash('photo-1582139329536-e7284fece509') # bullet CCTV cam
_CAM_STREET = unsplash('photo-1601597111158-2fceff292cdc') # outdoor cam on wall
_CAM_MULTI  = unsplash('photo-1555664424-778a1e5e1b48')   # surveillance room

# NVR / DVR / server rack
_NVR_RACK   = unsplash('photo-1558494949-ef010cbdcc31')   # server rack
_NVR_SERVER = unsplash('photo-1548092372-0d1bd40894a3')   # server room

# Network equipment
_NET_CABLES = unsplash('photo-1563206767-5b18f218e8de')   # network cables
_NET_SWITCH = unsplash('photo-1544197150-b99a580bb7a8')   # ethernet/switch

# Access control
_ACC_PANEL  = unsplash('photo-1614064641938-3bbee52942c7') # door access panel
_ACC_TECH   = unsplash('photo-1518770660439-4636190af475') # biometric/tech board


# ── Category images ───────────────────────────────────────────────
CATEGORY_IMAGES = {
    'ip-kamery':           (_CAM_DOME,   'cat_ip_cameras.jpg'),
    'videoregistratory':   (_NVR_RACK,   'cat_nvr.jpg'),
    'setevoe-oborudovanie':(_NET_CABLES, 'cat_network.jpg'),
    'kontrol-dostupa':     (_ACC_PANEL,  'cat_access.jpg'),
}

# ── Per-product images ────────────────────────────────────────────
PRODUCT_IMAGES = {
    # IP cameras
    'dahua-ipc-hdw2831t-as':                (_CAM_DOME,   'dahua_hdw2831.jpg'),
    'dahua-ipc-hfw2849s-s-il':              (_CAM_BULLET, 'dahua_hfw2849.jpg'),
    'uniview-ipc3614sb-adf28km-i0':         (_CAM_STREET, 'uniview_ipc3614.jpg'),
    'uniview-ipc2228se-df40k-wl-i0':        (_CAM_BULLET, 'uniview_ipc2228.jpg'),
    'dahua-ipc-hfw3849h-as-pv':             (_CAM_STREET, 'dahua_hfw3849.jpg'),
    'uniview-ipc868-adu-wl':                (_CAM_DOME,   'uniview_ipc868.jpg'),
    # NVR / DVR
    'dahua-dhi-nvr4108hs-8p-4ks2l':        (_NVR_RACK,   'dahua_nvr4108.jpg'),
    'dahua-dhi-nvr5216-16p-ei':             (_NVR_RACK,   'dahua_nvr5216.jpg'),
    'uniview-nvr302-16s':                   (_NVR_SERVER, 'uniview_nvr302.jpg'),
    'dahua-dhi-xvr5116he-i3':              (_NVR_RACK,   'dahua_xvr5116.jpg'),
    'dahua-dhi-nvr2104hs-p-s3':            (_NVR_SERVER, 'dahua_nvr2104.jpg'),
    # Network
    'tp-link-tl-sg1024de':                  (_NET_SWITCH, 'tplink_sg1024.jpg'),
    'tp-link-tl-sg2210p-v36':               (_NET_CABLES, 'tplink_sg2210.jpg'),
    'mikrotik-rb2011uias-2hnd-in':          (_NET_SWITCH, 'mikrotik_rb2011.jpg'),
    'mikrotik-crs326-24g-2srm':             (_NET_CABLES, 'mikrotik_crs326.jpg'),
    'tp-link-tl-sg3452p':                   (_NET_SWITCH, 'tplink_sg3452.jpg'),
    'mikrotik-hap-ax3-c53uig5hpaxd2hpaxd': (_NET_CABLES, 'mikrotik_hap_ax3.jpg'),
    'tp-link-tl-sf1016p':                   (_NET_SWITCH, 'tplink_sf1016.jpg'),
    'd-link-dgs-1210-10p':                  (_NET_CABLES, 'dlink_dgs1210.jpg'),
    'ubiquiti-unifi-uap-ac-pro':            (_NET_SWITCH, 'ubiquiti_uap_ac_pro.jpg'),
    # Access control
    'dahua-dhi-asi7223x-t1':               (_ACC_PANEL,  'dahua_asi7223.jpg'),
    'dahua-dhi-asm100':                    (_ACC_TECH,   'dahua_asm100.jpg'),
}

BAD_EXTENSIONS = ('.pdf', '.doc', '.docx', '.txt')


class Command(BaseCommand):
    help = 'Download missing product/category images from Unsplash.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Replace ALL existing images, not just missing ones.',
        )

    def handle(self, *args, **options):
        force = options['force']
        self._fix_categories(force)
        self._fix_products(force)
        self.stdout.write(self.style.SUCCESS('\n✅  Done.'))

    # ── Categories ────────────────────────────────────────────────
    def _fix_categories(self, force):
        self.stdout.write('\n📁  Categories:')
        for cat in Category.objects.all():
            entry = CATEGORY_IMAGES.get(cat.slug)
            if not entry:
                self.stdout.write(f'  [skip] {cat.name} — no URL configured')
                continue
            if cat.image and not force:
                self.stdout.write(f'  [skip] {cat.name} — already has image')
                continue
            url, fname = entry
            if cat.image:
                cat.image.delete(save=False)
            cf = fetch(url, fname)
            if cf:
                cat.image.save(fname, cf, save=True)
                self.stdout.write(f'  ✓ {cat.name}')
            else:
                self.stdout.write(f'  ✗ {cat.name} — download failed')

    # ── Products ──────────────────────────────────────────────────
    def _fix_products(self, force):
        self.stdout.write('\n📦  Products:')
        for product in Product.objects.prefetch_related('images').all():
            imgs = list(product.images.all())

            has_bad = any(
                not img.image or str(img.image).lower().endswith(BAD_EXTENSIONS)
                for img in imgs
            )
            has_real = any(
                img.image and not str(img.image).lower().endswith(BAD_EXTENSIONS)
                for img in imgs
            )

            need_fix = has_bad or not has_real or force

            if not need_fix:
                self.stdout.write(f'  [skip] {product.name}')
                continue

            entry = PRODUCT_IMAGES.get(product.slug)
            if not entry:
                self.stdout.write(f'  [no url] {product.name}')
                continue

            url, fname = entry
            cf = fetch(url, fname)
            if not cf:
                self.stdout.write(f'  ✗ {product.name} — download failed')
                continue

            if force:
                product.images.all().delete()
            else:
                # Remove only bad/empty records
                for img in imgs:
                    if not img.image or str(img.image).lower().endswith(BAD_EXTENSIONS):
                        img.delete()

            img_obj = Image(product=product, is_main=True, order=0)
            img_obj.image.save(fname, cf, save=True)
            self.stdout.write(f'  ✓ {product.name}')
