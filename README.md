# Пояснительная записка по проекту GeoSM
## Идея.

Идея проекта довольно изменилась от первоначальной. Мы отказались от использования геолокации, но приняли во внимание идею с игрой. 

## Результат

Основа сайта всё ещё социальная сеть. Реализованны следующие её компоненты:

1. Разделение пользователей на обычных и админов. Разница присутствует одна - первые могут создавать новости на её главной странице.
2. У каждого пользователя есть логин и пароль, сам аккаунт и личный блог в нём.
3. Присутствуют группы, которые пользователи могут создавать и подписываться. Делать там записи, в зависимости от настроек группы. Также пользователь, если захочет, может сделать запись анонимным, тогда ссылки на его страничку в теле записи не будет.
4. Есть стена, на которой отображаются записи групп, на которые вы подписаны.
5. Под новостями и записями (и групп, и пользователей) в зависимости от натроек, можно комментировать. Будет сообщаться автор.
6. Новости могут удалять очевидно админы, а также авторы свои записи(и в группе, и на личной странице) и админ группы в случае группы.
7. Можно по кнопке начать игру. Очки каждой сессии сохраняются, и выводятся в рекордах его странички.

Идея с игрой оказалась не совсем удачной. Пользователю придётся её устанавливать. Клиент её, зная расположение, запускает и запрашиват данные о себе у сервера. После сессии сервер принимает новые данные и записывает в базу данных. (Возможно, это не правильное обяснение работы)

## Не реализованные идеи и будущее проекта

Перечисленные выше достояния сайта - не всё, что мы хотели сделать. Например:

1. Не была сделана возможность добавлять в друзья и переписовываться с ними.

2. Та же геолокация каждого пользователя.

3. Идея игры совершенно другая, отличная от того, что задумал автор общей идеи проекта.

4. Более понятный и приятный интерфейс.

Будущего у проекта, скорее всего, нет, если кому то из нас когда-нибудь вдруг не захочется его развить дальше (это произодёт с вероятностью меньше одной тысячи).

## Использовано при разработке

Следующее:
* ЯП Python
* Библиотеки Flask, Werkzeug и Pygame
* Для интерфейса Bulma

### Послесловие от одного из нас.
Я признаю, что идея с игрой, как уже было сказано, оказалась не совсем удачной. Картина в моей голове была совершенно другой. Наверное, надо было полностью идти в идею с соц сетью и геолокацией.
