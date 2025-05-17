"""
Интерактивный дашборд для визуализации данных Gapminder
----------------------------------------------------
Этот скрипт создает Dash-приложение с интерактивными визуализациями данных Gapminder.
Пользователи могут исследовать демографические и экономические данные разных стран 
с 1952 по 2007 год с помощью интерактивных графиков и фильтров.

Функциональность:
1. Линейный график с возможностью выбора нескольких стран для сравнения
2. Пузырьковая диаграмма с настраиваемыми осями и размером пузырьков
3. Топ-15 стран по населению с возможностью выбора года
4. Круговая диаграмма распределения населения по континентам

Автор: snaart
Дата: 10.05.2025
"""

# ---------------------------------- ИМПОРТ БИБЛИОТЕК ----------------------------------
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ---------------------------------- КОНСТАНТЫ И ПАРАМЕТРЫ ----------------------------------

# URL набора данных
DATASET_URL = 'https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv'

# Словарь для человекочитаемых названий метрик
METRIC_LABELS = {
    'lifeExp': 'Продолжительность жизни (лет)',
    'pop': 'Население (человек)',
    'gdpPercap': 'ВВП на душу населения (USD)'
}

# Цветовые схемы для разных графиков
COLOR_SCHEME = {
    'line': px.colors.qualitative.Plotly,
    'bubble': px.colors.qualitative.Bold,
    'bar': px.colors.qualitative.G10,
    'pie': px.colors.qualitative.Pastel
}

# Словарь стилей для единообразного оформления элементов
STYLES = {
    # Основной контейнер дашборда
    'container': {
        'max-width': '1200px',
        'margin': '0 auto',
        'padding': '20px',
        'font-family': 'Arial, sans-serif',
        'background-color': '#f8f9fa'
    },
    
    # Заголовок дашборда
    'header': {
        'text-align': 'center',
        'padding': '20px 0',
        'margin-bottom': '20px',
        'color': '#2c3e50',
        'font-weight': 'bold',
        'background-color': 'white',
        'border-radius': '8px',
        'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
    },
    
    # Карточка для графика
    'card': {
        'background-color': 'white',
        'border-radius': '8px',
        'box-shadow': '0 2px 6px rgba(0,0,0,0.1)',
        'padding': '20px',
        'margin-bottom': '20px'
    },
    
    # Заголовок карточки
    'card_title': {
        'color': '#2c3e50',
        'font-size': '18px',
        'margin-bottom': '15px',
        'border-bottom': '1px solid #eee',
        'padding-bottom': '10px'
    },
    
    # Панель управления
    'control_panel': {
        'background-color': '#f0f2f5',
        'border-radius': '8px',
        'padding': '15px',
        'margin-right': '20px'
    },
    
    # Метка для элементов ввода
    'label': {
        'font-weight': 'bold',
        'margin-top': '10px',
        'margin-bottom': '5px',
        'color': '#34495e'
    },
    
    # Выпадающий список
    'dropdown': {
        'margin-bottom': '15px'
    },
    
    # Слайдер
    'slider': {
        'margin-top': '5px',
        'margin-bottom': '20px',
        'padding': '10px 0'
    },
    
    # Панель с подсказкой
    'hint_panel': {
        'background-color': '#e8f4f8',
        'border-left': '4px solid #3498db',
        'padding': '10px 15px',
        'margin-top': '15px',
        'border-radius': '4px',
        'font-size': '14px'
    },
    
    # Контейнер графика
    'graph_container': {
        'height': '550px'
    },
    
    # Нижний колонтитул
    'footer': {
        'text-align': 'center',
        'padding': '20px 0',
        'margin-top': '20px',
        'color': '#7f8c8d',
        'font-size': '14px',
        'border-top': '1px solid #eee'
    }
}

# ---------------------------------- ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ ----------------------------------

