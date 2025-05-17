from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import folium
from folium.plugins import MarkerCluster, Search, Fullscreen, MeasureControl, LocateControl, MiniMap, Draw
import os
import json
from typing import List, Dict, Any, Optional

# Создаем FastAPI приложение
app = FastAPI(title="ИГУ Карта Корпусов")

# Настраиваем шаблоны и статические файлы
templates_dir = "templates"
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

static_dir = "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Данные о корпусах ИГУ
campus_data = [
    {
        "id": 1,
        "name": "Главный корпус ИГУ",
        "address": "ул. Карла Маркса, 1, Иркутск",
        "lat": 52.2851,
        "lon": 104.2813,
        "category": "администрация",
        "description": "Главный административный корпус Иркутского государственного университета",
        "year_built": 1931,
        "floors": 4,
        "students_capacity": 500,
        "phone": "+7 (3952) 24-34-53",
        "website": "https://isu.ru",
        "faculties": ["Ректорат", "Приемная комиссия"]
    },
    {
        "id": 2,
        "name": "Исторический факультет",
        "address": "ул. Чкалова, 2, Иркутск",
        "lat": 52.2842,
        "lon": 104.2855,
        "category": "учебное",
        "description": "Корпус исторического факультета ИГУ",
        "year_built": 1940,
        "floors": 3,
        "students_capacity": 800,
        "phone": "+7 (3952) 24-37-25",
        "website": "https://hist.isu.ru",
        "faculties": ["Исторический факультет", "Факультет психологии"]
    },
    {
        "id": 3,
        "name": "Биолого-почвенный факультет",
        "address": "ул. Сухэ-Батора, 5, Иркутск",
        "lat": 52.2867,
        "lon": 104.2826,
        "category": "учебное",
        "description": "Корпус биолого-почвенного факультета ИГУ",
        "year_built": 1960,
        "floors": 4,
        "students_capacity": 600,
        "phone": "+7 (3952) 24-18-55",
        "website": "https://bio.isu.ru",
        "faculties": ["Биолого-почвенный факультет"]
    },
    {
        "id": 4,
        "name": "Физический факультет",
        "address": "бульвар Гагарина, 20, Иркутск",
        "lat": 52.2731,
        "lon": 104.2767,
        "category": "учебное",
        "description": "Корпус физического факультета ИГУ",
        "year_built": 1965,
        "floors": 5,
        "students_capacity": 750,
        "phone": "+7 (3952) 52-12-70",
        "website": "https://physdep.isu.ru",
        "faculties": ["Физический факультет"]
    },
    {
        "id": 5,
        "name": "Химический факультет",
        "address": "ул. Лермонтова, 126, Иркутск",
        "lat": 52.2501,
        "lon": 104.2591,
        "category": "учебное",
        "description": "Корпус химического факультета ИГУ",
        "year_built": 1975,
        "floors": 6,
        "students_capacity": 700,
        "phone": "+7 (3952) 42-59-51",
        "website": "https://chem.isu.ru",
        "faculties": ["Химический факультет"]
    },
    {
        "id": 6,
        "name": "Факультет психологии",
        "address": "ул. Чкалова, 2, Иркутск",
        "lat": 52.2845,
        "lon": 104.2858,
        "category": "учебное",
        "description": "Корпус факультета психологии ИГУ",
        "year_built": 1940,
        "floors": 3,
        "students_capacity": 400,
        "phone": "+7 (3952) 24-39-95",
        "website": "https://psycho.isu.ru",
        "faculties": ["Факультет психологии"]
    },
    {
        "id": 7,
        "name": "Юридический институт",
        "address": "ул. Улан-Баторская, 10, Иркутск",
        "lat": 52.2611,
        "lon": 104.3020,
        "category": "учебное",
        "description": "Юридический институт ИГУ",
        "year_built": 1998,
        "floors": 5,
        "students_capacity": 1200,
        "phone": "+7 (3952) 52-11-91",
        "website": "https://lawinst.isu.ru",
        "faculties": ["Юридический институт"]
    },
    {
        "id": 8,
        "name": "Международный институт экономики и лингвистики",
        "address": "ул. Ленина, 8, Иркутск",
        "lat": 52.2889,
        "lon": 104.2836,
        "category": "учебное",
        "description": "Международный институт экономики и лингвистики ИГУ",
        "year_built": 1988,
        "floors": 4,
        "students_capacity": 900,
        "phone": "+7 (3952) 24-68-39",
        "website": "https://miel.isu.ru",
        "faculties": ["Институт экономики и лингвистики"]
    },
    {
        "id": 9,
        "name": "Институт математики, экономики и информатики",
        "address": "бульвар Гагарина, 20, Иркутск",
        "lat": 52.2735,
        "lon": 104.2773,
        "category": "учебное",
        "description": "Институт математики, экономики и информатики ИГУ",
        "year_built": 1965,
        "floors": 5,
        "students_capacity": 1000,
        "phone": "+7 (3952) 52-12-77",
        "website": "https://math.isu.ru",
        "faculties": ["Институт математики, экономики и информатики"]
    },
    {
        "id": 10,
        "name": "Педагогический институт",
        "address": "ул. Нижняя Набережная, 6, Иркутск",
        "lat": 52.2905,
        "lon": 104.2796,
        "category": "учебное",
        "description": "Педагогический институт ИГУ",
        "year_built": 1955,
        "floors": 4,
        "students_capacity": 1500,
        "phone": "+7 (3952) 20-07-20",
        "website": "https://pi.isu.ru",
        "faculties": ["Педагогический институт"]
    },
    {
        "id": 11,
        "name": "Общежитие №1",
        "address": "ул. Улан-Баторская, 2, Иркутск",
        "lat": 52.2606,
        "lon": 104.3005,
        "category": "общежитие",
        "description": "Общежитие №1 ИГУ",
        "year_built": 1980,
        "floors": 9,
        "students_capacity": 450,
        "phone": "+7 (3952) 52-15-44",
        "website": "https://isu.ru/hostel",
        "facilities": ["Прачечная", "Спортзал", "Читальный зал"]
    },
    {
        "id": 12,
        "name": "Общежитие №2",
        "address": "ул. Улан-Баторская, 4, Иркутск",
        "lat": 52.2608,
        "lon": 104.3010,
        "category": "общежитие",
        "description": "Общежитие №2 ИГУ",
        "year_built": 1982,
        "floors": 9,
        "students_capacity": 500,
        "phone": "+7 (3952) 52-15-46",
        "website": "https://isu.ru/hostel",
        "facilities": ["Прачечная", "Кафе", "Читальный зал"]
    },
    {
        "id": 13,
        "name": "Научная библиотека",
        "address": "бульвар Гагарина, 24, Иркутск",
        "lat": 52.2722,
        "lon": 104.2761,
        "category": "библиотека",
        "description": "Научная библиотека ИГУ",
        "year_built": 1970,
        "floors": 3,
        "capacity": 300,
        "book_count": 1500000,
        "phone": "+7 (3952) 24-29-74",
        "website": "https://library.isu.ru",
        "services": ["Абонемент", "Читальный зал", "Электронные ресурсы"]
    },
    {
        "id": 14,
        "name": "Спортивный комплекс",
        "address": "ул. Ленина, 3, Иркутск",
        "lat": 52.2893,
        "lon": 104.2823,
        "category": "спорт",
        "description": "Спортивный комплекс ИГУ",
        "year_built": 1972,
        "floors": 2,
        "capacity": 500,
        "phone": "+7 (3952) 24-63-62",
        "website": "https://sport.isu.ru",
        "facilities": ["Большой зал", "Тренажерный зал", "Бассейн", "Тир"]
    },
    {
        "id": 15,
        "name": "Общежитие №3",
        "address": "ул. Улан-Баторская, 6, Иркутск",
        "lat": 52.2610,
        "lon": 104.3015,
        "category": "общежитие",
        "description": "Общежитие №3 ИГУ",
        "year_built": 1985,
        "floors": 9,
        "students_capacity": 480,
        "phone": "+7 (3952) 52-15-48",
        "website": "https://isu.ru/hostel",
        "facilities": ["Прачечная", "Комната отдыха", "Учебная комната"]
    },
    {
        "id": 16,
        "name": "Культурно-досуговый центр",
        "address": "ул. Карла Маркса, 3, Иркутск",
        "lat": 52.2855,
        "lon": 104.2820,
        "category": "культура",
        "description": "Культурно-досуговый центр ИГУ",
        "year_built": 1995,
        "floors": 2,
        "capacity": 300,
        "phone": "+7 (3952) 24-35-90",
        "website": "https://culture.isu.ru",
        "facilities": ["Актовый зал", "Танцевальные студии", "Музей"]
    },
    {
        "id": 17,
        "name": "Столовая ИГУ",
        "address": "ул. Карла Маркса, 2, Иркутск",
        "lat": 52.2853,
        "lon": 104.2817,
        "category": "питание",
        "description": "Главная столовая ИГУ",
        "year_built": 1960,
        "floors": 1,
        "capacity": 200,
        "phone": "+7 (3952) 24-36-50",
        "website": "https://isu.ru/dining",
        "meal_times": {"Завтрак": "8:00-10:00", "Обед": "12:00-15:00", "Ужин": "17:00-19:00"}
    },
    {
        "id": 18,
        "name": "Медицинский пункт",
        "address": "ул. Карла Маркса, 1, Иркутск",
        "lat": 52.2850,
        "lon": 104.2814,
        "category": "медицина",
        "description": "Медицинский пункт ИГУ",
        "year_built": 1970,
        "floors": 1,
        "capacity": 50,
        "phone": "+7 (3952) 24-34-70",
        "website": "https://health.isu.ru",
        "services": ["Первая помощь", "Профосмотры", "Вакцинация"]
    }
]

