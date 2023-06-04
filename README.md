# NadeBot (публічна версія)



Discord бот з відкриитим кодом для серверу [**&lt;Підвал Нейда>**](https://discord.gg/nadecgt)


## Функціонал
*Ця версія є публічною та може сутільно відрізнятись від оригіналу на [сервері](https://discord.gg/nadecgt)*

### Команди
- `/alert` - Команда реалізована на базі API [alerts.com.ua](https://alerts.com.ua), все що вона робить це відправляє карту повітряних тривог.
- `/dontpingme` - Команда конфігурацій для функції, коли ви пінгуєте бота, той відповість випадковим текстом(чи мемною пікчою у вигляді посилання).
- `/war-states` - Реалізована на базі [russianwarship.rip](https://russianwarship.rip), виводить кількість втрат раісії в Україні.
- `/help` - Список команд бота.
- `/top` - Топ 50 учасників по рівню.
- `/cmgr` - Команда конфігурації когів бота.
- `/ctxmgr` - Команда конфігурації контекстних меню бота.
- `/exp` - Змінити кількість exp для учасників серверу.
- `/levelrole` - Виставити винагороди за досягнення певного рівня.

### Функції
 
- `DontPingMe` - Відправить випадковий текст, пікчуЮ відео (у випадку якщо налаштовано в `/dontpingme`)
- `ChannelFilter` - (нажаль поки може налаштовуватись лише розробником в конфігураційних файлах)  Не дозволяє учасникам в певних каналах відправляти повідомлення без посилання чи вкладень.
- `Rank` - Рангова система що також працює і в голосових каналах (частково налаштовується в конфігураційних файлах)
- `Counting` - (наразі на етапі перенесення, зберігається як чернетка) Перевіряє в певному каналі дотрмування ітерації.

## Встановлення

1. Копіюємо весь код зручним для вас методом (тут буде використано [git](https://git-scm.com/downloads) а також буде використовуватись Windows Powershell)
  ```bash
  cd Your_dir
  git clone https://github.com/Beengoo/nade-bot.git
  cd nade-bot-master
  ```
2. Заходимо в файл config.json і в значення ключа `botToken` вставляємо токен вашого бота.
3. Для доступу до команд розробника (як то `/cmgr`) треба вставити id вашого акаунту Discord в список колюча `devIds`.
4. Також зазначте id цільової гільдії (бот розрахований на одну гільдію).
5. Тепер повертаємось в командний рядок та пишемо наступні команди (з кореневої директорії)
  ```bash
  python -m venv venv
  .\venv\Scripts\activate.ps1
  pip install -r requirements.txt
  ```
6. Та нарешні запускаємо бота командою `python main.py`

## Допомога по налаштуванню

Якщо бот не запускається, швидше за все проблема в незавершеній конфігурації бота.

Налаштування окремого функціоналу завжди розташовано в папці `assets/configs` для деталей звертайтесь до beengoo.ua на сервері [**Підвал Нейда**](https://discord.gg/nadecgt)


## Плани на майбутнє

Поки нічого.


