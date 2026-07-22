//router/index.ts
import { createRouter, createWebHistory } from "vue-router";
import type { RouteRecordRaw } from "vue-router";

// Only HomePage is loaded eagerly for fast initial load
import HomePage from "../views/HomePage.vue";

// Lazy load all other pages
const CatalogPage = () => import("../views/CatalogPage.vue");
const CategoryProductsPage = () => import("../views/CategoryProductsPage.vue");
const ProductDetailPage = () => import("../views/ProductDetailPage.vue");
const NewsPage = () => import("../views/NewsPage.vue");
const NewsDetailPage = () => import("../views/NewsDetailPage.vue");
const AboutPage = () => import("../views/AboutPage.vue");
const ContactPage = () => import("../views/ContactPage.vue");
const NotFound = () => import("../views/NotFound.vue");
const Brand = () => import("../views/Brand.vue");
const AllBrandsPage = () => import("../views/AllBrandsPage.vue");
const FavoritesPage = () => import("../views/FavoritesPage.vue");
const ComparePage = () => import("../views/ComparePage.vue");
const CartPage = () => import("../views/CartPage.vue");

// Admin imports (lazy loaded)
const AdminLayout = () => import("../components/admin/AdminLayout.vue");
const AdminLogin = () => import("../views/AdminLogin.vue");
const AdminDashboard = () => import("../views/AdminDashboard.vue");
const AdminProfile = () => import("../views/AdminProfile.vue");
const ProductsManagement = () => import("../views/ProductsManagement.vue");

// Auth store for route guards
import { useAuthStore } from "../stores/auth";

const routes: RouteRecordRaw[] = [
  {
    path: "/",
    name: "Home",
    component: HomePage,
  },

  {
    path: "/brands/:slug",
    name: "Brand",
    component: Brand,
  },
  {
    path: "/brands",
    name: "AllBrands",
    component: AllBrandsPage,
  },
  {
    path: "/favorites",
    name: "Favorites",
    component: FavoritesPage,
  },
  {
    path: "/compare",
    name: "Compare",
    component: ComparePage,
  },
  {
    path: "/cart",
    name: "Cart",
    component: CartPage,
  },
  {
    path: "/catalog",
    name: "Catalog",
    component: CatalogPage,
  },
  {
    path: "/catalog/:categorySlug",
    name: "CategoryProducts",
    component: CategoryProductsPage,
  },
  {
    path: "/product/:slug",
    name: "ProductDetail",
    component: ProductDetailPage,
  },
  {
    path: "/news",
    name: "News",
    component: NewsPage,
  },
  {
    path: "/news/:slug",
    name: "NewsDetail",
    component: NewsDetailPage,
  },
  {
    path: "/about",
    name: "About",
    component: AboutPage,
  },
  {
    path: "/contact",
    name: "Contact",
    component: ContactPage,
  },

  // Admin routes
  {
    path: "/admin/login",
    name: "AdminLogin",
    component: AdminLogin,
    meta: { requiresGuest: true },
  },
  {
    path: "/admin",
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "AdminDashboard",
        component: AdminDashboard,
      },
      {
        path: "products",
        name: "ProductsManagement",
        component: ProductsManagement,
      },
      {
        path: "categories",
        name: "CategoriesManagement",
        component: () => import("../views/CategoriesManagement.vue"),
      },
      {
        path: "brands",
        name: "BrandsManagement",
        component: () => import("../views/BrandsManagement.vue"),
      },
      {
        path: "tags",
        name: "TagsManagement",
        component: () => import("../views/TagsManagement.vue"),
      },
      {
        path: "features",
        name: "FeaturesManagement",
        component: () => import("../views/FeaturesManagement.vue"),
      },
      {
        path: "news",
        name: "NewsManagement",
        component: () => import("../views/NewsManagement.vue"),
      },
      {
        path: "banners",
        name: "BannersManagement",
        component: () => import("../views/BannersManagement.vue"),
      },
      {
        path: "messages",
        name: "MessagesManagement",
        component: () => import("../views/MessagesManagement.vue"),
      },
      {
        path: "orders",
        name: "OrdersManagement",
        component: () => import("../views/OrdersManagement.vue"),
      },
      {
        path: "reviews",
        name: "ReviewsManagement",
        component: () => import("../views/ReviewsManagement.vue"),
      },
      {
        path: "questions",
        name: "QuestionsManagement",
        component: () => import("../views/QuestionsManagement.vue"),
      },
      {
        path: "settings",
        name: "AdminSettings",
        component: () => import("../views/AdminSettings.vue"),
      },
      {
        path: "profile",
        name: "AdminProfile",
        component: AdminProfile,
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

// Navigation guards
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();

  // Initialize auth state
  if (!authStore.initialized) {
    await authStore.init();
  }

  // If authenticated and trying to access login page, redirect to admin
  if (to.name === "AdminLogin" && authStore.isAuthenticated) {
    const redirect = (to.query.redirect as string) || "/admin";
    next(redirect);
    return;
  }

  // Check if route requires auth
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: "AdminLogin", query: { redirect: to.fullPath } });
    return;
  }

  next();
});

export default router;