# Определение категорий и иконок для них
category_icons = {
    "администрация": "/static/icons/admin.png",
    "учебное": "/static/icons/education.png",
    "общежитие": "/static/icons/dormitory.png",
    "библиотека": "/static/icons/library.png",
    "спорт": "/static/icons/sport.png",
    "культура": "/static/icons/culture.png",
    "питание": "/static/icons/food.png",
    "медицина": "/static/icons/medicine.png"
}

# Цвета маркеров для каждой категории
category_colors = {
    "администрация": "darkblue",
    "учебное": "green",
    "общежитие": "orange",
    "библиотека": "purple",
    "спорт": "red",
    "культура": "pink",
    "питание": "cadetblue",
    "медицина": "darkred"
}


# Создаем иконки для каждой категории
def create_icon_files():
    """Создает директорию для иконок и создает заглушки для иконок"""
    icons_dir = os.path.join(static_dir, "icons")
    os.makedirs(icons_dir, exist_ok=True)

    # Определение иконок для различных категорий
    icon_mapping = {
        "admin.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
        "education.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
        "dormitory.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png",
        "library.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png",
        "sport.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
        "culture.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-pink.png",
        "food.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-cadetblue.png",
        "medicine.png": "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-darkred.png"
    }

    # Создаем заглушки для иконок
    for icon_name in icon_mapping.keys():
        icon_path = os.path.join(icons_dir, icon_name)
        if not os.path.exists(icon_path):
            with open(icon_path, 'w') as f:
                f.write(f"# Icon placeholder for {icon_name}")


