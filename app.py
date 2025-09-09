# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from gigachat_client import giga_client
import os

# Создаём приложение Flask
app = Flask(__name__, static_folder="files", static_url_path="/files")

# Настраиваем CORS — разрешаем только твой домен
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://aidevushka.ru",
            "https://www.aidevushka.ru"
        ]
    }
})

DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"


# === Роуты ===

@app.route('/')
def home():
    return """
    <h1>🚀 Сервер ИИ-девушки Ани работает!</h1>
    <p>Перейдите на <a href="https://aidevushka.ru/">страницу чата</a>.</p>
    <p>API доступно по адресу: <code>/api/chat</code></p>
    """


@app.route('/index.html')
def serve_index():
    return send_from_directory('.', 'index.html')


@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Нет данных в запросе"}), 400

        user_message = data.get('message')
        user_id = data.get('user_id', 'default_user')

        if not user_message or not user_message.strip():
            return jsonify({"error": "Сообщение пустое"}), 400

        if DEBUG_MODE:
            print(f"[{user_id}] >>> {user_message}")

        ai_response = giga_client.send_message(user_id, user_message.strip())

        if DEBUG_MODE:
            print(f"[{user_id}] <<< {ai_response}")

        return jsonify({"reply": ai_response, "user_id": user_id})

    except Exception as e:
        print(f"❌ Ошибка в chat_api: {e}")
        return jsonify({
            "error": "Внутренняя ошибка сервера",
            "reply": "Ой, что-то я сегодня рассеянная... 😅 Давай попробуем еще раз?",
            "user_id": data.get('user_id', 'unknown') if 'data' in locals() else 'unknown'
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        test_response = giga_client.send_message('health_check', 'привет')
        return jsonify({
            "status": "healthy",
            "server": "running",
            "gigachat": "connected",
            "test_response": test_response[:50] + "..." if len(test_response) > 50 else test_response
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "server": "running",
            "gigachat": "disconnected",
            "error": str(e)
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_chat():
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')

        if user_id in giga_client.sessions:
            del giga_client.sessions[user_id]
            if DEBUG_MODE:
                print(f"♻️ История сброшена для {user_id}")

        return jsonify({"status": "success", "message": "История диалога сброшена", "user_id": user_id})

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# === Запуск ===
if __name__ == "__main__":
    print("🔄 Запуск локального сервера...")
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=DEBUG_MODE,
        threaded=True
    )


