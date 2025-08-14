import os
from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from opensearch_utils import get_opensearch_client, create_index, load_sample_documents, search_documents

app = FastAPI() # 
templates = Jinja2Templates(directory="templates") #
OPENSEARCH_HOST = os.getenv('OPENSEARCH_HOST', 'localhost')
OPENSEARCH_PORT = int(os.getenv('OPENSEARCH_PORT', 9200))

client = get_opensearch_client(host=OPENSEARCH_HOST, port=OPENSEARCH_PORT)

create_index(client) # создаём клиента
load_sample_documents(client) # загружаем доки

CONTENT_TYPES = ['article', 'guide', 'tutorial', 'report']


@app.get("/")
async def index(request: Request):
    '''отображает главную страницу (GET-запрос)
    возвращаем HTML-шаблон с пустыми результатами поиска'''
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,  # передаём запрос для Jinja2
            "results": [],  # пока нет результатов
            "keyword": "",  # пустое поле поиска
            "content_types": CONTENT_TYPES,  # список типов для радиокнопок
            "selected_type": None  # ничего не выбрано
        }
    )

@app.post("/")
async def search(request: Request, keyword: str = Form(""), content_type: str = Form(None)):
    '''обрабатывает поиск (POST-запрос от формы)'''
    results = []
    # есть ключевое слово, делаем поиск
    if keyword:
        results = search_documents(client, keyword, content_type)
    
    # Возвращаем HTML-шаблон с результатами поиска
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,  # передаём запрос для Jinja2
            "results": results,  # результаты поиска
            "keyword": keyword,  # введённое ключевое слово
            "content_types": CONTENT_TYPES,  # список типов для радиокнопок
            "selected_type": content_type  # выбранный тип или None
        }
    )
