# Tutorial 05: Изоляция конфигов для нескольких роботов

## Проблема
В одном репозитории конфиги разных роботов легко «перетирают» друг друга.

## Цель
Сделать profile-based конфигурацию через переменные окружения, чтобы изменения одного профиля не влияли на другие.

## Файлы примера
- `ros-meetup-2026/examples/multi_robot_profiles/config_paths.py`
- `ros-meetup-2026/examples/multi_robot_profiles/config/system_bringup/params/lab/picker_node.yaml`
- `ros-meetup-2026/examples/multi_robot_profiles/config/system_bringup/params/line_a/picker_node.yaml`
- `ros-meetup-2026/examples/multi_robot_profiles/config/system_bringup/params/line_b/picker_node.yaml`

## Механика
1. Читаем `CONFIG_PKG` и `ROBOT_PROFILE`.
2. Ищем профильный файл.
3. Если отсутствует, копируем fallback в профиль (опционально).
4. Возвращаем профильный путь.

## Пример запуска профиля
```bash
export CONFIG_PKG=system_bringup
export ROBOT_PROFILE=line_a
```

## Почему это решение принято
Оно делает поведение робота воспроизводимым: профиль становится явной частью запуска, а не «состоянием машины». 
