# Tutorial 03: Базовый класс ноды

Соответствует слайдам 19-21 из [presentation](../../2026%20-%20ros%20meetup%20-%20presentation.md).

## Проблема

Если каждая нода отдельно реализует параметры, ROS-интерфейсы, runtime update и запуск, проект быстро расходится по стилю и поведению.

## Цель

Вынести общую инфраструктуру в базовые классы и оставить в дочерних нодах только предметную логику.

## Файлы примера

- [examples/base_node/node_base.py](../examples/base_node/node_base.py)
- [examples/base_node/simple_sync_node.py](../examples/base_node/simple_sync_node.py)
- [examples/base_node/simple_async_node.py](../examples/base_node/simple_async_node.py)
- [examples/base_node/simple_async_pub.py](../examples/base_node/simple_async_pub.py)

## Что делает базовый класс

[node_base.py](../examples/base_node/node_base.py) задаёт общий контракт:
- `init_params`;
- `init_ros_interfaces`;
- `update_params`.

`BaseNode` берёт на себя:
- объявление общих параметров;
- подключение callback для динамических параметров;
- сохранение параметров в YAML.

`AsyncBaseNode` добавляет:
- базовый `ros_loop`;
- авто-регистрацию async loop через `@register_loop`;
- единый `run()` для нескольких фоновых задач.

## Sync-пример

[simple_sync_node.py](../examples/base_node/simple_sync_node.py) показывает обычную service-node рамку:
- параметр `message`;
- publisher и timer;
- сохранение параметров через `BaseNode.update_params(...)`.

## Async-примеры

[simple_async_node.py](../examples/base_node/simple_async_node.py) показывает async-ноду с runtime-параметром `period_sec`.

[simple_async_pub.py](../examples/base_node/simple_async_pub.py) соответствует примеру со слайда 21:
- publisher создаётся в `init_ros_interfaces`;
- `heartbeat_loop` оформлен как линейный async-цикл;
- запуск идёт через `base_main(...)`.

## Почему это решение принято

Так новая нода собирается по понятному шаблону, а sync и async варианты сохраняют общий стиль и единый жизненный цикл.
