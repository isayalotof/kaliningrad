/**
 * Скрипт для аутентификации пользователей
 */

// Инициализация аутентификации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация аутентификации...');
    
    // Инициализация формы входа
    initLoginForm();
    
    // Инициализация формы регистрации
    initSignupForm();
    
    // Проверка текущего пользователя
    checkCurrentUser();
});

// Инициализация формы входа
function initLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;
    
    console.log('Инициализация формы входа...');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Получаем данные формы
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        // Блокируем кнопку отправки
        const submitBtn = document.getElementById('login-submit');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Вход...';
        }
        
        // Скрываем сообщения об ошибках
        hideErrors();
        
        try {
            // Отправляем запрос на вход
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // В случае успеха сохраняем токен и перенаправляем
                localStorage.setItem('auth_token', result.access_token);
                
                // Обновляем UI для авторизованного пользователя
                updateUIForLoggedInUser(result.user);
                
                // Перенаправляем на страницу профиля или дашборда
                if (result.redirect_url) {
                    window.location.href = result.redirect_url;
                } else if (window.location.pathname === '/login') {
                    window.location.href = '/';
                } else {
                    // Если мы на той же странице, просто обновляем страницу
                    location.reload();
                }
            } else {
                // В случае ошибки показываем сообщение
                showError('login-error', result.detail || 'Неверный email или пароль');
                
                // Разблокируем кнопку отправки
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Войти';
                }
            }
        } catch (error) {
            console.error('Ошибка входа:', error);
            
            // Показываем сообщение об ошибке
            showError('login-error', 'Произошла ошибка при попытке входа');
            
            // Разблокируем кнопку отправки
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Войти';
            }
        }
    });
}

// Инициализация формы регистрации
function initSignupForm() {
    const signupForm = document.getElementById('signup-form');
    if (!signupForm) return;
    
    console.log('Инициализация формы регистрации...');
    
    signupForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Получаем данные формы
        const fullName = document.getElementById('signup-fullname').value;
        const email = document.getElementById('signup-email').value;
        const password = document.getElementById('signup-password').value;
        const passwordConfirm = document.getElementById('signup-password-confirm').value;
        
        // Блокируем кнопку отправки
        const submitBtn = document.getElementById('signup-submit');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Регистрация...';
        }
        
        // Скрываем сообщения об ошибках
        hideErrors();
        
        // Проверяем совпадение паролей
        if (password !== passwordConfirm) {
            showError('signup-error', 'Пароли не совпадают');
            
            // Разблокируем кнопку отправки
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Зарегистрироваться';
            }
            return;
        }
        
        try {
            // Отправляем запрос на регистрацию
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    full_name: fullName, 
                    email, 
                    password 
                })
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // В случае успеха сохраняем токен и перенаправляем
                localStorage.setItem('auth_token', result.access_token);
                
                // Обновляем UI для авторизованного пользователя
                updateUIForLoggedInUser(result.user);
                
                // Показываем сообщение об успешной регистрации
                showSuccessMessage('signup-success', 'Регистрация успешна! Перенаправление...');
                
                // Перенаправляем на страницу профиля или дашборда
                setTimeout(() => {
                    if (result.redirect_url) {
                        window.location.href = result.redirect_url;
                    } else {
                        window.location.href = '/';
                    }
                }, 1500);
            } else {
                // В случае ошибки показываем сообщение
                showError('signup-error', result.detail || 'Ошибка при регистрации');
                
                // Разблокируем кнопку отправки
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Зарегистрироваться';
                }
            }
        } catch (error) {
            console.error('Ошибка регистрации:', error);
            
            // Показываем сообщение об ошибке
            showError('signup-error', 'Произошла ошибка при регистрации');
            
            // Разблокируем кнопку отправки
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Зарегистрироваться';
            }
        }
    });
}

// Проверка текущего пользователя
async function checkCurrentUser() {
    // Получаем токен из localStorage
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
        // Если токен отсутствует, пользователь не авторизован
        updateUIForLoggedOutUser();
        return;
    }
    
    try {
        // Отправляем запрос на получение текущего пользователя
        const response = await fetch('/api/auth/me', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const user = await response.json();
            
            // Обновляем UI для авторизованного пользователя
            updateUIForLoggedInUser(user);
        } else {
            // Если запрос вернул ошибку, пользователь не авторизован
            localStorage.removeItem('auth_token');
            updateUIForLoggedOutUser();
        }
    } catch (error) {
        console.error('Ошибка проверки пользователя:', error);
        
        // В случае ошибки считаем пользователя не авторизованным
        localStorage.removeItem('auth_token');
        updateUIForLoggedOutUser();
    }
}

// Обновление UI для авторизованного пользователя
function updateUIForLoggedInUser(user) {
    console.log('Пользователь авторизован:', user);
    
    // Скрываем элементы для неавторизованных пользователей
    const guestElements = document.querySelectorAll('.guest-only');
    guestElements.forEach(el => {
        el.style.display = 'none';
    });
    
    // Показываем элементы для авторизованных пользователей
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(el => {
        el.style.display = '';
    });
    
    // Обновляем информацию о пользователе
    const userNameElements = document.querySelectorAll('.user-name');
    userNameElements.forEach(el => {
        el.textContent = user.full_name || user.email;
    });
    
    // Обновляем аватар пользователя, если есть
    const userAvatarElements = document.querySelectorAll('.user-avatar');
    userAvatarElements.forEach(el => {
        if (user.avatar) {
            el.src = user.avatar;
        }
    });
}

// Обновление UI для неавторизованного пользователя
function updateUIForLoggedOutUser() {
    console.log('Пользователь не авторизован');
    
    // Показываем элементы для неавторизованных пользователей
    const guestElements = document.querySelectorAll('.guest-only');
    guestElements.forEach(el => {
        el.style.display = '';
    });
    
    // Скрываем элементы для авторизованных пользователей
    const authElements = document.querySelectorAll('.auth-only');
    authElements.forEach(el => {
        el.style.display = 'none';
    });
}

// Выход из системы
function logout() {
    // Удаляем токен из localStorage
    localStorage.removeItem('auth_token');
    
    // Обновляем UI для неавторизованного пользователя
    updateUIForLoggedOutUser();
    
    // Перенаправляем на главную страницу
    window.location.href = '/';
}

// Показать сообщение об ошибке
function showError(elementId, message) {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.remove('d-none');
        
        // Прокручиваем к сообщению об ошибке
        errorElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Показать сообщение об успехе
function showSuccessMessage(elementId, message) {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.textContent = message;
        successElement.classList.remove('d-none');
        
        // Прокручиваем к сообщению об успехе
        successElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Скрыть все сообщения об ошибках
function hideErrors() {
    const errorElements = document.querySelectorAll('.alert-danger');
    errorElements.forEach(el => {
        el.classList.add('d-none');
    });
    
    const successElements = document.querySelectorAll('.alert-success');
    successElements.forEach(el => {
        el.classList.add('d-none');
    });
}

// Устанавливаем обработчик для кнопки выхода
document.addEventListener('DOMContentLoaded', function() {
    const logoutButtons = document.querySelectorAll('.logout-btn');
    logoutButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    });
}); 