from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import json

from app.models.form_template import FormTemplate

class FormTemplateService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_template_by_business_type(self, business_type: str) -> Optional[FormTemplate]:
        """Получает шаблон формы по типу бизнеса"""
        return self.db.query(FormTemplate).filter(
            FormTemplate.business_type == business_type,
            FormTemplate.is_active == True
        ).first()
    
    def get_all_templates(self) -> List[FormTemplate]:
        """Получает все активные шаблоны форм"""
        return self.db.query(FormTemplate).filter(FormTemplate.is_active == True).all()
    
    def create_template(self, business_type: str, name: str, fields: List[Dict], description: str = None) -> FormTemplate:
        """Создает новый шаблон формы"""
        template = FormTemplate(
            business_type=business_type,
            name=name,
            description=description,
            fields=fields
        )
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def update_template(self, template_id: int, data: Dict[str, Any]) -> Optional[FormTemplate]:
        """Обновляет существующий шаблон формы"""
        template = self.db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
        if not template:
            return None
        
        for key, value in data.items():
            if hasattr(template, key):
                setattr(template, key, value)
        
        self.db.commit()
        self.db.refresh(template)
        return template
    
    def delete_template(self, template_id: int) -> bool:
        """Удаляет шаблон формы (помечает как неактивный)"""
        template = self.db.query(FormTemplate).filter(FormTemplate.id == template_id).first()
        if not template:
            return False
        
        template.is_active = False
        self.db.commit()
        return True

    def init_default_templates(self):
        """Инициализирует базовые шаблоны форм для разных типов бизнеса"""
        # Проверяем, есть ли уже шаблоны в базе
        if self.db.query(FormTemplate).count() > 0:
            return
        
        # Словарь с шаблонами форм для разных типов бизнеса
        templates = {
            "restaurant": {
                "name": "Шаблон для ресторана",
                "fields": [
                    {"name": "menu", "label": "Меню", "type": "text_array", "required": True},
                    {"name": "cuisine", "label": "Кухня", "type": "select", "options": ["Русская", "Итальянская", "Азиатская", "Европейская"]},
                    {"name": "average_check", "label": "Средний чек", "type": "number"},
                    {"name": "reservation", "label": "Возможность бронирования", "type": "checkbox"}
                ]
            },
            "beauty": {
                "name": "Шаблон для салона красоты",
                "fields": [
                    {"name": "services", "label": "Услуги", "type": "text_array", "required": True},
                    {"name": "specialists", "label": "Специалисты", "type": "text_array"},
                    {"name": "brands", "label": "Используемые бренды", "type": "text"},
                    {"name": "online_booking", "label": "Онлайн-запись", "type": "checkbox"}
                ]
            },
            "shop": {
                "name": "Шаблон для магазина",
                "fields": [
                    {"name": "products", "label": "Товары", "type": "text_array", "required": True},
                    {"name": "delivery", "label": "Доставка", "type": "checkbox"},
                    {"name": "payment_methods", "label": "Способы оплаты", "type": "select_multiple", 
                     "options": ["Наличные", "Карта", "Онлайн", "Криптовалюта"]}
                ]
            },
            "fitness": {
                "name": "Шаблон для фитнес-центра",
                "fields": [
                    {"name": "activities", "label": "Виды занятий", "type": "text_array", "required": True},
                    {"name": "trainers", "label": "Тренеры", "type": "text_array"},
                    {"name": "equipment", "label": "Оборудование", "type": "text"},
                    {"name": "group_classes", "label": "Групповые занятия", "type": "checkbox"}
                ]
            },
            "medical": {
                "name": "Шаблон для медицинского центра",
                "fields": [
                    {"name": "specializations", "label": "Специализации", "type": "text_array", "required": True},
                    {"name": "doctors", "label": "Врачи", "type": "text_array"},
                    {"name": "insurances", "label": "Принимаемые страховки", "type": "text_array"},
                    {"name": "licenses", "label": "Лицензии", "type": "text"}
                ]
            },
            "other": {
                "name": "Общий шаблон для бизнеса",
                "fields": [
                    {"name": "type", "label": "Тип бизнеса", "type": "text", "required": True},
                    {"name": "services", "label": "Услуги", "type": "text_array", "required": True},
                    {"name": "special_features", "label": "Особенности", "type": "text"}
                ]
            }
        }
        
        # Создаем шаблоны в базе данных
        for business_type, template_data in templates.items():
            self.create_template(
                business_type=business_type,
                name=template_data["name"],
                fields=template_data["fields"],
                description=f"Базовый шаблон для типа бизнеса: {business_type}"
            ) 