# Создаем CSS файл для темной темы
def create_css_files():
    """Создает CSS файлы для темной и светлой темы"""
    css_dir = static_dir

    # Тёмная тема CSS
    dark_css = """
    body.dark-theme {
        background-color: #121212;
        color: #e0e0e0;
    }

    .dark-theme .sidebar {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border-color: #333;
    }

    .dark-theme .btn {
        background-color: #333;
        color: #e0e0e0;
        border-color: #444;
    }

    .dark-theme .btn:hover {
        background-color: #444;
    }

    .dark-theme .form-control {
        background-color: #333;
        color: #e0e0e0;
        border-color: #444;
    }

    .dark-theme .card {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border-color: #333;
    }

    .dark-theme .modal-content {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border-color: #333;
    }

    .dark-theme .dropdown-menu {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border-color: #333;
    }

    .dark-theme .dropdown-item {
        color: #e0e0e0;
    }

    .dark-theme .dropdown-item:hover {
        background-color: #333;
    }
    """

    # Основной CSS
    main_css = """
    body {
        margin: 0;
        padding: 0;
        font-family: 'Roboto', sans-serif;
        transition: background-color 0.3s, color 0.3s;
    }

    #map-container {
        position: relative;
        height: 100vh;
        width: 100%;
    }

    #map {
        height: 100%;
        width: 100%;
    }

    .sidebar {
        position: absolute;
        top: 10px;
        left: 10px;
        background: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        max-width: 300px;
        max-height: 90vh;
        overflow-y: auto;
        transition: all 0.3s ease;
    }

    .sidebar h3 {
        margin-top: 0;
    }

    .search-container {
        margin-bottom: 15px;
    }

    .search-container input {
        width: 100%;
        padding: 8px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .filter-container {
        margin-bottom: 15px;
    }

    .filter-title {
        font-weight: bold;
        margin-bottom: 5px;
    }

    .theme-toggle {
        margin-top: 15px;
    }

    .legend {
        margin-top: 15px;
    }

    .legend-item {
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }

    .legend-color {
        width: 20px;
        height: 20px;
        margin-right: 10px;
        border-radius: 50%;
    }

    .info-panel {
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        max-width: 300px;
        display: none;
        transition: all 0.3s ease;
    }

    .info-panel h4 {
        margin-top: 0;
    }

    .info-close {
        position: absolute;
        top: 5px;
        right: 5px;
        cursor: pointer;
    }

    .btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 8px 16px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 4px;
        transition: background-color 0.3s;
    }

    .btn:hover {
        background-color: #45a049;
    }

    .toggle-switch {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }

    .toggle-switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: .4s;
        border-radius: 34px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: white;
        transition: .4s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: #2196F3;
    }

    input:focus + .slider {
        box-shadow: 0 0 1px #2196F3;
    }

    input:checked + .slider:before {
        transform: translateX(26px);
    }

    .hide-sidebar {
        transform: translateX(-320px);
    }

    .toggle-sidebar {
        position: absolute;
        top: 10px;
        left: 320px;
        background: white;
        padding: 8px 12px;
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        cursor: pointer;
    }

    @media screen and (max-width: 768px) {
        .sidebar {
            max-width: 250px;
        }

        .toggle-sidebar {
            left: 270px;
        }
    }
    """

    # Записываем CSS файлы
    with open(os.path.join(css_dir, "dark-theme.css"), 'w') as f:
        f.write(dark_css)

    with open(os.path.join(css_dir, "style.css"), 'w') as f:
        f.write(main_css)


