from nicegui import PageArguments, ui
from typing import Callable, Dict, Any

from . import doc


class FakeSubPages(ui.column):

    def __init__(self, routes: Dict[str, Callable], *, data: Dict[str, Any] = {}) -> None:
        super().__init__()
        self.routes = routes
        self.data = data

    def init(self) -> None:
        self._render('/')
        self.move()  # move to end

    def link(self, text: str, route: str) -> None:
        ui.label(text).classes('nicegui-link cursor-pointer').on('click', lambda: self._render(route))

    def _render(self, route: str) -> None:
        self.clear()
        with self:
            ui.timer(0, lambda: self.routes[route](**self.data), once=True)  # NOTE: timer for sync and async functions


class FakeArguments:

    def __init__(self, **kwargs: Any) -> None:
        self.query_parameters = kwargs


@doc.demo('Sub Pages', '''
    Sub pages provide URL-based navigation between different views.
    This allows you to easily build a single page application (SPA).
    The `ui.sub_pages` element itself functions as the container for the currently active sub page.
    You only need to provide the routes for each view builder function.
    NiceGUI takes care of replacing the content without triggering a full page reload when the URL changes.

    **NOTE: This is an experimental feature, and the API is subject to change.**
''')
def main_demo() -> None:
    from uuid import uuid4

    # @ui.page('/')
    # @ui.page('/{_:path}')  # NOTE: our page should catch all paths
    # def index():
    #     ui.label(f'This ID {str(uuid4())[:6]} changes only on reload.')
    #     ui.separator()
    #     ui.sub_pages({'/': main, '/other': other})

    def main():
        ui.label('Main page content')
        # ui.link('Go to other page', '/other')
        sub_pages.link('Go to other page', '/other')  # HIDE

    def other():
        ui.label('Another page content')
        # ui.link('Go to main page', '/')
        sub_pages.link('Go to main page', '/')  # HIDE

    # END OF DEMO
    ui.label(f'This ID {str(uuid4())[:6]} changes only on reload.')
    ui.separator()
    sub_pages = FakeSubPages({'/': main, '/other': other})
    sub_pages.init()


@doc.demo('Passing Parameters to Sub Page', '''
    If a sub page needs data from its parent, a `data` dictionary can be passed to the `ui.sub_pages` element.
    The data will be available as keyword arguments in the sub page function or as `PageArguments.data` object.
''')
def parameters_demo():
    # @ui.page('/')
    # @ui.page('/{_:path}') # NOTE: our page should catch all paths
    # def index():
    #     with ui.row():
    #         ui.label('Title:')
    #         title = ui.label()
    #     ui.separator()
    #     ui.sub_pages({
    #        '/': main,
    #        '/other': other,
    #     }, data={'title': title})

    def main(title: ui.label):
        title.text = 'Main page content'
        # ui.button('Go to other page', on_click=lambda: ui.navigate.to('/other'))
        sub_pages.link('Go to other page', '/other')  # HIDE

    def other(title: ui.label):
        title.text = 'Other page content'
        # ui.button('Go to main page', on_click=ui.navigate.to('/'))
        sub_pages.link('Go to main page', '/')  # HIDE

    # END OF DEMO
    with ui.row():
        ui.label('Title:')
        title = ui.label()
    ui.separator()
    sub_pages = FakeSubPages({'/': main, '/other': other}, data={'title': title})
    sub_pages.init()


@doc.demo('Async Sub Pages', '''
    Sub pages also work with async builder functions.
''')
def async_demo():
    import asyncio

    # @ui.page('/')
    # @ui.page('/{_:path}')
    # def index():
    #     with ui.row():
    #         ui.link('main', '/')
    #         ui.link('other', '/other')
    #     ui.sub_pages({'/': main, '/other': lambda: other('other page')})

    async def main():
        ui.label('main page').classes('font-bold')
        await asyncio.sleep(2)
        ui.label('after 2 sec')

    async def other(title: str):
        ui.label(title).classes('font-bold')
        await asyncio.sleep(1)
        ui.label('after 1 sec')

    # END OF DEMO
    sub_pages = FakeSubPages({'/': main, '/other': lambda: other('other page')})
    with ui.row():
        sub_pages.link('main', '/')
        sub_pages.link('other', '/other')
    sub_pages.init()


