import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [ws, setWs] = useState(null);
  const [progress, setProgress] = useState({ completed: 0, total: 0 });
  const [status, setStatus] = useState('Готов к пути');
  const [currentTranslation, setCurrentTranslation] = useState('');
  const [stats, setStats] = useState({});

  useEffect(() => {
    const websocket = new WebSocket('ws://localhost:8000/ws');
    
    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'progress':
          setProgress(data.data);
          setCurrentTranslation(`${data.data.current_key} -> ${data.data.current_translation}`);
          break;
        case 'status':
          setStatus(data.data.message);
          break;
        case 'error':
          setStatus(`Ошибка: ${data.data.message}`);
          break;
      }
    };
    
    setWs(websocket);
    
    axios.get('/api/stats').then(res => setStats(res.data));
    
    return () => websocket.close();
  }, []);

  const startTranslation = async () => {
    try {
      await axios.post('/api/start-translation');
    } catch (error) {
      setStatus('Ошибка запуска: ' + error.message);
    }
  };

  const translateSingle = async () => {
    const text = prompt('Введите текст для перевода:');
    if (text) {
      try {
        const response = await axios.post('/api/translate', { text });
        alert(`Перевод: ${response.data.translated}`);
      } catch (error) {
        alert('Ошибка перевода: ' + error.message);
      }
    }
  };

  const progressPercent = progress.total > 0 ? 
    Math.round((progress.completed / progress.total) * 100) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
            🌟 GTNH Переводчик 🌟
          </h1>
          <p className="text-xl text-blue-200">Путь к просветлению через перевод</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold mb-2">📊 Всего записей</h3>
            <p className="text-3xl font-bold text-yellow-400">{stats.total_entries || 0}</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold mb-2">📚 В словаре</h3>
            <p className="text-3xl font-bold text-green-400">{stats.dictionary_size || 0}</p>
          </div>
          
          <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
            <h3 className="text-lg font-semibold mb-2">✅ Переведено</h3>
            <p className="text-3xl font-bold text-cyan-400">{stats.completed_count || 0}</p>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">🌀 Прогресс перевода</h2>
            <span className="text-lg font-semibold">{progressPercent}%</span>
          </div>
          
          <div className="w-full bg-gray-700 rounded-full h-4 mb-4">
            <div 
              className="bg-gradient-to-r from-green-400 to-blue-500 h-4 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
          
          <p className="text-center text-lg">
            {progress.completed || 0} / {progress.total || 0}
          </p>
          
          {currentTranslation && (
            <p className="text-center text-cyan-300 mt-2">
              🔄 {currentTranslation}
            </p>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 mb-8">
          <h2 className="text-2xl font-bold mb-4">🧘‍♂️ Состояние пути</h2>
          <p className="text-xl text-center py-4 bg-black/20 rounded-lg">
            {status}
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <button
            onClick={startTranslation}
            className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl font-bold text-lg hover:from-green-600 hover:to-emerald-700 transition-all transform hover:scale-105 shadow-lg"
          >
            🚀 Начать путь к просветлению
          </button>
          
          <button
            onClick={translateSingle}
            className="px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl font-bold text-lg hover:from-purple-600 hover:to-pink-700 transition-all transform hover:scale-105 shadow-lg"
          >
            🔮 Перевести строку
          </button>
        </div>

        <div className="text-center text-blue-200">
          <p className="italic">"Каждый ключ в JSON - это мантра, каждый перевод - шаг к нирване"</p>
          <p className="mt-2">Создано с ❤️ для сообщества GTNH</p>
        </div>
      </div>
    </div>
  );
}

export default App;