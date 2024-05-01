# %%


import os
import json
import pandas as pd
import ipywidgets as widgets
from ipywidgets import VBox, HBox, Layout, GridBox

from QuocAnh_py.execute.init import import_settings


# %%


class MyWidgets:
    def __init__(self):
        settings = import_settings()
        models = settings["models"]
        preferences = settings["preferences"]
        default_data = settings["paths"]["default_data"]

        self.data_header = widgets.Label(value="Data Availability")
        if os.path.exists(default_data):
            self.default_data = widgets.Text(
                value="Spotify Data is available at: " + default_data
            )
            self.output = widgets.Output(
                layout=Layout(height="400px", overflow_x="scroll", overflow_y="auto")
            )
            with self.output:
                display(pd.read_csv(default_data))
        else:
            self.default_data = widgets.Text(
                value="Spotify Data is not available at: " + default_data
            )

        self.reimport = widgets.Checkbox(
            value=False,
            description="Re-import Playlist from Spotify?",
            style={"description_width": "initial"},
        )

        self.input_header = widgets.Label(value="Input")
        self.input_option = widgets.Dropdown(
            options=["Track ID", "Find Track"],
            value="Find Track",
            description="Input Option:",
            style={"description_width": "initial"},
        )
        self.track_id = widgets.Text(value="Insert Track ID (Required): ")
        self.track_id.layout.visibility = "hidden"
        self.track_name = widgets.Text(value="Insert Track Name (Required): ")
        self.artist = widgets.Text(value="Insert Artist Name (Recommended): ")
        self.album = widgets.Text(value="Insert Album Name (Optional): ")
        self.track_name.layout.visibility = "hidden"
        self.artist.layout.visibility = "hidden"
        self.album.layout.visibility = "hidden"
        self.my_playlist_name = widgets.Text(
            value="Insert Your Playlist Name: My Mixtape Vol.1"
        )

        self.input_option.observe(self.on_input_option_change, names="value")

        self.my_playlist_length = widgets.IntSlider(
            value=0,
            min=0,
            max=180,
            step=5,
            description="My Playlist Length (minutes)",
            style={"description_width": "initial"},
        )

        self.common_genre_checkbox = widgets.Checkbox(
            value=True,
            description=models["common_text_score"]["desc"],
            style={"description_width": "initial"},
        )

        self.harmonic_checkbox = widgets.Checkbox(
            value=True,
            description=models["harmonic_keys"]["desc"],
            style={"description_width": "initial"},
        )

        self.similarity_checkbox = widgets.Checkbox(
            value=True,
            description=models["nearest_neighbor"]["desc"],
            style={"description_width": "initial"},
        )

        random_options = preferences["randomize"]["options"].keys()
        self.random_choices = widgets.RadioButtons(
            options=[key for key in random_options],
            value=list(random_options)[0],
            description="Track Selection Type:",
            style={"description_width": "initial"},
        )

        self.weighted_input = widgets.Textarea(
            value="",
            placeholder="Type the weights separated by commas. E.g. 0.3, 0.2, 0.1",
            description="Favor:",
            style={"description_width": "initial"},
        )

        def widget_weight_input(change):
            self.weighted_input.layout.visibility = (
                "visible" if change["new"] == "Weighted" else "hidden"
            )

        self.random_choices.observe(widget_weight_input, names="value")

        # Initially hide the weighted_input widget if the selected choice is not 'Weighted Random'
        self.weighted_input.layout.visibility = (
            "hidden" if self.random_choices.value != "Weighted Random" else "visible"
        )

        # self.preferred_order = widgets.

        self.print_msg = widgets.Checkbox(
            value=False, description="Show Log", style={"description_width": "initial"}
        )

        self.print_plt = widgets.Checkbox(
            value=False,
            description="Print Playlist plots",
            style={"description_width": "initial"},
        )

        self.to_csv = widgets.Checkbox(
            value=False,
            description="Export Playlist to CSV",
            style={"description_width": "initial"},
        )

        self.to_spotify = widgets.Checkbox(
            value=False,
            description="Create Playlist on Spotify",
            style={"description_width": "initial"},
        )

        # JSON Settings
        self.json_settings = widgets.Textarea(
            value=json.dumps(import_settings(), indent=4),
            placeholder="Type something",
            description="JSON: ",
            # layout=widgets.Layout(width="100%", height="400px")
        )
        self.json_settings.layout = Layout(visibility="hidden", width="auto")

        # Create a button to save the changes
        self.button_json = widgets.Button(description="Save JSON Changes")
        self.button_json.layout = Layout(visibility="hidden")

        self.show_json = widgets.Button(description="Show Advanced Settings")

        def on_show_json_clicked(b):
            self.json_settings.value = json.dumps(import_settings(), indent=4)
            if self.json_settings.layout.visibility == "hidden":
                self.json_settings.layout.visibility = "visible"
                self.button_json.layout.visibility = "visible"
            else:
                self.json_settings.layout.visibility = "hidden"
                self.button_json.layout.visibility = "hidden"

        self.show_json.on_click(on_show_json_clicked)

        self.button_save = widgets.Button(
            value=False,
            description="Save Settings",
            button_style="info",
            tooltip="Description",
            icon="save",
            style={"description_width": "initial"},
        )

        self.button_run = widgets.Button(
            value=False,
            description="Let's DJ!",
            button_style="success",
            tooltip="Description",
            icon="start",
            style={"description_width": "initial"},
        )

        self.data_availability = VBox(
            [self.data_header, self.default_data, self.output, self.reimport],
            layout=Layout(grid_area="data_availability"),
        )
        self.track_input = VBox(
            [self.input_option, self.track_id, self.track_name, self.artist, self.album]
        )
        self.input_settings = VBox(
            [
                self.input_header,
                self.track_input,
                self.my_playlist_name,
                self.my_playlist_length,
                self.common_genre_checkbox,
                self.harmonic_checkbox,
                self.similarity_checkbox,
                self.random_choices,
                self.weighted_input,
                self.print_msg,
                self.print_plt,
                self.to_csv,
                self.to_spotify,
                self.button_save,
                self.button_run,
            ],
            layout=Layout(grid_area="input_settings"),
        )
        self.advanced_settings = VBox(
            [self.show_json, self.json_settings, self.button_json],
            layout=Layout(grid_area="advanced_settings"),
        )

    def on_input_option_change(self, change):
        if change["new"] == "Track ID":
            self.track_id.layout.visibility = "visible"
            self.track_name.layout.visibility = "hidden"
            self.artist.layout.visibility = "hidden"
            self.album.layout.visibility = "hidden"

        elif change["new"] == "Find Track":
            self.track_id.layout.visibility = "hidden"
            self.track_name.layout.visibility = "visible"
            self.artist.layout.visibility = "visible"
            self.album.layout.visibility = "visible"

            self.track_id = None

    def get_widgets(self):
        # Create a GridBox with the VBox widgets arranged in the four quadrants
        grid = GridBox(
            children=[
                self.data_availability,
                self.input_settings,
                self.advanced_settings,
            ],
            layout=Layout(
                width="100%",
                grid_template_rows="auto auto",
                grid_template_columns="50% 50%",
                grid_template_areas="""
                            "data_availability data_availability"
                            "input_settings advanced_settings"
                            """,
            ),
        )
        return grid
