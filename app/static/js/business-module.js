/**
 * JavaScript функционал для бизнес-модуля Qwerty.town
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Бизнес-модуль Qwerty.town загружен');
    
    // Инициализация компонентов
    initBusinessTypeSelection();
    initNavigationControls();
    initMobileAdaptation();
    
    // Установка текущего года в футере
    setCurrentYear();
    
    // Инициализация формы регистрации бизнеса
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        initializeRegistrationForm();
        
        // Проверяем, есть ли сохраненный черновик
        try {
            if (localStorage.getItem('business_registration_draft')) {
                // Показываем уведомление о наличии черновика
                const restoreBtn = document.createElement('button');
                restoreBtn.className = 'btn btn-outline-primary btn-sm mt-2';
                restoreBtn.innerHTML = 'Восстановить данные из черновика';
                restoreBtn.addEventListener('click', restoreFormDraft);
                
                const restoreNotice = document.createElement('div');
                restoreNotice.className = 'alert alert-info mt-3';
                restoreNotice.innerHTML = 'У вас есть несохраненные данные формы. ';
                restoreNotice.appendChild(restoreBtn);
                
                const formHeader = document.querySelector('.form-header');
                if (formHeader) {
                    formHeader.parentNode.insertBefore(restoreNotice, formHeader.nextSibling);
                } else {
                    registrationForm.prepend(restoreNotice);
                }
            }
        } catch (e) {
            console.error('Ошибка при проверке наличия черновика:', e);
        }
    }
    
    // Проверяем видимость страницы
    if (document.visibilityState === "visible") {
        console.log("Страница загружена и видима");
    } else {
        console.log("Страница загружена, но не видима");
    }
    
    // Инициализация кнопки завершения регистрации
    const completeRegistrationBtn = document.getElementById('complete-registration');
    if (completeRegistrationBtn) {
        completeRegistrationBtn.addEventListener('click', submitRegistrationForm);
    }
    
    // Инициализация обработчиков дней недели для расписания
    const dayCheckboxes = document.querySelectorAll('[id$="-is-open"]');
    dayCheckboxes.forEach(checkbox => {
        const day = checkbox.id.replace('-is-open', '');
        const openTimeInput = document.getElementById(`${day}-open-time`);
        const closeTimeInput = document.getElementById(`${day}-close-time`);
        
        // Первоначальная настройка состояния полей времени
        if (openTimeInput && closeTimeInput) {
            openTimeInput.disabled = !checkbox.checked;
            closeTimeInput.disabled = !checkbox.checked;
        }
        
        // Обработчик изменения состояния чекбокса
        checkbox.addEventListener('change', function() {
            if (openTimeInput && closeTimeInput) {
                openTimeInput.disabled = !this.checked;
                closeTimeInput.disabled = !this.checked;
            }
        });
    });
    
    // Инициализация карты, если она есть на странице
    if (document.getElementById('location-map')) {
        initMap();
    }
    
    initSidebar();
    
    // Инициализируем первый шаг с прогрессом
    updateProgress(15);
    
    // Привязываем обработчики к кнопкам навигации
    const nextButtons = document.querySelectorAll('.next-step');
    nextButtons.forEach(button => {
        button.addEventListener('click', () => {
            const nextStep = button.getAttribute('data-next');
            if (nextStep) {
                goToFormStep(nextStep);
            }
        });
    });
    
    const prevButtons = document.querySelectorAll('.prev-step');
    prevButtons.forEach(button => {
        button.addEventListener('click', () => {
            const prevStep = button.getAttribute('data-prev');
            if (prevStep) {
                goToFormStep(prevStep);
            }
        });
    });
    
    // Активируем кнопки следующего шага при выборе типа бизнеса
    const businessTypeCards = document.querySelectorAll('.business-type-card');
    const nextButton = document.querySelector('.next-step[data-next="contact-info"]');
    
    businessTypeCards.forEach(card => {
        card.addEventListener('click', function() {
            // Активируем кнопку Далее
            if (nextButton) {
                nextButton.disabled = false;
                console.log('Кнопка "Далее" активирована после выбора типа бизнеса');
            }
            
            // Выделяем выбранную карточку
            businessTypeCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            // Устанавливаем значение скрытого поля
            const radioInput = this.querySelector('input[type="radio"]');
            if (radioInput) {
                radioInput.checked = true;
            }
        });
    });
    
    // Проверяем выбран ли уже тип бизнеса
    const selectedRadio = document.querySelector('input[name="business_type"]:checked');
    if (selectedRadio) {
        const selectedType = selectedRadio.value;
        const selectedCard = document.querySelector(`.business-type-card[data-type="${selectedType}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
            if (nextButton) {
                nextButton.disabled = false;
            }
        }
    }
});

/**
 * Установка текущего года в футере
 */
function setCurrentYear() {
    const yearElements = document.querySelectorAll('.current-year');
    const currentYear = new Date().getFullYear();
    
    yearElements.forEach(element => {
        element.textContent = currentYear;
    });
}

/**
 * Инициализация выбора типа бизнеса
 */
