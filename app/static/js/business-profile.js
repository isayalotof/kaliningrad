// JavaScript для страницы профиля бизнеса

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация подсказок Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Галерея: открытие изображения в модальном окне
    const galleryItems = document.querySelectorAll('.gallery-item');
    const galleryModalImage = document.getElementById('galleryModalImage');
    
    galleryItems.forEach(item => {
        item.addEventListener('click', function(e) {
            e.preventDefault();
            const imageSrc = this.getAttribute('data-image');
            if (galleryModalImage) {
                galleryModalImage.src = imageSrc;
            }
        });
    });

    // Кнопка "Поделиться"
    const shareBtn = document.querySelector('.share-btn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            if (navigator.share) {
                // Если доступно нативное API share
                navigator.share({
                    title: document.title,
                    url: window.location.href
                }).catch(err => {
                    console.error('Ошибка при шаринге:', err);
                });
            } else {
                // Запасной вариант: копирование ссылки в буфер обмена
                navigator.clipboard.writeText(window.location.href).then(function() {
                    // Создаем временное уведомление
                    const toast = document.createElement('div');
                    toast.className = 'position-fixed bottom-0 end-0 p-3';
                    toast.style.zIndex = 1050;
                    toast.innerHTML = `
                        <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                            <div class="toast-header">
                                <strong class="me-auto">Qwerty.town</strong>
                                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
                            </div>
                            <div class="toast-body">
                                Ссылка скопирована в буфер обмена!
                            </div>
                        </div>
                    `;
                    document.body.appendChild(toast);
                    
                    // Удаляем уведомление через 3 секунды
                    setTimeout(() => {
                        toast.remove();
                    }, 3000);
                }).catch(err => {
                    console.error('Не удалось скопировать ссылку:', err);
                    alert('Не удалось скопировать ссылку. Пожалуйста, скопируйте её вручную.');
                });
            }
        });
    }

    // Обработка бронирования
    const bookingDate = document.getElementById('booking-date');
    const bookingTime = document.getElementById('booking-time');
    const confirmBookingBtn = document.getElementById('confirmBooking');
    const bookServiceBtns = document.querySelectorAll('.book-service-btn');

    // Заполнение временных слотов при выборе даты
    if (bookingDate) {
        bookingDate.addEventListener('change', function() {
            const selectedDate = this.value;
            if (!selectedDate) {
                if (bookingTime) {
                    bookingTime.disabled = true;
                    bookingTime.innerHTML = '<option value="">Сначала выберите дату</option>';
                }
                return;
            }

            // Разблокируем выбор времени
            if (bookingTime) {
                bookingTime.disabled = false;
                
                // Здесь должен быть AJAX запрос к серверу для получения доступных временных слотов
                // Пока используем заглушку с временными слотами
                const date = new Date(selectedDate);
                const dayOfWeek = date.getDay(); // 0 - воскресенье, 1 - понедельник и т.д.
                const isWeekend = (dayOfWeek === 0 || dayOfWeek === 6);
                
                // Разное время для будней и выходных
                let startHour = isWeekend ? 10 : 9;
                let endHour = isWeekend ? 18 : 20;
                
                let timeOptions = '<option value="">Выберите время</option>';
                
                for (let hour = startHour; hour < endHour; hour++) {
                    for (let minute of ['00', '30']) {
                        const timeValue = `${hour.toString().padStart(2, '0')}:${minute}`;
                        timeOptions += `<option value="${timeValue}">${timeValue}</option>`;
                    }
                }
                
                bookingTime.innerHTML = timeOptions;
            }
        });
    }

    // Выбор услуги из списка
    if (bookServiceBtns.length > 0) {
        bookServiceBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const serviceId = this.getAttribute('data-service-id');
                const serviceName = this.getAttribute('data-service-name');
                
                // Открываем модальное окно бронирования
                const bookingModal = new bootstrap.Modal(document.getElementById('bookingModal'));
                bookingModal.show();
                
                // Выбираем услугу в выпадающем списке
                const serviceSelect = document.getElementById('service');
                if (serviceSelect) {
                    for (let i = 0; i < serviceSelect.options.length; i++) {
                        if (serviceSelect.options[i].value === serviceId) {
                            serviceSelect.selectedIndex = i;
                            break;
                        }
                    }
                }
            });
        });
    }

    // Подтверждение бронирования
    if (confirmBookingBtn) {
        confirmBookingBtn.addEventListener('click', function() {
            const form = document.getElementById('bookingForm');
            if (!form) return;
            
            // Проверка заполнения формы
            const serviceSelect = document.getElementById('service');
            const bookingDate = document.getElementById('booking-date');
            const bookingTime = document.getElementById('booking-time');
            const bookingName = document.getElementById('booking-name');
            const bookingPhone = document.getElementById('booking-phone');
            
            if (!serviceSelect || !bookingDate || !bookingTime || !bookingName || !bookingPhone) return;
            
            if (!serviceSelect.value) {
                alert('Пожалуйста, выберите услугу');
                return;
            }
            
            if (!bookingDate.value) {
                alert('Пожалуйста, выберите дату');
                return;
            }
            
            if (!bookingTime.value) {
                alert('Пожалуйста, выберите время');
                return;
            }
            
            if (!bookingName.value) {
                alert('Пожалуйста, укажите ваше имя');
                return;
            }
            
            if (!bookingPhone.value) {
                alert('Пожалуйста, укажите ваш телефон');
                return;
            }
            
            // Здесь должен быть AJAX запрос на сервер для отправки данных бронирования
            // Пока просто показываем сообщение об успешном бронировании
            
            // Закрываем модальное окно
            const bookingModal = bootstrap.Modal.getInstance(document.getElementById('bookingModal'));
            if (bookingModal) {
                bookingModal.hide();
            }
            
            // Показываем сообщение об успешном бронировании
            const toast = document.createElement('div');
            toast.className = 'position-fixed bottom-0 end-0 p-3';
            toast.style.zIndex = 1050;
            toast.innerHTML = `
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-success text-white">
                        <strong class="me-auto">Успешно!</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        Ваше бронирование успешно создано! Ожидайте подтверждения от компании.
                    </div>
                </div>
            `;
            document.body.appendChild(toast);
            
            // Удаляем уведомление через 5 секунд
            setTimeout(() => {
                toast.remove();
            }, 5000);
        });
    }

    // Отправка отзыва
    const submitReviewBtn = document.getElementById('submitReview');
    if (submitReviewBtn) {
        submitReviewBtn.addEventListener('click', function() {
            const form = document.getElementById('reviewForm');
            if (!form) return;
            
            // Проверка заполнения формы
            const rating = form.querySelector('input[name="rating"]:checked');
            const reviewName = document.getElementById('review-name');
            const reviewEmail = document.getElementById('review-email');
            const reviewText = document.getElementById('review-text');
            
            if (!rating || !reviewName || !reviewEmail || !reviewText) return;
            
            if (!rating.value) {
                alert('Пожалуйста, поставьте оценку');
                return;
            }
            
            if (!reviewName.value) {
                alert('Пожалуйста, укажите ваше имя');
                return;
            }
            
            if (!reviewEmail.value) {
                alert('Пожалуйста, укажите ваш email');
                return;
            }
            
            if (!reviewText.value) {
                alert('Пожалуйста, напишите отзыв');
                return;
            }
            
            // Здесь должен быть AJAX запрос на сервер для отправки отзыва
            // Пока просто показываем сообщение об успешной отправке
            
            // Закрываем модальное окно
            const reviewModal = bootstrap.Modal.getInstance(document.getElementById('reviewModal'));
            if (reviewModal) {
                reviewModal.hide();
            }
            
            // Показываем сообщение об успешной отправке отзыва
            const toast = document.createElement('div');
            toast.className = 'position-fixed bottom-0 end-0 p-3';
            toast.style.zIndex = 1050;
            toast.innerHTML = `
                <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="toast-header bg-success text-white">
                        <strong class="me-auto">Успешно!</strong>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
                    </div>
                    <div class="toast-body">
                        Ваш отзыв успешно отправлен! Спасибо за обратную связь.
                    </div>
                </div>
            `;
            document.body.appendChild(toast);
            
            // Удаляем уведомление через 5 секунд
            setTimeout(() => {
                toast.remove();
            }, 5000);
        });
    }

    // Обновление текущего года в футере
    const currentYearElements = document.querySelectorAll('.current-year');
    if (currentYearElements.length > 0) {
        const currentYear = new Date().getFullYear();
        currentYearElements.forEach(element => {
            element.textContent = currentYear;
        });
    }
}); 