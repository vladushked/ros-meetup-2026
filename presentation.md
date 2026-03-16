## 1) Улучшаем опыт разработки в ROS2

### Слайд:
Владислав Плотников, разработчик ПО верхнего уровня

### Текст:

---

## 2) План доклада

### Слайд:
подпись - ололо 8 минут

- О компании l-labs.tech 
- РАМ3.0 - робот-сортировщик ТКО
- Практики и лайфхаки

---

## 3) L-Labs

### Слайд:
- робототехника
- видеоаналитика
- контроль процессов

### Заметки:
- L-Labs разрабатывает решения в робототехнике, компьютерном зрении и видеоаналитике
- фокус на прикладных задачах автоматизации: контроль качества, безопасность, экологические задачи
- основной роботехнический продукт - автоматический робот-сортировщик ТКО
- это не учебный пример, а production-система с реальными ограничениями;
- нужна воспроизводимая эксплуатация, а не только рабочий прототип.

### Текст:

---

## 4) 

### Слайд:
видео гифка с роботом
Демонстрация робота-сортировщика ТКО от l-labs.tech


### Заметки:
- промышленный робот-манипулятор портального типа
- устанавливается на конвейерную ленту и автономно сортирует до 4-х фракций одновременно без участия человека
- СТЗ распознает до 54 фракций мусора
- ПО робота написано на базе ROS 2

**Что это за система**
- промышленный робот-манипулятор портального типа;
- 4 степени свободы: перемещение по `X/Y/Z` и вращение хвата вокруг вертикальной оси;
- сверху установлены робот и модуль технического зрения над конвейерной лентой;
- ПО робота написано на базе ROS 2.

**Что умеет система**
- распознает объекты с помощью RGB-D и детектора объектов;
- определяет точки и углы захвата;
- может сортировать до 4 целевых фракций одновременно;
- решение ориентировано на промышленную эксплуатацию и российскую морфологию отходов.

**Цикл работы**
1. При запуске выполняются калибровка МТЗ и проверка подсистем.
2. Оператор задает целевые фракции на панели.
3. МТЗ передает изображения в ПО верхнего уровня.
4. Vision-стек выполняет детекцию и трекинг объектов.
5. Алгоритм выбирает наиболее релевантный объект.
6. Робот захватывает объект и отправляет его в нужную урну.

### Текст:
---

## 5) Как улучшить DX в ROS2
### Слайд:

**Код один, роботов много**
Как организовать хранение и подгрузку конфиг файлов для отдельных роботов?

Много подсистем
Как не запутаться в launch файлах и аргументах

Отладка - рутина
Как сделать отладку эффективнее и убрать рутинные действия?

Как сделать красиво?
Красивый код - понятный код

### Заметки:
здесь на слайде 4 главные темы презентации

Проблемы, которые проявились в production:
- один и тот же код должен работать на разных роботах и стендах;
- аргументы launch теряются между include-уровнями;
- сборка и запуск нужного пакета занимают слишком много рутинных шагов;
- параметры удобно менять в runtime, но без сохранения они откатываются после рестарта;
- изменение конфигурации одного робота не должно влиять на другого;
- callback-heavy код трудно читать, тестировать и сопровождать.

Главная мысль:
- дальше не набор абстрактных best practices, а конкретные решения под реальную роботизированную систему.

### Текст:
---

## 6) Launch система разумиста


---

## 7) Систематизация launch файлов
### Слайд:
диаграмма с пакетами. показано что проект содержит много пакетов, лаунч файлов и нод

подпись
ros пакеты с launch файлами, отдельные ноды

### Заметки:
**Проблема**
- когда entrypoint не централизован, команда не понимает, какие аргументы реально поддерживает система.

**Решение**
- единая точка входа: `src/system_bringup/launch/system_bringup.launch.py`;
- в root launch объявляются общие аргументы и интерфейсные топики;
- package-level launch файлы получают только явно прокинутые значения.

```python
DeclareLaunchArgument("visualize", default_value="false")
DeclareLaunchArgument("robot_pose_topic", default_value="/robot/pose")
DeclareLaunchArgument("fsm_state_topic", default_value="/fsm/state")

IncludeLaunchDescription(
    PythonLaunchDescriptionSource(... "manipulator_stack.launch.py"),
    launch_arguments={
        "visualize": LaunchConfiguration("visualize"),
        "robot_pose_topic": LaunchConfiguration("robot_pose_topic"),
        "fsm_state_topic": LaunchConfiguration("fsm_state_topic"),
    }.items()
)
```

Эффект:
- появляется одно место для ревью launch-контракта;
- поведение системы становится предсказуемым.

### Текст:

---

## 8) Систематизация launch файлов
### Слайд:
диаграмма с иерархией лаунч файлов, от корневого до ноды

подпись
robot_grasping.launch.py - entrypoint проекта

### Заметки:

