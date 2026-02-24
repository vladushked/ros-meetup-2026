from transitions.extensions.asyncio import AsyncMachine


class TaskFSM:
    class State:
        CHECKS = "CHECKS"
        READY = "READY"
        EXECUTION = "EXECUTION"
        STOP = "STOP"

    class Transition:
        OK = "ok"
        START = "start"
        HALT = "halt"

    def __init__(self, logger):
        self._logger = logger
        self.updated = True
        self._pending_transition = None

        states = [
            TaskFSM.State.CHECKS,
            TaskFSM.State.READY,
            TaskFSM.State.EXECUTION,
            TaskFSM.State.STOP,
        ]
        transitions = [
            [TaskFSM.Transition.OK, TaskFSM.State.CHECKS, TaskFSM.State.READY],
            [TaskFSM.Transition.START, TaskFSM.State.READY, TaskFSM.State.EXECUTION],
            [TaskFSM.Transition.HALT, [TaskFSM.State.READY, TaskFSM.State.EXECUTION], TaskFSM.State.STOP],
            [TaskFSM.Transition.OK, TaskFSM.State.STOP, TaskFSM.State.CHECKS],
        ]

        self.machine = AsyncMachine(
            model=self,
            states=states,
            transitions=transitions,
            initial=TaskFSM.State.CHECKS,
            auto_transitions=False,
            after_state_change="_after_state_change",
        )

    def set_transition(self, transition: str):
        if self._pending_transition is None:
            self._pending_transition = transition

    async def _after_state_change(self):
        self.updated = True
        self._logger.info(f"FSM state -> {self.state}")

    async def step(self):
        if not self._pending_transition:
            return

        pending = self._pending_transition
        self._pending_transition = None
        if pending in self.machine.get_triggers(self.state):
            await self.trigger(pending)
        else:
            self._logger.error(
                f"Invalid transition {pending} from {self.state}. Allowed: {self.machine.get_triggers(self.state)}"
            )
