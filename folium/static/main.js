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
                    // Перезагружаем страницу для обновления карты
                    window.location.reload();
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
                    // Если есть результаты поиска
                    if (data.results && data.results.length > 0) {
                        // Центрируем карту на первом результате
                        const firstResult = data.results[0];
                        const map = window.leafletMap;
                        if (map) {
                            map.setView([firstResult.lat, firstResult.lon], 17);

                            // Показываем информационную панель
                            showDetails(firstResult.id);
                        }
                    } else {
                        alert('Ничего не найдено');
                    }
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

// Функция для отображения детальной информации о корпусе
function showDetails(campusId) {
    fetch(`/campus/${campusId}`)
        .then(response => response.json())
        .then(campus => {
            const infoPanel = document.getElementById('info-panel');
            const infoTitle = document.getElementById('info-title');
            const infoContent = document.getElementById('info-content');

            infoTitle.textContent = campus.name;

            let content = `
                <p><strong>Адрес:</strong> ${campus.address}</p>
                <p><strong>Категория:</strong> ${campus.category.charAt(0).toUpperCase() + campus.category.slice(1)}</p>
                <p><strong>Телефон:</strong> ${campus.phone}</p>
                <p><strong>Год постройки:</strong> ${campus.year_built}</p>
                <p><strong>Количество этажей:</strong> ${campus.floors}</p>
            `;

            if (campus.students_capacity) {
                content += `<p><strong>Вместимость студентов:</strong> ${campus.students_capacity}</p>`;
            }

            if (campus.capacity) {
                content += `<p><strong>Вместимость:</strong> ${campus.capacity}</p>`;
            }

            if (campus.faculties) {
                content += `<p><strong>Факультеты:</strong> ${campus.faculties.join(', ')}</p>`;
            }

            if (campus.facilities) {
                content += `<p><strong>Удобства:</strong> ${campus.facilities.join(', ')}</p>`;
            }

            if (campus.services) {
                content += `<p><strong>Услуги:</strong> ${campus.services.join(', ')}</p>`;
            }

            if (campus.meal_times) {
                content += `<p><strong>Время приёма пищи:</strong></p><ul>`;
                for (const [meal, time] of Object.entries(campus.meal_times)) {
                    content += `<li>${meal}: ${time}</li>`;
                }
                content += `</ul>`;
            }

            content += `<p><a href="${campus.website}" target="_blank">Официальный сайт</a></p>`;

            infoContent.innerHTML = content;
            infoPanel.style.display = 'block';
        });
}