function initBusinessTypeSelection() {
    console.log('Инициализация выбора типа бизнеса...');
    
    const typeCards = document.querySelectorAll('.business-type-card');
    
    if (typeCards.length === 0) {
        console.warn('Элементы выбора типа бизнеса не найдены');
        return;
    }
    
    // Обработчик выбора типа бизнеса
    typeCards.forEach(card => {
        card.addEventListener('click', function(e) {
            e.preventDefault(); // Предотвращаем стандартное поведение ссылки
            
            // Удаляем класс selected у всех карточек
            typeCards.forEach(c => c.classList.remove('selected'));
            
            // Добавляем класс selected к выбранной карточке
            this.classList.add('selected');
            
            // Находим и выбираем соответствующий радио-инпут
            const businessType = this.getAttribute('data-type');
            const radioInput = document.querySelector(`input[name="business_type"][value="${businessType}"]`);
            
            if (radioInput) {
                // Отмечаем выбранный радио-инпут
                radioInput.checked = true;
                
                // Дополнительно убеждаемся, что значение выбрано
                const allRadios = document.querySelectorAll('input[name="business_type"]');
                allRadios.forEach(radio => {
                    radio.checked = (radio === radioInput);
                });
                
                // Активируем скрытое поле для бизнес-типа
                const hiddenInput = document.querySelector('input[name="business_type_hidden"]');
                if (hiddenInput) {
                    hiddenInput.value = businessType;
                } else {
                    // Если скрытого поля нет, создаем его
                    const newHiddenInput = document.createElement('input');
                    newHiddenInput.type = 'hidden';
                    newHiddenInput.name = 'business_type_hidden';
                    newHiddenInput.value = businessType;
                    document.getElementById('registration-form').appendChild(newHiddenInput);
                }
            } else {
                console.error(`Радио-инпут для типа бизнеса "${businessType}" не найден`);
                
                // Создаем скрытое поле для типа бизнеса, если радио не найден
                const form = document.getElementById('registration-form');
                if (form) {
                    let hiddenInput = document.querySelector('input[name="business_type"]');
                    if (!hiddenInput) {
                        hiddenInput = document.createElement('input');
                        hiddenInput.type = 'hidden';
                        hiddenInput.name = 'business_type';
                        form.appendChild(hiddenInput);
                    }
                    hiddenInput.value = businessType;
                }
            }
            
            // Обновляем превью в зависимости от выбранного типа
            updatePreview(businessType);
            
            // Активируем кнопку "Далее"
            const nextButton = document.querySelector('.next-step[data-next="contact-info"]');
            if (nextButton) {
                nextButton.disabled = false;
            }
        });
    });
    
    // Проверяем, есть ли уже выбранный тип
    const selectedRadio = document.querySelector('input[name="business_type"]:checked');
    if (selectedRadio) {
        const selectedType = selectedRadio.value;
        const selectedCard = document.querySelector(`.business-type-card[data-type="${selectedType}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
            updatePreview(selectedType);
        }
    }
}

/**
 * Переход к определенному шагу формы
 */
function goToFormStep(stepId) {
    // Скрываем все шаги
    const formSteps = document.querySelectorAll('.form-step');
    formSteps.forEach(step => {
        step.style.display = 'none';
    });
    
    // Показываем нужный шаг
    const targetStep = document.getElementById(stepId + '-form');
    if (targetStep) {
        targetStep.style.display = 'block';
    }
    
    // Обновляем активный пункт в меню
    updateActiveStep(stepId);
    
    // Обновляем прогресс
    const stepsProgress = {
        'business-type': 15,
        'contact-info': 30,
        'location': 45,
        'working-hours': 60,
        'services': 75,
        'media': 90,
        'completion': 100
    };
    
    updateProgress(stepsProgress[stepId] || 0);
    
    // Прокручиваем к началу формы
    window.scrollTo(0, 0);
}

/**
 * Загрузка формы для определенного шага
 */
function loadFormStep(step) {
    // Эта функция больше не нужна, так как все формы уже есть в HTML
    // Остается только для совместимости
    console.log('Функция loadFormStep устарела. Используйте goToFormStep.');
}

/**
 * Инициализация обработчиков событий для формы
 */
function initFormHandlers(step) {
    console.log('Инициализация обработчиков для шага:', step);
    
    // Обновляем предпросмотр при изменении данных формы
    const formStep = document.getElementById(`${step}-form`);
    if (!formStep) {
        // Пытаемся найти форму по альтернативному формату ID
        formStep = document.querySelector(`[data-step="${step}"]`);
        if (!formStep) {
            console.warn(`Форма для шага ${step} не найдена`);
            return;
        }
    }
    
    const formInputs = formStep.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        // Удаляем старые обработчики, чтобы избежать дублирования
        input.removeEventListener('change', updatePreviewFromForm);
        input.removeEventListener('input', updatePreviewFromForm);
        
        // Добавляем новые обработчики
        input.addEventListener('change', updatePreviewFromForm);
        if (input.type === 'text' || input.type === 'email' || input.type === 'tel' || input.tagName === 'TEXTAREA') {
            input.addEventListener('input', updatePreviewFromForm);
        }
    });
    
    // Инициализация кнопки завершения регистрации
    if (step === 'finish') {
        const completeButton = document.querySelector('#complete-registration');
        if (completeButton) {
            // Удаляем старые обработчики
            const newButton = completeButton.cloneNode(true);
            if (completeButton.parentNode) {
                completeButton.parentNode.replaceChild(newButton, completeButton);
            }
            
            // Добавляем новый обработчик
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                submitRegistrationForm();
            });
        }
    }
}

/**
 * Обновление предпросмотра профиля
 */
function updatePreview(businessType) {
    const previewContainer = document.querySelector('.registration-preview');
    
    // Временная реализация - будет заменена на реальный предпросмотр
    let previewContent = '';
    
    switch(businessType) {
        case 'restaurant':
            previewContent = `
                <div class="preview-content">
                    <i class="bi bi-cup-hot display-1 text-primary"></i>
                    <h3>Ресторан / Кафе</h3>
                    <p>Предпросмотр профиля ресторана</p>
                    <div class="preview-details">
                        <p><strong>Название:</strong> <span id="preview-name">Не указано</span></p>
                        <p><strong>Адрес:</strong> <span id="preview-address">Не указан</span></p>
                        <p><strong>Время работы:</strong> <span id="preview-hours">Не указано</span></p>
                    </div>
                </div>
            `;
            break;
        case 'beauty':
            previewContent = `
                <div class="preview-content">
                    <i class="bi bi-scissors display-1 text-primary"></i>
                    <h3>Салон красоты</h3>
                    <p>Предпросмотр профиля салона красоты</p>
                    <div class="preview-details">
                        <p><strong>Название:</strong> <span id="preview-name">Не указано</span></p>
                        <p><strong>Адрес:</strong> <span id="preview-address">Не указан</span></p>
                        <p><strong>Время работы:</strong> <span id="preview-hours">Не указано</span></p>
                    </div>
                </div>
            `;
            break;
        // Другие типы бизнеса...
        default:
            previewContent = `
                <div class="preview-placeholder">
                    <i class="bi bi-shop display-1"></i>
                    <h3>Предпросмотр профиля</h3>
                    <p>Выберите тип бизнеса для просмотра</p>
                </div>
            `;
    }
    
    previewContainer.innerHTML = previewContent;
}

/**
 * Обновление предпросмотра на основе данных формы
 */
function updatePreviewFromForm() {
    // Получаем данные из текущей формы
    const nameInput = document.querySelector('#business-name');
    const addressInput = document.querySelector('#business-address');
    const hoursInput = document.querySelector('#business-hours');
    
    // Обновляем предпросмотр, если элементы существуют
    if (nameInput) {
        const previewName = document.querySelector('#preview-name');
        if (previewName) previewName.textContent = nameInput.value || 'Не указано';
    }
    
    if (addressInput) {
        const previewAddress = document.querySelector('#preview-address');
        if (previewAddress) previewAddress.textContent = addressInput.value || 'Не указан';
    }
    
    if (hoursInput) {
        const previewHours = document.querySelector('#preview-hours');
        if (previewHours) previewHours.textContent = hoursInput.value || 'Не указано';
    }
}

/**
 * Обновление индикатора прогресса
 */
function updateProgress(percent) {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        progressBar.style.width = percent + '%';
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.textContent = percent + '%';
    }
}

/**
 * Инициализация элементов навигации
 */
function initNavigationControls() {
    console.log('Инициализация элементов навигации...');
    
    try {
        // Инициализация кнопок "Далее"
        const nextButtons = document.querySelectorAll('.next-step');
        nextButtons.forEach(button => {
            // Удаляем старые обработчики, чтобы избежать дублирования
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                const nextStep = this.getAttribute('data-next');
                if (nextStep) {
                    // Валидируем текущий шаг перед переходом к следующему
                    const currentStep = this.closest('.form-step').getAttribute('data-step') || 
                                       this.closest('[data-step]').getAttribute('data-step') ||
                                       this.closest('.form-step').id.replace('-form', '');
                    
                    if (validateFormStep(currentStep)) {
                        goToFormStep(nextStep);
                    }
                }
            });
        });
        
        // Инициализация кнопок "Назад"
        const prevButtons = document.querySelectorAll('.prev-step');
        prevButtons.forEach(button => {
            // Удаляем старые обработчики, чтобы избежать дублирования
            const newButton = button.cloneNode(true);
            if (button.parentNode) {
                button.parentNode.replaceChild(newButton, button);
            }
            
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                const prevStep = this.getAttribute('data-prev');
                if (prevStep) {
                    goToFormStep(prevStep);
                }
            });
        });
        
        // Инициализация пунктов меню
        const listItems = document.querySelectorAll('.list-item');
        listItems.forEach(item => {
            // Удаляем старые обработчики, чтобы избежать дублирования
            const newItem = item.cloneNode(true);
            if (item.parentNode) {
                item.parentNode.replaceChild(newItem, item);
            }
            
            newItem.addEventListener('click', function(e) {
                e.preventDefault();
                const step = this.getAttribute('data-step');
                if (step) {
                    goToFormStep(step);
                }
            });
        });
    } catch (e) {
        console.error('Ошибка при инициализации элементов навигации:', e);
    }
}

/**
 * Валидация определенного шага формы
 */
function validateFormStep(step) {
    console.log('Валидация шага формы:', step);
    
    // По умолчанию считаем шаг валидным
    let isValid = true;
    
    try {
        switch(step) {
            case 'business-type':
                // Проверяем, выбран ли тип бизнеса
                const selectedType = document.querySelector('input[name="business_type"]:checked');
                if (!selectedType) {
                    showNotification('warning', 'Пожалуйста, выберите тип бизнеса');
                    isValid = false;
                }
                break;
                
            case 'contact-info':
                // Проверяем обязательные поля контактной информации
                const nameInput = document.querySelector('input[name="name"]');
                if (!nameInput || !nameInput.value.trim()) {
                    showNotification('warning', 'Пожалуйста, укажите название бизнеса');
                    isValid = false;
                }
                
                // Проверяем email если он указан
                const emailInput = document.querySelector('input[name="contact_email"]');
                if (emailInput && emailInput.value.trim() && !isValidEmail(emailInput.value)) {
                    showNotification('warning', 'Пожалуйста, укажите корректный email');
                    isValid = false;
                }
                break;
                
            case 'location':
                // Проверка адреса не обязательна, но если указан город, должен быть и адрес
                const cityInput = document.querySelector('input[name="city"]');
                const streetInput = document.querySelector('input[name="street"]');
                
                if (cityInput && cityInput.value.trim() && (!streetInput || !streetInput.value.trim())) {
                    showNotification('warning', 'Пожалуйста, укажите адрес компании, если указан город');
                    isValid = false;
                }
                break;
                
            case 'working-hours':
                // Проверяем корректность формата времени
                const timeInputs = document.querySelectorAll('input[type="time"]');
                timeInputs.forEach(input => {
                    if (input.value && !isValidTime(input.value)) {
                        showNotification('warning', 'Время должно быть в формате ЧЧ:ММ');
                        isValid = false;
                    }
                });
                break;
                
            case 'services':
                // Проверка услуг: если есть хотя бы одна услуга, она должна иметь название
                const serviceNames = document.querySelectorAll('.service-name');
                const hasServices = serviceNames.length > 0;
                let hasValidService = false;
                
                serviceNames.forEach(input => {
                    if (input.value.trim()) {
                        hasValidService = true;
                    }
                });
                
                if (hasServices && !hasValidService) {
                    showNotification('warning', 'Пожалуйста, укажите название хотя бы для одной услуги или удалите пустые услуги');
                    isValid = false;
                }
                break;
                
            case 'media':
                // Проверяем размер и тип загружаемых файлов
                const logoInput = document.querySelector('input[name="logo"]');
                if (logoInput && logoInput.files.length > 0) {
                    const file = logoInput.files[0];
                    
                    if (file.size > 10 * 1024 * 1024) { // 10 MB
                        showNotification('warning', 'Размер логотипа не должен превышать 10 МБ');
                        isValid = false;
                    }
                    
                    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                    if (!allowedTypes.includes(file.type)) {
                        showNotification('warning', 'Логотип должен быть в формате JPG, PNG или GIF');
                        isValid = false;
                    }
                }
                
                const photosInput = document.querySelector('input[name="photos"]');
                if (photosInput && photosInput.files.length > 0) {
                    const maxPhotos = 5;
                    if (photosInput.files.length > maxPhotos) {
                        showNotification('warning', `Максимальное количество фотографий: ${maxPhotos}`);
                        // Не блокируем переход, просто предупреждаем
                    }
                    
                    // Проверяем каждое фото
                    for (let i = 0; i < Math.min(photosInput.files.length, maxPhotos); i++) {
                        const file = photosInput.files[i];
                        
                        if (file.size > 15 * 1024 * 1024) { // 15 MB
                            showNotification('warning', `Размер фото #${i+1} не должен превышать 15 МБ`);
                            isValid = false;
                            break;
                        }
                        
                        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                        if (!allowedTypes.includes(file.type)) {
                            showNotification('warning', `Фото #${i+1} должно быть в формате JPG, PNG или GIF`);
                            isValid = false;
                            break;
                        }
                    }
                }
                break;
                
            case 'finish':
                // Финальная проверка всей формы
                // Проверяем наличие типа бизнеса и названия
                const finalBusinessType = document.querySelector('input[name="business_type"]:checked');
                const finalName = document.querySelector('input[name="name"]');
                
                if (!finalBusinessType) {
                    showNotification('warning', 'Пожалуйста, выберите тип бизнеса');
                    goToFormStep('business-type');
                    isValid = false;
                } else if (!finalName || !finalName.value.trim()) {
                    showNotification('warning', 'Пожалуйста, укажите название бизнеса');
                    goToFormStep('contact-info');
                    isValid = false;
                }
                break;
                
            default:
                // Для остальных шагов особой валидации нет
                break;
        }
    } catch (e) {
        console.error('Ошибка при валидации шага формы:', e);
        // В случае ошибки не блокируем переход
        isValid = true;
    }
    
    return isValid;
}

