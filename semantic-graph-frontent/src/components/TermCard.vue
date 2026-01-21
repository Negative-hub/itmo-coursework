<template>
  <div class="term-card" @click="handleClick">
    <div class="term-card-header">
      <h3 class="term-title">{{ term.name }}</h3>
      <span class="term-id">#{{ term.id }}</span>
    </div>

    <p class="term-description">{{ term.description }}</p>

    <div class="term-card-footer">
      <a :href="term.source_url" target="_blank" class="source-link" @click.stop>
        📚 Источник определений
      </a>
      <button class="details-btn" @click.stop="navigateToTerm">
        🔗 Связи термина
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TermCard',
  props: {
    term: {
      type: Object,
      required: true
    }
  },
  methods: {
    handleClick() {
      this.$emit('term-click', this.term.id)
    },
    navigateToTerm() {
      // Можно добавить модальное окно или другую логику для просмотра связей
      alert(`Связи термина "${this.term.name}" можно увидеть на странице графа`)
    }
  }
}
</script>

<style scoped>
.term-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.term-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.term-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.term-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  flex: 1;
  margin-right: 1rem;
}

.term-id {
  background: #edf2f7;
  color: #4a5568;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 600;
}

.term-description {
  color: #4a5568;
  line-height: 1.5;
  flex: 1;
  margin-bottom: 1rem;
}

.term-card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
}

.source-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.source-link:hover {
  color: #5a67d8;
  text-decoration: underline;
}

.details-btn {
  background: #e6fffa;
  color: #234e52;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.details-btn:hover {
  background: #b2f5ea;
}
</style>