# Tutorial 01: Launch-архитектура и прокидка аргументов

Соответствует слайдам 7-10 из [presentation](../../2026%20-%20ros%20meetup%20-%20presentation.md).

## Проблема

В большом ROS 2 проекте launch-файлы быстро расползаются по пакетам. Если публичные аргументы объявлены в одном месте, а до `Node(...)` не доходят, контракт системы становится неявным.

## Цель

Собрать единый launch-контракт по цепочке:
`root launch -> package launch -> Node(parameters/remappings)`.

## Файлы примера

- [examples/launch_contract/system_bringup.launch.py](../examples/launch_contract/system_bringup.launch.py)
- [examples/launch_contract/manipulator_stack.launch.py](../examples/launch_contract/manipulator_stack.launch.py)

## Шаг 1. Root launch

В [system_bringup.launch.py](../examples/launch_contract/system_bringup.launch.py):
1. объявляются публичные аргументы системы;
2. package launch подключается через `IncludeLaunchDescription`;
3. аргументы явно передаются через `launch_arguments`.

Именно root launch становится точкой входа и местом ревью launch-контракта.

## Шаг 2. Package launch

В [manipulator_stack.launch.py](../examples/launch_contract/manipulator_stack.launch.py):
1. повторно объявляются аргументы package-level launch;
2. значения `LaunchConfiguration(...)` мапятся в `parameters`;
3. интерфейсные имена мапятся в `remappings`.

Это не даёт аргументам "потеряться" между уровнями include.

## Шаг 3. Что считать launch-аргументом

В launch-аргументы имеет смысл выносить:
- имена топиков, action и других ROS-интерфейсов;
- флаги сценария вроде `visualize`;
- параметры, которые управляют самим процессом запуска.

В файлы параметров лучше оставлять численные и алгоритмические настройки ноды.

## Проверка

Пример smoke-test команды:

```bash
ros2 launch system_bringup system_bringup.launch.py \
  visualize:=true \
  robot_pose_topic:=/demo/pose \
  fsm_state_topic:=/demo/fsm \
  trajectory_action_name:=/demo/execute_trajectory
```

Критерий успеха:
- root launch остаётся единой точкой входа;
- package launch не создаёт своих скрытых дефолтов;
- переданные имена интерфейсов реально доходят до `Node(...)`.

## Почему это решение принято

Так launch-файлы масштабируются предсказуемо: у системы есть один публичный вход, а каждый следующий уровень только явно применяет уже объявленный контракт.
