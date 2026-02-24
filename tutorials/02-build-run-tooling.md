# Tutorial 02: Система сборки и запуска через launch-файлы

## Проблема
В проекте с большим количеством ROS-пакетов основная потеря времени происходит не в коде, а в операционных шагах:
- найти нужный пакет и launch-файл;
- собрать только то, что нужно, а не весь workspace;
- запускать одинаково у всех разработчиков (локально/в контейнере).

## Цель
Сделать единый DX-поток: `docker -> build -> launch`, с короткими командами и автодополнением.

## Референс из рабочего проекта
- `docker/ros2_build_completion.sh`
- `docker/ros2_launch_completion.sh`
- `scripts/docker.sh`
- `scripts/build.sh`
- `scripts/run.sh`

## Учебные файлы в этом наборе
- `ros-meetup-2026/examples/build_run_tooling/build.sh`
- `ros-meetup-2026/examples/build_run_tooling/run.sh`
- `ros-meetup-2026/examples/build_run_tooling/ros2_build_completion.sh`
- `ros-meetup-2026/examples/build_run_tooling/ros2_launch_completion.sh`
- `ros-meetup-2026/examples/build_run_tooling/docker.sh`

## Шаг 1. Build wrapper
`build.sh` добавляет управление сборкой поверх `colcon`:
1. `--packages-select / --packages-up-to / --packages-skip`;
2. `-c` clean по workspace или по выбранным пакетам;
3. `-p` для `rosdep install` перед сборкой;
4. `-j/-w/-v` для контроля производительности и логов.

Пример:
```bash
./build.sh -u -v manipulator_stack
```

## Шаг 2. Launch wrapper
`run.sh` стандартизирует запуск:
1. `-v` автоматически пробрасывает `visualize:=true`;
2. проверяет существование пакета и launch-файла;
3. пишет консольный вывод в timestamp-папку `debug/console_logs/...`.

Пример:
```bash
./run.sh -v system_bringup
```

## Шаг 3. Shell completion
Автодополнения ускоряют повседневные команды:
- `ros2_build_completion.sh` предлагает имена пакетов из `src/*/package.xml`;
- `ros2_launch_completion.sh` предлагает пакеты/launch-файлы из install-space.

Подключение в shell-сессию:
```bash
source ros-meetup-2026/examples/build_run_tooling/ros2_build_completion.sh
source ros-meetup-2026/examples/build_run_tooling/ros2_launch_completion.sh
```

## Шаг 4. Docker entrypoint
`docker.sh` делает запуск окружения воспроизводимым:
1. читает `.env`;
2. выставляет `ROS_DOMAIN_ID`;
3. прокидывает workspace и X11;
4. запускает dev image в одинаковой конфигурации.

## Почему это решение принято
Потому что в больших ROS2-репозиториях стабильный процесс сборки/запуска снижает количество ошибок сильнее, чем точечные улучшения в отдельных пакетах.