### Текст:

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

подпись
Корневой launch - контракт всей системы


### Заметки:
**Проблема**
- объявленный аргумент бесполезен, если он не дошел до `Node(...)`.

**Решение**
- прокидка должна быть явной на каждом уровне;
- package launch мапит аргументы в `parameters` и `remappings` ноды.

```python
Node(
    package="manipulator_stack",
    executable="motion_executor_node",
    parameters=[
        motion_params_file,
        {
            "visualize": LaunchConfiguration("visualize"),
            "trajectory_action_name": LaunchConfiguration("trajectory_action_name"),
        },
    ],
    remappings=[
        ("robot/pose", LaunchConfiguration("robot_pose_topic")),
        ("fsm/state", LaunchConfiguration("fsm_state_topic")),
    ],
)
```

Эффект:
- изменение аргумента в root launch предсказуемо влияет на конкретную ноду;
- проще сопровождать систему при росте числа пакетов.

### Текст:

---

## 10) Launch-аргументы
### Слайд:
картинка - 
    object detection topic = /od/dets
    visualize = True
    camera = realsense
    x_tol = 0.1 (зачеркнуто) - в параметры

подпись
launch-аргументы - имена ROS интерфейсов, флаги, launch specific аргументы. Все остальное - в файлы параметров

### Заметки:

### Текст:

---

## 11) Организация конфиг файлов


---

## 12) Изоляция конфигов
### Слайд:
диаграмма показывающая что раньше код разрабатывался и тестировался на одном роботе, но потом роботов стало два и начался ад с мерж конфликтами

подпись
Один конфиг и несколько роботов - мерж конфликты🤯

### Заметки:
**Проблема**
- при общей кодовой базе конфиги разных роботов легко смешиваются.



### Текст:

---


## 13) Изоляция конфигов
### Слайд:
текст
    export CONFIG_PKG=robot_grasping
    export ROBOT_PROFILE=lab
диаграмма показывающая как конфиги лежат в CONFIG_PKG разделенные по папкам ROBOT_PROFILE

подпись - Изменения параметров профиля lab не влияют на pilot


### Заметки:

**Решение**
- профильные пути задаются через `CONFIG_PKG` и `ROBOT_PROFILE`;
- поиск конфигов и fallback-логика вынесены в общий util.

```python
config_pkg = os.getenv("CONFIG_PKG", "").strip()
robot_profile = os.getenv("ROBOT_PROFILE", "").strip()
profiled_config_file = package_share / config_dir / robot_profile / config_name

if profiled_config_file.exists():
    return profiled_config_file
```

Практика запуска:
```bash
export CONFIG_PKG=system_bringup
export ROBOT_PROFILE=lab
ros2 launch system_bringup system_bringup.launch.py visualize:=true
```

Эффект:
- правки профиля `lab` не перетирают `line_a` и `line_b`;
- один код работает на нескольких конфигурациях без ручного хаоса.

### Текст:

---




## 9) Система сборки и запуска в большом ROS 2 workspace

**Проблема**
- в многопакетном проекте длинные команды становятся медленными и ошибкоопасными;
- dev-запуск в Docker начинает отличаться между разработчиками.

**Решение**
- стандартизировать workflow через утилитарные скрипты:
  - `scripts/build.sh` для selective build и типовых сценариев сборки;
  - `scripts/run.sh` для короткого запуска launch-файлов;
  - `scripts/docker.sh` как единая точка входа в dev-контейнер;
  - shell completion для `b` и `r`.

```bash
./d                         # вход в контейнер
b -u manipulator_stack      # сборка пакета с зависимостями
r -v system_bringup         # запуск launch с visualize:=true
```

Эффект:
- сокращается путь "изменил код -> собрал -> запустил -> проверил";
- ниже порог входа в проект и меньше операционных ошибок.

---

## 10) Базовый класс ноды: единая рамка для sync и async

**Проблема**
- без общей рамки каждая нода дублирует lifecycle и параметрическую логику.

**Решение**
- `BaseNodeAbstract` задает обязательный контракт;
- `BaseNode` берет на себя общий runtime;
- `AsyncBaseNode` расширяет модель асинхронными циклами.

```python
class BaseNodeAbstract(ABC, Node):
    @abstractmethod
    def init_params(self): ...
    @abstractmethod
    def init_ros_interfaces(self): ...
    @abstractmethod
    def update_params(self, param_list): ...

class BaseNode(BaseNodeAbstract):
    def __init__(self, package_name: str, node_name: str):
        super().__init__(node_name)
        self.params_file = get_param_path(package_name, node_name, self.logger)
        self.init_params()
        if self.dynamic_params:
            self.add_on_set_parameters_callback(self.update_params)
        self.init_ros_interfaces()
```

Эффект:
- новую ноду проще собрать по понятному шаблону;
- поведение sync и async нод становится более единообразным.

---

