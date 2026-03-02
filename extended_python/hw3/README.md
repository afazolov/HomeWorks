# Продвинутый Python — ДЗ #3 (extended_python/hw3)

## Что сделано (на максимум по критериям)

- **К1:** реализована многопоточная загрузка через `ThreadPoolExecutor` —
  каждая категория в пакете загружается в отдельном потоке.
- **К2:** метод `_download_batch()` использует `ThreadPoolExecutor.map`,
  который принимает функцию `_fetch_category` и список категорий пакета,
  возвращая результаты в исходном порядке.
- **К3:** метод `_split_into_batches()` разделяет список категорий на пакеты:
  использует `np.array_split` если numpy установлен, иначе — срезы списка.

`ThreadedLoader` полностью совместим с `Loader` (ДЗ #1) и `AsyncLoader` (ДЗ #2):
те же абстрактные методы `download()` и `to_dict()`, тот же паттерн Singleton.

## Запуск

```bash
pip install requests          # обязательно
pip install numpy             # опционально — для np.array_split
python main.py
```

## Пример использования

```python
from main import ThreadedLoader

loader = ThreadedLoader(batch_size=5, max_workers=8)

data = loader.download(["beauty", "smartphones", "laptops"])

# data -> dict: {category: {product_id: product_dict}}
print(len(data["smartphones"]))
```

## Архитектура

```
download(categories)              ← основной метод (К1, К2, К3)
  └─ _split_into_batches          ← разбивка на пакеты (К3)
       │  np.array_split          ← если numpy доступен
       │  или срезы списка        ← иначе
       └─ for batch:
            _download_batch       ← многопоточная загрузка пакета (К1, К2)
              └─ ThreadPoolExecutor.map(_fetch_category, batch)
```
