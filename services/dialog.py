
class Dialog:
    def __init__(self):
        # словник user_id -> режим (string)
        self._modes = {}

    def get_mode(self, user_id):
        return self._modes.get(user_id, 'main')  # 'main' — режим за замовчуванням

    def set_mode(self, user_id, mode):
        self._modes[user_id] = mode

# створити глобальний об'єкт
dialog = Dialog()
