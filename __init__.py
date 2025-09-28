
import threading
#──────────────────────────
# comfyui-sequential-prompt
#──────────────────────────
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

threading.Thread(target=nodes.load).start()
