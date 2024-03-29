## Продуктовый помощник Grocery assistant

Grocery assistant — сайт, на котором пользователи могут опубликовать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. 
Пользователям сайта также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Также есть возможность скачивания данного списка в формате txt.

## Описание проекта:

### Главная страница

На данной странице список первых шести рецептов, отсортированных по дате публикации «от новых к старым». На данной странице реализованна постраничную пагинация. Остальные рецепты доступны на следующих страницах.
 
### Страница рецепта

Полное описание рецепта. Страница доступна всем пользователям. Авторизованные пользователи могут добавить рецепт в избранное и список покупок, а также подписаться на автора рецепта.

### Страница пользователя

На странице — имя пользователя, все рецепты, опубликованные пользователем и возможность подписаться на пользователя.

### Страница подписок

Подписка на публикации доступна только авторизованному пользователю. Страница подписок доступна только владельцу.
Сценарий поведения пользователя:
1. Пользователь переходит на страницу другого пользователя или на страницу рецепта и подписывается на публикации автора кликом по кнопке «Подписаться на автора».
2. Пользователь переходит на страницу «Мои подписки» и просматривает
список рецептов, опубликованных теми авторами, на которых он подписался. Сортировка записей - по дате публикации (от новых к старым). 
3. При необходимости пользователь может отказаться от подписки на автора: переходит на страницу автора или на страницу его рецепта и нажимает «Отписаться от автора».

### Избранное

Добавлять рецепты в избранное может только авторизованный пользователь. Сам список избранного может просмотреть только его владелец.
Сценарий поведения пользователя:
1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в избранное».
2. Пользователь переходит на страницу «Список избранного» и просматривает свой список избранных рецептов.
3. При необходимости пользователь может удалить рецепт из избранного.

### Список покупок

Работать со списком покупок могут только авторизованные пользователи. Доступ к своему списку покупок есть быть только у владельца аккаунта.
Сценарий поведения пользователя:
1. Пользователь отмечает один или несколько рецептов кликом по кнопке «Добавить в покупки».
2. Пользователь переходит на страницу «Список покупок», там доступны все добавленные в список рецепты. 
3. Пользователь нажимает кнопку «Скачать список» и получает файл с перечнем и количеством необходимых ингредиентов для всех рецептов, сохранённых в «Списке покупок».
4. При необходимости пользователь может удалить рецепт из списка покупок.

### Создание и редактирование рецепта

Доступ к этой странице есть только у авторизованных пользователей. Все поля на ней обязательны для заполнения. 
Сценарий поведения пользователя:
1. Пользователь заполняет все обязательные поля.
2. Пользователь нажимает кнопку «Создать рецепт».
Также пользователю доступна возможность отредактировать любой рецепт, который он создал.

### Фильтрация по тегам

При нажатии на название тега выводится список рецептов, отмеченных этим тегом. Фильтрация может проводится по нескольким тегам. 
При фильтрации на странице пользователя фильтруются только рецепты выбранного пользователя. 
Такой же принцип соблюдается при фильтрации списка избранного.

## Технологии

- Python
- Django
- Django Rest Framework
- PostgreSQL
- Docker
- Gunicorn
- NGINX
- Continuous Integration
- Continuous Deployment

### Автор:

Денис Дриц