@doc.demo('Adding Sub Pages', '''
    Sometimes not all routes are known when creating the `ui.sub_pages` element.
    In such cases, the `add` method can be used to add routes after the element has been created.
    This can also be used to pass elements which should be placed below the `ui.sub_pages` container.
''')
def adding_sub_pages_demo() -> None:
    # @ui.page('/')
    # @ui.page('/{_:path}') # NOTE: our page should catch all paths
    # def index():
    #     pages = ui.sub_pages()
    #     ui.separator()
    #     footer = ui.label()
    #     pages.add('/', lambda: main(footer))
    #     pages.add('/other', lambda: other(footer))

    def main(footer: ui.label):
        footer.text = 'normal footer'
        # ui.link('Go to other page', '/other')
        sub_pages.link('Go to other page', '/other')  # HIDE

    def other(footer: ui.label):
        footer.text = 'other footer'
        # ui.link('Go to main page', '/')
        sub_pages.link('Go to main page', '/')  # HIDE

    # END OF DEMO
    sub_pages = FakeSubPages({'/': lambda: main(footer), '/other': lambda: other(footer)})
    sub_pages.init()
    ui.separator()
    footer = ui.label()


@doc.demo('Using PageArguments', '''
    By type-hinting a parameter as `PageArguments`,
    the sub page builder function gets unified access to query parameters, path parameters, and more.
''')
def page_arguments_demo():
    from nicegui import PageArguments

    # @ui.page('/')
    # @ui.page('/{_:path}') # NOTE: our page should catch all paths
    # def index():
    #     ui.link('msg=hello', '/?msg=hello')
    #     ui.link('msg=world', '/?msg=world')
    #     ui.sub_pages({'/': main})

    def main(args: PageArguments):
        ui.label(args.query_parameters.get('msg', 'no message'))

    # END OF DEMO
    sub_pages = FakeSubPages({
        '/': lambda: main(FakeArguments()),  # type: ignore
        '/?msg=hello': lambda: main(FakeArguments(msg='hello')),  # type: ignore
        '/?msg=world': lambda: main(FakeArguments(msg='world')),  # type: ignore
    })
    sub_pages.link('msg=hello', '/?msg=hello')
    sub_pages.link('msg=world', '/?msg=world')
    sub_pages.init()


@doc.demo('Nested Sub Pages', '''
    Sub pages elements can be nested to create a hierarchical page structure.
    Each of these elements determines which part of the path they should handle by:

    1. getting the full URL path from `ui.context.client.sub_pages_router`,
    2. removing the leading part which was handled by the parent element,
    3. matching the route with the most specific path, and
    4. leaving the remaining part of the path for the next element (or if there is none, show a 404 error).
''')
def nested_sub_pages_demo():
    # @ui.page('/')
    # @ui.page('/{_:path}')  # NOTE: our page should catch all paths
    # def index():
    #     ui.link('Go to main', '/')
    #     ui.link('Go to other', '/other')
    #     ui.sub_pages({
    #         '/': main,
    #         '/other': other,
    #     }).classes('border-2 p-2')

    def main():
        ui.label('main page')

    def other():
        ui.label('sub page')
        # ui.link('Go to A', '/sub/a')
        # ui.link('Go to B', '/sub/b')
        # ui.sub_pages({
        #     '/': sub_main,
        #     '/a': sub_page_a,
        #     '/b': sub_page_b
        # }).classes('border-2 p-2')
        sub_pages = FakeSubPages({'/': sub_main, '/a': sub_page_a, '/b': sub_page_b}).classes('border-2 p-2')  # HIDE
        sub_pages.link('Go to main', '/')  # HIDE
        sub_pages.link('Go to A', '/a')  # HIDE
        sub_pages.link('Go to B', '/b')  # HIDE
        sub_pages.init()  # HIDE

    def sub_main():
        ui.label('sub main page')

    def sub_page_a():
        ui.label('sub A page')

    def sub_page_b():
        ui.label('sub B page')

    # END OF DEMO
    sub_pages = FakeSubPages({'/': main, '/other': other}).classes('border-2 p-2')
    sub_pages.link('Go to main', '/')
    sub_pages.link('Go to other', '/other')
    sub_pages.init()


doc.reference(ui.sub_pages, title='Reference for ui.sub_pages')

doc.reference(PageArguments, title='Reference for PageArguments')