/**
 * Проверка валидности email
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Проверка валидности времени
 */
function isValidTime(time) {
    const re = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/;
    return re.test(time);
}

/**
 * Инициализация формы регистрации
 */
function initializeRegistrationForm() {
    console.log('Инициализация формы регистрации...');
    
    try {
        // Проверяем, не является ли это повторной инициализацией
        if (window.formInitialized) {
            console.log('Форма уже была инициализирована');
            return;
        }
        
        // Настраиваем загрузку изображений
        setupImageUploads();
        
        // Настраиваем менеджер услуг
        setupServicesManager();
        
        // Настраиваем менеджер рабочих часов
        setupWorkingHoursManager();
        
        // Настраиваем валидацию формы
        setupFormValidation();
        
        // Инициализируем начальный шаг формы
        goToFormStep('business-type');
        
        window.formInitialized = true;
    } catch (e) {
        console.error('Ошибка при инициализации формы регистрации:', e);
    }
}

/**
 * Настройка валидации формы
 */
function setupFormValidation() {
    console.log('Настройка валидации формы...');
    
    // Настраиваем валидацию полей при вводе
    const form = document.getElementById('registration-form');
    if (!form) return;
    
    // Находим все поля с атрибутом required
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        field.addEventListener('blur', function() {
            validateField(this);
        });
    });
    
    // Добавляем валидацию email
    const emailFields = form.querySelectorAll('input[type="email"], input[name*="email"]');
    emailFields.forEach(field => {
        field.addEventListener('blur', function() {
            if (this.value.trim() && !isValidEmail(this.value)) {
                this.classList.add('is-invalid');
                
                // Добавляем сообщение об ошибке, если его еще нет
                let feedback = this.nextElementSibling;
                if (!feedback || !feedback.classList.contains('invalid-feedback')) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'Пожалуйста, введите корректный email';
                    this.parentNode.insertBefore(feedback, this.nextSibling);
                }
            } else {
                this.classList.remove('is-invalid');
                
                // Удаляем сообщение об ошибке
                const feedback = this.nextElementSibling;
                if (feedback && feedback.classList.contains('invalid-feedback')) {
                    feedback.remove();
                }
            }
        });
    });
}

