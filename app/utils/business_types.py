"""
Утилиты для работы с типами бизнеса
"""

def get_business_type_name(type_code):
    """
    Получение человекочитаемого названия типа бизнеса
    """
    business_types = {
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
        'cleaning': 'Клининговая компания',
        'other': 'Другое'
    }
    
    return business_types.get(type_code, 'Другое')

def get_all_business_types():
    """
    Получение всех возможных типов бизнеса
    """
    return {
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
        'cleaning': 'Клининговая компания',
        'other': 'Другое'
    } 