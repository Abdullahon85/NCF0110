// src/api/admin.ts
import axios from "axios";
import type {
  AxiosError,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL ?? "/api";
//   "http://localhost:8000/api" "https://ncb-1.onrender.com/api" "https://ncb-r1l6.onrender.com/api"  "https://nargizacompanyb.onrender.com/api" "https://a673a7823281.ngrok-free.app/api"
// ============ SECURITY CONSTANTS ============
const TOKEN_KEY = "admin_token";
const REFRESH_KEY = "admin_refresh";
const REQUEST_TIMEOUT = 30000; // 30 seconds
const RATE_LIMIT_DELAY = 150; // 150ms between requests

// ============ RATE LIMITER ============
class RateLimiter {
  private lastRequest = 0;

  async wait() {
    const now = Date.now();
    const timeSinceLastRequest = now - this.lastRequest;

    if (timeSinceLastRequest < RATE_LIMIT_DELAY) {
      await new Promise((resolve) =>
        setTimeout(resolve, RATE_LIMIT_DELAY - timeSinceLastRequest),
      );
    }

    this.lastRequest = Date.now();
  }
}

const rateLimiter = new RateLimiter();

// ============ SECURE TOKEN STORAGE ============
const tokenStorage = {
  setTokens(access: string, refresh?: string) {
    sessionStorage.setItem(TOKEN_KEY, access);
    if (refresh) sessionStorage.setItem(REFRESH_KEY, refresh);
  },

  getToken(): string | null {
    return sessionStorage.getItem(TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    return sessionStorage.getItem(REFRESH_KEY);
  },

  clearTokens() {
    sessionStorage.removeItem(TOKEN_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, `=;expires=${new Date().toUTCString()};path=/`);
    });
  },

  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      return payload.exp * 1000 < Date.now();
    } catch {
      return true;
    }
  },
};

// ============ AXIOS INSTANCE ============
const adminApi = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: {
    "Content-Type": "application/json",
    "Cache-Control": "no-cache, no-store, must-revalidate",
    Pragma: "no-cache",
    Expires: "0",
  },
  withCredentials: true,
});

// ============ REQUEST INTERCEPTOR ============
adminApi.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // Rate limiting
    await rateLimiter.wait();

    // CSRF Token
    const csrfToken = document.cookie
      .split("; ")
      .find((row) => row.startsWith("csrftoken="))
      ?.split("=")[1];

    if (csrfToken && config.headers) {
      config.headers["X-CSRFToken"] = csrfToken;
    }

    // JWT Token
    const token = tokenStorage.getToken();
    if (token && config.headers) {
      if (tokenStorage.isTokenExpired(token)) {
        const refreshToken = tokenStorage.getRefreshToken();
        if (refreshToken) {
          try {
            const { data } = await axios.post(
              `${API_BASE_URL}/admin/auth/refresh/`,
              {
                refresh: refreshToken,
              },
            );
            tokenStorage.setTokens(data.access);
            config.headers.Authorization = `Bearer ${data.access}`;
          } catch {
            tokenStorage.clearTokens();
            return Promise.reject(new Error("Session expired"));
          }
        }
      } else {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => Promise.reject(error),
);

// ============ RESPONSE INTERCEPTOR ============
adminApi.interceptors.response.use(
  (response: AxiosResponse) => {
    // Allow empty responses for DELETE requests (204 No Content)
    if (!response.data && response.status !== 204) {
      console.error("Invalid response: no data");
      return Promise.reject(new Error("Invalid server response"));
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = tokenStorage.getRefreshToken();
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${API_BASE_URL}/admin/auth/refresh/`,
            {
              refresh: refreshToken,
            },
          );
          tokenStorage.setTokens(data.access);

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${data.access}`;
          }

          return adminApi(originalRequest);
        } catch {
          tokenStorage.clearTokens();
        }
      } else {
        tokenStorage.clearTokens();
      }
    }

    if (error.response?.status === 429) {
      console.error("Too many requests - rate limited");
    }

    console.error("API Error:", {
      status: error.response?.status,
      message: error.message,
      url: originalRequest?.url,
    });

    return Promise.reject(error);
  },
);

// ============ HELPER: VALIDATE ID ============
const validateId = (id: number, resource: string) => {
  if (!id || id < 1 || !Number.isInteger(id)) {
    throw new Error(`Invalid ${resource} ID`);
  }
};

