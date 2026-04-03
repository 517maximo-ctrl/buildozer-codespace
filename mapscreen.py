from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.properties import ListProperty
from kivy_garden.mapview import MapView, MapMarker, MapLayer
from kivy.graphics import Color, Line

class PathLayer(MapLayer):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self.path = path

    def reposition(self):
        self.canvas.clear()
        if len(self.path) < 2:
            return
        with self.canvas:
            Color(1, 0, 0, 0.8)
            points = []
            mapview = self.parent
            for lat, lon in self.path:
                x, y = mapview.get_window_xy_from(lat, lon, mapview.zoom)
                points.extend([x, y])
            Line(points=points, width=2)

class MapScreen(Screen):
    path = ListProperty([])

    def on_pre_enter(self):
        map_widget = self.ids.map
        map_widget.clear_widgets()

        if not self.path:
            if not hasattr(self, "map_label"):
                self.map_label = Label(
                    text="Nessun percorso disponibile",
                    size_hint=(1, None),
                    height=50,
                    color=(0,0,0,1)
                )
                self.add_widget(self.map_label)
            return
        else:
            if hasattr(self, "map_label"):
                self.remove_widget(self.map_label)
                del self.map_label

        start_lat, start_lon = self.path[0]
        map_widget.add_widget(MapMarker(lat=start_lat, lon=start_lon, source="Images/start.png"))

        if len(self.path) > 1:
            end_lat, end_lon = self.path[-1]
            map_widget.add_widget(MapMarker(lat=end_lat, lon=end_lon, source="Images/finish.png"))

            path_layer = PathLayer(self.path)
            map_widget.add_layer(path_layer)
