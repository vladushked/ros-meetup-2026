# ROS Meetup 2026 Materials

Репозиторий собирает материалы к докладу про практики DX в ROS 2 на production-системе.

Здесь лежат:
- [presentation.md](presentation.md) - структура презентации по слайдам.
- [speech.md](speech.md) - готовый короткий спич для каждого слайда.
- [tutorials/](tutorials/) - компактные туториалы по темам доклада.
- [examples/](examples/) - примеры кода и конфигов, на которые ссылаются туториалы.

## Маршрут чтения

1. [Tutorial 01: Launch-архитектура и прокидка аргументов](tutorials/01-launch-contract.md)
2. [Tutorial 05: Изоляция конфигов для нескольких роботов](tutorials/05-multi-robot-config-isolation.md)
3. [Tutorial 04: Runtime изменение и сохранение параметров](tutorials/04-runtime-params-persistence.md)
4. [Tutorial 02: Система сборки и запуска](tutorials/02-build-run-tooling.md)
5. [Tutorial 03: Базовый класс ноды](tutorials/03-base-node-sync-async.md)
6. [Tutorial 06: Asyncio в ROS 2](tutorials/06-ros2-asyncio.md)
7. [Tutorial 07: Паттерн `register_loop`](tutorials/07-register-loop-pattern.md)
8. [Tutorial 08: Асинхронная FSM](tutorials/08-async-fsm.md)

## Как темы связаны со слайдами

- Слайды 7-10: [Tutorial 01](tutorials/01-launch-contract.md), примеры в [examples/launch_contract](examples/launch_contract)
- Слайды 12-15: [Tutorial 05](tutorials/05-multi-robot-config-isolation.md) и [Tutorial 04](tutorials/04-runtime-params-persistence.md)
- Слайды 16-17: [Tutorial 02](tutorials/02-build-run-tooling.md), примеры в [examples/build_run_tooling](examples/build_run_tooling)
- Слайды 19-21: [Tutorial 03](tutorials/03-base-node-sync-async.md), [Tutorial 06](tutorials/06-ros2-asyncio.md), [Tutorial 07](tutorials/07-register-loop-pattern.md)
- Итоговый пункт про FSM из резюме: [Tutorial 08](tutorials/08-async-fsm.md)

## Примеры по разделам

- Launch-контракт: [system_bringup.launch.py](examples/launch_contract/system_bringup.launch.py), [manipulator_stack.launch.py](examples/launch_contract/manipulator_stack.launch.py)
- Build/run tooling: [build.sh](examples/build_run_tooling/build.sh), [run.sh](examples/build_run_tooling/run.sh), [docker.sh](examples/build_run_tooling/docker.sh)
- Base node: [node_base.py](examples/base_node/node_base.py), [simple_sync_node.py](examples/base_node/simple_sync_node.py), [simple_async_node.py](examples/base_node/simple_async_node.py), [simple_async_pub.py](examples/base_node/simple_async_pub.py)
- Runtime params: [tunable_node.py](examples/runtime_params/tunable_node.py), [tunable_node.yaml](examples/runtime_params/tunable_node.yaml)
- Multi-robot profiles: [config_paths.py](examples/multi_robot_profiles/config_paths.py), [config](examples/multi_robot_profiles/config)
- Asyncio and loops: [async_node_demo.py](examples/asyncio/async_node_demo.py), [async_subscription.py](examples/asyncio/async_subscription.py), [task_orchestrator_node.py](examples/register_loop/task_orchestrator_node.py)
- Async FSM: [task_fsm.py](examples/async_fsm/task_fsm.py), [fsm_driver_node.py](examples/async_fsm/fsm_driver_node.py)

## Контакты

- Докладчик: Владислав Плотников, разработчик ПО верхнего уровня
- Telegram: [@vladislavplotnikov](https://t.me/vladislavplotnikov)
- Сайт: [vladislavplotnikov.ru](https://vladislavplotnikov.ru)
- Telegram-канал: [ВЛАДОС НАКОДИЛ](https://t.me/vladosnakodil)
- Компания: [l-labs.tech](https://l-labs.tech)
- Telegram компании: [@L_Labs](https://t.me/L_Labs)
