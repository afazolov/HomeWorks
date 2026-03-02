# Продвинутый Python — ДЗ #1 (extended_python/hw1)

## Что сделано (на максимум по критериям)

- **К1:** создан базовый абстрактный класс `Model` с методами `download()` и `to_dict()`
- **К2–К3:** реализован наследник `Loader` для загрузки данных с **DummyJSON** по категориям
- **К4:** `Loader` реализован как **Singleton** (все экземпляры — один объект)

## Запуск

```bash
python main.py
```

Зависимость: `requests` (`pip install requests`).

## Пример использования

```python
from main import Loader

loader = Loader()
data = loader.download(["beauty", "smartphones"])

# data -> dict: {category: {product_id: product_dict}}
print(len(data["smartphones"]))
```

