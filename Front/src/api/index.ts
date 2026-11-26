// src/api/index.ts
import axios from "axios";
import type { CatalogFacets } from "@/utils/catalogQuery";
import type {
  Category,
  Product,
  NewsItem,
  AboutContent,
  ContactInfo,
  ContactMessage,
  PaginatedResponse,
  Order,
  Review,
  ProductQuestion,
  Brand,
  BrandFilters,
  Banner,
} from "@/types";

const API_BASE_URL = import.meta.env.VITE_API_URL || "/api"; // empty value in .env -> same-domain /api
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

// Helper function to delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const config = error.config;

    // Handle 429 Too Many Requests with retry
    if (error.response?.status === 429) {
      config._retryCount = config._retryCount || 0;

      if (config._retryCount < MAX_RETRIES) {
        config._retryCount++;
        const retryDelay = RETRY_DELAY * config._retryCount;

        console.warn(
          `Rate limit hit. Retrying in ${retryDelay}ms... (Attempt ${config._retryCount}/${MAX_RETRIES})`,
        );

        await delay(retryDelay);
        return api(config);
      } else {
        console.error("Max retries reached for rate-limited request");
      }
    }

    console.error("API Error:", error);
    return Promise.reject(error);
  },
);

export const categoriesAPI = {
  getAll: (limit?: number) => {
    const params = limit ? { limit } : {};
    return api.get<PaginatedResponse<Category>>("/categories/", { params });
  },

  getBySlug: (slug: string) => {
    return api.get<Category>(`/categories/${slug}/`);
  },
};

export const productsAPI = {
  // Product lists of the site: filters, sorting, page (see utils/catalogQuery.ts).
  list: (params: Record<string, string>) =>
    api.get<PaginatedResponse<Product> & { page: number; page_size: number }>("/products/", {
      params,
    }),
  // Filter groups with counts for the same parameters.
  facets: (params: Record<string, string>) =>
    api.get<CatalogFacets>("/products/facets/", { params }),
  getBySlug: (slug: string) => {
    return api.get<Product>(`/products/${slug}/`);
  },
};

export const newsAPI = {
  getAll: (limit?: number) => {
    const params = limit ? { limit } : {};
    return api.get<PaginatedResponse<NewsItem>>("/news/", { params });
  },

  getBySlug: (slug: string) => {
    return api.get<NewsItem>(`/news/${slug}/`);
  },
};

export const brandsAPI = {
  getAll: (params?: BrandFilters) => {
    return api.get<PaginatedResponse<Brand>>("/brands/", { params });
  },
  getBySlug: (slug: string) => {
    return api.get<Brand>(`/brands/${slug}/`);
  },
};

export const aboutAPI = {
  get: () => {
    return api.get<AboutContent>("/about/");
  },
};

export const contactAPI = {
  getInfo: () => {
    return api.get<ContactInfo>("/contact/");
  },
  sendMessage: (data: ContactMessage) => {
    return api.post("/contact/message/", data);
  },
};

export const ordersAPI = {
  create: (payload: Order) => api.post<Order>("/orders/", payload),
};

export const reviewsAPI = {
  listByProduct: (productSlug: string, params?: any) =>
    api.get<PaginatedResponse<Review>>(`/products/${productSlug}/reviews/`, {
      params,
    }),
  create: (productSlug: string, payload: { author_name: string; rating: number; text: string }) =>
    api.post<Review>(`/products/${productSlug}/reviews/`, payload),
};

export const questionsAPI = {
  listByProduct: (productSlug: string, params?: any) =>
    api.get<PaginatedResponse<ProductQuestion>>(`/products/${productSlug}/questions/`, {
      params,
    }),
  create: (productSlug: string, payload: { author_name: string; text: string }) =>
    api.post<ProductQuestion>(`/products/${productSlug}/questions/`, payload),
};

export const similarProductsAPI = {
  get: (slug: string) => api.get<Product[]>(`/products/${slug}/similar/`),
};

// Pages for buyers (Оплата, Доставка...): list for the footer, one page by slug.
export const pagesAPI = {
  list: () => api.get<{ slug: string; title: string }[]>("/pages/"),
  get: (slug: string) =>
    api.get<{ slug: string; title: string; content: string; updated_at: string }>(
      `/pages/${slug}/`,
    ),
};

export const bannersAPI = {
  getAll: () => api.get<Banner[]>("/banners/"),
};

/**
 * Construct full image URL from API path
 * @param path - image path from API (relative or absolute URL)
 * @returns full image URL
 */
// API on its own domain (absolute VITE_API_URL): the backend returns absolute
// image URLs (MEDIA_URL=https://api.../media/), keep them as they are.
const API_IS_CROSS_DOMAIN = /^https?:\/\//.test(API_BASE_URL);

export const getImageUrl = (path: string | null): string => {
  if (!path) return "";
  if (API_IS_CROSS_DOMAIN && /^https?:\/\//.test(path)) return path;
  // Same domain: strip the backend origin so /media/* goes through the proxy (dev) or nginx (prod)
  if (path.startsWith("http://") || path.startsWith("https://")) {
    try {
      const url = new URL(path);
      return url.pathname;
    } catch {
      return path;
    }
  }
  return `/${path.replace(/^\//, "")}`;
};
