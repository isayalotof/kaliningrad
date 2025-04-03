/**
 * Скрипт для инициализации и управления картой компаний
 */

// Глобальные переменные
let map;
let markers = [];
let infoWindow;
let currentInfoWindow = null;
let businessTypes = [];
let activeFilters = {
    type: null,
    city: null,
    search: ''
};

// Инициализация карты при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Инициализация карты компаний...');
    
    // Инициализация карты
    initMap();
    
    // Инициализация фильтров
    initFilters();
    
    // Инициализация поиска
    initSearch();
});

// Инициализация карты
function initMap() {
    console.log('Инициализация карты...');
    
    // Проверяем, есть ли контейнер для карты
    const mapContainer = document.getElementById('map');
    if (!mapContainer) {
        console.warn('Контейнер для карты не найден');
        return;
    }
    
    // Создаем объект карты
    map = new google.maps.Map(mapContainer, {
        center: { lat: 55.751244, lng: 37.618423 }, // Москва по умолчанию
        zoom: 10,
        styles: mapStyles,
        gestureHandling: 'greedy',
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
    });
    
    // Создаем объект информационного окна
    infoWindow = new google.maps.InfoWindow({
        maxWidth: 300
    });
    
    // Получаем данные о компаниях и отображаем их на карте
    loadLocations();
    
    // Получаем список типов бизнеса для фильтрации
    loadBusinessTypes();
    
    // Получаем список городов для фильтрации
    loadCities();
}

// Загрузка локаций компаний
async function loadLocations() {
    try {
        const url = buildFilterUrl('/api/map/locations');
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (response.ok) {
            // Очищаем текущие маркеры
            clearMarkers();
            
            // Добавляем новые маркеры
            createMarkers(data);
            
            // Центрируем карту, если есть маркеры
            if (data.length > 0) {
                centerMapOnMarkers();
            }
            
            // Обновляем счетчик найденных компаний
            updateCompanyCount(data.length);
        } else {
            console.error('Ошибка при загрузке локаций:', data);
        }
    } catch (error) {
        console.error('Ошибка при загрузке локаций:', error);
    }
}

// Создание URL с учетом активных фильтров
function buildFilterUrl(baseUrl) {
    const params = new URLSearchParams();
    
    if (activeFilters.type) {
        params.append('type', activeFilters.type);
    }
    
    if (activeFilters.city) {
        params.append('city', activeFilters.city);
    }
    
    if (activeFilters.search) {
        params.append('search', activeFilters.search);
    }
    
    const paramString = params.toString();
    return paramString ? `${baseUrl}?${paramString}` : baseUrl;
}

// Создание маркеров на карте
function createMarkers(locations) {
    markers = [];
    
    locations.forEach(location => {
        // Создаем маркер
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
            icon: getMarkerIcon(location.type)
        });
        
        // Привязываем данные локации к маркеру
        marker.locationData = location;
        
        // Добавляем обработчик клика
        marker.addListener('click', function() {
            // Закрываем предыдущее инфо-окно, если оно открыто
            if (currentInfoWindow) {
                currentInfoWindow.close();
            }
            
            // Создаем содержимое инфо-окна
            const content = createInfoWindowContent(location);
            
            // Открываем инфо-окно
            infoWindow.setContent(content);
            infoWindow.open(map, marker);
            
            // Запоминаем текущее инфо-окно
            currentInfoWindow = infoWindow;
        });
        
        // Добавляем маркер в массив
        markers.push(marker);
    });
}

// Получение иконки маркера в зависимости от типа бизнеса
function getMarkerIcon(type) {
    // Иконки для разных типов бизнеса
    const icons = {
        'beauty_salon': '/static/img/map/beauty_salon.png',
        'barbershop': '/static/img/map/barbershop.png',
        'gym': '/static/img/map/gym.png',
        'spa': '/static/img/map/spa.png',
        'massage': '/static/img/map/massage.png',
        'restaurant': '/static/img/map/restaurant.png',
        'cafe': '/static/img/map/cafe.png',
        'medical': '/static/img/map/medical.png',
        'dental': '/static/img/map/dental.png',
        'pet': '/static/img/map/pet.png',
        'repair': '/static/img/map/repair.png',
        'cleaning': '/static/img/map/cleaning.png'
    };
    
    // Возвращаем иконку для типа или иконку по умолчанию
    return {
        url: icons[type] || '/static/img/map/default.png',
        scaledSize: new google.maps.Size(32, 32),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(16, 32)
    };
}

