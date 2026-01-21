<template>
	<div class="graph-view">
		<div class="view-header">
			<h2>🗺️ Семантический граф терминов</h2>
			<p class="subtitle">Визуализация связей между терминами веб-разработки</p>

			<div class="controls">
				<div class="layout-controls">
					<label>Расположение:</label>
					<select v-model="selectedLayout" class="layout-select">
						<option value="circle">Круг (автоматическое)</option>
						<option value="cose">COSE</option>
						<option value="grid">Сетка</option>
						<option value="random">Случайное</option>
					</select>
				</div>

				<div class="filter-controls">
					<label>
						<input type="checkbox" v-model="showLabels"> Показывать подписи связей
					</label>
				</div>

				<button @click="refreshGraph" class="refresh-btn">
					↻ Обновить граф
				</button>

				<router-link to="/" class="list-link">
					📋 К списку терминов
				</router-link>
			</div>
		</div>

		<div class="graph-container">
			<div v-if="error" class="error">
				<p>❌ Ошибка при загрузке графа: {{ error }}</p>
				<button @click="loadGraph" class="retry-btn">Повторить попытку</button>
			</div>

			<div v-else class="graph-wrapper">
				<div id="cy" class="cy-container" />
			</div>
		</div>

		<!-- Панель информации о термине -->
		<div v-if="selectedNodeInfo" class="info-panel">
			<div class="info-header">
				<h3>{{ selectedNodeInfo.name }}</h3>
				<button class="close-btn" @click="closeInfoPanel">×</button>
			</div>
			<div class="info-content">
				<p><strong>Описание:</strong> {{ selectedNodeInfo.description }}</p>
				<p><strong>Источник: </strong>
					<a :href="selectedNodeInfo.source_url" target="_blank">Открыть документ</a>
				</p>

				<div v-if="nodeRelationships" class="relationships">
					<div v-if="nodeRelationships.influences.length" class="relationship-section">
						<h4>Влияет на:</h4>
						<ul>
							<li v-for="term in nodeRelationships.influences" :key="term.id">
								{{ term.name }}
							</li>
						</ul>
					</div>

					<div v-if="nodeRelationships.influenced_by.length" class="relationship-section">
						<h4>На него влияют:</h4>
						<ul>
							<li v-for="term in nodeRelationships.influenced_by" :key="term.id">
								{{ term.name }}
							</li>
						</ul>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import cytoscape from 'cytoscape'
import coseBilkent from 'cytoscape-cose-bilkent'

// Регистрация расширения для layout
cytoscape.use(coseBilkent)