/**
 * Валидация отдельного поля
 */
function validateField(field) {
    if (field.hasAttribute('required') && !field.value.trim()) {
        field.classList.add('is-invalid');
        
        // Добавляем сообщение об ошибке, если его еще нет
        let feedback = field.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = 'Это поле обязательно для заполнения';
            field.parentNode.insertBefore(feedback, field.nextSibling);
        }
        
        return false;
    } else {
        field.classList.remove('is-invalid');
        
        // Удаляем сообщение об ошибке
        const feedback = field.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.remove();
        }
        
        return true;
    }
}

/**
 * Настройка загрузки изображений
 */
function setupImageUploads() {
    console.log('Настройка загрузки изображений...');
    
    // Предпросмотр логотипа
    const logoUpload = document.getElementById('logo-upload');
    const logoPreview = document.getElementById('logo-preview');
    
    if (logoUpload && logoPreview) {
        logoUpload.addEventListener('change', function(e) {
            if (this.files && this.files[0]) {
                logoPreview.innerHTML = '';
                
                const img = document.createElement('img');
                img.classList.add('img-thumbnail', 'logo-preview-img');
                img.file = this.files[0];
                logoPreview.appendChild(img);
                
                const reader = new FileReader();
                reader.onload = (function(aImg) {
                    return function(e) {
                        aImg.src = e.target.result;
                    };
                })(img);
                
                reader.readAsDataURL(this.files[0]);
            }
        });
    }
    
    // Предпросмотр фотографий
    const photosUpload = document.getElementById('photos-upload');
    const photosPreview = document.getElementById('photos-preview');
    
    if (photosUpload && photosPreview) {
        photosUpload.addEventListener('change', function(e) {
            if (this.files && this.files.length > 0) {
                photosPreview.innerHTML = '';
                
                const maxFiles = Math.min(5, this.files.length);
                
                for (let i = 0; i < maxFiles; i++) {
                    const file = this.files[i];
                    
                    const col = document.createElement('div');
                    col.classList.add('col-md-4', 'mb-2');
                    
                    const img = document.createElement('img');
                    img.classList.add('img-thumbnail', 'photo-preview-img');
                    img.file = file;
                    
                    col.appendChild(img);
                    photosPreview.appendChild(col);
                    
                    const reader = new FileReader();
                    reader.onload = (function(aImg) {
                        return function(e) {
                            aImg.src = e.target.result;
                        };
                    })(img);
                    
                    reader.readAsDataURL(file);
                }
                
                if (this.files.length > 5) {
                    const notice = document.createElement('div');
                    notice.classList.add('col-12', 'text-muted', 'small', 'mt-2');
                    notice.textContent = `Выбрано ${this.files.length} файлов. Будут загружены только первые 5.`;
                    photosPreview.appendChild(notice);
                }
            }
        });
    }
}

