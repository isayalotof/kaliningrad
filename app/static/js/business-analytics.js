/**
 * JavaScript функционал для аналитического модуля Qwerty.town
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Аналитический модуль Qwerty.town загружен');
    
    // Инициализация аналитических компонентов
    if (document.getElementById('analytics-dashboard')) {
        // Сначала инициализируем графики с пустыми данными
        initCharts();
        setupDateRangePicker();
        
        // Загружаем данные аналитики с сервера
        loadAnalyticsFromServer('30d');
    }
});

/**
 * Инициализация графиков
 */
function initCharts() {
    // График посещаемости по дням
    const visitorsCtx = document.getElementById('visitors-chart');
    if (visitorsCtx) {
        new Chart(visitorsCtx, {
            type: 'line',
            data: {
                labels: getDaysLabels(30),
                datasets: [{
                    label: 'Просмотры',
                    data: generateRandomData(30, 10, 150),
                    borderColor: '#4287f5',
                    backgroundColor: 'rgba(66, 135, 245, 0.1)',
                    tension: 0.3,
                    fill: true
                }, {
                    label: 'Действия',
                    data: generateRandomData(30, 5, 50),
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    legend: {
                        position: 'top'
                    }
                }
            }
        });
    }

    // График популярных услуг
    const servicesCtx = document.getElementById('services-chart');
    if (servicesCtx) {
        new Chart(servicesCtx, {
            type: 'bar',
            data: {
                labels: ['Услуга 1', 'Услуга 2', 'Услуга 3', 'Услуга 4', 'Услуга 5'],
                datasets: [{
                    label: 'Просмотры',
                    data: generateRandomData(5, 20, 100),
                    backgroundColor: 'rgba(66, 135, 245, 0.7)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                indexAxis: 'y'
            }
        });
    }

    // График источников трафика
    const sourcesCtx = document.getElementById('sources-chart');
    if (sourcesCtx) {
        new Chart(sourcesCtx, {
            type: 'doughnut',
            data: {
                labels: ['Поиск', 'Рекомендации', 'Прямые запросы', 'Другое'],
                datasets: [{
                    data: [45, 25, 20, 10],
                    backgroundColor: [
                        'rgba(66, 135, 245, 0.7)',
                        'rgba(40, 167, 69, 0.7)',
                        'rgba(255, 193, 7, 0.7)',
                        'rgba(108, 117, 125, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                }
            }
        });
    }

    // График конверсий
    const conversionCtx = document.getElementById('conversion-chart');
    if (conversionCtx) {
        new Chart(conversionCtx, {
            type: 'line',
            data: {
                labels: getDaysLabels(14),
                datasets: [{
                    label: 'Конверсия (%)',
                    data: generateRandomData(14, 1, 5),
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10
                    }
                }
            }
        });
    }
}

/**
 * Настройка выбора диапазона дат
 */
function setupDateRangePicker() {
    const dateRangePicker = document.getElementById('date-range-picker');
    
    if (dateRangePicker) {
        // В реальном приложении здесь будет инициализация компонента выбора дат
        dateRangePicker.addEventListener('change', function() {
            // Обновление данных при изменении диапазона дат
            const selectedRange = this.value;
            loadAnalyticsFromServer(selectedRange);
        });
    }
}

/**
 * Загрузка аналитических данных с сервера
 */
function loadAnalyticsFromServer(dateRange) {
    console.log('Загрузка аналитики с сервера, диапазон:', dateRange);
    
    // Показываем спиннеры загрузки
    document.getElementById('total-views').innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
    document.getElementById('total-actions').innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
    document.getElementById('conversion-rate').innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
    document.getElementById('avg-time').innerHTML = '<div class="spinner-border spinner-border-sm"></div>';
    
    // Отправляем запрос на сервер
    fetch(`/business/analytics/data/1?date_range=${dateRange}`)
        .then(response => response.json())
        .then(data => {
            console.log('Получены данные аналитики:', data);
            
            // Обновляем сводную информацию
            if (data.summary) {
                updateSummaryWidget('total-views', data.summary.total_views);
                updateSummaryWidget('total-actions', data.summary.total_actions);
                updateSummaryWidget('conversion-rate', data.summary.conversion_rate + '%');
                updateSummaryWidget('avg-time', data.summary.avg_time);
            }
            
            // Обновляем графики
            updateVisitorsChart(data.visitors_chart);
            updateServicesChart(data.services_chart);
            updateSourcesChart(data.sources_chart);
            updateConversionChart(data.conversion_chart);
        })
        .catch(error => {
            console.error('Ошибка при загрузке аналитики:', error);
            
            // В случае ошибки показываем демо-данные
            loadAnalyticsSummary();
            
            // Показываем сообщение об ошибке
            showNotification('Ошибка при загрузке аналитических данных. Показаны демонстрационные данные.', 'danger');
        });
}

/**
 * Обновление графика посещаемости
 */
function updateVisitorsChart(data) {
    if (!data) return;
    
    const visitorsChart = Chart.getChart('visitors-chart');
    if (visitorsChart) {
        if (data.labels) visitorsChart.data.labels = data.labels;
        
        if (data.datasets && data.datasets.length > 0) {
            visitorsChart.data.datasets.forEach((dataset, index) => {
                if (data.datasets[index] && data.datasets[index].data) {
                    dataset.data = data.datasets[index].data;
                }
            });
        }
        
        visitorsChart.update();
    }
}

/**
 * Обновление графика услуг
 */
function updateServicesChart(data) {
    if (!data) return;
    
    const servicesChart = Chart.getChart('services-chart');
    if (servicesChart) {
        if (data.labels) servicesChart.data.labels = data.labels;
        if (data.data) servicesChart.data.datasets[0].data = data.data;
        
        servicesChart.update();
    }
}

/**
 * Обновление графика источников трафика
 */
function updateSourcesChart(data) {
    if (!data) return;
    
    const sourcesChart = Chart.getChart('sources-chart');
    if (sourcesChart) {
        if (data.labels) sourcesChart.data.labels = data.labels;
        if (data.data) sourcesChart.data.datasets[0].data = data.data;
        
        sourcesChart.update();
    }
}

/**
 * Обновление графика конверсии
 */
function updateConversionChart(data) {
    if (!data) return;
    
    const conversionChart = Chart.getChart('conversion-chart');
    if (conversionChart) {
        if (data.labels) conversionChart.data.labels = data.labels;
        if (data.data) conversionChart.data.datasets[0].data = data.data;
        
        conversionChart.update();
    }
}

/**
 * Загрузка сводной информации по аналитике
 */
function loadAnalyticsSummary() {
    // В реальном приложении здесь будет загрузка данных с сервера
    // Временная реализация с случайными данными
    updateSummaryWidget('total-views', getRandomInt(500, 2000));
    updateSummaryWidget('total-actions', getRandomInt(50, 500));
    updateSummaryWidget('conversion-rate', (getRandomInt(2, 8) / 10).toFixed(1) + '%');
    updateSummaryWidget('avg-time', getRandomInt(2, 10) + ':' + getRandomInt(10, 59));
}

/**
 * Обновление данных графиков при изменении диапазона дат
 */
function updateChartsData(dateRange) {
    console.log('Обновление данных для диапазона:', dateRange);
    
    // В реальном приложении здесь будет запрос новых данных с сервера
    // и обновление графиков
    
    // Временная реализация - просто показываем уведомление
    showNotification('Данные обновлены для диапазона: ' + dateRange, 'success');
}

/**
 * Обновление значения в виджете сводной информации
 */
function updateSummaryWidget(id, value) {
    const widget = document.getElementById(id);
    if (widget) {
        widget.textContent = value;
        
        // Добавляем анимацию для счетчика
        widget.classList.add('counter-animation');
        setTimeout(() => {
            widget.classList.remove('counter-animation');
        }, 1000);
    }
}

/**
 * Формирование меток дней для осей графиков
 */
function getDaysLabels(count) {
    const labels = [];
    const today = new Date();
    
    for (let i = count - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(today.getDate() - i);
        labels.push(date.getDate() + '.' + (date.getMonth() + 1));
    }
    
    return labels;
}

/**
 * Генерация случайных данных для графиков
 */
function generateRandomData(count, min, max) {
    const data = [];
    for (let i = 0; i < count; i++) {
        data.push(getRandomInt(min, max));
    }
    return data;
}

/**
 * Получение случайного целого числа
 */
function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Отображение уведомления
 */
function showNotification(message, type = 'info', duration = 3000) {
    // Проверяем, существует ли контейнер для уведомлений
    let container = document.getElementById('notification-container');
    
    // Если нет, создаем его
    if (!container) {
        container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Создаем уведомление
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Добавляем в контейнер
    container.appendChild(notification);
    
    // Автоматически скрываем через указанное время
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

/**
 * Экспорт данных аналитики
 */
function exportAnalyticsData(format) {
    console.log('Экспорт данных в формате:', format);
    
    // В реальном приложении здесь будет логика экспорта данных
    // Временная реализация - просто показываем уведомление
    showNotification(`Данные успешно экспортированы в формате ${format.toUpperCase()}`, 'success');
} 