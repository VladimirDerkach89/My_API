from flask import Flask, jsonify, request  # Исправленный импорт

app = Flask(__name__)

# Пример данных (список задач)
tasks = [
    {"id": 1, "title": "Купить молоко", "done": False},
    {"id": 2, "title": "Выучить Python", "done": True},
]

# Маршрут для получения всех задач
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

# Маршрут для получения одной задачи по ID
@app.route('/tasks/<int:task_id>', methods=['GET'])  # Исправлено
def get_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        return jsonify({"error": "Задача не найдена"}), 404
    return jsonify(task)

# Маршрут для добавления новой задачи
@app.route('/tasks', methods=['POST'])
def create_task():
    new_task = {
        "id": len(tasks) + 1,
        "title": request.json.get('title'),
        "done": False,
    }
    tasks.append(new_task)
    return jsonify(new_task), 201

# Маршрут для обновления задачи
@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task is None:
        return jsonify({"error": "Задача не найдена"}), 404

    task['title'] = request.json.get('title', task['title'])
    task['done'] = request.json.get('done', task['done'])
    return jsonify(task)

# Маршрут для удаления задачи
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return jsonify({"message": "Задача удалена"}), 200

# Запуск приложения
if __name__ == '__main__':
    app.run(debug=True)