/**
 * Настройка менеджера услуг
 */
function setupServicesManager() {
    console.log('Настройка менеджера услуг...');
    
    const servicesContainer = document.getElementById('services-container');
    const addServiceBtn = document.getElementById('add-service-btn');
    
    if (!servicesContainer || !addServiceBtn) return;
    
    // Счетчик услуг для создания уникальных ID
    let serviceCounter = 0;
    
    // Функция добавления новой услуги
    function addService() {
        const serviceId = `service-${serviceCounter}`;
        
        const serviceCard = document.createElement('div');
        serviceCard.classList.add('card', 'mb-3', 'service-item');
        serviceCard.setAttribute('data-service-id', serviceId);
        
        serviceCard.innerHTML = `
            <div class="card-body">
                <div class="row">
                    <div class="col-md-5 mb-2">
                        <label for="${serviceId}-name" class="form-label">Название услуги</label>
                        <input type="text" class="form-control service-name" id="${serviceId}-name" placeholder="Например: Стрижка" required>
                    </div>
                    <div class="col-md-3 mb-2">
                        <label for="${serviceId}-price" class="form-label">Цена, ₽</label>
                        <input type="number" class="form-control service-price" id="${serviceId}-price" placeholder="1000" min="0">
                    </div>
                    <div class="col-md-3 mb-2">
                        <label for="${serviceId}-duration" class="form-label">Длительность, мин</label>
                        <input type="number" class="form-control service-duration" id="${serviceId}-duration" placeholder="60" min="1">
                    </div>
                    <div class="col-md-1 d-flex align-items-end justify-content-end mb-2">
                        <button type="button" class="btn btn-outline-danger btn-sm remove-service" title="Удалить услугу">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="row">
                    <div class="col-12">
                        <label for="${serviceId}-description" class="form-label">Описание услуги</label>
                        <textarea class="form-control service-description" id="${serviceId}-description" rows="2"></textarea>
                    </div>
                </div>
            </div>
        `;
        
        servicesContainer.appendChild(serviceCard);
        
        // Добавляем обработчик для кнопки удаления
        const removeBtn = serviceCard.querySelector('.remove-service');
        if (removeBtn) {
            removeBtn.addEventListener('click', function() {
                serviceCard.remove();
            });
        }
        
        serviceCounter++;
    }
    
    // Добавляем обработчик для кнопки "Добавить услугу"
    addServiceBtn.addEventListener('click', addService);
    
    // Добавляем первую услугу по умолчанию
    addService();
}

/**
 * Получение данных об услугах
 */