def load_data():
    """
    Загружает и подготавливает набор данных Gapminder
    
    Returns:
        pd.DataFrame: Данные Gapminder
    """
    print("Загрузка набора данных Gapminder...")
    df = pd.read_csv(DATASET_URL)
    
    # Преобразуем численные данные к соответствующим типам
    if df['pop'].dtype != 'int64':
        df['pop'] = df['pop'].astype('int64')
    if df['year'].dtype != 'int64':
        df['year'] = df['year'].astype('int64')
        
    print(f"Загружено {df.shape[0]} записей с данными о {df['country'].nunique()} странах за {df['year'].nunique()} лет")
    return df

# ---------------------------------- ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ----------------------------------

app = Dash(
    __name__, 
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    title="Интерактивный дашборд Gapminder"
)

# Настройка макета страницы
app.config.suppress_callback_exceptions = True

# Загрузка данных
df = load_data()

# Получение уникальных значений для элементов управления
years = sorted(df['year'].unique())
countries = sorted(df['country'].unique())

# Опции для выпадающих списков метрик
metric_options = [{'label': label, 'value': metric} for metric, label in METRIC_LABELS.items()]

# ---------------------------------- КОМПОНЕНТЫ ИНТЕРФЕЙСА ----------------------------------

def create_info_box():
    """
    Создает информационную панель с описанием дашборда
    
    Returns:
        html.Div: Информационная панель
    """
    return html.Div([
        html.H4("О данных Gapminder", style={"margin-bottom": "10px", "color": "#2c3e50"}),
        html.P([
            "Этот дашборд визуализирует набор данных Gapminder, который содержит информацию ",
            "о продолжительности жизни, численности населения и ВВП на душу населения для ",
            "различных стран мира с 1952 по 2007 год. Вы можете исследовать изменения этих ",
            "показателей с течением времени и сравнивать разные страны и континенты."
        ], style={"line-height": "1.5"}),
    ], style={
        "background-color": "#e3f2fd", 
        "padding": "15px", 
        "border-radius": "8px",
        "margin-bottom": "20px",
        "box-shadow": "0 2px 4px rgba(0,0,0,0.05)"
    })

def create_hint(text):
    """
    Создает панель с подсказкой
    
    Args:
        text (str): Текст подсказки
    
    Returns:
        html.Div: Панель с подсказкой
    """
    return html.Div([
        html.P([html.Strong("💡 Подсказка: "), text]),
    ], style=STYLES["hint_panel"])

# ---------------------------------- КОМПОНЕНТЫ ВКЛАДОК ----------------------------------

def create_line_chart_tab():
    """
    Создает вкладку с линейным графиком и элементами управления
    
    Returns:
        html.Div: Содержимое вкладки с линейным графиком
    """
    return html.Div([
        html.Div([
            html.H3("Сравнение стран на линейном графике", style=STYLES["card_title"]),
            
            # Структура с панелью управления и графиком
            html.Div([
                # Панель управления
                html.Div([
                    html.Label("Выберите страны для сравнения:", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="line-country-selection",
                        options=[{"label": country, "value": country} for country in countries],
                        value=["China", "United States", "Russia", "India"],
                        multi=True,
                        style=STYLES["dropdown"],
                        placeholder="Выберите одну или несколько стран"
                    ),
                    
                    html.Label("Выберите показатель для оси Y:", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="line-y-axis-selection",
                        options=metric_options,
                        value="lifeExp",
                        style=STYLES["dropdown"]
                    ),
                    
                    create_hint(
                        "Выберите несколько стран, чтобы сравнить изменение выбранного показателя "
                        "с течением времени. Для удаления страны из выбора нажмите на её название "
                        "в легенде графика."
                    )
                ], style={"width": "25%", "display": "inline-block", "vertical-align": "top", **STYLES["control_panel"]}),
                
                # График
                html.Div([
                    dcc.Graph(id="line-chart", style=STYLES["graph_container"])
                ], style={"width": "70%", "display": "inline-block", "vertical-align": "top"})
            ], style={"display": "flex"})
        ], style=STYLES["card"])
    ])

