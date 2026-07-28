// src/api/index.ts
import axios from "axios";
import type {
  Category,
  Product,
  NewsItem,
  AboutContent,
  ContactInfo,
  ContactMessage,
  PaginatedResponse,
  ProductFilters,
  Order,
  Review,
  ProductQuestion,
  Tag,
  Brand,
  BrandFilters,
  ProductTagGroup,
  Banner,
} from "@/types";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "/api";
//   "http://127.0.0.1:8000/api" "https://ncb-1.onrender.com/api" "https://ncb-r1l6.onrender.com/api"  "https://nargizacompanyb.onrender.com/api" "https://a673a7823281.ngrok-free.app/api"
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
// api.interceptors.request.use(async (cfg) => {
//   const token = localStorage.getItem('token');
//   if (token) cfg.headers = { ...cfg.headers, Authorization: `Bearer ${token}` };
//   return cfg;
// });

export const categoriesAPI = {
  getAll: (limit?: number) => {
    const params = limit ? { limit } : {};
    return api.get<PaginatedResponse<Category>>("/categories/", { params });
  },

  getBySlug: (slug: string) => {
    return api.get<Category>(`/categories/${slug}/`);
  },

  getProducts: (slug: string, params?: Record<string, any>) => {
    return api.get<PaginatedResponse<Product>>(
      `/categories/${slug}/products/`,
      { params },
    );
  },

  getPriceRange(categorySlug: string) {
    // Update to match backend price range endpoint
    return api.get(`/categories/${categorySlug}/price-range/`);
  },

  getBrands: (slug: string, params?: Record<string, any>) =>
    api.get<Brand[]>(`/categories/${slug}/brands/`, { params }),
  // Endpoint may return either a flat Tag[] or grouped ProductTagGroup[] depending on backend.
  getTags: (
    slug: string,
    params?: { price_min?: number | null; price_max?: number | null },
  ) =>
    api.get<Tag[] | ProductTagGroup[]>(`/categories/${slug}/tags/`, { params }),
  getFeatured: () =>
    api.get("/categories/", {
      params: {
        page: 1,
        page_size: 3,
      },
    }),
};

export const productsAPI = {
  getAll: (params?: ProductFilters) => {
    return api.get<PaginatedResponse<Product>>("/products/", { params });
  },
  search: (query: string, params?: Partial<ProductFilters>) => {
    return api.get<PaginatedResponse<Product>>("/products/", {
      params: {
        search: query,
        ...params,
      },
    });
  },
  getByFeatureValue: (value: string) => {
    return api.get<Product[]>("/products/by-feature/", { params: { value } });
  },
  getBySlug: (slug: string) => {
    return api.get<Product>(`/products/${slug}/`);
  },

  getByBrand: (
    brandSlug: string,
    params?: { page?: number; page_size?: number },
  ) => {
    return api.get<PaginatedResponse<Product>>(
      `/brands/${brandSlug}/products/`,
      { params },
    );
  },
  getPriceRange(categorySlug: string) {
    return api.get("/products/price-range/", {
      params: { category: categorySlug },
    });
  },

  // CRUD operations
  create: (data: Record<string, any>) => {
    return api.post<Product>("/products/", data);
  },

  update: (slug: string, data: Record<string, any>) => {
    return api.patch<Product>(`/products/${slug}/`, data);
  },

  delete: (slug: string) => {
    return api.delete(`/products/${slug}/`);
  },

  uploadImages: (slug: string, formData: FormData) => {
    return api.post(`/products/${slug}/upload-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
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
  getById: (id: number | string) => {
    return api.get<Brand>(`/brands/${id}/`);
  },
  getBySlug: (slug: string) => {
    return api.get<Brand>(`/brands/${slug}/`);
  },

  getCategories: (slug: string) => {
    return api.get<Category[]>(`/brands/${slug}/categories/`);
  },
  getTags: (slug: string) => {
    return api.get<Tag[]>(`/brands/${slug}/tags/`);
  },
  getProducts: (slug: string, params?: Record<string, any>) => {
    return api.get<PaginatedResponse<Product>>(`/brands/${slug}/products/`, {
      params,
    });
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
  getById: (id: number) => api.get<Order>(`/orders/${id}/`),
  list: (params?: Record<string, any>) =>
    api.get<{ results: Order[]; count: number }>("/orders/", { params }),
};

export const reviewsAPI = {
  listByProduct: (productSlug: string, params?: any) =>
    api.get<PaginatedResponse<Review>>(`/products/${productSlug}/reviews/`, {
      params,
    }),
  create: (
    productSlug: string,
    payload: { author_name: string; rating: number; text: string },
  ) => api.post<Review>(`/products/${productSlug}/reviews/`, payload),
};

export const questionsAPI = {
  listByProduct: (productSlug: string, params?: any) =>
    api.get<PaginatedResponse<ProductQuestion>>(
      `/products/${productSlug}/questions/`,
      {
        params,
      },
    ),
  create: (
    productSlug: string,
    payload: { author_name: string; text: string },
  ) =>
    api.post<ProductQuestion>(`/products/${productSlug}/questions/`, payload),
};

export const similarProductsAPI = {
  get: (slug: string) => api.get<Product[]>(`/products/${slug}/similar/`),
};

export const tagsAPI = {
  getAll: (params?: Record<string, any>) =>
    api.get<PaginatedResponse<Tag>>("/tags/", { params }),
};

export const bannersAPI = {
  getAll: () => api.get<Banner[]>("/banners/"),
};

/**
 * Construct full image URL from API path
 * @param path - image path from API (relative or absolute URL)
 * @returns full image URL
 */
export const getImageUrl = (path: string | null): string => {
  if (!path) return "";
  // Strip the backend origin so Vite proxy can handle /media/* correctly
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
