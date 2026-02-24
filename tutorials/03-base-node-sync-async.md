# Tutorial 03: Базовый класс ноды (sync + async)

## Проблема
Если каждая нода вручную реализует один и тот же lifecycle, проект быстро расходится по стилю и по поведению.

## Цель
Свести общую инфраструктуру в базовый класс и оставить в дочерней ноде только предметную логику.

## Файлы примера
- `ros-meetup-2026/examples/base_node/node_base.py`
- `ros-meetup-2026/examples/base_node/simple_sync_node.py`
- `ros-meetup-2026/examples/base_node/simple_async_node.py`

## Что реализовано в базовом классе
1. Единый контракт: `init_params`, `init_ros_interfaces`, `update_params`.
2. Подключение callback для динамических параметров.
3. Сохранение параметров в YAML.
4. Для async-версии: авто-регистрация loop-методов и общий `run()`.

## Sync-нода
`simple_sync_node.py` показывает классический случай:
- таймер + publisher;
- параметр `message` в runtime;
- сохранение через `BaseNode.update_params`.

## Async-нода
`simple_async_node.py` показывает:
- отдельный `@register_loop` worker;
- управление частотой через параметр `period_sec`;
- общий `ros_loop` в `AsyncBaseNode`.

## Почему это решение принято
Оно делает поведение нод предсказуемым и уменьшает цену добавления новых сервисных нод.
