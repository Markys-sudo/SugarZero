class Dialog:
    def __init__(self):
        # user_id -> режим (string)
        self._modes = {}
        # user_id -> {ключ: значення}
        self._data = {}

    def get_mode(self, user_id):
        return self._modes.get(user_id, 'main')  # режим за замовчуванням

    def set_mode(self, user_id, mode):
        self._modes[user_id] = mode

    def set_data(self, user_id, key, value):
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id][key] = value

    def get_data(self, user_id, key, default=None):
        return self._data.get(user_id, {}).get(key, default)

    def clear_data(self, user_id):
        if user_id in self._data:
            self._data.pop(user_id)

# створити глобальний об'єкт
dialog = Dialog()
