# Tutorial 06: Asyncio в ROS 2

Источник вдохновения для подхода:
- https://github.com/m2-farzan/ros2-asyncio

## Проблема
Callback-centric код трудно сопровождать: бизнес-логика распадается на множество точек входа.

## Цель
Перенести бизнес-логику в линейные `async` циклы и оставить `spin_once` в отдельном ROS loop.

## Файлы примера
- `ros-meetup-2026/examples/asyncio/async_node_demo.py`
- `ros-meetup-2026/examples/asyncio/async_subscription.py`

## Ключевой паттерн
1. `ros_loop`: часто вызывает `rclpy.spin_once(..., timeout_sec=0)`.
2. `business_loop`: делает полезную работу, `await`-ит внешние операции.
3. `asyncio.wait(..., return_when=FIRST_EXCEPTION)` завершает процесс при первой ошибке.

## Минимальный запуск
```bash
python3 ros-meetup-2026/examples/asyncio/async_node_demo.py
```

## Почему это решение принято
Оно повышает читаемость сценариев и делает обработку ошибок более детерминированной.