export default {
	name: 'GraphView',
	setup() {
		const error = ref(null)
		const selectedLayout = ref('circle')
		const showLabels = ref(true)
		const selectedNodeInfo = ref(null)
		const nodeRelationships = ref(null)

		let cy = null

		// Цвета для разных типов связей
		const edgeColors = {
			'influences': '#7FDBFF',
			'improves': '#2ECC40',
			'requires': '#FF4136',
			'affects': '#FFDC00',
			'includes': '#B10DC9',
			'extends': '#01FF70'
		}

		// Инициализация Cytoscape.js
		const initCytoscape = (graphData) => {
			const container = document.getElementById('cy')

			cy = cytoscape({
				container: container,
				elements: {
					nodes: graphData.nodes,
					edges: graphData.edges
				},
				style: [
					// Стиль для узлов
					{
						selector: 'node',
						style: {
							'label': 'data(label)',
							'text-valign': 'center',
							'text-halign': 'center',
							'text-wrap': 'wrap',
							'text-max-width': '150px',
							'font-size': '12px',
							'font-weight': '600',
							'color': '#2d3748',
							'background-color': '#0074D9',
							'border-width': 2,
							'border-color': '#0056b3',
							'width': 'label',
							'height': 'label',
							'padding': '10px',
							'shape': 'round-rectangle'
						}
					},

					// Стиль для связей
					{
						selector: 'edge',
						style: {
							'width': 3,
							'line-color': function (ele) {
								return edgeColors[ele.data('type')] || '#7FDBFF'
							},
							'target-arrow-color': function (ele) {
								return edgeColors[ele.data('type')] || '#7FDBFF'
							},
							'target-arrow-shape': 'triangle',
							'curve-style': 'bezier',
							'label': function (ele) {
								return showLabels.value ? ele.data('label') : ''
							},
							'text-background-color': '#fff',
							'text-background-opacity': 0.8,
							'text-background-padding': '2px',
							'font-size': '10px',
							'text-margin-y': -10
						}
					},

					// Стиль для выбранного узла
					{
						selector: 'node:selected',
						style: {
							'border-width': 4,
							'border-color': '#FF4136',
							'background-color': '#ff6b6b'
						}
					}
				],

				layout: {
					name: selectedLayout.value,
					padding: 30
				}
			})

			// Обработчики событий
			cy.on('tap', 'node', async function (evt) {
				const node = evt.target
				node.select()

				// Показываем информацию о термине
				selectedNodeInfo.value = {
					id: node.data('id'),
					name: node.data('name'),
					description: node.data('description'),
					source_url: node.data('source_url')
				}

				// Загружаем связи термина
				await loadNodeRelationships(node.data('id'))
			})

			cy.on('tap', function (evt) {
				// Снимаем выделение при клике на пустое место
				if (evt.target === cy) {
					cy.elements().unselect()
					closeInfoPanel()
				}
			})

			// Добавляем тултипы при наведении
			cy.on('mouseover', 'node', function (evt) {
				const node = evt.target
				const tooltip = document.createElement('div')
				console.log(tooltip, '21241')

				tooltip.className = 'cytoscape-tooltip'
				tooltip.innerHTML = `<strong>${node.data('name')}</strong><br/>${node.data('description').substring(0, 100)}...`
				tooltip.style.position = 'absolute'
				tooltip.style.background = 'white'
				tooltip.style.padding = '5px'
				tooltip.style.border = '1px solid #ccc'
				tooltip.style.borderRadius = '3px'
				tooltip.style.pointerEvents = 'none'
				tooltip.style.zIndex = '1000'

				const pos = node.renderedPosition()
				tooltip.style.left = (pos.x + 20) + 'px'
				tooltip.style.top = (pos.y - 20) + 'px'

				document.getElementById('cy').appendChild(tooltip)
				node.data('tooltip', tooltip)
			})

			cy.on('mouseout', 'node', function (evt) {
				const node = evt.target
				const tooltip = node.data('tooltip')
				if (tooltip && tooltip.parentNode) {
					tooltip.parentNode.removeChild(tooltip)
				}
			})
		}

		// Загрузка данных графа
		const loadGraph = async () => {
			error.value = null

			try {
				const response = await fetch('/api/graph')
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}
				const graphData = await response.json()

				// Инициализация или обновление графа
				if (cy) {
					cy.elements().remove()
					cy.add(graphData.nodes)
					cy.add(graphData.edges)
					applyLayout()
				} else {
					initCytoscape(graphData)
				}
			} catch (err) {
				error.value = err.message
				console.error('Ошибка загрузки графа:', err)
			}
		}

		// Загрузка связей для узла
		const loadNodeRelationships = async (nodeId) => {
			try {
				const response = await fetch(`/api/terms/${nodeId}`)
				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`)
				}
				nodeRelationships.value = await response.json()
			} catch (err) {
				console.error('Ошибка загрузки связей узла:', err)
				nodeRelationships.value = null
			}
		}

		// Применение выбранного layout
		const applyLayout = () => {
			if (!cy) return

			const layout = cy.layout({
				name: selectedLayout.value,
				padding: 30
			})

			layout.run()
		}

		// Обновление графа
		const refreshGraph = () => {
			loadGraph()
		}

		// Закрытие панели информации
		const closeInfoPanel = () => {
			selectedNodeInfo.value = null
			nodeRelationships.value = null
			if (cy) {
				cy.elements().unselect()
			}
		}

		// Наблюдатель за изменением layout
		watch(selectedLayout, () => {
			applyLayout()
		})

		// Наблюдатель за показом подписей
		watch(showLabels, () => {
			if (cy) {
				cy.style()
					.selector('edge')
					.style('label', function (ele) {
						return showLabels.value ? ele.data('label') : ''
					})
					.update()
			}
		})

		// Загрузка данных при монтировании компонента
		onMounted(() => {
			loadGraph()
		})

		// Очистка при размонтировании
		onUnmounted(() => {
			if (cy) {
				cy.destroy()
			}
		})

		return {
			error,
			selectedLayout,
			showLabels,
			selectedNodeInfo,
			nodeRelationships,
			refreshGraph,
			closeInfoPanel
		}
	}
}
</script>

<style scoped>
.graph-view {
	width: 100%;
	height: calc(100vh - 200px);
}

.view-header {
	margin-bottom: 1.5rem;
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
	gap: 1.5rem;
	align-items: center;
	flex-wrap: wrap;
	margin-bottom: 1.5rem;
	padding: 1rem;
	background: #f7fafc;
	border-radius: 8px;
}

.layout-controls,
.filter-controls {
	display: flex;
	align-items: center;
	gap: 0.5rem;
}

.layout-controls label,
.filter-controls label {
	color: #4a5568;
	font-weight: 500;
}

.layout-select {
	padding: 0.5rem;
	border: 1px solid #e2e8f0;
	border-radius: 4px;
	background: white;
}

.filter-controls label {
	display: flex;
	align-items: center;
	gap: 0.5rem;
	cursor: pointer;
}

.refresh-btn {
	background: #edf2f7;
	color: #4a5568;
	border: none;
	padding: 0.5rem 1rem;
	border-radius: 4px;
	font-weight: 500;
	cursor: pointer;
	transition: background 0.2s ease;
}

.refresh-btn:hover {
	background: #e2e8f0;
}

.list-link {
	background: #38b2ac;
	color: white;
	text-decoration: none;
	padding: 0.5rem 1rem;
	border-radius: 4px;
	font-weight: 500;
	transition: background 0.2s ease;
}

.list-link:hover {
	background: #319795;
}

.graph-container {
	height: calc(100% - 200px);
	position: relative;
}

.graph-wrapper {
	display: flex;
	gap: 1rem;
	height: 100%;
}

.cy-container {
	flex: 1;
	border: 1px solid #e2e8f0;
	border-radius: 8px;
	background: white;
}

.error {
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	height: 400px;
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

.retry-btn {
	background: #667eea;
	color: white;
	border: none;
	padding: 0.5rem 1rem;
	border-radius: 4px;
	margin-top: 1rem;
	cursor: pointer;
}

/* Панель информации */
.info-panel {
	position: fixed;
	right: 0;
	top: 200px;
	width: 350px;
	height: calc(100vh - 250px);
	background: white;
	border: 1px solid #e2e8f0;
	border-radius: 8px 0 0 8px;
	box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
	display: flex;
	flex-direction: column;
	z-index: 100;
}

.info-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 1rem;
	border-bottom: 1px solid #e2e8f0;
	background: #f7fafc;
}

.info-header h3 {
	margin: 0;
	font-size: 1.1rem;
	color: #2d3748;
}

.info-content {
	padding: 1rem;
	overflow-y: auto;
	flex: 1;
}

.info-content p {
	margin-bottom: 1rem;
	line-height: 1.5;
}

.relationships {
	margin-top: 1.5rem;
}

.relationship-section {
	margin-bottom: 1rem;
}

.relationship-section h4 {
	color: #4a5568;
	margin-bottom: 0.5rem;
	font-size: 0.9rem;
}

.relationship-section ul {
	list-style: none;
	padding-left: 1rem;
}

.relationship-section li {
	padding: 0.25rem 0;
	color: #718096;
	font-size: 0.85rem;
	position: relative;
}

.relationship-section li:before {
	content: "→";
	color: #667eea;
	position: absolute;
	left: -1rem;
}

.close-btn {
	background: none;
	border: none;
	font-size: 1.5rem;
	cursor: pointer;
	color: #718096;
}

@media (max-width: 768px) {
	.graph-view {
		height: auto;
	}

	.graph-wrapper {
		flex-direction: column;
	}

	.legend {
		width: 100%;
		order: -1;
	}

	.cy-container {
		min-height: 400px;
	}

	.info-panel {
		width: 100%;
		height: 300px;
		bottom: 0;
		top: auto;
		border-radius: 8px 8px 0 0;
	}
}
</style>