// Создание содержимого информационного окна
function createInfoWindowContent(location) {
    // Получаем типы услуг в читаемом виде
    const businessTypeName = getBusinessTypeName(location.type);
    
    // Формируем содержимое
    let content = `
        <div class="info-window">
            <h5 class="info-window-title">${location.name}</h5>
            <p class="info-window-category"><i class="fas fa-tag"></i> ${businessTypeName}</p>
            <p class="info-window-address"><i class="fas fa-map-marker-alt"></i> ${location.address}</p>
    `;
    
    // Добавляем рабочие часы, если они есть
    if (location.working_hours) {
        content += `<p class="info-window-hours"><i class="far fa-clock"></i> ${location.working_hours}</p>`;
    }
    
    // Добавляем телефон, если он есть
    if (location.phone) {
        content += `<p class="info-window-phone"><i class="fas fa-phone"></i> <a href="tel:${location.phone}">${location.phone}</a></p>`;
    }
    
    // Добавляем кнопки действий
    content += `
        <div class="info-window-actions">
            <a href="/business/${location.id}" class="btn btn-primary btn-sm">Подробнее</a>
            <button class="btn btn-outline-secondary btn-sm info-window-route-btn" data-lat="${location.lat}" data-lng="${location.lng}">Проложить маршрут</button>
        </div>
    `;
    
    content += `</div>`;
    
    return content;
}

// Получение названия типа бизнеса
function getBusinessTypeName(type) {
    const typeMap = {
        'beauty_salon': 'Салон красоты',
        'barbershop': 'Барбершоп',
        'gym': 'Фитнес-центр',
        'spa': 'SPA-салон',
        'massage': 'Массажный салон',
        'restaurant': 'Ресторан',
        'cafe': 'Кафе',
        'medical': 'Медицинский центр',
        'dental': 'Стоматология',
        'pet': 'Ветеринарная клиника',
        'repair': 'Сервисный центр',
        'cleaning': 'Клининговая компания'
    };
    
    return typeMap[type] || 'Другое';
}

// Очистка маркеров с карты
function clearMarkers() {
    markers.forEach(marker => {
        marker.setMap(null);
    });
    markers = [];
}

// Центрирование карты на маркерах
function centerMapOnMarkers() {
    if (markers.length === 0) return;
    
    if (markers.length === 1) {
        // Если маркер один, центрируем на нем
        map.setCenter(markers[0].getPosition());
        map.setZoom(15);
        return;
    }
    
    // Если маркеров несколько, создаем границы и центрируем по ним
    const bounds = new google.maps.LatLngBounds();
    markers.forEach(marker => {
        bounds.extend(marker.getPosition());
    });
    
    map.fitBounds(bounds);
    
    // Устанавливаем минимальный зум для лучшего обзора
    const listener = google.maps.event.addListener(map, 'idle', function() {
        if (map.getZoom() > 16) {
            map.setZoom(16);
        }
        google.maps.event.removeListener(listener);
    });
}

// Загрузка типов бизнеса для фильтрации
async function loadBusinessTypes() {
    try {
        const response = await fetch('/api/map/business-types');
        const data = await response.json();
        
        if (response.ok) {
            businessTypes = data;
            
            // Заполняем селект типами бизнеса
            const typeSelect = document.getElementById('business-type-filter');
            if (typeSelect) {
                // Добавляем пустой пункт "Все типы"
                typeSelect.innerHTML = '<option value="">Все типы бизнеса</option>';
                
                // Добавляем типы бизнеса
                businessTypes.forEach(type => {
                    const option = document.createElement('option');
                    option.value = type.id;
                    option.textContent = type.name;
                    typeSelect.appendChild(option);
                });
            }
        } else {
            console.error('Ошибка при загрузке типов бизнеса:', data);
        }
    } catch (error) {
        console.error('Ошибка при загрузке типов бизнеса:', error);
    }
}