function getServicesData() {
    console.log('Сбор данных об услугах...');
    
    const services = [];
    const serviceElements = document.querySelectorAll('.service-item');
    
    serviceElements.forEach(element => {
        const nameInput = element.querySelector('.service-name');
        const priceInput = element.querySelector('.service-price');
        const durationInput = element.querySelector('.service-duration');
        const descriptionInput = element.querySelector('.service-description');
        
        if (nameInput && nameInput.value.trim()) {
            const service = {
                name: nameInput.value.trim(),
                price: priceInput ? parseFloat(priceInput.value) || 0 : 0,
                duration: durationInput ? parseInt(durationInput.value) || 30 : 30,
                description: descriptionInput ? descriptionInput.value.trim() : ''
            };
            
            services.push(service);
        }
    });
    
    console.log('Данные об услугах:', services);
    return services;
}

/**
 * Настройка менеджера рабочих часов
 */
function setupWorkingHoursManager() {
    // Обработчики изменения селекторов типа расписания
    const scheduleTypeSelectors = document.querySelectorAll('input[name="schedule-type"]');
    const everydaySchedule = document.getElementById('everyday-schedule');
    const weekdaySchedule = document.getElementById('weekday-schedule');
    
    if (scheduleTypeSelectors.length && everydaySchedule && weekdaySchedule) {
        scheduleTypeSelectors.forEach(selector => {
            selector.addEventListener('change', function() {
                if (this.value === 'everyday') {
                    everydaySchedule.style.display = 'block';
                    weekdaySchedule.style.display = 'none';
                } else {
                    everydaySchedule.style.display = 'none';
                    weekdaySchedule.style.display = 'block';
                }
            });
        });
    }
}

/**
 * Функция для получения данных о рабочих часах из формы
 * @returns {Object} Объект с данными о рабочих часах
 */
function getWorkingHoursData() {
    const workingHours = {};
    const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
    const daysRu = {
        'monday': 'Понедельник',
        'tuesday': 'Вторник',
        'wednesday': 'Среда',
        'thursday': 'Четверг',
        'friday': 'Пятница',
        'saturday': 'Суббота',
        'sunday': 'Воскресенье'
    };
    
    // Проверяем, какой тип расписания выбран
    const scheduleType = document.querySelector('input[name="schedule-type"]:checked')?.value || 'everyday';
    
    if (scheduleType === 'everyday') {
        // Одинаковое расписание для всех дней
        const openTime = document.getElementById('everyday-open-time')?.value || '09:00';
        const closeTime = document.getElementById('everyday-close-time')?.value || '18:00';
        
        // Устанавливаем одинаковые часы для всех дней, кроме воскресенья
        days.forEach(day => {
            const isWorking = day !== 'sunday'; // По умолчанию воскресенье - выходной
            workingHours[day] = {
                from: openTime,
                to: closeTime,
                isWorking: isWorking,
                humanReadableDay: daysRu[day]
            };
        });
    } else {
        // Индивидуальное расписание по дням
        days.forEach(day => {
            const isOpenCheckbox = document.getElementById(`${day}-is-open`);
            const isWorking = isOpenCheckbox ? isOpenCheckbox.checked : (day !== 'sunday');
            
            const openTimeInput = document.getElementById(`${day}-open-time`);
            const closeTimeInput = document.getElementById(`${day}-close-time`);
            
            const openTime = (openTimeInput && isWorking) ? openTimeInput.value : '';
            const closeTime = (closeTimeInput && isWorking) ? closeTimeInput.value : '';
            
            workingHours[day] = {
                from: openTime,
                to: closeTime,
                isWorking: isWorking,
                humanReadableDay: daysRu[day]
            };
        });
    }
    
    return workingHours;
}

/**
 * Инициализация карты
 */
function initMap() {
    // В реальном приложении здесь будет инициализация карты с использованием API
    console.log('Инициализация карты');
}

/**
 * Показать индикатор загрузки
 */
function showLoadingIndicator() {
    console.log('Показываем индикатор загрузки...');
    
    // Проверяем, существует ли уже индикатор загрузки
    let loadingIndicator = document.querySelector('.loading-indicator');
    
    // Если нет, создаем новый
    if (!loadingIndicator) {
        loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'loading-indicator';
        
        // Добавляем спиннер Bootstrap
        let spinner = document.createElement('div');
        spinner.className = 'spinner-border text-light mb-3';
        spinner.setAttribute('role', 'status');
        
        let spinnerText = document.createElement('span');
        spinnerText.className = 'visually-hidden';
        spinnerText.textContent = 'Загрузка...';
        
        spinner.appendChild(spinnerText);
        loadingIndicator.appendChild(spinner);
        
        // Добавляем текстовое сообщение
        let message = document.createElement('div');
        message.textContent = 'Пожалуйста, подождите...';
        loadingIndicator.appendChild(message);
        
        // Добавляем индикатор в тело документа
        document.body.appendChild(loadingIndicator);
    } else {
        // Если индикатор уже существует, просто показываем его
        loadingIndicator.style.display = 'flex';
    }
}

/**
 * Скрыть индикатор загрузки
 */
function hideLoadingIndicator() {
    console.log('Скрываем индикатор загрузки...');
    
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = 'none';
    }
}

/**
 * Функция для отображения уведомлений пользователю
 * @param {string} message - Текст уведомления
 * @param {string} type - Тип уведомления (success, error, warning, info)
 */
