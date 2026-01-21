<template>
	<div class="terms-view">
		<div class="view-header">
			<h2>📚 Список терминов</h2>
			<p class="subtitle">Всего терминов: {{ terms.length }}</p>

			<div class="controls">
				<div class="search-box">
					<input v-model="searchQuery" type="text" placeholder="Поиск терминов..." class="search-input" />
					<span class="search-icon">🔍</span>
				</div>

				<button @click="loadTerms" class="refresh-btn">
					↻ Обновить список
				</button>

				<router-link to="/graph" class="graph-link">
					🗺️ Перейти к графу
				</router-link>
			</div>
		</div>

		<div v-if="loading" class="loading">
			<div class="spinner"></div>
			<p>Загрузка терминов...</p>
		</div>

		<div v-else-if="error" class="error">
			<p>❌ Ошибка при загрузке терминов: {{ error }}</p>
			<button @click="loadTerms" class="retry-btn">Повторить попытку</button>
		</div>

		<div v-else class="terms-grid">
			<TermCard v-for="term in filteredTerms" :key="term.id" :term="term" @term-click="handleTermClick" />
		</div>

		<!-- Модальное окно для просмотра связей -->
		<div v-if="selectedTerm" class="modal-overlay" @click="closeModal">
			<div class="modal" @click.stop>
				<div class="modal-header">
					<h3>{{ selectedTerm.name }}</h3>
					<button class="close-btn" @click="closeModal">×</button>
				</div>
				<div class="modal-content">
					<p><strong>Описание:</strong> {{ selectedTerm.description }}</p>
					<p><strong>Источник:</strong>
						<a :href="selectedTerm.source_url" target="_blank">{{ selectedTerm.source_url }}</a>
					</p>

					<div v-if="selectedTermRelationships" class="relationships">
						<div v-if="selectedTermRelationships.influences.length" class="relationship-section">
							<h4>Влияет на:</h4>
							<ul>
								<li v-for="term in selectedTermRelationships.influences" :key="term.id">
									{{ term.name }}
								</li>
							</ul>
						</div>

						<div v-if="selectedTermRelationships.influenced_by.length" class="relationship-section">
							<h4>На него влияют:</h4>
							<ul>
								<li v-for="term in selectedTermRelationships.influenced_by" :key="term.id">
									{{ term.name }}
								</li>
							</ul>
						</div>

						<div v-if="!selectedTermRelationships.influences.length && !selectedTermRelationships.influenced_by.length">
							<p>Нет связей с другими терминами</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import TermCard from '../components/TermCard.vue'

export default {
	name: 'TermsView',
	components: {
		TermCard
	},
	setup() {
		const terms = ref([])
		const loading = ref(true)
		const error = ref(null)
		const searchQuery = ref('')
		const selectedTerm = ref(null)
		const selectedTermRelationships = ref(null)

		// Фильтрация терминов по поисковому запросу
		const filteredTerms = computed(() => {
			if (!searchQuery.value.trim()) {
				return terms.value
			}

			const query = searchQuery.value.toLowerCase()
			return terms.value.filter(term =>
				term.name.toLowerCase().includes(query) ||
				term.description.toLowerCase().includes(query)
			)
		})

		// Загрузка списка терминов
		const loadTerms = async () => {
			loading.value = true
			error.value = null

			try {
				const response = await fetch('/api/terms')
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}
				terms.value = await response.json()
			} catch (err) {
				error.value = err.message
				console.error('Ошибка загрузки терминов:', err)
			} finally {
				loading.value = false
			}
		}

		// Загрузка связей для выбранного термина
		const loadTermRelationships = async (termId) => {
			try {
				const response = await fetch(`/api/terms/${termId}`)
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}
				selectedTermRelationships.value = await response.json()
			} catch (err) {
				console.error('Ошибка загрузки связей термина:', err)
				selectedTermRelationships.value = null
			}
		}

		// Обработка клика по термину
		const handleTermClick = async (termId) => {
			selectedTerm.value = terms.value.find(term => term.id === termId)
			if (selectedTerm.value) {
				await loadTermRelationships(termId)
			}
		}

		// Закрытие модального окна
		const closeModal = () => {
			selectedTerm.value = null
			selectedTermRelationships.value = null
		}

		// Загрузка данных при монтировании компонента
		onMounted(() => {
			loadTerms()
		})

		return {
			terms,
			loading,
			error,
			searchQuery,
			filteredTerms,
			selectedTerm,
			selectedTermRelationships,
			loadTerms,
			handleTermClick,
			closeModal
		}
	}
}
</script>

