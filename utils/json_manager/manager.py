import json
import os
from typing import Dict, Any
from datetime import datetime, timedelta


class JSONDataManager:
    def __init__(self, file_path: str = 'data/chat_story/openai_data.json'):
        self.file_path = file_path
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """JSON fayl mavjudligini tekshirish va yo'q bo'lsa yaratish"""
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))

        if not os.path.exists(self.file_path):
            self.save_data({})

    def _datetime_to_str(self, dt: datetime) -> str:
        """Datetime ni string formatga o'tkazish"""
        return dt.isoformat()

    def _str_to_datetime(self, dt_str: str) -> datetime:
        """String ni datetime formatga o'tkazish"""
        try:
            return datetime.fromisoformat(dt_str)
        except (ValueError, TypeError):
            return datetime.now()

    def load_data(self) -> Dict[str, Any]:
        """JSON fayldan ma'lumotlarni yuklash"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {}

    def save_data(self, data: Dict[str, Any]) -> None:
        """Ma'lumotlarni JSON faylga saqlash"""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Foydalanuvchi ma'lumotlarini olish"""
        data = self.load_data()
        if user_id not in data:
            current_time = self._datetime_to_str(datetime.now())
            data[user_id] = {
                'messages': [],
                'last_message_time': current_time
            }
            self.save_data(data)
        return data[user_id]

    def update_user_messages(self, user_id: str, messages: list) -> None:
        """Foydalanuvchi xabarlarini yangilash"""
        data = self.load_data()
        if user_id not in data:
            data[user_id] = {}

        data[user_id]['messages'] = messages
        data[user_id]['last_message_time'] = self._datetime_to_str(datetime.now())
        self.save_data(data)

    def update_last_message_time(self, user_id: str) -> None:
        """Foydalanuvchining oxirgi xabar vaqtini yangilash"""
        data = self.load_data()
        if user_id not in data:
            data[user_id] = {
                'messages': [],
                'last_message_time': self._datetime_to_str(datetime.now())
            }
        else:
            data[user_id]['last_message_time'] = self._datetime_to_str(datetime.now())
        self.save_data(data)

    def check_rate_limit(self, user_id: str) -> bool:
        """Rate limitni tekshirish"""
        try:
            user_data = self.get_user_data(user_id)
            last_message_time = self._str_to_datetime(user_data['last_message_time'])
            time_diff = datetime.now() - last_message_time
            return time_diff >= timedelta(seconds=1)
        except Exception as e:
            # Xatolik bo'lsa, True qaytaramiz (ya'ni rate limit yo'q)
            return True

    def manage_conversation_history(self, user_id: str, max_messages: int = 5) -> list:
        """Suhbat tarixini boshqarish va cheklash"""
        user_data = self.get_user_data(user_id)
        messages = user_data.get('messages', [])

        # Sistema xabarini qo'shish
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant. Provide concise and clear answers."
        }

        # Oxirgi xabarlarni olish
        recent_messages = messages[-(max_messages * 2):] if messages else []

        # Sistema xabari bilan birlashtirish
        return [system_message] + recent_messages

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """Yangi xabar qo'shish"""
        data = self.load_data()
        if user_id not in data:
            data[user_id] = {
                'messages': [],
                'last_message_time': self._datetime_to_str(datetime.now())
            }

        # Xabarni qo'shish
        data[user_id]['messages'].append({
            "role": role,
            "content": content
        })

        # Xabarlar sonini cheklash (oxirgi 10 ta suhbat)
        if len(data[user_id]['messages']) > 20:  # 10 ta suhbat = 20 ta xabar
            data[user_id]['messages'] = data[user_id]['messages'][-20:]

        self.save_data(data)

    def clear_history(self, user_id: str) -> None:
        """Foydalanuvchi chat tarixini tozalash"""
        data = self.load_data()
        if user_id in data:
            data[user_id]['messages'] = []
            data[user_id]['last_message_time'] = self._datetime_to_str(datetime.now())
            self.save_data(data)