// ============ AUTH API (SECURE) ============
export const authAPI = {
  login: async (username: string, password: string) => {
    if (!username || !password) {
      throw new Error("Username and password are required");
    }

    if (password.length < 8) {
      throw new Error("Password too short");
    }

    const response = await adminApi.post("/admin/auth/login/", {
      username: username.trim(),
      password,
    });

    if (response.data.access) {
      tokenStorage.setTokens(response.data.access, response.data.refresh);
    }

    return response;
  },

  logout: async () => {
    try {
      await adminApi.post("/admin/auth/logout/");
    } finally {
      tokenStorage.clearTokens();
    }
  },

  getMe: () => adminApi.get("/admin/auth/me/"),

  changePassword: (oldPassword: string, newPassword: string) => {
    if (newPassword.length < 8) {
      return Promise.reject(new Error("Пароль должен быть минимум 8 символов"));
    }

    return adminApi.post("/admin/auth/change-password/", {
      old_password: oldPassword,
      new_password: newPassword,
    });
  },

  updateProfile: (data: {
    email?: string;
    first_name?: string;
    last_name?: string;
  }) => {
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
      return Promise.reject(new Error("Invalid email format"));
    }

    return adminApi.patch("/admin/auth/profile/", data);
  },

  refreshToken: async () => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error("No refresh token");
    }

    const { data } = await axios.post(`${API_BASE_URL}/admin/auth/refresh/`, {
      refresh: refreshToken,
    });

    tokenStorage.setTokens(data.access);
    return data;
  },

  checkSession: () => {
    const token = tokenStorage.getToken();
    if (!token || tokenStorage.isTokenExpired(token)) {
      return false;
    }
    return true;
  },
};

// ============ STATS API ============
export const statsAPI = {
  getDashboard: () => adminApi.get("/admin/stats/"),
};

// ============ FEATURES/TAGS BY CATEGORY ============
export const categoryDataAPI = {
  getByCategory: (categoryId: number) => {
    if (!categoryId || categoryId < 1) {
      return Promise.reject(new Error("Invalid category ID"));
    }
    return adminApi.get("/features-tags-by-category/", {
      params: { category: categoryId },
    });
  },

  getValuesByFeature: (featureId: number) => {
    if (!featureId || featureId < 1) {
      return Promise.reject(new Error("Invalid feature ID"));
    }
    return adminApi.get("/feature-values-by-feature/", {
      params: { feature_id: featureId },
    });
  },
};

