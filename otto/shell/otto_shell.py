import cmd
import inquirer
from langchain_core.messages import HumanMessage

from otto.ryu.intent_engine.intent_processor_agent import IntentProcessor


class OttoShell(cmd.Cmd):
    _model: str = None
    _controller: str = None
    _agent: IntentProcessor
    _verbosity_level: str = "VERBOSE"

    def __init__(self, controller, agent):
        super().__init__()
        self._controller = controller
        self._agent = agent
        self._model = agent.model.model_name

        self.prompt = "otto> "

        self.intro = f"""
        Otto - Intent Based Northbound Interface for SDN Controllers
        Author: Luke Marshall

        Configured model: {self._model}
        Configured Controller: {self._controller}
        """

    def do_get_model(self):
        print(self._model)

    def do_set_model(self, model):
        if model and model in ["gpt-4o", "gpt-4o-mini"]:
            self._agent.change_model(model)
        else:
            model_choice = inquirer.list_input("Available Models:", choices=["gpt-4o", "gpt-4o-mini"])
            self._agent.change_model(model_choice)

        self._model = self._agent.model.model_name
        print(f"Changed model to {self._model}")

    def do_set_controller(self, controller):
        if controller and controller in ["ryu", "onos"]:
            self._controller = controller
        else:
            self._controller = inquirer.list_input("Supported Controllers:", choices=["ryu", "onos"])

    def do_set_verbosity(self, verbosity):
        if verbosity and verbosity in ["LOW", "VERBOSE"]:
            self._verbosity_level = verbosity
        else:
            self._controller = inquirer.list_input("Supported Controllers:", choices=["ryu", "onos"])

    def do_intent(self, intent):
        messages = [HumanMessage(content=intent)]

        result = self._agent.graph.invoke({"messages": messages})

        print(result)

    def do_EOF(self, line):
        return True

    def postloop(self):
        return True
