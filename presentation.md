## 1) Как улучшить опыт разработки в ROS2

### Слайд:
Владислав Плотников
разработчик ПО верхнего уровня l-labs.tech

---

## 2) План доклада

### Слайд:

- О компании l-labs.tech
- РАМ30 - робот-сортировщик ТКО
- Практики и лайфхаки - как улучшить DX в ROS2

подпись - Время доклада ~11 минут

---

## 3) l-labs.tech

### Слайд:
- робототехника (картинка)
- видеоаналитика (картинка)

---

## 4)

### Слайд:
видео демо робота

подпись - Демонстрация робота-сортировщика ТКО от l-labs.tech

---

## 5) Как улучшить DX в ROS2

### Слайд:

**Код один, роботов много**
Как организовать хранение и подгрузку конфиг файлов для отдельных роботов?

**Много подсистем**
Как не запутаться в launch файлах и аргументах

**Отладка - рутина**
Как сделать отладку эффективнее и убрать рутинные действия?

**Как сделать красиво?**
Красивый код - понятный код

---

## 6) Launch система разумиста

---

## 7) Систематизация launch файлов

### Слайд:
диаграмма с пакетами. показано что проект содержит много пакетов, лаунч файлов и нод

подпись - ros пакеты с launch файлами, отдельные ноды

---

## 8) Систематизация launch файлов

### Слайд:
диаграмма с иерархией лаунч файлов, от корневого до ноды

подпись - robot_grasping.launch.py - entrypoint проекта

---

## 9) Launch-аргументы

### Слайд:
диаграмма с последовательностью передачи аргументов из корневого лаунч в ноду.
нода

    launch корневой
    Оркестрация аргументами

    launch пакета
    Применение флагов, remap интерфейсов, загрузка файлов параметров

    launch ноды
    Выбор ноды

подпись - Корневой launch - контракт всей системы

---

## 10) Launch-аргументы

### Слайд:
картинка -
    object detection topic = /od/dets
    visualize = True
    camera = realsense
    x_tol = 0.1 (зачеркнуто) - в параметры

подпись - launch-аргументы - имена ROS интерфейсов, флаги, launch specific аргументы. Все остальное - в файлы параметров

---

## 11) Про config-файлы

---

## 12) Несколько роботов, один config

### Слайд:
диаграмма показывающая что раньше код разрабатывался и тестировался на одном роботе, но потом роботов стало два и начался ад с мерж конфликтами

подпись
Один конфиг и несколько роботов - мерж конфликты🤯

---

## 13) Изоляция config-файлов

### Слайд:
текст
    export CONFIG_PKG=robot_grasping
    export ROBOT_PROFILE=lab
диаграмма показывающая как конфиги лежат в CONFIG_PKG разделенные по папкам ROBOT_PROFILE

подпись - Изменения параметров профиля lab не влияют на pilot

---

## 14) Убираем рутинные действия

---

## 15) Runtime-параметры: изменение и сохранение

### Слайд:
диаграмма показывающая как обновляются параметры в конфиг файлах
    add_on_set_parameters_callback (internal)
    update_params (node)
    save (yaml файл в папке config_pkg/robot_profile)

подпись - 💡 colcon build --symlink-install - изменения сразу в src

подпись - Файлы параметров легко версионируются через git

---

## 16) Система сборки и запуска

### Слайд:
4 подписи
    🏗️ scripts/build.sh
    Сборка и очистка workspace, выбор пакетов, bash alias “b”

    ▶️ scripts/run.sh
    Запуск launch файлов, флаги сценариев, bash alias “r”

    📦 scripts/docker.sh
    Запуск проекта в контейнере, загрузка .env, , symlink “./d”

    ⇄ Autocompletion
    Названия пакетов, launch файлов

подпись - Сокращается путь «изменение → сборка → запуск → отладка»

---

## 17)

### Слайд:

```bash
# запуск контейнера
./d
# запуск контейнера с указанием ROS_DOMAIN_ID=52
./d 52
# полная очистка (build, log, install)
b -с
# сборка всего проекта
b
# запуск entrypoint launch проекта (project_name/launch/project_name.launch.py)
r
# удаление файлов сборки для пакета robot_control
b -с robot_control
# сборка пакета robot_control
b robot_control
# запуск entrypoint launch пакета robot_control (robot_control/launch/project_name.launch.py) с аргументом visualize:=true
r -v robot_control
```

подпись - Пример dev workflow

---

## 18) Делаем красиво

---

## 19) Базовый класс ноды

### Слайд:
диаграмма показывающая наследование классов ноды
    AbstractNode
    BaseNode | AsyncNode
    YourNode

подпись
- инициализация параметров
- объявление ros интерфейсов
- обновление и сохранение параметров
- логгер

---

## 20) asyncio в ROS 2: линейный код без коллбеков

### Слайд:
2 подписи
    🔀 @register_loop
    Декоратор, который делает из метода async корутину

    🔀 ros_loop
    Цикл обновления событий ros внутри базового класса AsyncNode

картинка на которой показан пример кода с несколькими @register_loop
```python
@register_loop
async def grasping_loop(self):
    while ok():
        ...
        await asyncio.sleep(1e-4)

@register_loop
async def _fsm_loop(self):
    while ok():
        await self.fsm.step()
        await asyncio.sleep(1e-4)

@register_loop
async def _sensor_loop(self):
    while ok():
        ...
```

подпись - 💡 замена таймера для периодических задач

---

## 21)

### Слайд:

картинка
```python
class SimpleAsyncPubNode(AsyncBaseNode):
    def __init__(self):
        super().__init__(
            package_name="demo_pkg",
            node_name="simple_async_node",
        )

    def init_ros_interfaces(self) -> None:
        self.pub = self.create_publisher(String, "async/out", 10)

    @register_loop
    async def heartbeat_loop(self):
        while True:
            self.pub.publish(String(data=f"tick"))
            await asyncio.sleep(0.5)

def main(args=None):
    return base_main(SimpleAsyncPubNode, args=args)
```

подпись - Пример async publisher

---

## 22) Резюме

### Слайд:

- единый root launch и явная прокидка аргументов до ноды
- profile-based конфиги через CONFIG_PKG и ROBOT_PROFILE
- runtime-параметры с сохранением в YAML
- build/run/docker/completion для короткого dev workflow
- базовый класс ноды и async loop-модель вместо callback-heavy кода

подпись - Не ради красоты кода, а ради устойчивой эксплуатации нескольких роботов

---

## 23) l-labs.tech

**Владислав Плотников**

### Слайд:
подпись - докладчик:
Владислав Плотников
разработчик ПО верхнего уровня

подпись - Контакты и подробные туториалы: (картинка с куар кодом)