function showNotification(message, type = 'info') {
    console.log(`Показываю уведомление типа ${type}: ${message}`);
    
    // Проверяем наличие контейнера для уведомлений
    let notificationContainer = document.querySelector('.notification-container');
    
    // Создаем контейнер, если он отсутствует
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.className = 'notification-container';
        document.body.appendChild(notificationContainer);
    }
    
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Добавляем иконку в зависимости от типа уведомления
    let icon = '';
    switch (type) {
        case 'success':
            icon = '<i class="bi bi-check-circle-fill"></i>';
            break;
        case 'error':
            icon = '<i class="bi bi-exclamation-circle-fill"></i>';
            break;
        case 'warning':
            icon = '<i class="bi bi-exclamation-triangle-fill"></i>';
            break;
        default:
            icon = '<i class="bi bi-info-circle-fill"></i>';
    }
    
    // Устанавливаем содержимое уведомления
    notification.innerHTML = `
        <div class="notification-icon">${icon}</div>
        <div class="notification-content">${message}</div>
        <button class="notification-close"><i class="bi bi-x"></i></button>
    `;
    
    // Добавляем уведомление в контейнер
    notificationContainer.appendChild(notification);
    
    // Добавляем обработчик для закрытия уведомления по клику на кнопку
    const closeButton = notification.querySelector('.notification-close');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            notification.classList.add('fade-out');
            setTimeout(() => {
                notificationContainer.removeChild(notification);
            }, 300);
        });
    }
    
    // Автоматически скрываем уведомление через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.add('fade-out');
            setTimeout(() => {
                if (notification.parentNode) {
                    notificationContainer.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Восстановление данных формы из localStorage
 */
function restoreFormDraft() {
    try {
        const draftData = localStorage.getItem('business_registration_draft');
        if (!draftData) return;
        
        const formData = JSON.parse(draftData);
        const form = document.getElementById('registration-form');
        if (!form) return;
        
        // Восстанавливаем текстовые поля
        Object.keys(formData).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input && (input.tagName === 'INPUT' || input.tagName === 'TEXTAREA' || input.tagName === 'SELECT')) {
                input.value = formData[key];
            }
        });
        
        // Восстанавливаем тип бизнеса
        if (formData.business_type) {
            const businessTypeCard = document.querySelector(`.business-type-card[data-type="${formData.business_type}"]`);
            if (businessTypeCard) {
                businessTypeCard.click();
            }
        }
        
        console.log('Черновик формы восстановлен');
        
        // Показываем уведомление о восстановлении
        showNotification('info', 'Данные формы восстановлены из последнего сохранения');
    } catch (e) {
        console.error('Ошибка при восстановлении черновика формы:', e);
    }
}

/**
 * Отправка формы регистрации
 */
function submitRegistrationForm() {
    console.log('Начинаем процесс регистрации...');
    
    // Показываем индикатор загрузки
    showLoading(true, 'Отправка данных...');
    
    // Проверяем наличие формы
    const form = document.getElementById('registration-form');
    if (!form) {
        console.error('Форма регистрации не найдена!');
        showNotification('Ошибка: форма регистрации не найдена', 'error');
        showLoading(false);
        return;
    }
    
    // Валидация формы
    const businessType = form.querySelector('input[name="business_type"]:checked');
    const companyName = form.querySelector('input[name="name"]');
    
    if (!businessType) {
        console.error('Не выбран тип бизнеса!');
        showNotification('Пожалуйста, выберите тип бизнеса', 'error');
        showLoading(false);
        return;
    }
    
    if (!companyName || !companyName.value.trim()) {
        console.error('Не указано название компании!');
        showNotification('Пожалуйста, укажите название компании', 'error');
        showLoading(false);
        return;
    }
    
    // Создаем FormData из формы
    const formData = new FormData(form);
    
    // Добавляем рабочие часы
    try {
        const workingHoursData = getWorkingHoursData();
        formData.set('working_hours', JSON.stringify(workingHoursData));
        console.log('Добавлены рабочие часы:', workingHoursData);
    } catch (error) {
        console.error('Ошибка при получении рабочих часов:', error);
    }
    
    // Добавляем соц. сети
    try {
        const socialLinks = getSocialLinksData();
        formData.set('social_links', JSON.stringify(socialLinks));
        console.log('Добавлены социальные сети:', socialLinks);
    } catch (error) {
        console.error('Ошибка при получении данных соц. сетей:', error);
    }
    
    // Сохраняем черновик в localStorage на случай ошибки
    try {
        const formDataObj = {};
        for (const [key, value] of formData.entries()) {
            if (key !== 'logo' && key !== 'photos') {
                formDataObj[key] = value;
            }
        }
        localStorage.setItem('registration_draft', JSON.stringify(formDataObj));
        console.log('Черновик сохранен в localStorage');
    } catch (error) {
        console.error('Ошибка при сохранении черновика:', error);
    }
    
    // Отправка данных на сервер
    console.log('Отправляем данные на сервер...');
    
    // Устанавливаем таймаут для fetch запроса
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 секунд таймаут
    
    fetch('/business/api/register', {
        method: 'POST',
        body: formData,
        signal: controller.signal
    })
    .then(response => {
        console.log('Получен ответ от сервера:', response);
        clearTimeout(timeoutId);
        
        // Проверяем тип ответа
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return response.json().then(data => {
                if (!response.ok) {
                    throw new Error(data.error || 'Ошибка при регистрации бизнеса');
                }
                return data;
            });
        } else {
            return response.text().then(text => {
                if (!response.ok) {
                    throw new Error('Ошибка при регистрации бизнеса');
                }
                try {
                    return JSON.parse(text);
                } catch (e) {
                    console.warn('Ответ не в формате JSON:', text);
                    return { success: response.ok };
                }
            });
        }
    })
    .then(data => {
        console.log('Данные успешно отправлены:', data);
        showLoading(false);
        
        if (data.success) {
            // Очищаем черновик
            localStorage.removeItem('registration_draft');
            
            // Показываем уведомление об успехе
            showNotification('Регистрация бизнеса успешно завершена!', 'success');
            
            // Показываем шаг завершения регистрации
            showCompletionStep(data.company_id);
        } else {
            showNotification(data.error || 'Произошла ошибка при регистрации бизнеса', 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке данных:', error);
        showLoading(false);
        
        if (error.name === 'AbortError') {
            showNotification('Превышено время ожидания ответа от сервера. Пожалуйста, попробуйте позже.', 'error');
        } else {
            showNotification('Произошла ошибка при отправке данных: ' + error.message, 'error');
        }
    });
}

/**
 * Инициализация мобильной адаптации
 */
function initMobileAdaptation() {
    console.log('Инициализация мобильной адаптации...');
    
    // Проверка наличия мобильных элементов перед работой с ними
    const mobileNavButtons = document.querySelectorAll('.mobile-nav-btn');
    if (mobileNavButtons.length === 0) {
        console.log('Мобильная навигация не найдена, пропускаем инициализацию');
        return;
    }
    
    try {
        // Инициализация переключения между панелями
        mobileNavButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const targetPanel = this.getAttribute('data-target');
                if (!targetPanel) return;
                
                // Убираем класс active у всех кнопок
                mobileNavButtons.forEach(b => b.classList.remove('active'));
                
                // Добавляем класс active текущей кнопке
                this.classList.add('active');
                
                // Скрываем все панели
                const panels = document.querySelectorAll('.scene-container, .list-container, .info-container');
                panels.forEach(panel => {
                    panel.style.display = 'none';
                });
                
                // Показываем целевую панель
                const targetElement = document.getElementById(targetPanel);
                if (targetElement) {
                    targetElement.style.display = 'flex';
                }
            });
        });
        
        // Убеждаемся, что по умолчанию отображается первая панель в мобильном реживе
        if (window.innerWidth <= 991.98) {
            const firstBtn = mobileNavButtons[0];
            if (firstBtn) {
                firstBtn.click();
            }
        }
        
        // Инициализация жестов свайпа (если необходимо)
        // Здесь можно добавить код для обработки жестов свайпа
    } catch (e) {
        console.error('Ошибка при инициализации мобильной адаптации:', e);
    }
}