def create_bubble_chart_tab():
    """
    Создает вкладку с пузырьковой диаграммой и элементами управления
    
    Returns:
        html.Div: Содержимое вкладки с пузырьковой диаграммой
    """
    return html.Div([
        html.Div([
            html.H3("Многомерный анализ стран мира", style=STYLES["card_title"]),
            
            # Структура с панелью управления и графиком
            html.Div([
                # Панель управления
                html.Div([
                    html.Div("Настройте оси и размер пузырьков:", 
                             style={"font-weight": "bold", "margin-bottom": "15px", "color": "#34495e"}),
                    
                    html.Label("Ось X:", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="bubble-x-axis",
                        options=metric_options,
                        value="gdpPercap",
                        style=STYLES["dropdown"]
                    ),
                    
                    html.Label("Ось Y:", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="bubble-y-axis",
                        options=metric_options,
                        value="lifeExp",
                        style=STYLES["dropdown"]
                    ),
                    
                    html.Label("Размер пузырька:", style=STYLES["label"]),
                    dcc.Dropdown(
                        id="bubble-size",
                        options=metric_options,
                        value="pop",
                        style=STYLES["dropdown"]
                    ),
                    
                    html.Label("Выберите год:", style=STYLES["label"]),
                    dcc.Slider(
                        id="year-slider",
                        min=min(years),
                        max=max(years),
                        value=max(years),
                        marks={year: str(year) for year in years},
                        step=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        style=STYLES["slider"]
                    ),
                    
                    create_hint(
                        "Пузырьковая диаграмма позволяет анализировать сразу три метрики одновременно: "
                        "значения по осям X и Y, а также размер пузырька. Цвет пузырьков "
                        "соответствует континенту."
                    )
                ], style={"width": "25%", "display": "inline-block", "vertical-align": "top", **STYLES["control_panel"]}),
                
                # График
                html.Div([
                    dcc.Graph(id="bubble-chart", style=STYLES["graph_container"])
                ], style={"width": "70%", "display": "inline-block", "vertical-align": "top"})
            ], style={"display": "flex"})
        ], style=STYLES["card"])
    ])

def create_top15_chart_tab():
    """
    Создает вкладку с топ-15 стран по населению и элементами управления
    
    Returns:
        html.Div: Содержимое вкладки с топ-15 стран
    """
    return html.Div([
        html.Div([
            html.H3("Страны с наибольшим населением", style=STYLES["card_title"]),
            
            # Структура с панелью управления и графиком
            html.Div([
                # Панель управления
                html.Div([
                    html.Label("Выберите год:", style=STYLES["label"]),
                    dcc.Slider(
                        id="top15-year-slider",
                        min=min(years),
                        max=max(years),
                        value=max(years),
                        marks={year: str(year) for year in years},
                        step=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        style=STYLES["slider"]
                    ),
                    
                    create_hint(
                        "Перемещайте слайдер года, чтобы увидеть изменения в рейтинге стран по "
                        "населению в разные периоды времени. Обратите внимание на то, как меняется "
                        "относительная позиция стран с течением времени."
                    )
                ], style={"width": "25%", "display": "inline-block", "vertical-align": "top", **STYLES["control_panel"]}),
                
                # График
                html.Div([
                    dcc.Graph(id="top15-chart", style=STYLES["graph_container"])
                ], style={"width": "70%", "display": "inline-block", "vertical-align": "top"})
            ], style={"display": "flex"})
        ], style=STYLES["card"])
    ])