# Создаем JavaScript файл для интерактивных функций
def create_js_files():
    """Создает JavaScript файл для интерактивных функций"""
    js_dir = static_dir

    # Основной JavaScript
    main_js = """
    document.addEventListener('DOMContentLoaded', function() {
        // Переключение темы
        const themeToggle = document.getElementById('theme-toggle');
        const body = document.body;

        themeToggle.addEventListener('change', function() {
            if (this.checked) {
                body.classList.add('dark-theme');
                localStorage.setItem('theme', 'dark');
            } else {
                body.classList.remove('dark-theme');
                localStorage.setItem('theme', 'light');
            }
        });

        // Проверка сохраненной темы
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            body.classList.add('dark-theme');
            themeToggle.checked = true;
        }

        // Переключение боковой панели
        const toggleSidebarBtn = document.getElementById('toggle-sidebar');
        const sidebar = document.querySelector('.sidebar');

        toggleSidebarBtn.addEventListener('click', function() {
            sidebar.classList.toggle('hide-sidebar');
            this.textContent = sidebar.classList.contains('hide-sidebar') ? '>' : '<';
        });

        // Фильтрация категорий
        const categoryFilters = document.querySelectorAll('.category-filter');

        categoryFilters.forEach(filter => {
            filter.addEventListener('change', function() {
                const category = this.value;
                const isChecked = this.checked;

                // Отправляем запрос на сервер для фильтрации
                fetch(`/filter?category=${category}&show=${isChecked}`)
                    .then(response => response.json())
                    .then(data => {
                        // Здесь должен быть код для обновления маркеров на карте
                        console.log(`Category ${category} is now ${isChecked ? 'visible' : 'hidden'}`);
                    });
            });
        });

        // Поиск корпусов
        const searchInput = document.getElementById('search-input');
        const searchButton = document.getElementById('search-button');

        searchButton.addEventListener('click', function() {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                fetch(`/search?term=${encodeURIComponent(searchTerm)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Код для выделения найденных корпусов
                        console.log(`Search results for "${searchTerm}":`, data);
                    });
            }
        });

        // Обработка нажатия Enter в поле поиска
        searchInput.addEventListener('keyup', function(event) {
            if (event.key === "Enter") {
                searchButton.click();
            }
        });

        // Закрытие инфо-панели
        const closeInfoBtn = document.querySelector('.info-close');
        const infoPanel = document.querySelector('.info-panel');

        if (closeInfoBtn) {
            closeInfoBtn.addEventListener('click', function() {
                infoPanel.style.display = 'none';
            });
        }
    });
    """

    # Записываем JavaScript файл
    with open(os.path.join(js_dir, "main.js"), 'w') as f:
        f.write(main_js)


