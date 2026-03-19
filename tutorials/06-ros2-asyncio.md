# Tutorial 06: Asyncio в ROS 2

Соответствует слайду 20 из [presentation.md](../presentation.md).

Источник вдохновения:
- [m2-farzan/ros2-asyncio](https://github.com/m2-farzan/ros2-asyncio)

## Проблема

Callback-heavy код сложно читать и сопровождать: бизнес-логика распадается на набор несвязанных обработчиков.

## Цель

Перенести рабочую логику в линейные `async` циклы и оставить обработку ROS-событий в отдельном `ros_loop`.

## Файлы примера

- [examples/asyncio/async_node_demo.py](../examples/asyncio/async_node_demo.py)
- [examples/asyncio/async_subscription.py](../examples/asyncio/async_subscription.py)

## Базовый паттерн

1. `ros_loop` часто вызывает `rclpy.spin_once(..., timeout_sec=0)`.
2. Бизнес-циклы пишутся как обычные `async def`.
3. `asyncio.wait(..., return_when=asyncio.FIRST_EXCEPTION)` завершает общий раннер при первой ошибке.

В [async_node_demo.py](../examples/asyncio/async_node_demo.py) это выглядит как параллельный запуск `ros_loop()` и `business_loop()`.

## Async subscription

[async_subscription.py](../examples/asyncio/async_subscription.py) показывает, как превратить обычный subscriber в async-источник сообщений через `asyncio.Queue`.

Это полезно, когда чтение сообщений должно встраиваться в линейный async-сценарий, а не разбиваться на callback.

## Минимальный запуск

```bash
python3 examples/asyncio/async_node_demo.py
```

## Почему это решение принято

Так код бизнес-логики становится последовательным, а ошибки не теряются внутри дерева callback-обработчиков.
