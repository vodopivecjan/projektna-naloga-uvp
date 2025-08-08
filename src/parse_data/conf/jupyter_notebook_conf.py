# ## JUPYTER NOTEBOOK CONFIGURATION
# ## this is for enabling the autorealod feature of jupyter notebook to auto realod modules
import builtins
import io
from contextlib import redirect_stdout

from IPython.core.getipython import get_ipython
from IPython.core.interactiveshell import InteractiveShell

ipython: InteractiveShell | None = get_ipython()
if ipython is not None:
    with redirect_stdout(io.StringIO()):
        ipython.run_line_magic("load_ext", "autoreload")  # it is already loaded
    ipython.run_line_magic("autoreload", "2")
    ipython.run_line_magic("matplotlib", "inline")


from IPython.extensions.autoreload import DeduperReloader  # noqa: E402

# 1. Store the original functions
original_open = builtins.open
original_reloader = DeduperReloader.maybe_reload_module


# 2. Create our utf8 wrapper
def maybe_reload_module_utf8(self, module):
    # First try normal loading
    try:
        return original_reloader(self, module)
    except UnicodeDecodeError:

        def utf8_open(*args, **kwargs):
            if "encoding" not in kwargs:
                kwargs["encoding"] = "utf-8"
            return original_open(*args, **kwargs)

        # Temporarily patch open()
        builtins.open = utf8_open
        try:
            return original_reloader(self, module)
        finally:
            # Always restore original
            builtins.open = original_open
    # All other errors propagate normally
    except:
        raise


# 3. Apply our wrapper
DeduperReloader.maybe_reload_module = maybe_reload_module_utf8
