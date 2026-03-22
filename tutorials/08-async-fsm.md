# Tutorial 08: Асинхронная FSM

Развивает итоговый пункт из слайда 22 в [presentation](../../2026%20-%20ros%20meetup%20-%20presentation.md).

## Проблема

Если переходы состояний происходят в разных callback и сервисах, автомат быстро перестаёт быть явной моделью и становится набором side effects.

## Цель

Вынести состояние и переходы в отдельный объект FSM и исполнять их централизованно в async loop.

## Файлы примера

- [examples/async_fsm/task_fsm.py](../examples/async_fsm/task_fsm.py)
- [examples/async_fsm/fsm_driver_node.py](../examples/async_fsm/fsm_driver_node.py)

## Как устроен пример

1. [task_fsm.py](../examples/async_fsm/task_fsm.py) строит автомат на `transitions.AsyncMachine`.
2. Внешний код ставит только `pending transition`.
3. `step()` проверяет валидность перехода и выполняет его централизованно.
4. Нода публикует состояние только после фактического изменения.

Мини-сценарий из примера:
`CHECKS -> READY -> EXECUTION -> STOP`.

## Где это сочетается с async loop моделью

В [fsm_driver_node.py](../examples/async_fsm/fsm_driver_node.py):
- `ros_loop()` обрабатывает ROS-события;
- `fsm_loop()` регулярно вызывает `await self.fsm.step()`;
- отдельный `scenario_loop()` имитирует внешние события.

## Почему это решение принято

FSM становится проверяемым контрактом состояний и переходов, а не логикой, размазанной по коду.