def create_pie_chart_tab():
    """
    Создает вкладку с круговой диаграммой и элементами управления
    
    Returns:
        html.Div: Содержимое вкладки с круговой диаграммой
    """
    return html.Div([
        html.Div([
            html.H3("Распределение населения мира по континентам", style=STYLES["card_title"]),
            
            # Структура с панелью управления и графиком
            html.Div([
                # Панель управления
                html.Div([
                    html.Label("Выберите год:", style=STYLES["label"]),
                    dcc.Slider(
                        id="pie-year-slider",
                        min=min(years),
                        max=max(years),
                        value=max(years),
                        marks={year: str(year) for year in years},
                        step=None,
                        tooltip={"placement": "bottom", "always_visible": True},
                        style=STYLES["slider"]
                    ),
                    
                    create_hint(
                        "Круговая диаграмма наглядно показывает пропорции населения по континентам. "
                        "Перемещайте слайдер, чтобы увидеть, как менялось соотношение населения "
                        "континентов с течением времени."
                    )
                ], style={"width": "25%", "display": "inline-block", "vertical-align": "top", **STYLES["control_panel"]}),
                
                # График
                html.Div([
                    dcc.Graph(id="continent-pie-chart", style=STYLES["graph_container"])
                ], style={"width": "70%", "display": "inline-block", "vertical-align": "top"})
            ], style={"display": "flex"})
        ], style=STYLES["card"])
    ])

# ---------------------------------- МАКЕТ ПРИЛОЖЕНИЯ ----------------------------------

app.layout = html.Div([
    # Заголовок дашборда
    html.Div([
        html.H1("Интерактивная визуализация данных Gapminder"),
        html.P("Исследуйте демографические и экономические показатели стран мира с 1952 по 2007 год")
    ], style=STYLES["header"]),
    
    # Информационная панель
    create_info_box(),
    
    # Система вкладок
    dcc.Tabs([
        dcc.Tab(
            label="Динамика показателей", 
            children=create_line_chart_tab(),
            style={"padding": "10px"},
            selected_style={"padding": "10px", "border-top": "3px solid #3498db"}
        ),
        dcc.Tab(
            label="Пузырьковая диаграмма", 
            children=create_bubble_chart_tab(),
            style={"padding": "10px"},
            selected_style={"padding": "10px", "border-top": "3px solid #3498db"}
        ),
        dcc.Tab(
            label="Топ-15 стран по населению", 
            children=create_top15_chart_tab(),
            style={"padding": "10px"},
            selected_style={"padding": "10px", "border-top": "3px solid #3498db"}
        ),
        dcc.Tab(
            label="Население по континентам", 
            children=create_pie_chart_tab(),
            style={"padding": "10px"},
            selected_style={"padding": "10px", "border-top": "3px solid #3498db"}
        ),
    ], style={"margin-bottom": "20px"}),
    
    # Нижний колонтитул
    html.Footer([
        html.P("Дашборд данных Gapminder — 2025"),
        html.P(["Made with ", html.Span("❤", style={"color": "red"}), " using Dash & Plotly"])
    ], style=STYLES["footer"])
], style=STYLES["container"])

# ---------------------------------- CALLBACK ФУНКЦИИ ----------------------------------

