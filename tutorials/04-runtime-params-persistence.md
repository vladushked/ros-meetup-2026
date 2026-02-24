# Tutorial 04: Runtime изменение и сохранение параметров

## Проблема
Параметры меняются через rqt/CLI, но после перезапуска ноды изменения пропадают.

## Цель
Сделать runtime tuning персистентным: параметр обновляется в объекте ноды и сохраняется в YAML.

## Файлы примера
- `ros-meetup-2026/examples/runtime_params/tunable_node.py`
- `ros-meetup-2026/examples/runtime_params/tunable_node.yaml`

## Как работает
1. Нода объявляет параметры в `init_params`.
2. В `update_params` обновляет внутренние поля.
3. Вызывает `super().update_params(...)`, который сохраняет YAML.

## Проверка
Пример изменения параметра:
```bash
ros2 param set /tunable_node gain 1.8
ros2 param set /tunable_node bias -0.1
```

После рестарта должно остаться новое значение `gain/bias` в YAML.

## Почему это решение принято
Иначе каждая настройка превращается в ручной post-mortem после перезапуска и снижает управляемость в эксплуатации.
