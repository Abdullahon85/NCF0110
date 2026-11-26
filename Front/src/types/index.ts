//types\index.ts
export interface Category {
  id: number;
  name: string;
  slug: string;
  image: string | null;
  parent: number | null;
  children: Category[];
  products_count: number;
  ancestors?: { name: string; slug: string }[]; // detail only: from the root down to the parent
}

export interface Banner {
  id: number;
  title: string;
  description: string | null;
  image: string;
  link: string | null;
  order: number;
  is_active: boolean;
}

export interface Brand {
  id: number;
  name: string;
  slug: string;
  image: string | null;
  description: string | null;
  products_count?: number;
  product_count?: number;
}

export interface BrandFilters {
  search?: string;
  category?: string;
  has_products?: boolean;
  has_available?: boolean;
  price_min?: number;
  price_max?: number;
  ordering?: string;
  page?: number;
  page_size?: number;
}
export interface Product {
  id: number;
  name: string;
  slug: string;
  description?: string;
  price: number | null;
  is_available: boolean;
  category: number | Category;
  category_name?: string;
  main_image?: Image | null;
  images?: Image[];
  features?: ProductFeature[];
  manufacturer_sku: string | number;
  internal_sku: string | number;
  brand?: number | string | Brand | null;
  // Commerce fields (old price with the computed discount, stock, label), see utils/productView.ts
  old_price?: number | string | null;
  discount_percent?: number | null;
  stock_quantity?: number | null;
  status?: "" | "new" | "promo" | "sale";
  status_label?: string;
  // Product page only
  breadcrumbs?: { name: string; slug: string }[];
  feature_groups?: { group: string; items: { name: string; values: string[] }[] }[];
  related?: Product[];
  documents?: {
    id: number;
    title: string;
    url: string | null;
    ext: string;
    size: number | null;
    order: number;
  }[];
}
export interface Image {
  id: number;
  image: string;
  is_main: boolean;
  order: number;
}
export interface ProductFeature {
  id: number;
  feature_name: string;
  feature_id?: number;
  value_id?: number;
  value_name?: string | null;
  value_names?: string[]; // Массив значений для одной характеристики
  group_name?: string | null; // Группа характеристики (опционально, для группировки в сравнении)
}

export interface NewsItem {
  id: number;
  title: string;
  slug: string;
  content?: string;
  preview: string;
  image: string | null;
  pub_date: string;
}

export interface AboutContent {
  title: string;
  content: string;
  image: string | null;
}

export interface ContactInfo {
  phone: string;
  email: string;
  address: string;
  map_url: string | null;
  working_hours?: string | null;
  instagram?: string | null;
  telegram?: string | null;
  whatsapp?: string | null;
  facebook?: string | null;
}

export interface ContactMessage {
  name: string;
  email: string;
  message: string;
}
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
  // опциональные поля, которые может возвращать ваш бэк
  page?: number;
  total_pages?: number;
  min_price?: number;
  max_price?: number;
}
export interface CartItem {
  product: Product;
  quantity: number;
  selectedOptions?: Record<string, any>;
}

export interface OrderItem {
  product: number | null;
  product_name: string;
  product_sku: string;
  price: number | null;
  quantity: number;
}

export interface Order {
  id?: number;
  customer_name: string;
  customer_phone: string;
  customer_email?: string;
  comment?: string;
  status?: string;
  created_at?: string;
  items: OrderItem[];
}

export interface User {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  token?: string; // JWT хранить только в store (не в localStorage как plain)
}

export interface Review {
  id?: number;
  product: number;
  author_name: string;
  rating: number; // 1-5
  text: string;
  created_at?: string;
  is_published?: boolean;
  admin_reply?: string;
  admin_reply_date?: string;
}

export interface ProductQuestion {
  id?: number;
  product: number;
  author_name: string;
  text: string;
  created_at?: string;
  is_published?: boolean;
  admin_reply?: string;
  admin_reply_date?: string;
}
