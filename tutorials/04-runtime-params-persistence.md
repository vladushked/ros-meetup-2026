# Tutorial 04: Runtime изменение и сохранение параметров

Соответствует слайду 15 из [presentation](../../2026%20-%20ros%20meetup%20-%20presentation.md).

## Проблема

Менять параметры в runtime удобно, но без сохранения в YAML результат пропадает после перезапуска ноды.

## Цель

Сделать tuning персистентным: параметр меняется в объекте ноды и сразу записывается в конфиг.

## Файлы примера

- [examples/runtime_params/node_base.py](../examples/runtime_params/node_base.py)
- [examples/runtime_params/tunable_node.py](../examples/runtime_params/tunable_node.py)
- [examples/runtime_params/tunable_node.yaml](../examples/runtime_params/tunable_node.yaml)

## Как это устроено

1. Нода объявляет параметры в `init_params`.
2. В `update_params` обновляет внутренние поля.
3. Базовый класс сохраняет актуальные `ros__parameters` в YAML через `save_params(...)`.

В примере [tunable_node.py](../examples/runtime_params/tunable_node.py):
- `gain` и `bias` влияют на публикуемое значение;
- после `ros2 param set` новые значения остаются в [tunable_node.yaml](../examples/runtime_params/tunable_node.yaml).

## Проверка

```bash
ros2 param set /tunable_node gain 1.8
ros2 param set /tunable_node bias -0.1
```

После этого в YAML должны сохраниться новые значения `gain` и `bias`.

## Практический эффект

- оператор видит результат сразу в работе ноды;
- подобранные параметры не теряются после рестарта;
- конфиг легко версионировать через Git.

## Почему это решение принято

Иначе runtime tuning превращается в временный эксперимент, который нужно вручную повторять после каждого запуска.
