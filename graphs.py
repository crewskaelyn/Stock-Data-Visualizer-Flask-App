import pygal
from pygal.style import RedBlueStyle

def bar_graph(title, dates, open, high, low, close):
    style = RedBlueStyle()
    style.background = 'transparent'

    graph = pygal.Bar(x_label_rotation=45, style=style)
    graph.title = title
    graph.x_labels = dates
    graph.add('Open', open)
    graph.add('High', high)
    graph.add('Low', low)
    graph.add('Close', close)
    return graph.render_data_uri()


def line_graph(title, dates, open, high, low, close):
    style = RedBlueStyle()
    style.background = 'transparent'

    graph = pygal.Line(x_label_rotation=45, style=style)
    graph.title = title
    graph.x_labels = dates
    graph.add('Open', open)
    graph.add('High', high)
    graph.add('Low', low)
    graph.add('Close', close)
    return graph.render_data_uri()