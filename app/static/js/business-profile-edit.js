// JavaScript для страницы редактирования профиля бизнеса

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Обработка переключателей рабочих дней
    const workdayToggles = document.querySelectorAll('.working-day-toggle');
    workdayToggles.forEach(toggle => {
        toggle.addEventListener('change', function() {
            const day = this.getAttribute('data-day');
            const hoursBlock = document.getElementById(`hours_${day}`);
            
            if (hoursBlock) {
                if (this.checked) {
                    hoursBlock.style.display = 'block';
                } else {
                    hoursBlock.style.display = 'none';
                }
            }
        });
    });

    // Копирование времени работы
    const copyTimeButtons = document.querySelectorAll('.copy-time');
    copyTimeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const day = this.getAttribute('data-day');
            const openTimeInput = document.getElementById(`${day}_open`);
            const closeTimeInput = document.getElementById(`${day}_close`);
            
            if (!openTimeInput || !closeTimeInput) return;
            
            // Создаем временное модальное окно для выбора, на какие дни скопировать
            const modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'copyTimeModal';
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-hidden', 'true');
            
            const days = {
                'monday': 'Понедельник',
                'tuesday': 'Вторник',
                'wednesday': 'Среда',
                'thursday': 'Четверг',
                'friday': 'Пятница',
                'saturday': 'Суббота',
                'sunday': 'Воскресенье'
            };
            
            let checkboxesHtml = '';
            for (const [key, value] of Object.entries(days)) {
                if (key !== day) {
                    checkboxesHtml += `
                        <div class="form-check">
                            <input class="form-check-input copy-day-checkbox" type="checkbox" id="copy_${key}" value="${key}">
                            <label class="form-check-label" for="copy_${key}">
                                ${value}
                            </label>
                        </div>
                    `;
                }
            }
            
            modal.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Копировать время</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <p>Выберите дни, на которые нужно скопировать время:</p>
                            ${checkboxesHtml}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>
                            <button type="button" class="btn btn-primary" id="confirmCopyTime">Копировать</button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            
            // Обработчик подтверждения копирования
            document.getElementById('confirmCopyTime').addEventListener('click', function() {
                const openTime = openTimeInput.value;
                const closeTime = closeTimeInput.value;
                
                const selectedDays = document.querySelectorAll('.copy-day-checkbox:checked');
                selectedDays.forEach(checkbox => {
                    const targetDay = checkbox.value;
                    const targetOpenInput = document.getElementById(`${targetDay}_open`);
                    const targetCloseInput = document.getElementById(`${targetDay}_close`);
                    
                    if (targetOpenInput && targetCloseInput) {
                        targetOpenInput.value = openTime;
                        targetCloseInput.value = closeTime;
                        
                        // Активируем переключатель рабочего дня
                        const targetToggle = document.getElementById(`workday_${targetDay}`);
                        if (targetToggle && !targetToggle.checked) {
                            targetToggle.checked = true;
                            const targetHoursBlock = document.getElementById(`hours_${targetDay}`);
                            if (targetHoursBlock) {
                                targetHoursBlock.style.display = 'block';
                            }
                        }
                    }
                });
                
                modalInstance.hide();
                
                // Удаляем модальное окно после закрытия
                modal.addEventListener('hidden.bs.modal', function() {
                    modal.remove();
                });
            });
            
            // Удаляем модальное окно при закрытии
            modal.addEventListener('hidden.bs.modal', function() {
                modal.remove();
            });
        });
    });

    // Обработка формы редактирования профиля
    const companyEditForm = document.getElementById('companyEditForm');
    if (companyEditForm) {
        companyEditForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Валидация полей перед отправкой
            if (!validateForm()) {
                return;
            }
            
            // Сбор данных формы
            const formData = new FormData(this);
            
            // Добавление данных о рабочих часах
            const workingHours = {};
            workdayToggles.forEach(toggle => {
                const day = toggle.getAttribute('data-day');
                workingHours[day] = {
                    is_working_day: toggle.checked,
                    open_time: document.getElementById(`${day}_open`).value,
                    close_time: document.getElementById(`${day}_close`).value
                };
            });
            
            formData.append('working_hours', JSON.stringify(workingHours));
            
            // Сбор данных о местоположении
            const location = {
                city: formData.get('city'),
                street: formData.get('street'),
                building: formData.get('building'),
                floor: formData.get('floor'),
                office: formData.get('office'),
                additional_info: formData.get('additional_info')
            };
            
            formData.append('location', JSON.stringify(location));
            
            // Сбор данных о социальных сетях
            const socialNetworks = {
                vk: formData.get('vk'),
                telegram: formData.get('telegram'),
                whatsapp: formData.get('whatsapp'),
                youtube: formData.get('youtube')
            };
            
            formData.append('social_networks', JSON.stringify(socialNetworks));
            
            // Имитация отправки данных на сервер (в реальном приложении здесь будет AJAX запрос)
            showSavingOverlay();
            
            // Имитация задержки для демонстрации
            setTimeout(() => {
                hideSavingOverlay();
                showSuccessMessage();
            }, 2000);
            
            // В реальном приложении здесь будет AJAX запрос к серверу
            /*
            fetch('/api/business/profile/update', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                hideSavingOverlay();
                if (data.success) {
                    showSuccessMessage();
                } else {
                    showErrorMessage(data.error);
                }
            })
            .catch(error => {
                hideSavingOverlay();
                showErrorMessage('Произошла ошибка при сохранении данных. Пожалуйста, попробуйте позже.');
                console.error('Ошибка:', error);
            });
            */
        });
    }

    // Функция валидации формы
    function validateForm() {
        // Получаем все обязательные поля
        const requiredFields = document.querySelectorAll('[required]');
        let isValid = true;
        
        // Сбрасываем предыдущие ошибки
        document.querySelectorAll('.is-invalid').forEach(field => {
            field.classList.remove('is-invalid');
        });
        
        // Проверяем каждое обязательное поле
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
                
                // Создаем сообщение об ошибке
                if (!field.nextElementSibling || !field.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Это поле обязательно для заполнения';
                    field.parentNode.insertBefore(feedback, field.nextSibling);
                }
            }
        });
        
        // Проверка email
        const emailField = document.getElementById('email');
        if (emailField && emailField.value.trim()) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(emailField.value.trim())) {
                emailField.classList.add('is-invalid');
                isValid = false;
                
                if (!emailField.nextElementSibling || !emailField.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Пожалуйста, введите корректный email';
                    emailField.parentNode.insertBefore(feedback, emailField.nextSibling);
                } else {
                    emailField.nextElementSibling.textContent = 'Пожалуйста, введите корректный email';
                }
            }
        }
        
        // Проверка телефона
        const phoneField = document.getElementById('phone');
        if (phoneField && phoneField.value.trim()) {
            const phoneRegex = /^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$/;
            if (!phoneRegex.test(phoneField.value.trim().replace(/\s/g, ''))) {
                phoneField.classList.add('is-invalid');
                isValid = false;
                
                if (!phoneField.nextElementSibling || !phoneField.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Пожалуйста, введите корректный номер телефона';
                    phoneField.parentNode.insertBefore(feedback, phoneField.nextSibling);
                } else {
                    phoneField.nextElementSibling.textContent = 'Пожалуйста, введите корректный номер телефона';
                }
            }
        }
        
        // Проверка веб-сайта
        const websiteField = document.getElementById('website');
        if (websiteField && websiteField.value.trim()) {
            const websiteRegex = /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/;
            if (!websiteRegex.test(websiteField.value.trim())) {
                websiteField.classList.add('is-invalid');
                isValid = false;
                
                if (!websiteField.nextElementSibling || !websiteField.nextElementSibling.classList.contains('invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Пожалуйста, введите корректный URL сайта';
                    websiteField.parentNode.insertBefore(feedback, websiteField.nextSibling);
                } else {
                    websiteField.nextElementSibling.textContent = 'Пожалуйста, введите корректный URL сайта';
                }
            }
        }
        
        return isValid;
    }

    // Функция отображения оверлея сохранения
    function showSavingOverlay() {
        const overlay = document.createElement('div');
        overlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center';
        overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        overlay.style.zIndex = '9999';
        overlay.id = 'savingOverlay';
        
        overlay.innerHTML = `
            <div class="bg-white p-4 rounded shadow-lg text-center">
                <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <h5>Сохранение изменений...</h5>
                <p class="text-muted mb-0">Пожалуйста, подождите</p>
            </div>
        `;
        
        document.body.appendChild(overlay);
    }

    // Функция скрытия оверлея сохранения
    function hideSavingOverlay() {
        const overlay = document.getElementById('savingOverlay');
        if (overlay) {
            overlay.remove();
        }
    }

    // Функция отображения сообщения об успешном сохранении
    function showSuccessMessage() {
        const toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-success text-white">
                    <strong class="me-auto">Успешно!</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    Изменения успешно сохранены.
                </div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Удаляем toast через 5 секунд
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    // Функция отображения сообщения об ошибке
    function showErrorMessage(message) {
        const toast = document.createElement('div');
        toast.className = 'position-fixed bottom-0 end-0 p-3';
        toast.style.zIndex = '9999';
        
        toast.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-header bg-danger text-white">
                    <strong class="me-auto">Ошибка!</strong>
                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
                <div class="toast-body">
                    ${message}
                </div>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Удаляем toast через 5 секунд
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    // Обновление текущего года в футере
    const currentYearElements = document.querySelectorAll('.current-year');
    if (currentYearElements.length > 0) {
        const currentYear = new Date().getFullYear();
        currentYearElements.forEach(element => {
            element.textContent = currentYear;
        });
    }

    // Обработка предпросмотра загружаемых изображений
    const imageInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const reader = new FileReader();
                
                // Найдем ближайший контейнер для предпросмотра
                let previewContainer = this.previousElementSibling;
                while (previewContainer && !previewContainer.classList.contains('mb-3')) {
                    previewContainer = previewContainer.previousElementSibling;
                }
                
                if (!previewContainer) return;
                
                reader.onload = function(e) {
                    // Проверяем, есть ли уже изображение
                    let imgElement = previewContainer.querySelector('img');
                    if (imgElement) {
                        // Обновляем существующее изображение
                        imgElement.src = e.target.result;
                    } else {
                        // Заменяем placeholder на изображение
                        previewContainer.innerHTML = `<img src="${e.target.result}" alt="Превью" class="img-thumbnail" style="max-height: 150px;">`;
                    }
                };
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    });
}); 