/**
 * Функция для получения данных о социальных сетях из формы
 * @returns {Object} Объект с данными о социальных сетях
 */
function getSocialLinksData() {
    const socialLinks = {};
    
    // Получаем значения полей с социальными сетями
    const telegramInput = document.getElementById('social-telegram');
    if (telegramInput && telegramInput.value.trim()) {
        socialLinks.telegram = telegramInput.value.trim();
    }
    
    const vkInput = document.getElementById('social-vk');
    if (vkInput && vkInput.value.trim()) {
        socialLinks.vk = vkInput.value.trim();
    }
    
    // Вы можете добавить дополнительные соц. сети по аналогии
    
    return socialLinks;
}

/**
 * Функция для отображения/скрытия индикатора загрузки
 * @param {boolean} show - показать или скрыть индикатор
 * @param {string} message - сообщение, отображаемое под индикатором
 */
function showLoading(show, message = 'Загрузка...') {
    // Удаляем существующий оверлей, если он есть
    const existingOverlay = document.querySelector('.loading-overlay');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Если нужно показать индикатор загрузки
    if (show) {
        // Создаем элемент оверлея загрузки
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        
        // Создаем элемент спиннера
        const spinner = document.createElement('div');
        spinner.className = 'loading-spinner';
        
        // Создаем элемент сообщения
        const messageElement = document.createElement('div');
        messageElement.className = 'loading-message';
        messageElement.textContent = message;
        
        // Добавляем элементы в оверлей
        loadingOverlay.appendChild(spinner);
        loadingOverlay.appendChild(messageElement);
        
        // Добавляем оверлей в body
        document.body.appendChild(loadingOverlay);
    }
}

// Функция для отображения шага завершения регистрации
function showCompletionStep(companyId) {
    // Скрываем все шаги формы
    document.querySelectorAll('.form-step').forEach(step => {
        step.style.display = 'none';
    });
    
    // Показываем шаг завершения
    const completionStep = document.getElementById('completion-form');
    if (completionStep) {
        completionStep.style.display = 'block';
        
        // Устанавливаем ID компании для последующего использования
        if (companyId) {
            const companyIdElement = document.getElementById('registered-company-id');
            if (companyIdElement) {
                companyIdElement.setAttribute('data-company-id', companyId);
            }
        }
        
        // Прокручиваем страницу к началу
        window.scrollTo(0, 0);
    } else {
        // Если шага завершения нет, перенаправляем на дашборд через 1.5 секунды
        setTimeout(() => {
            window.location.href = `/business/dashboard`;
        }, 1500);
    }
}

// Функция для обновления активного шага в боковом меню
function updateActiveStep(stepId) {
    const steps = document.querySelectorAll('.step-item');
    steps.forEach(step => {
        step.classList.remove('active');
        if (step.getAttribute('data-step') === stepId) {
            step.classList.add('active');
        }
    });
}

// Инициализация событий для боковой панели
function initSidebar() {
    // Привязываем клики по пунктам меню
    const stepItems = document.querySelectorAll('.step-item');
    stepItems.forEach(item => {
        item.addEventListener('click', () => {
            const stepId = item.getAttribute('data-step');
            goToFormStep(stepId);
        });
    });
} 