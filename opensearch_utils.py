import time
INDEX_NAME = 'documents'  # название индекса

import time
from opensearchpy import OpenSearch, ConnectionError, SSLError

def get_opensearch_client(host='opensearch', port=9200, max_retries=5, retry_interval=5):
    for attempt in range(max_retries):
        try:
            client = OpenSearch(
                hosts=[{'host': host, 'port': port}],
                http_auth=('admin', 'Mango!Tree42Safe'),
                use_ssl=False,
                verify_certs=False,
                ssl_show_warn=False,
                timeout=30
            )
            if client.ping():
                print(f"!!!success FROM {attempt + 1}!!!")
                return client
            else:
                print(f"!!! (attemp {attempt + 1})!!!")
        except ConnectionError as ce:
            print(f"!!!CONNECTION ERROR (attemp {attempt + 1}): {str(ce)}!!!")
        except SSLError as se:
            print("ssl")
        except Exception as e:
            print(f"!EERROR (attemp {attempt + 1}): {str(e)}!!!")
        if attempt < max_retries - 1:
            print(f"!!!RETRY {retry_interval} !!!")
            time.sleep(retry_interval)
    raise Exception(f"!!!ENABLE TO CONNECT!!!")

def create_index(client):
    '''создаёт новый индекс в OpenSearch'''
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)  # удаляем старый индекс
        print(f"!!!INDEX '{INDEX_NAME}' DELETED!!!.")
    mapping = {
        'mappings': {
            'properties': {
                'title': {'type': 'text'},  # title для поиска
                'content': {'type': 'text'},  # content текст
                'content_type': {'type': 'keyword'}  # content_type для точного соответствия
            }
        }
    }
    client.indices.create(index=INDEX_NAME, body=mapping)  # создаём индекс
    print(f"!!!INDEX '{INDEX_NAME}' CREATED!!!")

def load_sample_documents(client):
    '''загружает тестовые документы в индекс'''
    documents = [
        {
            'title': 'Doc1(MiB)',
            'content': '"Men in Black" refers to two main concepts: a science fiction film franchise and a supposed phenomenon of mysterious individuals in black suits who are rumored to be involved in UFO cover-ups. The movie series, starring Tommy Lee Jones and Will Smith, follows a top-secret organization that monitors and regulates extraterrestrial activity on Earth.',
            'content_type': 'tutorial'
        },
        {
            'title': 'Doc2(Matrix)',
            'content': '"The Matrix" refers to two main concepts: a groundbreaking science fiction film franchise and a philosophical idea about simulated reality. The movies, starring Keanu Reeves as Neo, explore a dystopian future in which humanity is unknowingly trapped inside a computer-generated simulation controlled by intelligent machines.',
            'content_type': 'guide'
        },
        {
            'title': 'Doc3(Titanic)',
            'content': '"Titanic" refers to two main concepts: a historical British passenger liner that tragically sank in 1912 and a 1997 epic romance-disaster film directed by James Cameron. The movie, starring Leonardo DiCaprio and Kate Winslet, dramatizes the ill-fated voyage through a fictional love story set against the backdrop of the real disaster.',
            'content_type': 'article'
        },
        {
            'title': 'Doc4(Sherlock Holmes)',
            'content': '"Sherlock Holmes" refers to two main concepts: a fictional detective created by Sir Arthur Conan Doyle and a cultural icon representing sharp deduction and investigative skill. The character has appeared in countless adaptations, from classic novels to modern films and TV series, with portrayals by actors like Robert Downey Jr. and Benedict Cumberbatch.',
            'content_type': 'tutorial'
        },
        {
            'title': 'Doc5(Jurasssic Park)',
            'content': '"Jurassic Park" refers to two main concepts: a best-selling science fiction novel by Michael Crichton and a blockbuster film franchise directed by Steven Spielberg and others. The story centers on a theme park filled with cloned dinosaurs, where scientific ambition and human error lead to thrilling — and often dangerous — encounters with prehistoric creatures.',
            'content_type': 'report'
        }
    ]
    
    for doc in documents:
        client.index(index=INDEX_NAME, body=doc)
    client.indices.refresh(index=INDEX_NAME)  # обновляем индекс
    print("!!!DOCS LOADED!!!")

def search_documents(client, keyword, content_type=None):
    '''документы по ключевому слову с фильтром по content_type'''
    # запрос для поиска: ищем слово в title и content
    query = {
        'query': {
            'bool': {
                'must': {
                    'multi_match': {
                        'query': keyword,
                        'fields': ['title', 'content']  # ищем в двух полях
                    }
                }
            }
        },
        '_source': ['title', 'content']  # возвращаем title и content
    }

    # if указан content_type, добавляем фильтр
    if content_type:
        query['query']['bool']['filter'] = {
            'term': {'content_type': content_type}  # фильтруем по точному совпадению
        }
    # поиск в OpenSearch
    response = client.search(index=INDEX_NAME, body=query)
    results = []
    # обрабатываем результаты поиска
    for hit in response['hits']['hits']:
        source = hit['_source']
        # первые 50 символов для сниппета
        snippet = source['content'][:50] + '...' if len(source['content']) > 50 else source['content']
        results.append({
            'title': source['title'],
            'snippet': snippet
        })
    return results  # возвращаем результаты
