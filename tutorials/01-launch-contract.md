# Tutorial 01: Launch-архитектура и прокидка аргументов

## Проблема
В больших системах launch-файлы превращаются в несвязанный набор скриптов: аргументы объявляются в одном месте, а до конкретной ноды не доходят.

## Цель
Сделать launch-контракт, где аргумент проходит всю цепочку:
`root launch -> package launch -> Node(parameters/remappings)`.

## Файлы примера
- `ros-meetup-2026/examples/launch_contract/system_bringup.launch.py`
- `ros-meetup-2026/examples/launch_contract/manipulator_stack.launch.py`

## Шаг 1. Root launch
В `system_bringup.launch.py`:
1. объявляем публичные аргументы;
2. подключаем package launch через `IncludeLaunchDescription`;
3. пробрасываем аргументы через `launch_arguments`.

## Шаг 2. Package launch
В `manipulator_stack.launch.py`:
1. повторно объявляем аргументы (чтобы интерфейс package launch был самодокументируемым);
2. подставляем `LaunchConfiguration(...)` в `parameters`;
3. мапим топики в `remappings`.

## Шаг 3. Проверка
Минимальный smoke-test команды:
```bash
ros2 launch system_bringup system_bringup.launch.py \
  visualize:=true \
  robot_pose_topic:=/demo/pose \
  fsm_state_topic:=/demo/fsm
```

Критерий успеха:
- нода поднимается;
- remap-имена совпадают с переданными аргументами;
- при изменении root-аргумента поведение ноды меняется без правки package launch.

## Почему это решение принято
Потому что это минимизирует «скрытые» launch-зависимости и упрощает поддержку при росте числа пакетов.