// ============ CATEGORIES API ============
export const categoriesAdminAPI = {
  getAll: (params?: { search?: string; parent?: string | number }) =>
    adminApi.get("/admin/categories/", { params }),

  getById: (id: number) => {
    validateId(id, "category");
    return adminApi.get(`/admin/categories/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/categories/", data),

  update: (id: number, data: any) => {
    validateId(id, "category");
    return adminApi.patch(`/admin/categories/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "category");
    return adminApi.delete(`/admin/categories/${id}/`);
  },

  uploadImage: (id: number, formData: FormData) => {
    validateId(id, "category");
    const file = formData.get("image") as File;
    if (file && file.size > 5 * 1024 * 1024) {
      return Promise.reject(new Error("File too large (max 5MB)"));
    }

    return adminApi.post(`/admin/categories/${id}/upload-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  deleteImage: (id: number) => {
    validateId(id, "category");
    return adminApi.delete(`/admin/categories/${id}/delete-image/`);
  },
};

// ============ BRANDS API ============
export const brandsAdminAPI = {
  getAll: (params?: { search?: string }) =>
    adminApi.get("/admin/brands/", { params }),

  getById: (id: number) => {
    validateId(id, "brand");
    return adminApi.get(`/admin/brands/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/brands/", data),

  update: (id: number, data: any) => {
    validateId(id, "brand");
    return adminApi.patch(`/admin/brands/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "brand");
    return adminApi.delete(`/admin/brands/${id}/`);
  },

  uploadLogo: (id: number, formData: FormData) => {
    validateId(id, "brand");
    const file = formData.get("logo") as File;
    if (file && file.size > 2 * 1024 * 1024) {
      return Promise.reject(new Error("Logo too large (max 2MB)"));
    }

    return adminApi.post(`/admin/brands/${id}/upload-logo/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ============ TAGS API ============
export const tagsAdminAPI = {
  getAll: (params?: {
    search?: string;
    category?: number;
    tag_name?: number;
  }) => adminApi.get("/admin/tags/", { params }),

  getById: (id: number) => {
    validateId(id, "tag");
    return adminApi.get(`/admin/tags/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/tags/", data),

  update: (id: number, data: any) => {
    validateId(id, "tag");
    return adminApi.patch(`/admin/tags/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "tag");
    return adminApi.delete(`/admin/tags/${id}/`);
  },

  getByTagName: (tagNameId: number) =>
    adminApi.get(`/admin/tags-by-tag-name/${tagNameId}/`),
};

// ============ TAG NAMES API ============
export const tagNamesAdminAPI = {
  getAll: (params?: { search?: string; category?: number }) =>
    adminApi.get("/admin/tag-names/", { params }),

  getById: (id: number) => {
    validateId(id, "tag name");
    return adminApi.get(`/admin/tag-names/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/tag-names/", data),

  update: (id: number, data: any) => {
    validateId(id, "tag name");
    return adminApi.patch(`/admin/tag-names/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "tag name");
    return adminApi.delete(`/admin/tag-names/${id}/`);
  },
};

// ============ FEATURES API ============
export const featuresAdminAPI = {
  getAll: (params?: {
    search?: string;
    category?: number;
    page?: number;
    page_size?: number;
  }) => adminApi.get("/admin/features/", { params }),

  getById: (id: number) => {
    validateId(id, "feature");
    return adminApi.get(`/admin/features/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/features/", data),

  update: (id: number, data: any) => {
    validateId(id, "feature");
    return adminApi.patch(`/admin/features/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "feature");
    return adminApi.delete(`/admin/features/${id}/`);
  },

  debugFirst: () => adminApi.get("/admin/features/debug_first/"),
};

// ============ FEATURE VALUES API ============
export const featureValuesAdminAPI = {
  getAll: (params?: {
    search?: string;
    category?: number;
    feature?: number;
    page?: number;
    page_size?: number;
  }) => adminApi.get("/admin/feature-values/", { params }),

  getById: (id: number) => {
    validateId(id, "feature value");
    return adminApi.get(`/admin/feature-values/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/feature-values/", data),

  update: (id: number, data: any) => {
    validateId(id, "feature value");
    return adminApi.patch(`/admin/feature-values/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "feature value");
    return adminApi.delete(`/admin/feature-values/${id}/`);
  },

  getByFeature: (featureId: number) => {
    validateId(featureId, "feature");
    return adminApi.get("/admin/feature-values/", {
      params: { feature: featureId },
    });
  },
};

// ============ NEWS API ============
export const newsAdminAPI = {
  getAll: (params?: { search?: string; is_published?: boolean }) =>
    adminApi.get("/admin/news/", { params }),

  getById: (id: number) => {
    validateId(id, "news");
    return adminApi.get(`/admin/news/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/news/", data),

  update: (id: number, data: any) => {
    validateId(id, "news");
    return adminApi.patch(`/admin/news/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "news");
    return adminApi.delete(`/admin/news/${id}/`);
  },
};

// ============ IMAGES API ============
export const imagesAdminAPI = {
  getAll: (params?: { product?: number }) =>
    adminApi.get("/admin/images/", { params }),

  create: (data: any) => adminApi.post("/admin/images/", data),

  update: (id: number, data: any) => {
    validateId(id, "image");
    return adminApi.patch(`/admin/images/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "image");
    return adminApi.delete(`/admin/images/${id}/`);
  },
};

// ============ SETTINGS API ============
export const settingsAdminAPI = {
  getAbout: () => adminApi.get("/admin/about/"),
  updateAbout: (data: any) => adminApi.put("/admin/about/", data),
  getContact: () => adminApi.get("/admin/contact/"),
  updateContact: (data: any) => adminApi.put("/admin/contact/", data),
  patchContact: (data: any) => adminApi.patch("/admin/contact/", data),
};

// ============ MESSAGES API ============
export const messagesAdminAPI = {
  getAll: (params?: { is_processed?: boolean }) =>
    adminApi.get("/admin/messages/", { params }),

  getById: (id: number) => {
    validateId(id, "message");
    return adminApi.get(`/admin/messages/${id}/`);
  },

  markProcessed: (id: number) => {
    validateId(id, "message");
    return adminApi.post(`/admin/messages/${id}/mark-processed/`);
  },

  markUnprocessed: (id: number) => {
    validateId(id, "message");
    return adminApi.post(`/admin/messages/${id}/mark-unprocessed/`);
  },

  delete: (id: number) => {
    validateId(id, "message");
    return adminApi.delete(`/admin/messages/${id}/`);
  },
};

// ============ BANNERS API ============
export const bannersAdminAPI = {
  getAll: () => adminApi.get("/admin/banners/"),

  getById: (id: number) => {
    validateId(id, "banner");
    return adminApi.get(`/admin/banners/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/banners/", data),

  update: (id: number, data: any) => {
    validateId(id, "banner");
    return adminApi.patch(`/admin/banners/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "banner");
    return adminApi.delete(`/admin/banners/${id}/`);
  },

  uploadImage: (id: number, formData: FormData) => {
    validateId(id, "banner");
    return adminApi.post(`/admin/banners/${id}/upload-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

// ============ PRODUCTS API ============
export const productsAdminAPI = {
  getAll: (params?: {
    search?: string;
    category?: number;
    brand?: number;
    is_available?: boolean;
    ordering?: string;
    page?: number;
    page_size?: number;
  }) => adminApi.get("/admin/products/", { params }),

  getById: (id: number) => {
    validateId(id, "product");
    return adminApi.get(`/admin/products/${id}/`);
  },

  create: (data: any) => adminApi.post("/admin/products/", data),

  update: (id: number, data: any) => {
    validateId(id, "product");
    return adminApi.patch(`/admin/products/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "product");
    return adminApi.delete(`/admin/products/${id}/`);
  },

  uploadImage: (id: number, formData: FormData) => {
    validateId(id, "product");
    const file = formData.get("image") as File;
    if (file && file.size > 10 * 1024 * 1024) {
      return Promise.reject(new Error("Image too large (max 10MB)"));
    }

    return adminApi.post(`/admin/products/${id}/upload-image/`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000, // 2 minutes for file upload
    });
  },

  deleteImage: (productId: number, imageId: number) => {
    validateId(productId, "product");
    validateId(imageId, "image");
    return adminApi.delete(
      `/admin/products/${productId}/delete-image/${imageId}/`,
    );
  },
};

export default adminApi;
export { tokenStorage };

// ============ ORDERS ADMIN API ============
export const ordersAdminAPI = {
  getAll: (params?: {
    status?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }) => adminApi.get("/orders/", { params }),

  getById: (id: number) => {
    validateId(id, "order");
    return adminApi.get(`/orders/${id}/`);
  },

  updateStatus: (id: number, status: string) => {
    validateId(id, "order");
    return adminApi.patch(`/orders/${id}/`, { status });
  },

  delete: (id: number) => {
    validateId(id, "order");
    return adminApi.delete(`/orders/${id}/`);
  },
};

// ============ REVIEWS ADMIN API ============
export const reviewsAdminAPI = {
  getAll: (params?: {
    search?: string;
    product?: number;
    rating?: number;
    is_published?: string;
  }) => adminApi.get("/admin/reviews/", { params }),

  getById: (id: number) => {
    validateId(id, "review");
    return adminApi.get(`/admin/reviews/${id}/`);
  },

  update: (id: number, data: any) => {
    validateId(id, "review");
    return adminApi.patch(`/admin/reviews/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "review");
    return adminApi.delete(`/admin/reviews/${id}/`);
  },
};

// ============ QUESTIONS ADMIN API ============
export const questionsAdminAPI = {
  getAll: (params?: {
    search?: string;
    product?: number;
    is_published?: string;
  }) => adminApi.get("/admin/questions/", { params }),

  getById: (id: number) => {
    validateId(id, "question");
    return adminApi.get(`/admin/questions/${id}/`);
  },

  update: (id: number, data: any) => {
    validateId(id, "question");
    return adminApi.patch(`/admin/questions/${id}/`, data);
  },

  delete: (id: number) => {
    validateId(id, "question");
    return adminApi.delete(`/admin/questions/${id}/`);
  },
};
