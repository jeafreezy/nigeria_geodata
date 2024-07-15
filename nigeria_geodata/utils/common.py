def in_jupyter_notebook():
    try:
        # Jupyter-specific module
        get_ipython
        return True
    except NameError:
        return False