# Создаем HTML шаблон для Jinja2
def create_html_template():
    """Создает HTML шаблон для Jinja2"""
    template = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карта корпусов ИГУ</title>
    <link rel="stylesheet" href="{{ url_for('static', path='style.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', path='dark-theme.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    {{ folium_css|safe }}
</head>
<body>
    <div id="map-container">
        <div class="sidebar">
            <h3>Карта корпусов ИГУ</h3>

            <div class="search-container">
                <input type="text" id="search-input" placeholder="Поиск корпуса...">
                <button id="search-button" class="btn">Найти</button>
            </div>

            <div class="filter-container">
                <div class="filter-title">Фильтр по категориям:</div>
                {% for category, color in category_colors.items() %}
                <div>
                    <input type="checkbox" id="filter-{{ category }}" class="category-filter" value="{{ category }}" checked>
                    <label for="filter-{{ category }}">
                        <span class="legend-color" style="background-color: {{ color }};"></span>
                        {{ category|capitalize }}
                    </label>
                </div>
                {% endfor %}
            </div>

            <div class="theme-toggle">
                <label for="theme-toggle" class="toggle-label">Тёмная тема</label>
                <label class="toggle-switch">
                    <input type="checkbox" id="theme-toggle">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="legend">
                <div class="filter-title">Легенда:</div>
                {% for category, color in category_colors.items() %}
                <div class="legend-item">
                    <div class="legend-color" style="background-color: {{ color }};"></div>
                    <div>{{ category|capitalize }}</div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div id="toggle-sidebar" class="toggle-sidebar">&lt;</div>

        <div class="info-panel" id="info-panel">
            <span class="info-close">×</span>
            <h4 id="info-title"></h4>
            <div id="info-content"></div>
        </div>

        <div id="map">
            {{ folium_map|safe }}
        </div>
    </div>

    <script src="{{ url_for('static', path='main.js') }}"></script>
    {{ folium_js|safe }}
