# Продвинутый Python — ДЗ #2 (extended_python/hw2)

## Что сделано (на максимум по критериям)

- **К1:** реализован асинхронный метод `download_async()` — загружает все
  категории параллельно через `aiohttp`.
- **К2:** внутри каждого пакета все HTTP-запросы выполняются одновременно
  через `asyncio.gather` — многопоточная/асинхронная загрузка по категориям.
- **К3:** список категорий разбивается на пакеты (`_split_into_batches`,
  аналог `np.array_split`) и обрабатывается пакетно.

`AsyncLoader` полностью совместим с `Loader` из ДЗ #1: те же абстрактные
методы `download()` и `to_dict()`, тот же паттерн Singleton.

## Запуск

```bash
pip install aiohttp requests
python main.py
```

## Пример использования

```python
import asyncio
from main import AsyncLoader

loader = AsyncLoader(batch_size=5)

# Синхронно (обёртка, как в ДЗ #1)
data = loader.download(["beauty", "smartphones"])

# Асинхронно
data = asyncio.run(loader.download_async(["beauty", "smartphones", "laptops"]))

# data -> dict: {category: {product_id: product_dict}}
print(len(data["smartphones"]))
```

## Архитектура

```
download(categories)           ← синхронная обёртка (обратная совместимость)
  └─ asyncio.run(download_async)
       └─ _split_into_batches  ← разбивка на пакеты (К3)
            └─ for batch:
                 _fetch_batch  ← параллельная загрузка пакета (К2)
                   └─ asyncio.gather(_fetch_category × N)  ← К1
```