## 11) Runtime-параметры: менять в работе и сохранять на диск

**Проблема**
- tuning в runtime ценен только тогда, когда параметры переживают рестарт.

**Решение**
- callback изменений обновляет runtime-поля;
- после изменения параметры сохраняются в YAML.

```python
def update_params(self, param_list):
    for param in param_list:
        match param.name:
            case "robot_vel":
                self.robot.vel = param.value
            case "robot_accel":
                self.robot.accel = param.value
    self.save_params(param_list)
    return SetParametersResult(successful=True)

def save_params(self, param_list):
    params = {
        self.get_name(): {
            "ros__parameters": {p.name: p.value for p in self._parameters.values()}
        }
    }
    with open(self.params_file, "w") as f:
        yaml.dump(params, f, default_flow_style=False)
```

Эффект:
- параметр меняется сразу в работе ноды;
- результат настройки не теряется после перезапуска.

---


## 13) Asyncio в ROS 2: линейный код вместо каскада коллбеков

Источник вдохновения:
- https://github.com/m2-farzan/ros2-asyncio

**Проблема**
- callback-heavy код плохо читается и усложняет обработку ошибок.

**Решение**
- отдельный `ros_loop` с `spin_once`;
- бизнес-циклы пишутся как обычные `async def`;
- исключения поднимаются через `FIRST_EXCEPTION`.

```python
@register_loop
async def ros_loop(self):
    while rclpy.ok():
        rclpy.spin_once(self, timeout_sec=0)
        await asyncio.sleep(1e-4)

def run(self):
    futures = [loop(self) for loop in self.async_loops]
    done, _pending = asyncio.get_event_loop().run_until_complete(
        asyncio.wait(futures, return_when=asyncio.FIRST_EXCEPTION)
    )
    for task in done:
        task.result()
```

Эффект:
- код бизнес-логики становится линейнее;
- ошибки не теряются внутри дерева коллбеков.

---

## 14) `@register_loop`: несколько независимых async-задач в одной ноде

**Проблема**
- у робота одновременно живут grasping, FSM, heartbeat, watchdog и работа с внешними сервисами.

**Решение**
- декоратор помечает loop-методы;
- `AsyncBaseNode` автоматически собирает их и запускает параллельно.

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

Эффект:
- у каждой фоновой задачи остается локальная, читаемая логика;
- проще масштабировать ноду без переписывания orchestration-кода.

---

## 15) Асинхронная FSM: явные переходы вместо скрытых side effects

**Проблема**
- сложные переходы состояния в управлении роботом быстро становятся неявными.

**Решение**
- `TaskFSM` построена на `transitions.AsyncMachine`;
- pending transition исполняется централизованно в `step()`.

```python
self.machine = AsyncMachine(
    model=self,
    states=states,
    transitions=transitions,
    initial=TaskFSM.State.CHECKS,
    auto_transitions=False,
    after_state_change="_execute_state",
)

async def step(self):
    if self._pending_transition:
        pending = self._pending_transition
        self._pending_transition = None
        if pending in self.machine.get_triggers(self.state):
            await self.trigger(pending)
```

Интеграция:
```python
@register_loop
async def _fsm_loop(self):
    while ok():
        await self.fsm.step()
        await asyncio.sleep(1e-4)
```

Эффект:
- переходы становятся явными, валидируемыми и воспроизводимыми;
- проще отлаживать поведение робота в сложных сценариях.

---

## 16) Что можно внедрить в другой ROS 2 проект уже завтра

1. Ввести единый root launch и правило явной прокидки аргументов до node-level.
2. Обернуть dev workflow в `build/run/docker` и дать команде completion.
3. Вынести общую рамку ноды в базовый класс.
4. Сохранять runtime-параметры сразу после изменения.
5. Разделять конфиги по профилям через `CONFIG_PKG/ROBOT_PROFILE`.
6. Использовать async loop-модель для читаемой конкуррентности.
7. Делать FSM явной и управляемой, а не размазанной по коллбекам.

**Главная идея доклада**
- эти решения нужны не ради "красоты кода", а ради устойчивой эксплуатации нескольких роботов в одной кодовой базе.

---

## 17) Контакты

**Владислав Плотников**

Разработчик ПО верхнего уровня

Что показать на слайде:
- имя и должность;
- QR-код на Telegram-канал: `https://t.me/vladosnakodil`;
- подпись: "В Telegram-канале будет ссылка на tutorial-репозиторий GitHub";
- подпись: "Все остальные контакты можно найти в канале".

Контакты для speaker notes или мелкого текста на слайде:
- личный Telegram: `https://t.me/vladislavplotnikov`;
- сайт: `vladislavplotnikov.ru`;
- канал: `ВЛАДОС НАКОДИЛ` — `https://t.me/vladosnakodil`;
- компания: `l-labs.tech`;
- Telegram компании: `https://t.me/L_Labs`.
