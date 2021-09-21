import subprocess

def get_show_hide_context(page):
    if hasattr(page, 'showhidecontext'):
        return page.showhidecontext
    return None

def get_or_make_show_hide_context(page):
    context = get_show_hide_context(page)
    if context is None:
        context = PageAuxData()
        page.showhidecontext = context
    return context

class PageAuxData:
    def __init__(self):
        self.context_ids = set()

class ShowHideContext:
    def __init__(self, guake_instance):
        self.guake = guake_instance
        self.context_id = None

    def before_show(self):
        active_window = subprocess.check_output(["xdotool", "getactivewindow"]).decode("utf-8").strip()
        self.context_id = active_window
        notebook = self.guake.notebook_manager.get_current_notebook()
        for i, page in enumerate(notebook.iter_pages()):
            data = get_show_hide_context(page)
            if data:
                if active_window in data.context_ids:
                    notebook.set_current_page(i)
                    return

    def before_hide(self):
        if not self.context_id: return
        notebook = self.guake.notebook_manager.get_current_notebook()

        current_page_index =notebook.get_current_page()
        if current_page_index<0: return
        for i, page in enumerate(notebook.iter_pages()):
            data = get_or_make_show_hide_context(page)
            if i == current_page_index:
                data.context_ids.add(self.context_id)
            else:
                data.context_ids.discard(self.context_id)

        self.context_id = None
