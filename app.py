"""
Flask REST API для управления задачами с Swagger документацией

Основные функции:
- Создание, чтение, обновление и удаление задач
- Автоматическая генерация документации API
- Валидация входящих данных
"""

# Импорт необходимых модулей
from flask import Flask, jsonify, request  # Основные компоненты Flask
from flasgger import Swagger  # Для Swagger-документации

# Инициализация Flask приложения
app = Flask(__name__)  # Создаем экземпляр Flask приложения

"""
Конфигурация Swagger для автоматической генерации документации
Доступна по адресу /apidocs после запуска приложения
"""
app.config['SWAGGER'] = {
    'title': 'Tasks API',  # Название API
    'description': 'API для управления списком задач (CRUD операции)',  # Описание
    'version': '1.0.0',  # Версия API
    'uiversion': 3,  # Версия интерфейса Swagger UI
    'specs_route': '/apidocs/'  # URL для документации
}
swagger = Swagger(app)  # Инициализация Swagger

"""
"База данных" - список задач в памяти
Используется для демонстрации, в реальном приложении следует использовать БД
Формат каждой задачи:
{
    "id": уникальный числовой идентификатор,
    "title": текст задачи,
    "done": статус выполнения (True/False)
}
"""
tasks = [
    {"id": 1, "title": "Купить молоко", "done": False},
    {"id": 2, "title": "Выучить Python", "done": True},
]

"""
Генератор ID для новых задач
Находит максимальный существующий ID и добавляет 1
"""
def generate_id():
    return max(task['id'] for task in tasks) + 1 if tasks else 1

"""
Маршрут для получения списка всех задач
Endpoint: GET /tasks
"""
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Получение списка всех задач
    ---
    tags: [Tasks]  # Группировка в Swagger UI
    responses:
      200:
        description: Успешный ответ со списком задач
        examples:
          application/json: [
            {"id": 1, "title": "Купить молоко", "done": false},
            {"id": 2, "title": "Выучить Python", "done": true}
          ]
    """
    return jsonify(tasks)  # Автоматическая сериализация в JSON

"""
Маршрут для получения конкретной задачи по ID
Endpoint: GET /tasks/<int:task_id>
"""
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Получение задачи по ID
    ---
    tags: [Tasks]
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: Числовой ID задачи
        example: 1
    responses:
      200:
        description: Задача найдена
        examples:
          application/json: {"id": 1, "title": "Купить молоко", "done": false}
      404:
        description: Задача не найдена
        examples:
          application/json: {"error": "Задача не найдена"}
    """
    task = next((task for task in tasks if task['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    return jsonify(task)

"""
Маршрут для создания новой задачи
Endpoint: POST /tasks
Требует заголовок Content-Type: application/json
"""
@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Создание новой задачи
    ---
    tags: [Tasks]
    consumes: [application/json]  # Указываем принимаемый формат
    produces: [application/json]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [title]  # Обязательные поля
          properties:
            title:
              type: string
              description: Текст задачи
              example: "Новая задача"
    responses:
      201:
        description: Задача успешно создана
        examples:
          application/json: {"id": 3, "title": "Новая задача", "done": false}
      400:
        description: Неверный запрос
        examples:
          application/json: {"error": "Title is required"}
      415:
        description: Неподдерживаемый тип данных
        examples:
          application/json: {"error": "Request must be JSON"}
    """
    # Проверка формата запроса
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    
    # Парсинг JSON данных
    data = request.get_json(silent=True) or {}
    
    # Валидация данных
    if 'title' not in data or not isinstance(data['title'], str) or not data['title'].strip():
        return jsonify({"error": "Title is required and must be non-empty string"}), 400
    
    # Создание новой задачи
    new_task = {
        "id": generate_id(),
        "title": data['title'].strip(),
        "done": False
    }
    tasks.append(new_task)
    
    return jsonify(new_task), 201  # 201 - Created

"""
Маршрут для обновления задачи
Endpoint: PUT /tasks/<int:task_id>
"""
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Обновление задачи
    ---
    tags: [Tasks]
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: ID задачи
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            title:
              type: string
              example: "Обновленный заголовок"
            done:
              type: boolean
              example: true
    responses:
      200:
        description: Задача обновлена
      404:
        description: Задача не найдена
      400:
        description: Неверный запрос
    """
    # Поиск задачи
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    
    # Проверка формата
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 415
    
    data = request.get_json(silent=True) or {}
    
    # Обновление полей
    if 'title' in data and isinstance(data['title'], str) and data['title'].strip():
        task['title'] = data['title'].strip()
    
    if 'done' in data and isinstance(data['done'], bool):
        task['done'] = data['done']
    
    return jsonify(task)

"""
Маршрут для удаления задачи
Endpoint: DELETE /tasks/<int:task_id>
"""
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Удаление задачи
    ---
    tags: [Tasks]
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Задача удалена
      404:
        description: Задача не найдена
    """
    global tasks
    initial_length = len(tasks)
    tasks = [t for t in tasks if t['id'] != task_id]
    
    if len(tasks) == initial_length:
        return jsonify({"error": "Задача не найдена"}), 404
    
    return jsonify({"message": "Задача удалена"}), 200

# Точка входа при запуске скрипта напрямую
if __name__ == '__main__':
    """
    Запуск Flask-приложения
    Параметры:
    - debug=True: включение режима отладки
    - host='0.0.0.0': доступ с других устройств в сети
    - port=5000: порт по умолчанию
    """
    app.run(debug=True, host='0.0.0.0', port=5000)