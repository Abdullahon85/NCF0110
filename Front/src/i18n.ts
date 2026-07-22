import { createI18n } from 'vue-i18n';

const messages = {
  uz: {
    home: "Bosh sahifa",
    products: "Mahsulotlar",
    categories: "Kategoriyalar",
    brands: "Brendlar",
    cart: "Savat",
    login: "Kirish",
    logout: "Chiqish",
    about: "Biz haqimizda",
    contact: "Aloqa",
    news: "Yangiliklar",
    price: "Narx",
    available: "Mavjud",
    filter: "Filtrlash",
    reset: "Tozalash",
    not_found: "Sahifa topilmadi",
    send: "Yuborish",
    search: "Qidirish",
    // ... boshqa matnlar ...
  },
  ru: {
    home: "Главная",
    products: "Товары",
    categories: "Категории",
    brands: "Бренды",
    cart: "Корзина",
    login: "Войти",
    logout: "Выйти",
    about: "О нас",
    contact: "Контакты",
    news: "Новости",
    price: "Цена",
    available: "В наличии",
    filter: "Фильтр",
    reset: "Сбросить",
    not_found: "Страница не найдена",
    send: "Отправить",
    search: "Поиск",
    // ... другие тексты ...
  },
  en: {
    home: "Home",
    products: "Products",
    categories: "Categories",
    brands: "Brands",
    cart: "Cart",
    login: "Login",
    logout: "Logout",
    about: "About us",
    contact: "Contact",
    news: "News",
    price: "Price",
    available: "Available",
    filter: "Filter",
    reset: "Reset",
    not_found: "Page not found",
    send: "Send",
    search: "Search",
    // ... other texts ...
  }
};

export const i18n = createI18n({
  legacy: false,
  locale: 'uz',
  fallbackLocale: 'en',
  messages,
});