<template>
  <div id="app">
    <header class="header">
      <nav class="nav">
        <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
          📋 Список терминов
        </router-link>
        <router-link to="/graph" class="nav-link" :class="{ active: $route.path === '/graph' }">
          🗺️ Семантический граф
        </router-link>
      </nav>
      <h1 class="title">Семантический граф терминов веб-разработки</h1>
    </header>

    <main class="main">
      <router-view></router-view>
    </main>

    <footer class="footer">
      <p>Для практического отчета • Семантический граф • Vue.js + FastAPI</p>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.nav-link {
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  color: white;
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
}

.title {
  font-size: 1.8rem;
  font-weight: 600;
}

.main {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.footer {
  background-color: #2d3748;
  color: #cbd5e0;
  text-align: center;
  padding: 1.5rem;
  font-size: 0.9rem;
}
</style>