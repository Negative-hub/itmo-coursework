import { createRouter, createWebHistory } from "vue-router";

const routes = [
  { path: "/", component: () => import("../views/TermsView.vue") },
  { path: "/graph", component: () => import("../views/GraphView.vue") },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
