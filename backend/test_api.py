import requests

def test_api():
    try:
        # Проверяем здоровье API
        response = requests.get("http://127.0.0.1:8080/api/health")
        print("✅ API здоровье:", response.json())
        
        # Проверяем статистику
        response = requests.get("http://127.0.0.1:8080/api/stats")
        print("📊 Статистика:", response.json())
        
        # Тестируем перевод
        response = requests.post("http://127.0.0.1:8080/api/translate", 
                               json={"text": "Energy Hatch"})
        print("🔄 Перевод:", response.json())
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_api()