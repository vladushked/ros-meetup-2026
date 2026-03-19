# Tutorial 05: Изоляция конфигов для нескольких роботов

Соответствует слайдам 12-13 из [presentation.md](../presentation.md).

## Проблема

Когда одна кодовая база обслуживает несколько роботов и стендов, общий конфиг быстро превращается в источник merge conflicts и случайных регрессий.

## Цель

Разделить конфиги по профилям, чтобы изменения одного робота не влияли на другого.

## Файлы примера

- [examples/multi_robot_profiles/config_paths.py](../examples/multi_robot_profiles/config_paths.py)
- [examples/multi_robot_profiles/config/system_bringup/params/lab/picker_node.yaml](../examples/multi_robot_profiles/config/system_bringup/params/lab/picker_node.yaml)
- [examples/multi_robot_profiles/config/system_bringup/params/line_a/picker_node.yaml](../examples/multi_robot_profiles/config/system_bringup/params/line_a/picker_node.yaml)
- [examples/multi_robot_profiles/config/system_bringup/params/line_b/picker_node.yaml](../examples/multi_robot_profiles/config/system_bringup/params/line_b/picker_node.yaml)

## Механика

Паттерн строится вокруг двух переменных окружения:
- `CONFIG_PKG` - пакет, в котором лежат профили конфигурации;
- `ROBOT_PROFILE` - активный профиль, например `lab`, `line_a` или `line_b`.

[config_paths.py](../examples/multi_robot_profiles/config_paths.py) решает задачу в таком порядке:
1. читает `CONFIG_PKG` и `ROBOT_PROFILE`;
2. ищет профильный файл в каталоге пакета конфигов;
3. при необходимости берёт shared/fallback конфиг;
4. опционально копирует fallback в профильный путь.

## Пример запуска

```bash
export CONFIG_PKG=system_bringup
export ROBOT_PROFILE=lab
ros2 launch system_bringup system_bringup.launch.py visualize:=true
```

## Что это даёт

- правки в профиле `lab` не затрагивают `line_a` и `line_b`;
- профиль становится явной частью запуска;
- один и тот же код работает на разных конфигурациях без ручной подмены файлов.

## Почему это решение принято

Так конфигурация перестаёт быть "состоянием машины" и становится управляемой частью проекта.
