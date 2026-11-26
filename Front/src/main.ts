import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";
import "@fontsource-variable/onest";
import "./styles/site/index.css";
import "./styles/admin/index.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.mount("#app");
