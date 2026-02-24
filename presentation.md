## 1) Улучшаем опыт разработки в ROS 2

**Практики из production-стека: launch-контракт, build/run tooling, базовые ноды, runtime-параметры, asyncio и async FSM**

Проблема, с которой стартовали:
- один и тот же код должен работать на разных роботах и стендах;
- при росте проекта launch/параметры/коллбеки становятся хрупкими;
- runtime-настройки должны сохраняться и не ломать соседние профили.

---

## 2) Что именно ломается без архитектурных правил

**Проблема**
- аргументы launch теряются между include-уровнями;
- сборка и запуск нужного пакета занимают слишком много рутинных шагов;
- параметры «крутятся» в rqt, но после рестарта откатываются;
- изменение конфигурации одного робота случайно влияет на другого;
- callback-heavy код трудно читать и сопровождать.

**Почему нужны системные решения, а не локальные фиксы**
- проект должен масштабироваться по количеству нод и стендов;
- поведение должно быть предсказуемым для всей команды.

---

## 3) Launch как контракт системы, а не «скрипт запуска»

**Проблема**
- когда entrypoint не централизован, сложно понять, какие аргументы реально поддерживаются системой.

**Решение**
- единая точка входа: `src/system_bringup/launch/system_bringup.launch.py`;
- здесь объявляются общие аргументы и интерфейсные топики;
- здесь же подключаются package-level launch файлы.

```python
# src/system_bringup/launch/system_bringup.launch.py
DeclareLaunchArgument("visualize", default_value="false")
DeclareLaunchArgument("robot_pose_topic", default_value="/robot/pose")
DeclareLaunchArgument("fsm_state_topic", default_value="/fsm/state")

IncludeLaunchDescription(
    PythonLaunchDescriptionSource(...'manipulator_stack.launch.py'),
    launch_arguments={
        'visualize': LaunchConfiguration("visualize"),
        'robot_pose_topic': LaunchConfiguration("robot_pose_topic"),
        'fsm_state_topic': LaunchConfiguration("fsm_state_topic"),
    }.items()
)
```

Эффект:
- появилось единое место для ревью launch-контракта.

---

## 4) Прокидка аргументов по цепочке: root -> package -> node

**Проблема**
- даже объявленный аргумент бесполезен, если он не дошел до `Node(...)`.

**Решение**
- явная прокидка на каждом уровне;
- в package launch аргументы мапятся в `parameters` и `remappings` ноды.

```python
# src/manipulator_stack/launch/manipulator_stack.launch.py
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
- изменения аргумента в root-launch предсказуемо влияют на конкретную ноду.

---

## 5) Система сборки и запуска в большом ROS 2 workspace

**Проблема**
- в многопакетном проекте сложно быстро собрать и запустить нужный кусок системы;
- команды `colcon build` и `ros2 launch` становятся длинными и ошибкоопасными;
- без автодополнений теряется время на поиск имен пакетов и launch-файлов;
- dev-запуск в Docker часто отличается между разработчиками.

**Решение**
- стандартизировать workflow через утилитарные скрипты:
  - `scripts/build.sh` — сборка workspace/пакетов, selective build, clean, verbose, rosdep;
  - `scripts/run.sh` — запуск launch с коротким интерфейсом и флагом `-v` для `visualize:=true`;
  - `scripts/docker.sh` — единая точка входа в dev-контейнер с `.env`, `ROS_DOMAIN_ID`, GPU/X11;
  - `docker/ros2_build_completion.sh` и `docker/ros2_launch_completion.sh` — автодополнения для `b` и `r`.

```bash
# ключевой dev workflow
./d                         # вход в контейнер (alias на scripts/docker.sh)
b -u manipulator_stack      # сборка пакета с зависимостями (completion по package.xml)
r -v system_bringup         # запуск launch с visualize:=true (completion по install/.../launch)
```

Эффект:
- сокращается путь «изменил код -> собрал -> запустил -> проверил»;
- ниже порог входа в проект и меньше операционных ошибок в командах.

---

## 6) Базовый класс ноды: единая рамка для sync и async

**Проблема**
- без базового класса каждая нода дублирует lifecycle и параметрическую логику.

**Решение**
- `BaseNodeAbstract` задает обязательный контракт;
- `BaseNode` реализует общий runtime (логгер, параметрический файл, callbacks);
- `AsyncBaseNode` расширяет `BaseNode` async-механикой.

```python
# src/ros_runtime_utils/ros_runtime_utils/node_base.py
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

```python
# как строится конечная нода на базе класса
class MySyncNode(BaseNode):
    def __init__(self):
        super().__init__(package_name="my_pkg", node_name="my_sync_node")
    def init_params(self): ...
    def init_ros_interfaces(self): ...
    def update_params(self, param_list): ...

class MyAsyncNode(AsyncBaseNode):
    def __init__(self):
        super().__init__(package_name="my_pkg", node_name="my_async_node")
    @register_loop
    async def worker_loop(self):
        while rclpy.ok():
            await asyncio.sleep(0.01)
```

Эффект:
- новую ноду проще собирать по шаблону, меньше расхождений в поведении.

---

## 7) Runtime изменение и сохранение параметров

**Проблема**
- tuning в runtime полезен только если переживает рестарт.

**Решение**
- в базовом классе: callback изменений + сохранение в YAML;
- в конкретной ноде: обновление runtime-полей в `update_params`.

