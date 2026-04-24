from app import models, routes
from app.database import engine, Base, SessionLocal
from app.schemas import TermCreate, RelationshipCreate


def init_database():
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Проверяем, есть ли уже данные
        existing_terms = db.query(models.Term).first()
        if existing_terms:
            print("База данных уже инициализирована")
            return

        # Создаем термины
        terms_data = [{"name": "Клиентский рендеринг (Client-Side Rendering, CSR)",
                       "description": "Техника рендеринга, при которой браузер загружает минимальный HTML-документ, а затем JavaScript строит весь DOM и обновляет его динамически.",
                       "source_url": "https://reactjs.org/docs/react-dom.html#client-side-rendering"},
                      {"name": "Серверный рендеринг (Server-Side Rendering, SSR)",
                       "description": "Процесс рендеринга компонента или страницы на сервере и отправки готового HTML клиенту.",
                       "source_url": "https://nextjs.org/docs/basic-features/pages#server-side-rendering"},
                      {"name": "Гидрирование (Hydration)",
                       "description": "Процесс, при котором клиентский JavaScript добавляет состояние и интерактивность к HTML-контенту, предварительно отрендеренному на сервере.",
                       "source_url": "https://reactjs.org/docs/react-dom.html#hydrate"},
                      {"name": "Предварительный рендеринг (Pre-rendering)",
                       "description": "Общий термин для техник, при которых HTML для страницы генерируется во время сборки, а не по запросу на сервере.",
                       "source_url": "https://nextjs.org/docs/basic-features/pages#pre-rendering"},
                      {"name": "Статическая генерация сайта (Static Site Generation, SSG)",
                       "description": "Метод предварительного рендеринга, при котором HTML-страницы генерируются во время сборки приложения.",
                       "source_url": "https://nextjs.org/docs/basic-features/pages#static-generation"},
                      {"name": "Инкрементальная статическая регенерация (Incremental Static Regeneration, ISR)",
                       "description": "Расширение SSG, позволяющее обновлять статические страницы после сборки, периодически регенерируя их в фоновом режиме.",
                       "source_url": "https://nextjs.org/docs/basic-features/data-fetching/incremental-static-regeneration"},
                      {"name": "Первоначальная загрузка (First Load)",
                       "description": "Момент, когда пользователь впервые переходит на веб-сайт. Ключевой для восприятия производительности.",
                       "source_url": "https://web.dev/first-contentful-paint/"},
                      {"name": "Core Web Vitals",
                       "description": "Набор метрик от Google, измеряющих пользовательский опыт веб-страниц по трём аспектам: загрузка, отзывчивость и визуальная стабильность.",
                       "source_url": "https://web.dev/vitals/"},
                      {"name": "Наибольшая содержательная отрисовка (Largest Contentful Paint, LCP)",
                       "description": "Метрика, измеряющая время от начала загрузки страницы до отрисовки самого крупного видимого элемента в области просмотра.",
                       "source_url": "https://web.dev/lcp/"},
                      {"name": "Задержка первого ввода (First Input Delay, FID)",
                       "description": "Метрика, измеряющая время от первого взаимодействия пользователя до момента, когда браузер может начать обрабатывать обработчики событий.",
                       "source_url": "https://web.dev/fid/"},
                      {"name": "Дерево DOM (Document Object Model)",
                       "description": "Программный интерфейс для HTML-документов, представляющий структуру документа в виде дерева объектов.",
                       "source_url": "https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model"},
                      {"name": "Совокупное смещение макета (Cumulative Layout Shift, CLS)",
                       "description": "Метрика, измеряющая визуальную стабильность страницы. Показывает, насколько неожиданно смещаются элементы во время загрузки.",
                       "source_url": "https://web.dev/cls/"},
                      {"name": "Индексация (Search Engine Indexing)",
                       "description": "Процесс, при котором поисковые роботы анализируют, читают и добавляют веб-страницы в свою базу данных.",
                       "source_url": "https://developers.google.com/search/docs/beginner/how-search-works"},
                      {"name": "Поисковая оптимизация (SEO)",
                       "description": "Практика увеличения качества и количества трафика на сайт через органические результаты поисковых систем.",
                       "source_url": "https://developers.google.com/search/docs/beginner/seo-starter-guide"},
                      {"name": "Сервер (Backend Server / Node.js Server)",
                       "description": "В контексте рендеринга — это среда выполнения, которая выполняет код для SSR или обслуживает функции для ISR.",
                       "source_url": "https://nodejs.org/en/docs/"}]

        term_ids = {}
        for i, term_data in enumerate(terms_data, 1):
            term = routes.create_term(db, TermCreate(**term_data))
            term_ids[term.name] = term.id
            print(f"Создан термин: {term.name}")

        # Создаем связи между терминами
        relationships_data = [
            # Центральные стратегии рендеринга
            {"parent": "Клиентский рендеринг (Client-Side Rendering, CSR)",
             "child": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "type": "альтернатива"},

            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Гидрирование (Hydration)",
             "type": "требует"},

            {"parent": "Предварительный рендеринг (Pre-rendering)",
             "child": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "type": "включает"},

            {"parent": "Предварительный рендеринг (Pre-rendering)",
             "child": "Статическая генерация сайта (Static Site Generation, SSG)",
             "type": "включает"},

            {"parent": "Статическая генерация сайта (Static Site Generation, SSG)",
             "child": "Инкрементальная статическая регенерация (Incremental Static Regeneration, ISR)",
             "type": "расширяется до"},

            # Влияние на метрики производительности
            {"parent": "Клиентский рендеринг (Client-Side Rendering, CSR)",
             "child": "Core Web Vitals",
             "type": "влияет на"},

            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Наибольшая содержательная отрисовка (Largest Contentful Paint, LCP)",
             "type": "улучшает"},

            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Первоначальная загрузка (First Load)",
             "type": "ускоряет"},

            {"parent": "Гидрирование (Hydration)",
             "child": "Задержка первого ввода (First Input Delay, FID)",
             "type": "влияет на"},

            {"parent": "Статическая генерация сайта (Static Site Generation, SSG)",
             "child": "Первоначальная загрузка (First Load)",
             "type": "ускоряет"},

            # Связи с DOM и визуальной стабильностью
            {"parent": "Дерево DOM (Document Object Model)",
             "child": "Совокупное смещение макета (Cumulative Layout Shift, CLS)",
             "type": "влияет на"},

            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Дерево DOM (Document Object Model)",
             "type": "создает"},

            {"parent": "Клиентский рендеринг (Client-Side Rendering, CSR)",
             "child": "Дерево DOM (Document Object Model)",
             "type": "манипулирует"},

            # SEO и индексация
            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Индексация (Search Engine Indexing)",
             "type": "улучшает"},

            {"parent": "Статическая генерация сайта (Static Site Generation, SSG)",
             "child": "Индексация (Search Engine Indexing)",
             "type": "улучшает"},

            {"parent": "Индексация (Search Engine Indexing)",
             "child": "Поисковая оптимизация (SEO)",
             "type": "влияет на"},

            {"parent": "Core Web Vitals",
             "child": "Поисковая оптимизация (SEO)",
             "type": "влияет на"},

            # Серверная инфраструктура
            {"parent": "Серверный рендеринг (Server-Side Rendering, SSR)",
             "child": "Сервер (Backend Server / Node.js Server)",
             "type": "требует"},

            {"parent": "Инкрементальная статическая регенерация (Incremental Static Regeneration, ISR)",
             "child": "Сервер (Backend Server / Node.js Server)",
             "type": "требует"},

            # Дополнительные связи для полной связности
            {"parent": "Core Web Vitals",
             "child": "Наибольшая содержательная отрисовка (Largest Contentful Paint, LCP)",
             "type": "включает"},

            {"parent": "Core Web Vitals",
             "child": "Задержка первого ввода (First Input Delay, FID)",
             "type": "включает"},

            {"parent": "Core Web Vitals",
             "child": "Совокупное смещение макета (Cumulative Layout Shift, CLS)",
             "type": "включает"},

            {"parent": "Первоначальная загрузка (First Load)",
             "child": "Наибольшая содержательная отрисовка (Largest Contentful Paint, LCP)",
             "type": "влияет на"},

            {"parent": "Клиентский рендеринг (Client-Side Rendering, CSR)",
             "child": "Задержка первого ввода (First Input Delay, FID)",
             "type": "влияет на"},

            {"parent": "Дерево DOM (Document Object Model)",
             "child": "Гидрирование (Hydration)",
             "type": "обрабатывается в"},

            {"parent": "Поисковая оптимизация (SEO)",
             "child": "Первоначальная загрузка (First Load)",
             "type": "зависит от"},
        ]

        for rel_data in relationships_data:
            parent_id = term_ids.get(rel_data["parent"])
            child_id = term_ids.get(rel_data["child"])

            if parent_id and child_id:
                relationship = RelationshipCreate(
                    parent_id=parent_id,
                    child_id=child_id,
                    relationship_type=rel_data["type"]
                )
                routes.create_relationship(db, relationship)
                print(
                    f"Создана связь: {rel_data['parent']} -> {rel_data['child']}")

        db.commit()
        print("База данных успешно инициализирована!")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
