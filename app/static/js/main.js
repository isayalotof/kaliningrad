/**
 * Основной JavaScript-файл для Qwerty.town
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Qwerty.town - Бизнес-модуль загружен');
    
    // Установка текущего года в футере
    setCurrentYear();
    
    // Активация всех подсказок Bootstrap
    activateTooltips();
    
    // Добавление эффекта для карточек
    animateCards();
});

/**
 * Установка текущего года в футере
 */
function setCurrentYear() {
    const year = new Date().getFullYear();
    const yearElements = document.querySelectorAll('.current-year');
    yearElements.forEach(el => {
        el.textContent = year;
    });
}

/**
 * Активация подсказок Bootstrap
 */
function activateTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Добавление анимации для карточек
 */
function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
}

/**
 * Отправка AJAX-запроса
 * @param {string} url - URL для запроса
 * @param {string} method - Метод запроса (GET, POST, PUT, DELETE)
 * @param {Object} data - Данные для отправки
 * @param {Function} callback - Функция обратного вызова
 */
function sendRequest(url, method, data, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('Accept', 'application/json');
    
    xhr.onload = function() {
        if (this.status >= 200 && this.status < 300) {
            callback(null, JSON.parse(this.responseText));
        } else {
            callback(new Error(`${this.status}: ${this.statusText}`), null);
        }
    };
    
    xhr.onerror = function() {
        callback(new Error('Ошибка сети'), null);
    };
    
    xhr.send(data ? JSON.stringify(data) : null);
}

/**
 * Отображение уведомления
 * @param {string} message - Сообщение для отображения
 * @param {string} type - Тип уведомления (success, error, warning, info)
 * @param {number} duration - Длительность отображения в мс
 */
function showNotification(message, type = 'info', duration = 3000) {
    const notificationContainer = document.getElementById('notification-container');
    
    // Если контейнера нет, создаем его
    if (!notificationContainer) {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    // Создание элемента уведомления
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.role = 'alert';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Добавление уведомления в контейнер
    document.getElementById('notification-container').appendChild(notification);
    
    // Автоматическое закрытие через указанное время
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
} 