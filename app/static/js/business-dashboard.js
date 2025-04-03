// JavaScript для дашборда бизнеса

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Обработка чекбоксов в задачах
    const taskCheckboxes = document.querySelectorAll('.form-check-input');
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            if (this.checked) {
                label.classList.add('text-decoration-line-through', 'text-muted');
                updateTaskProgress();
                
                // Здесь можно добавить AJAX запрос для сохранения состояния задачи на сервере
            } else {
                label.classList.remove('text-decoration-line-through', 'text-muted');
                updateTaskProgress();
            }
        });
    });

    // Функция обновления прогресса выполнения задач
    function updateTaskProgress() {
        const totalTasks = taskCheckboxes.length;
        if (totalTasks === 0) return;
        
        const completedTasks = document.querySelectorAll('.form-check-input:checked').length;
        const progressPercent = Math.round((completedTasks / totalTasks) * 100);
        
        // Здесь можно обновить прогресс-бар, если он есть на странице
        const taskProgressBar = document.querySelector('.task-progress .progress-bar');
        if (taskProgressBar) {
            taskProgressBar.style.width = `${progressPercent}%`;
            taskProgressBar.setAttribute('aria-valuenow', progressPercent);
            taskProgressBar.textContent = `${progressPercent}%`;
        }
    }

    // Инициализация графиков, если они есть
    const viewsChartElement = document.getElementById('viewsChart');
    if (viewsChartElement && typeof Chart !== 'undefined') {
        // Данные для графика (в реальном приложении должны приходить с сервера)
        const viewsData = {
            labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
            datasets: [{
                label: 'Просмотры профиля',
                data: [65, 59, 80, 81, 56, 155, 140],
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        };
        
        new Chart(viewsChartElement, {
            type: 'line',
            data: viewsData,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Просмотры профиля за неделю'
                    }
                }
            }
        });
    }

    // Обработка кнопки "Пригласить сотрудников"
    const inviteStaffBtn = document.querySelector('button.btn-outline-primary');
    if (inviteStaffBtn) {
        inviteStaffBtn.addEventListener('click', function() {
            // Здесь будет код для отображения модального окна приглашения
            // или перенаправление на страницу приглашения сотрудников
            
            // Пока просто показываем сообщение
            alert('Функция приглашения сотрудников будет доступна в ближайшее время!');
        });
    }

    // Форматирование дат в последних активностях
    const dateElements = document.querySelectorAll('.list-group-item small.text-muted');
    dateElements.forEach(element => {
        const text = element.textContent;
        if (text.includes(',')) {
            const parts = text.split(',');
            const dateTimeStr = parts[parts.length - 1].trim();
            
            // Проверяем, является ли строка датой
            const dateRegex = /\d{2}.\d{2}.\d{4}/;
            if (dateRegex.test(dateTimeStr)) {
                // Преобразуем дату в более читаемый формат, например "2 дня назад"
                const dateParts = dateTimeStr.split('.');
                if (dateParts.length === 3) {
                    const date = new Date(`${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`);
                    const now = new Date();
                    const diffTime = Math.abs(now - date);
                    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    
                    if (diffDays === 0) {
                        parts[parts.length - 1] = ' сегодня';
                    } else if (diffDays === 1) {
                        parts[parts.length - 1] = ' вчера';
                    } else if (diffDays < 7) {
                        parts[parts.length - 1] = ` ${diffDays} дня назад`;
                    }
                    
                    element.textContent = parts.join(',');
                }
            }
        }
    });

    // Обновление текущего года в футере
    const currentYearElements = document.querySelectorAll('.current-year');
    if (currentYearElements.length > 0) {
        const currentYear = new Date().getFullYear();
        currentYearElements.forEach(element => {
            element.textContent = currentYear;
        });
    }

    // Функция для форматирования цифр с разделителями тысяч
    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    // Анимация счетчиков статистики
    const counterElements = document.querySelectorAll('.card-title');
    counterElements.forEach(element => {
        const text = element.textContent.trim();
        if (/^\d+(\.\d+)?$/.test(text)) {
            const finalValue = parseFloat(text);
            let startValue = 0;
            const duration = 1000; // 1 секунда
            const startTime = performance.now();
            
            function updateCounter(currentTime) {
                const elapsedTime = currentTime - startTime;
                if (elapsedTime < duration) {
                    const progress = elapsedTime / duration;
                    const currentValue = progress * finalValue;
                    
                    if (Number.isInteger(finalValue)) {
                        element.textContent = formatNumber(Math.floor(currentValue));
                    } else {
                        element.textContent = finalValue.toFixed(1);
                    }
                    
                    requestAnimationFrame(updateCounter);
                } else {
                    element.textContent = Number.isInteger(finalValue) ? formatNumber(finalValue) : finalValue.toFixed(1);
                }
            }
            
            requestAnimationFrame(updateCounter);
        }
    });
}); 