# Annual Budget — сценарий записи экрана

Итог: квадратное видео 1080×1080, 14,9 с, без звука, в той же рамке, что и
Reading Tracker (мятный фон из палитры файла, макет ноутбука, подписи, бейдж).
Ты записываешь экран по этому сценарию — я монтирую.

## 1. Что в товаре (по факту разбора файла)

7 вкладок: **Start Here · Setup · Transactions · Annual Dashboard · Month View ·
Bill Calendar · Savings & Net Worth**.

Механика: одна таблица `Transactions` кормит всё остальное через SUMIFS.
Тип строки — `Income` / `Expense` / `Transfer`; «Saved» на дашборде — это сумма
строк `Transfer`. Колонки `Month#`, `Year#`, `50/30/20` считаются формулами.
4 диаграммы на Annual Dashboard: *Income vs Expenses by month*, *Spending by
Category*, *50/30/20 Split*, *Saved by Month*. Все листы защищены, вводимые
ячейки — синие.

Палитра файла совпадает с трекером книг: акцент `DFF3EA`, заголовки `33566B`,
ввод `3E7CC0`, приглушённый `9AA7B4`. Рамка видео подойдёт без переделки.

## 2. Обязательная подготовка (иначе снимать нечего)

**Файл пустой** — 0 строк в Transactions, пустые Bill Calendar и Savings.
Дашборд сейчас показывает нули и пустые диаграммы.

1. **Setup**: `C4` = `$`, `F4` = `2026`, **`J4` = `4700`** — без J4 цели
   50/30/20 будут нулевыми.
2. **Transactions**: вставить `demo_transactions.csv` в ячейку **A5**
   (272 строки за 2026: доход 56 110, расходы 36 299, переводы 11 300, net 8 511).
   Все категории взяты из встроенного дропдауна — предупреждающих маркеров не будет.
3. **Bill Calendar**: заполнить A5:C18, F, G по таблице ниже.
4. **Savings & Net Worth**: фонд `Savings` (имя должно совпадать с категорией
   переводов) — target 15000, посчитается 11 300 = 75%. Плюс блок Net Worth.
5. **Переместить диаграмму «Spending by Category»** — она стоит на A32:I46 и
   закрывает таблицу «50 / 30 / 20 (year)» в A32:D36. Перетащи её правее
   (например, в столбцы F–N) или ниже. Иначе таблицу в кадре не будет видно.

### Bill Calendar

| Bill | Amount | Frequency | Due day | Paid? |
|---|---|---|---|---|
| Rent | 1250 | Monthly | 1 | Yes |
| Electric | 78 | Monthly | 4 | Yes |
| Water | 46 | Quarterly | 12 | No |
| Home insurance | 88 | Monthly | 6 | Yes |
| Car insurance | 540 | Yearly | 20 | No |
| Fibre + mobile | 65 | Monthly | 8 | Yes |
| Streaming | 27.97 | Monthly | 7 | Yes |
| Cloud + music | 15.99 | Monthly | 10 | Yes |
| Gym | 42 | Monthly | 18 | Yes |
| Council tax | 165 | Monthly | 15 | No |
| Loan payment | 220 | Monthly | 12 | Yes |
| Cleaner | 60 | Biweekly | 21 | No |
| Car service | 380 | Yearly | 25 | No |

### Savings & Net Worth

Фонд: `Savings`, target `15000`.

| Assets | Value | Liabilities | Value |
|---|---|---|---|
| Checking | 3180 | Mortgage | 168400 |
| Savings | 11300 | Car loan | 5900 |
| Investments | 18450 | Credit card | 1240 |
| Car | 9200 | | |
| Home | 245000 | | |

Net worth получится ≈ 111 590.

## 3. Требования к записи

- **Интерфейс браузера и Google Sheets — на английском.** В прошлый раз русские
  меню попали в кадр и 35 секунд материала ушло в корзину.
- Разрешение окна 1920×1080, масштаб браузера 100 %, зум таблицы 100 %.
- `Ctrl+Shift+F` — скрыть меню Sheets; `F11` — полный экран. В кадре остаётся
  только таблица.
- **View → Show → снять галочку Gridlines** на всех вкладках — выглядит дороже.
- Один дубль на 60–90 секунд, на каждом экране пауза **5–8 секунд** без движения,
  курсор двигать плавно.
- Не открывать контекстные меню, не трогать панель записи, не показывать шторку ОС.
- 30 fps, без звука, mp4 или webm.

## 4. Покадровый сценарий (9 планов)

Порядок съёмки = порядок в монтаже. В финале каждый план ≈ 1,8 с, кроссфейд 0,35 с.

| № | Вкладка | Что в кадре | Что делает мышь | Подпись в видео |
|---|---|---|---|---|
| 1 | Annual Dashboard | Строки 1–14: INCOME / EXPENSES / SAVED / NET и таблица по месяцам | Медленно ведёт вдоль строки месяцев слева направо | Your whole year on one screen |
| 2 | Transactions | Строки 4–30, видно 272 записи | Открыть дропдаун `Type` в строке 12 (Income / Expense / Transfer), подержать 3 с | Log it once — the year fills itself in |
| 3 | Transactions | Те же строки | Открыть дропдаун `Category`, подержать раскрытым 3 с | 17 categories, all yours to rename |
| 4 | Annual Dashboard | Строки 16–30: SPENDING BY CATEGORY по месяцам | Провести по столбцу одного месяца сверху вниз | See where the money actually goes |
| 5 | Annual Dashboard | Таблица 50/30/20 + пончик 50/30/20 Split | Ничего, просто держать кадр | 50 / 30 / 20, checked for you |
| 6 | Annual Dashboard | Диаграммы Income vs Expenses by month и Saved by Month | Плавный скролл на один экран вниз | Charts build themselves |
| 7 | Month View | Верх листа | Кликнуть `D4`, выбрать месяц `6`, дождаться пересчёта, выбрать `11` | Any month on its own — one dropdown |
| 8 | Bill Calendar | Все 13 счетов, колонки Monthly cost / Yearly cost, строка TOTAL | Открыть дропдаун `Frequency` (Weekly → Yearly), сменить одну строку и показать, как поменялся Monthly cost | Weekly or yearly bills — the true monthly cost |
| 9 | Savings & Net Worth | Фонд с прогрессом 75 % + блок NET WORTH | Провести от фонда к итогу Net worth | Savings goals and net worth |

Если 9 планов окажется слишком плотно, выброшу план 3 — он самый необязательный.

## 5. Что будет в рамке

- Надзаголовок: `GOOGLE SHEETS & EXCEL · INSTANT DOWNLOAD`
- Заголовок: `The Annual Budget`
- Бейдж: `UPDATES ITSELF`
- Футер: `7 TABS · SETUP · TRANSACTIONS · ANNUAL DASHBOARD · MONTH VIEW · BILL CALENDAR · SAVINGS & NET WORTH`
  и `ONE LOG FEEDS THE WHOLE YEAR — NO TAB PER MONTH`

Все формулировки взяты из листа Start Here, ничего придуманного про отзывы и
количество покупателей.

## 6. Замеченное в товаре (к видео не относится)

Вспомогательный список категорий `Setup!K7:K23`, на который смотрит дропдаун в
Transactions, — это статичный текст, а не формулы. Если покупатель переименует
категорию в `Setup!D`, дропдаун останется со старыми названиями. Стоит заменить
`K7:K23` на формулы вида `=IF(D7="","",D7)` и расширить диапазон — заодно
заработают собственные имена фондов на листе Savings.
