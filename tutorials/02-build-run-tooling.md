# Tutorial 02: Система сборки и запуска

Соответствует слайдам 16-17 из [presentation.md](../presentation.md).

## Проблема

В многопакетном ROS 2 workspace основные потери времени происходят в рутине:
- собрать только нужные пакеты;
- запустить типовой entrypoint без длинной команды;
- держать одинаковый dev workflow у всей команды.

## Цель

Сделать единый путь `контейнер -> сборка -> запуск -> логи` с короткими командами и автодополнением.

## Файлы примера

- [examples/build_run_tooling/build.sh](../examples/build_run_tooling/build.sh)
- [examples/build_run_tooling/run.sh](../examples/build_run_tooling/run.sh)
- [examples/build_run_tooling/docker.sh](../examples/build_run_tooling/docker.sh)
- [examples/build_run_tooling/ros2_build_completion.sh](../examples/build_run_tooling/ros2_build_completion.sh)
- [examples/build_run_tooling/ros2_launch_completion.sh](../examples/build_run_tooling/ros2_launch_completion.sh)

В реальном проекте такие утилиты обычно лежат в `scripts/`, а в этом репозитории они собраны в `examples/build_run_tooling`.

## Build wrapper

[build.sh](../examples/build_run_tooling/build.sh) добавляет удобную обёртку вокруг `colcon build`:
- `-c` очищает весь workspace или выбранные пакеты;
- `-u` собирает пакет вместе с зависимостями;
- `-x` пропускает указанные пакеты;
- `-j`, `-w`, `-v` управляют производительностью и логами;
- `-p` запускает `rosdep install`.

Примеры:

```bash
./examples/build_run_tooling/build.sh
./examples/build_run_tooling/build.sh -u manipulator_stack
./examples/build_run_tooling/build.sh -c manipulator_stack
```

## Launch wrapper

[run.sh](../examples/build_run_tooling/run.sh) стандартизирует запуск:
- по умолчанию стартует `system_bringup`;
- `-v` автоматически добавляет `visualize:=true`;
- проверяет наличие пакета и launch-файла;
- складывает консольный вывод в `debug/console_logs/<timestamp>`.

Примеры:

```bash
./examples/build_run_tooling/run.sh
./examples/build_run_tooling/run.sh -v system_bringup
./examples/build_run_tooling/run.sh manipulator_stack manipulator_stack
```

## Docker entrypoint

[docker.sh](../examples/build_run_tooling/docker.sh) приводит dev-окружение к одному виду:
- подхватывает `.env`, если он есть;
- выставляет `ROS_DOMAIN_ID`;
- монтирует workspace в `/workspace`;
- одинаково запускает контейнер у всех разработчиков.

Примеры:

```bash
./examples/build_run_tooling/docker.sh
./examples/build_run_tooling/docker.sh 52
```

## Shell completion

Автодополнения ускоряют повседневные действия:
- [ros2_build_completion.sh](../examples/build_run_tooling/ros2_build_completion.sh) подсказывает имена пакетов из `src/*/package.xml`;
- [ros2_launch_completion.sh](../examples/build_run_tooling/ros2_launch_completion.sh) подсказывает пакеты и launch-файлы из `install/`.

Подключение:

```bash
source ./examples/build_run_tooling/ros2_build_completion.sh
source ./examples/build_run_tooling/ros2_launch_completion.sh
```

## Почему это решение принято

Эти утилиты сокращают путь "изменил код -> собрал -> запустил -> проверил" и уменьшают количество операционных ошибок без изменений в бизнес-логике.