```python
# src/ros_runtime_utils/ros_runtime_utils/node_base.py
# + src/manipulator_stack/manipulator_stack/task_orchestrator_node.py
def update_params(self, param_list):
    for param in param_list:
        match param.name:
            case 'robot_vel':
                self.robot.vel = param.value
            case 'robot_accel':
                self.robot.accel = param.value
    self.save_params(param_list)
    return SetParametersResult(successful=True)

def save_params(self, param_list):
    params = {self.get_name(): {'ros__parameters': {p.name: p.value for p in self._parameters.values()}}}
    with open(self.params_file, 'w') as f:
        yaml.dump(params, f, default_flow_style=False)
```

Эффект:
- параметр меняется сразу в работе ноды и фиксируется на диск.

---

## 8) Изоляция параметров между роботами

**Проблема**
- конфиги разных роботов могут смешиваться при общей кодовой базе.

**Решение**
- профильные пути через `CONFIG_PKG` + `ROBOT_PROFILE`;
- чтение/поиск реализованы в `ros_runtime_utils.config_paths`;
- для `params/models/rviz/rqt` применяется профильная стратегия.

```python
# src/ros_runtime_utils/ros_runtime_utils/config_paths.py
config_pkg = os.getenv("CONFIG_PKG", "").strip()
robot_profile = os.getenv("ROBOT_PROFILE", "").strip()
profiled_config_file = package_share / config_dir / robot_profile / config_name

if profiled_config_file.exists():
    return profiled_config_file

if copy_fallback_to_profile and fallback_source.exists():
    profiled_config_file_src.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fallback_source, profiled_config_file_src)
    return profiled_config_file_src
```

Практика запуска:
```bash
export CONFIG_PKG=system_bringup
export ROBOT_PROFILE=lab
ros2 launch system_bringup system_bringup.launch.py visualize:=true
```

Эффект:
- правки профиля `lab` не перетирают `line_a` и `line_b`.

---

## 9) Asyncio в ROS 2: что взяли из `asyncio.md` и проверили в коде

Источник вдохновения для async-подхода:
- https://github.com/m2-farzan/ros2-asyncio

**Проблема**
- «каскадный» callback-код хуже читается, труднее управлять ошибками.

**Решение**
- отдельный `ros_loop` с `spin_once`;
- бизнес-циклы пишутся как `async def`;
- ошибки поднимаются через `FIRST_EXCEPTION`.

```python
# src/ros_runtime_utils/ros_runtime_utils/node_base.py
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

Проверка с `asyncio.md`:
- идея «отдельный ros-loop + линейный async-код» совпадает;
- использование `FIRST_EXCEPTION` для видимости ошибок реализовано.

---

## 10) `@register_loop`: масштабирование async-задач внутри одной ноды

**Проблема**
- множество таймеров и коллбеков без общей модели выполнения.

**Решение**
- декоратор отмечает loop-методы;
- `AsyncBaseNode.__init_subclass__` автоматически собирает их;
- `run()` запускает все циклы параллельно.

```python
# src/manipulator_stack/manipulator_stack/task_orchestrator_node.py
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
- в одной ноде можно прозрачно держать несколько независимых воркеров.

---

## 11) Пример: несколько async loop в `TaskOrchestratorNode`

**Проблема**
- нужно одновременно вести grasping-пайплайн, FSM, watchdog и обмен с внешними сервисами.

**Решение**
- разделение по отдельным циклам с разной частотой и ответственностью:
- `grasping_loop`: стадии захвата;
- `_execute_fsm_state_loop`: реакции на состояние автомата;
- `_send_status_loop`: heartbeat/статус;
- `_watchdog_loop`: контроль доступности каналов.

Почему это решение принято:
- каждая задача получает локальную, читаемую логику;
- меньше перекрестных зависимостей, проще дебаг.

Ограничение:
- нельзя блокировать event loop; все тяжелые операции должны быть async-friendly.

---

## 12) Асинхронная FSM: управляемые переходы вместо скрытых side effects

**Проблема**
- сложные переходы состояния в управлении роботом быстро становятся неявными.

**Решение**
- `TaskFSM` на `transitions.AsyncMachine`;
- pending transition исполняется централизованно в `step()`.

```python
# src/manipulator_stack/manipulator_stack/async_state_machine.py
self.machine = AsyncMachine(
    model=self,
    states=states,
    transitions=transitions,
    initial=TaskFSM.State.CHECKS,
    auto_transitions=False,
    after_state_change='_execute_state',
)

async def step(self):
    if self._pending_transition:
        pending = self._pending_transition
        self._pending_transition = None
        if pending in self.machine.get_triggers(self.state):
            await self.trigger(pending)
```

Интеграция в ноду:
```python
@register_loop
async def _fsm_loop(self):
    while ok():
        await self.fsm.step()
        await asyncio.sleep(1e-4)
```

Эффект:
- переходы стали явными, валидируемыми и воспроизводимыми.

---

## 13) Что можно внедрить в другой ROS 2 проект уже завтра

1. Ввести единый root launch и правило: любой аргумент прокидывается до node-level без потерь.
2. Обернуть dev workflow в скрипты `build/run/docker` и добавить shell completion для `b/r`.
3. Базовый класс ноды с обязательными `init_params/init_ros_interfaces/update_params`.
4. Runtime persistence параметров в YAML сразу после изменения.
5. Профильные конфиги через `CONFIG_PKG/ROBOT_PROFILE`, чтобы исключить смешивание роботов.
6. Async loop-модель (`register_loop`) для читаемой конкуррентности.
7. Async FSM для явного контроля состояний и переходов.

**Главная идея доклада**
- эти решения приняты не ради «красоты кода», а для устойчивой эксплуатации нескольких роботов в одной кодовой базе.