</body>
</html>
"""

    # Создаем директорию для шаблонов, если она не существует
    os.makedirs(templates_dir, exist_ok=True)

    # Записываем шаблон
    with open(os.path.join(templates_dir, "index.html"), 'w') as f:
        f.write(template)


# Функция для создания карты с Folium
def create_map(filter_categories=None):
    """
    Создает карту с использованием Folium

    Args:
        filter_categories (list): Список категорий для отображения

    Returns:
        str: HTML-код карты
    """
    # Создаем базовую карту, центрированную на координатах ИГУ
    m = folium.Map(
        location=[52.2851, 104.2813],  # Координаты главного корпуса ИГУ
        zoom_start=14,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # Добавляем дополнительные слои карты
    folium.TileLayer("CartoDB dark_matter", name="Тёмная карта").add_to(m)
    folium.TileLayer("CartoDB positron", name="Светлая карта").add_to(m)
    folium.TileLayer("Stamen Terrain", name="Рельеф").add_to(m)
    folium.TileLayer("Stamen Watercolor", name="Акварель").add_to(m)

    # Добавляем контроль слоев
    folium.LayerControl().add_to(m)

    # Добавляем плагины
    Fullscreen().add_to(m)
    MeasureControl(position="topleft", primary_length_unit="kilometers", secondary_length_unit="miles").add_to(m)
    LocateControl(auto_start=False).add_to(m)
    MiniMap().add_to(m)
    Draw(export=True).add_to(m)

    # Создаем кластеризацию маркеров
    marker_cluster = MarkerCluster().add_to(m)

    # Если категории для фильтрации не указаны, показываем все
    if filter_categories is None:
        filter_categories = list(category_colors.keys())

    # Добавляем маркеры на карту
    for campus in campus_data:
        if campus["category"] in filter_categories:
            # Создаем всплывающее окно с информацией
            popup_content = f"""
            <div style="min-width: 200px;">
                <h4>{campus['name']}</h4>
                <p><strong>Адрес:</strong> {campus['address']}</p>
                <p><strong>Категория:</strong> {campus['category'].capitalize()}</p>
                <p><strong>Телефон:</strong> {campus['phone']}</p>
                <a href="{campus['website']}" target="_blank">Сайт</a>
                <button onclick="showDetails({campus['id']})" style="display: block; margin-top: 10px;">Подробнее</button>
            </div>
            """

            # Создаем маркер с иконкой соответствующей категории
            icon = folium.Icon(color=category_colors[campus["category"]], icon="info-sign")

            folium.Marker(
                location=[campus["lat"], campus["lon"]],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=campus["name"],
                icon=icon
            ).add_to(marker_cluster)

    return m._repr_html_()


# API для фильтрации и поиска
@app.get("/filter")
async def filter_map(category: str, show: bool = True):
    """API для фильтрации карты по категориям"""
    return {"status": "success", "category": category, "show": show}


@app.get("/search")
async def search_campus(term: str):
    """API для поиска корпусов по названию или адресу"""
    term = term.lower()
    results = []

    for campus in campus_data:
        if term in campus["name"].lower() or term in campus["address"].lower():
            results.append(campus)

    return {"results": results}


@app.get("/campus/{campus_id}")
async def get_campus_details(campus_id: int):
    """API для получения детальной информации о корпусе"""
    for campus in campus_data:
        if campus["id"] == campus_id:
            return campus

    return {"error": "Campus not found"}


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с картой"""
    # Создаем файлы перед рендерингом страницы
    create_icon_files()
    create_css_files()
    create_js_files()
    create_html_template()

    # Создаем карту
    folium_map = create_map()

    # Рендерим шаблон
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "folium_map": folium_map,
            "category_colors": category_colors
        }
    )


# Функция для генерации готового HTML для самостоятельного использования
@app.get("/export", response_class=HTMLResponse)
async def export_html():
    """Создает автономный HTML-файл с картой"""
    # Создаем карту
    folium_map = create_map()

    # Создаем HTML-код с встроенными CSS и JavaScript
    with open(os.path.join(static_dir, "style.css"), 'r') as f:
        css = f.read()

    with open(os.path.join(static_dir, "dark-theme.css"), 'r') as f:
        dark_css = f.read()

    with open(os.path.join(static_dir, "main.js"), 'r') as f:
        js = f.read()

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карта корпусов ИГУ</title>
    <style>
        {css}
        {dark_css}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