@callback(
    Output("line-chart", "figure"),
    [Input("line-country-selection", "value"),
     Input("line-y-axis-selection", "value")]
)
def update_line_chart(countries, y_axis):
    """
    Обновляет линейный график на основе выбранных стран и метрики
    
    Args:
        countries (list): Список выбранных стран
        y_axis (str): Метрика для оси Y
    
    Returns:
        dict: Объект figure для графика
    """
    # Обработка пустого выбора стран
    if not countries:
        fig = go.Figure()
        fig.update_layout(
            title="Выберите хотя бы одну страну",
            xaxis_title="Год",
            yaxis_title="Значение",
            template="plotly_white"
        )
        return fig
    
    # Фильтрация данных по выбранным странам
    filtered_df = df[df["country"].isin(countries)]
    
    # Создание линейного графика с улучшенным форматированием
    fig = px.line(
        filtered_df, 
        x="year", 
        y=y_axis, 
        color="country",
        labels={
            y_axis: METRIC_LABELS.get(y_axis, y_axis), 
            "year": "Год", 
            "country": "Страна"
        },
        title=f"Динамика показателя «{METRIC_LABELS.get(y_axis, y_axis)}» по странам",
        color_discrete_sequence=COLOR_SCHEME["line"],
        template="plotly_white",
        markers=True,  # Добавляем маркеры для улучшения читаемости точек
        line_shape="spline"  # Сглаживаем линии для лучшего восприятия
    )
    
    # Настройка внешнего вида графика
    fig.update_layout(
        legend={"title": "Страны", "orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"},
        hovermode="closest",
        plot_bgcolor="rgba(240, 240, 240, 0.5)"
    )
    
    # Форматирование осей для улучшения читаемости
    fig.update_xaxes(tickangle=-45, gridcolor="rgba(200, 200, 200, 0.2)")
    fig.update_yaxes(gridcolor="rgba(200, 200, 200, 0.2)")
    
    # Добавление аннотации для описания графика
    fig.add_annotation(
        x=0.5, y=1.12,
        xref="paper", yref="paper",
        text="Изменение показателя с течением времени",
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

@callback(
    Output("bubble-chart", "figure"),
    [Input("bubble-x-axis", "value"),
     Input("bubble-y-axis", "value"),
     Input("bubble-size", "value"),
     Input("year-slider", "value")]
)
def update_bubble_chart(x_axis, y_axis, size, year):
    """
    Обновляет пузырьковую диаграмму на основе выбранных параметров
    
    Args:
        x_axis (str): Метрика для оси X
        y_axis (str): Метрика для оси Y
        size (str): Метрика для размера пузырьков
        year (int): Выбранный год
    
    Returns:
        dict: Объект figure для графика
    """
    # Фильтрация данных по выбранному году
    filtered_df = df[df["year"] == year]
    
    # Используем логарифмический масштаб для больших значений
    use_log_x = x_axis in ["pop", "gdpPercap"]
    use_log_y = y_axis in ["pop", "gdpPercap"]
    
    # Создание пузырьковой диаграммы
    fig = px.scatter(
        filtered_df, 
        x=x_axis, 
        y=y_axis, 
        size=size,
        color="continent", 
        hover_name="country",
        log_x=use_log_x,
        log_y=use_log_y,
        size_max=50,  # Максимальный размер пузырька для лучшей наглядности
        opacity=0.8,  # Прозрачность пузырьков для снижения перекрытия
        labels={
            x_axis: METRIC_LABELS.get(x_axis, x_axis),
            y_axis: METRIC_LABELS.get(y_axis, y_axis),
            size: METRIC_LABELS.get(size, size),
            "continent": "Континент"
        },
        title=f"Сравнение стран по выбранным показателям в {year} году",
        color_discrete_sequence=COLOR_SCHEME["bubble"],
        template="plotly_white",
        hover_data={"country": True, x_axis: True, y_axis: True, size: True}  # Добавляем дополнительные данные для всплывающих подсказок
    )
    
    # Настройка внешнего вида графика
    fig.update_layout(
        legend={"title": "Континенты", "orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"},
        hovermode="closest",
        plot_bgcolor="rgba(240, 240, 240, 0.5)"
    )
    
    # Форматирование осей для улучшения читаемости
    fig.update_xaxes(gridcolor="rgba(200, 200, 200, 0.2)")
    fig.update_yaxes(gridcolor="rgba(200, 200, 200, 0.2)")
    
    # Добавление аннотации для описания графика
    fig.add_annotation(
        x=0.5, y=1.12,
        xref="paper", yref="paper",
        text=f"Данные за {year} год",
        showarrow=False,
        font=dict(size=14, color="#34495e")
    )
    
    return fig

@callback(
    Output("top15-chart", "figure"),
    [Input("top15-year-slider", "value")]
)
def update_top15_chart(year):
    """
    Обновляет столбчатую диаграмму топ-15 стран по населению
    
    Args:
        year (int): Выбранный год
    
    Returns:
        dict: Объект figure для графика
    """
    # Фильтрация данных по выбранному году
    filtered_df = df[df["year"] == year]
    
    # Получение топ-15 стран по населению
    top15 = filtered_df.sort_values("pop", ascending=False).head(15)
    
    # Создание столбчатой диаграммы
    fig = px.bar(
        top15, 
        x="country", 
        y="pop", 
        color="continent",
        text=top15["pop"].apply(lambda x: f"{x:,}".replace(",", " ")),  # Форматирование текста для удобочитаемости
        labels={
            "pop": "Население (человек)", 
            "country": "Страна", 
            "continent": "Континент"
        },
        title=f"Топ-15 стран по населению в {year} году",
        color_discrete_sequence=COLOR_SCHEME["bar"],
        template="plotly_white"
    )
    
    # Сортировка стран по убыванию числа населения
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    
    # Настройка внешнего вида графика
    fig.update_layout(
        legend={"title": "Континенты", "orientation": "h", "y": -0.2, "x": 0.5, "xanchor": "center"},
        plot_bgcolor="rgba(240, 240, 240, 0.5)",
        xaxis_tickangle=-45,  # Наклон подписей стран для лучшей читаемости
        uniformtext_minsize=8,  # Минимальный размер текста на столбцах
        uniformtext_mode='hide'  # Скрывать текст, если он не помещается
    )
    
    # Форматирование осей для улучшения читаемости
    fig.update_yaxes(
        tickformat=",", 
        gridcolor="rgba(200, 200, 200, 0.2)",
        title={"standoff": 20}  # Отступ от оси для лучшей читаемости
    )
    
    # Настройка текста столбцов
    fig.update_traces(texttemplate='%{text:.3s}', textposition='outside')
    
    return fig

@callback(
    Output("continent-pie-chart", "figure"),
    [Input("pie-year-slider", "value")]
)
def update_pie_chart(year):
    """
    Обновляет круговую диаграмму распределения населения по континентам
    
    Args:
        year (int): Выбранный год
    
    Returns:
        dict: Объект figure для графика
    """
    # Фильтрация данных по выбранному году
    filtered_df = df[df["year"] == year]
    
    # Группировка данных по континентам и суммирование населения
    continent_pop = filtered_df.groupby("continent")["pop"].sum().reset_index()
    
    # Добавляем процентный формат для лучшей наглядности
    total_pop = continent_pop["pop"].sum()
    continent_pop["percentage"] = continent_pop["pop"].apply(lambda x: f"{x/total_pop:.1%}")
    
    # Создание круговой диаграммы
    fig = px.pie(
        continent_pop, 
        values="pop", 
        names="continent",
        title=f"Распределение населения по континентам в {year} году",
        labels={
            "continent": "Континент", 
            "pop": "Население (человек)",
            "percentage": "Процент"
        },
        color_discrete_sequence=COLOR_SCHEME["pie"],
        hover_data=["pop", "percentage"],  # Добавляем данные для всплывающих подсказок
        template="plotly_white"
    )
    
    # Настройка отображения меток
    fig.update_traces(
        textinfo="percent+label",
        textposition="inside",
        textfont_size=12,
        marker=dict(line=dict(color="white", width=2))
    )
    
    # Настройка внешнего вида графика
    fig.update_layout(
        legend_title="Континенты",
        uniformtext_minsize=12,
        uniformtext_mode="hide",
        margin=dict(t=80, b=20, l=20, r=20)
    )
    
    # Добавление аннотации для отображения общего населения
    fig.add_annotation(
        x=0.5, y=-0.15,
        xref="paper", yref="paper",
        text=f"Общее население: {total_pop:,}".replace(",", " "),
        showarrow=False,
        font=dict(size=12)
    )
    
    return fig

# ---------------------------------- ЗАПУСК ПРИЛОЖЕНИЯ ----------------------------------

if __name__ == "__main__":
    print("Запуск дашборда Gapminder...")
    app.run_server(debug=True)
