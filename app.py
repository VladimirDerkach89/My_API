# Импорт необходимых модулей
from flask import Flask, jsonify, request  # Flask - ядро приложения, jsonify - для JSON-ответов, request - для обработки входящих запросов
from flasgger import Swagger  # Для автоматической генерации документации API

# Создание экземпляра Flask-приложения
# __name__ - имя текущего модуля, нужно Flask для правильной работы
app = Flask(__name__)

# Конфигурация Swagger для автоматической документации
app.config['SWAGGER'] = {
    'title': 'Tasks API',  # Название API
    'description': 'API для управления списком задач',  # Описание API
    'version': '1.0.0',  # Версия API
    'uiversion': 3  # Версия интерфейса Swagger UI
}
# Инициализация Swagger для нашего приложения
swagger = Swagger(app)

# Наша "база данных" - список задач в памяти
# Каждая задача - словарь с полями: id, title, done
tasks = [
    {"id": 1, "title": "Купить молоко", "done": False},
    {"id": 2, "title": "Выучить Python", "done": True},
]

# Маршрут для получения всех задач
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Получение списка всех задач
    ---
    responses:
      200:
        description: Успешный ответ со списком задач
        content:
          application/json:
            example: [
              {"id": 1, "title": "Купить молоко", "done": false},
              {"id": 2, "title": "Выучить Python", "done": true}
            ]
    """
    # Просто возвращаем весь список задач в формате JSON
    return jsonify(tasks)

# Маршрут для получения конкретной задачи по ID
@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    Получение задачи по её ID
    ---
    parameters:
      - name: task_id
        in: path  # Параметр передается в URL
        type: integer
        required: true
        description: Числовой идентификатор задачи
    responses:
      200:
        description: Задача найдена
        content:
          application/json:
            example: {"id": 1, "title": "Купить молоко", "done": false}
      404:
        description: Задача не найдена
        content:
          application/json:
            example: {"error": "Задача не найдена"}
    """
    # Ищем задачу с указанным ID
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    # Если задача не найдена - возвращаем 404
    if task is None:
        return jsonify({"error": "Задача не найдена"}), 404
    
    # Возвращаем найденную задачу
    return jsonify(task)

# Маршрут для создания новой задачи
@app.route('/tasks', methods=['POST'])
def create_task():
    """
    Создание новой задачи
    ---
    requestBody:
      required: true  # Обязательное тело запроса
      content:
        application/json:
          schema:  # Описание структуры данных
            type: object
            properties:
              title:
                type: string
                example: "Новая задача"
    responses:
      201:
        description: Задача успешно создана
        content:
          application/json:
            example: {"id": 3, "title": "Новая задача", "done": false}
    """
    # Создаем новую задачу на основе данных из запроса
    new_task = {
        "id": len(tasks) + 1,  # Генерируем новый ID
        "title": request.json.get('title'),  # Получаем title из тела запроса
        "done": False  # По умолчанию задача не выполнена
    }
    
    # Добавляем задачу в наш список
    tasks.append(new_task)
    
    # Возвращаем созданную задачу с кодом 201 (Created)
    return jsonify(new_task), 201

# Маршрут для обновления существующей задачи
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    Обновление существующей задачи
    ---
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: ID задачи для обновления
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              title:
                type: string
                example: "Обновленное название задачи"
              done:
                type: boolean
                example: true
    responses:
      200:
        description: Задача успешно обновлена
        content:
          application/json:
            example: {"id": 1, "title": "Обновленное название", "done": true}
      404:
        description: Задача не найдена
        content:
          application/json:
            example: {"error": "Задача не найдена"}
    """
    # Ищем задачу для обновления
    task = next((task for task in tasks if task['id'] == task_id), None)
    
    # Если задача не найдена - возвращаем 404
    if task is None:
        return jsonify({"error": "Задача не найдена"}), 404
    
    # Обновляем поля задачи, если они переданы в запросе
    # request.json.get('поле', текущее_значение) - если поле не передано, сохраняем старое значение
    task['title'] = request.json.get('title', task['title'])
    task['done'] = request.json.get('done', task['done'])
    
    # Возвращаем обновленную задачу
    return jsonify(task)

# Маршрут для удаления задачи
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    Удаление задачи
    ---
    parameters:
      - name: task_id
        in: path
        type: integer
        required: true
        description: ID задачи для удаления
    responses:
      200:
        description: Задача успешно удалена
        content:
          application/json:
            example: {"message": "Задача удалена"}
    """
    # Используем global, так как мы модифицируем глобальную переменную tasks
    global tasks
    
    # Создаем новый список без задачи с указанным ID
    tasks = [task for task in tasks if task['id'] != task_id]
    
    # Возвращаем подтверждение удаления
    return jsonify({"message": "Задача удалена"}), 200

# Точка входа при запуске скрипта напрямую
if __name__ == '__main__':
    # Запускаем Flask-приложение
    # debug=True включает:
    # - автоматическую перезагрузку при изменениях
    # - подробные ошибки в браузере
    # - отладочный режим
    app.run(debug=True)