<style scoped>
.terms-view {
	width: 100%;
}

.view-header {
	margin-bottom: 2rem;
}

.view-header h2 {
	font-size: 1.8rem;
	color: #2d3748;
	margin-bottom: 0.5rem;
}

.subtitle {
	color: #718096;
	margin-bottom: 1.5rem;
}

.controls {
	display: flex;
	gap: 1rem;
	align-items: center;
	flex-wrap: wrap;
	margin-bottom: 2rem;
}

.search-box {
	position: relative;
	flex: 1;
	max-width: 300px;
}

.search-input {
	width: 100%;
	padding: 0.75rem 1rem 0.75rem 2.5rem;
	border: 2px solid #e2e8f0;
	border-radius: 8px;
	font-size: 1rem;
	transition: border-color 0.2s ease;
}

.search-input:focus {
	outline: none;
	border-color: #667eea;
}

.search-icon {
	position: absolute;
	left: 0.75rem;
	top: 50%;
	transform: translateY(-50%);
	color: #a0aec0;
}

.refresh-btn {
	background: #edf2f7;
	color: #4a5568;
	border: none;
	padding: 0.75rem 1.5rem;
	border-radius: 8px;
	font-weight: 500;
	cursor: pointer;
	transition: all 0.2s ease;
}

.refresh-btn:hover {
	background: #e2e8f0;
}

.graph-link {
	background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
	color: white;
	text-decoration: none;
	padding: 0.75rem 1.5rem;
	border-radius: 8px;
	font-weight: 500;
	transition: all 0.2s ease;
}

.graph-link:hover {
	transform: translateY(-2px);
	box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.loading {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: 4rem;
}

.spinner {
	width: 50px;
	height: 50px;
	border: 4px solid #e2e8f0;
	border-top-color: #667eea;
	border-radius: 50%;
	animation: spin 1s linear infinite;
	margin-bottom: 1rem;
}

@keyframes spin {
	to {
		transform: rotate(360deg);
	}
}

.error {
	background: #fed7d7;
	color: #c53030;
	padding: 2rem;
	border-radius: 8px;
	text-align: center;
}

.retry-btn {
	background: #c53030;
	color: white;
	border: none;
	padding: 0.5rem 1rem;
	border-radius: 4px;
	margin-top: 1rem;
	cursor: pointer;
}

.terms-grid {
	display: grid;
	grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
	gap: 1.5rem;
}

/* Модальное окно */
.modal-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal {
	background: white;
	border-radius: 12px;
	width: 90%;
	max-width: 600px;
	max-height: 90vh;
	overflow-y: auto;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 1.5rem;
	border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
	margin: 0;
	color: #2d3748;
}

.close-btn {
	background: none;
	border: none;
	font-size: 1.5rem;
	cursor: pointer;
	color: #718096;
}

.modal-content {
	padding: 1.5rem;
}

.modal-content p {
	margin-bottom: 1rem;
	line-height: 1.5;
}

.relationships {
	margin-top: 1.5rem;
}

.relationship-section {
	margin-bottom: 1.5rem;
}

.relationship-section h4 {
	color: #4a5568;
	margin-bottom: 0.5rem;
}

.relationship-section ul {
	list-style: none;
	padding-left: 1rem;
}

.relationship-section li {
	padding: 0.25rem 0;
	color: #718096;
	position: relative;
}

.relationship-section li:before {
	content: "•";
	color: #667eea;
	font-weight: bold;
	position: absolute;
	left: -1rem;
}

@media (max-width: 768px) {
	.terms-grid {
		grid-template-columns: 1fr;
	}

	.controls {
		flex-direction: column;
		align-items: stretch;
	}

	.search-box {
		max-width: 100%;
	}
}
</style>