</head>
<body>
    <div id="map-container">
        <div class="sidebar">
            <h3>Карта корпусов ИГУ</h3>

            <div class="search-container">
                <input type="text" id="search-input" placeholder="Поиск корпуса...">
                <button id="search-button" class="btn">Найти</button>
            </div>

            <div class="filter-container">
                <div class="filter-title">Фильтр по категориям:</div>
                {generate_filter_html()}
            </div>

            <div class="theme-toggle">
                <label for="theme-toggle" class="toggle-label">Тёмная тема</label>
                <label class="toggle-switch">
                    <input type="checkbox" id="theme-toggle">
                    <span class="slider"></span>
                </label>
            </div>

            <div class="legend">
                <div class="filter-title">Легенда:</div>
                {generate_legend_html()}
            </div>
        </div>

        <div id="toggle-sidebar" class="toggle-sidebar">&lt;</div>

        <div class="info-panel" id="info-panel">
            <span class="info-close">×</span>
            <h4 id="info-title"></h4>
            <div id="info-content"></div>
        </div>

        <div id="map">
            {folium_map}
        </div>
    </div>

    <script>
        {js}

        // Дополнительный код для обработки информации о корпусах
        const campusData = {json.dumps(campus_data)};

        function showDetails(campusId) {{
            const campus = campusData.find(c => c.id === campusId);
            if (campus) {{
                const infoPanel = document.getElementById('info-panel');
                const infoTitle = document.getElementById('info-title');
                const infoContent = document.getElementById('info-content');

                infoTitle.textContent = campus.name;

                let content = `
                    <p><strong>Адрес:</strong> ${{campus.address}}</p>
                    <p><strong>Категория:</strong> ${{campus.category.charAt(0).toUpperCase() + campus.category.slice(1)}}</p>
                    <p><strong>Телефон:</strong> ${{campus.phone}}</p>
                    <p><strong>Год постройки:</strong> ${{campus.year_built}}</p>
                    <p><strong>Количество этажей:</strong> ${{campus.floors}}</p>
                `;

                if (campus.students_capacity) {{
                    content += `<p><strong>Вместимость студентов:</strong> ${{campus.students_capacity}}</p>`;
                }}

                if (campus.capacity) {{
                    content += `<p><strong>Вместимость:</strong> ${{campus.capacity}}</p>`;
                }}

                if (campus.faculties) {{
                    content += `<p><strong>Факультеты:</strong> ${{campus.faculties.join(', ')}}</p>`;
                }}

                if (campus.facilities) {{
                    content += `<p><strong>Удобства:</strong> ${{campus.facilities.join(', ')}}</p>`;
                }}

                if (campus.services) {{
                    content += `<p><strong>Услуги:</strong> ${{campus.services.join(', ')}}</p>`;
                }}

                if (campus.meal_times) {{
                    content += `<p><strong>Время приёма пищи:</strong></p><ul>`;
                    for (const [meal, time] of Object.entries(campus.meal_times)) {{
                        content += `<li>${{meal}}: ${{time}}</li>`;
                    }}
                    content += `</ul>`;
                }}

                content += `<p><a href="${{campus.website}}" target="_blank">Официальный сайт</a></p>`;

                infoContent.innerHTML = content;
                infoPanel.style.display = 'block';
            }}
        }}
    </script>
</body>
</html>
    """

    return html


def generate_filter_html():
    """Генерирует HTML-код для фильтров категорий"""
    html = ""
    for category, color in category_colors.items():
        html += f"""
        <div>
            <input type="checkbox" id="filter-{category}" class="category-filter" value="{category}" checked>
            <label for="filter-{category}">
                <span class="legend-color" style="background-color: {color};"></span>
                {category.capitalize()}
            </label>
        </div>
        """
    return html


def generate_legend_html():
    """Генерирует HTML-код для легенды"""
    html = ""
    for category, color in category_colors.items():
        html += f"""
        <div class="legend-item">
            <div class="legend-color" style="background-color: {color};"></div>
            <div>{category.capitalize()}</div>
        </div>
        """
    return html


# Запуск приложения
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)