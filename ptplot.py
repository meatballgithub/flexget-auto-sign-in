from matplotlib.pyplot import title
from flexget import plugin
from flexget.entry import Entry
from flexget.event import event

from .ptsites.saveentry import ptAnalysis
import json


class ptplot:
    schema = {
        "type": "object",
        "properties": {
            "sites": {"type": "array", "items": {"type": "string"}},
            "days": {"type": "integer", "default": 30},
        },
        "additionalProperties": False,
    }

    def on_task_input(self, task, config):
        sites = config.get("sites")
        days = config.get("days")
        with open("test.text", "w") as f:
            f.write(json.dumps(config))
        pt = ptAnalysis()
        pt.readdata()
        pt.plot(site_names=sites, days=days)
        entry = Entry(title="plot", url="")
        entry["message"] = pt.message
        return [entry]


@event("plugin.register")
def register_plugin():
    plugin.register(ptplot, "ptplot", api_ver=2)