// Загрузка городов для фильтрации
async function loadCities() {
    try {
        const response = await fetch('/api/map/cities');
        const data = await response.json();
        
        if (response.ok) {
            // Заполняем селект городами
            const citySelect = document.getElementById('city-filter');
            if (citySelect) {
                // Добавляем пустой пункт "Все города"
                citySelect.innerHTML = '<option value="">Все города</option>';
                
                // Добавляем города
                data.forEach(city => {
                    const option = document.createElement('option');
                    option.value = city;
                    option.textContent = city;
                    citySelect.appendChild(option);
                });
            }
        } else {
            console.error('Ошибка при загрузке городов:', data);
        }
    } catch (error) {
        console.error('Ошибка при загрузке городов:', error);
    }
}

// Инициализация фильтров
function initFilters() {
    // Фильтр по типу бизнеса
    const typeSelect = document.getElementById('business-type-filter');
    if (typeSelect) {
        typeSelect.addEventListener('change', function() {
            activeFilters.type = this.value;
            loadLocations();
        });
    }
    
    // Фильтр по городу
    const citySelect = document.getElementById('city-filter');
    if (citySelect) {
        citySelect.addEventListener('change', function() {
            activeFilters.city = this.value;
            loadLocations();
        });
    }
    
    // Кнопка сброса фильтров
    const resetButton = document.getElementById('reset-filters-btn');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            // Сбрасываем значения фильтров
            if (typeSelect) typeSelect.value = '';
            if (citySelect) citySelect.value = '';
            
            // Сбрасываем поле поиска
            const searchInput = document.getElementById('search-input');
            if (searchInput) searchInput.value = '';
            
            // Сбрасываем активные фильтры
            activeFilters = {
                type: null,
                city: null,
                search: ''
            };
            
            // Загружаем локации без фильтров
            loadLocations();
        });
    }
}

// Инициализация поиска
function initSearch() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    
    if (searchForm && searchInput) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Получаем значение поиска
            const searchValue = searchInput.value.trim();
            
            // Обновляем активные фильтры
            activeFilters.search = searchValue;
            
            // Загружаем локации с учетом поиска
            loadLocations();
        });
    }
}

// Обновление счетчика найденных компаний
function updateCompanyCount(count) {
    const countElement = document.getElementById('company-count');
    if (countElement) {
        countElement.textContent = count;
    }
}

// Стили для карты (можно настроить по вкусу)
const mapStyles = [
    {
        "featureType": "administrative",
        "elementType": "all",
        "stylers": [
            {
                "saturation": "-100"
            }
        ]
    },
    {
        "featureType": "administrative.province",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "off"
            }
        ]
    },
    {
        "featureType": "landscape",
        "elementType": "all",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": 65
            },
            {
                "visibility": "on"
            }
        ]
    },
    {
        "featureType": "poi",
        "elementType": "all",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "lightness": "50"
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road",
        "elementType": "all",
        "stylers": [
            {
                "saturation": "-100"
            }
        ]
    },
    {
        "featureType": "road.highway",
        "elementType": "all",
        "stylers": [
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "road.arterial",
        "elementType": "all",
        "stylers": [
            {
                "lightness": "30"
            }
        ]
    },
    {
        "featureType": "road.local",
        "elementType": "all",
        "stylers": [
            {
                "lightness": "40"
            }
        ]
    },
    {
        "featureType": "transit",
        "elementType": "all",
        "stylers": [
            {
                "saturation": -100
            },
            {
                "visibility": "simplified"
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "geometry",
        "stylers": [
            {
                "hue": "#ffff00"
            },
            {
                "lightness": -25
            },
            {
                "saturation": -97
            }
        ]
    },
    {
        "featureType": "water",
        "elementType": "labels",
        "stylers": [
            {
                "lightness": -25
            },
            {
                "saturation": -100
            }
        ]
    }
]; 