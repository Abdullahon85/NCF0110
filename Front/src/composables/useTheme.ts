import { ref, watchEffect } from 'vue';

const theme = ref(localStorage.getItem('theme') || 'light');

function toggleTheme() {
  theme.value = theme.value === 'light' ? 'dark' : 'light';
  localStorage.setItem('theme', theme.value);
}

watchEffect(() => {
  if (theme.value === 'dark') {
    document.documentElement.classList.add('dark-theme');
  } else {
    document.documentElement.classList.remove('dark-theme');
  }
});

export function useTheme() {
  return { theme, toggleTheme };
}