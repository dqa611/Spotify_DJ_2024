# %%

import ast
import json
from QuocAnh_py.execute.run_main import main_func
from QuocAnh_py.execute.init import import_settings
from QuocAnh_py.execute.widgets import MyWidgets


# %%


class Main:
    def __init__(self):
        self.widgets = MyWidgets()
        self.widgets.button_save.on_click(self.overwrite_settings_from_widgets)
        self.widgets.button_json.on_click(self.save_json_settings)
        self.widgets.button_run.on_click(self.run_main_function)

    # Process all the Input from Widgets
    def get_info(self, b=None):
        track_name = self.widgets.track_name.value
        artist = "{}" if None else self.widgets.artist.value
        album = "{}" if None else self.widgets.album.value
        my_playlist_name = self.widgets.my_playlist_name.value

        return track_name, artist, album, my_playlist_name

    def get_models_settings(self, b=None):
        common_genre_checkbox = self.widgets.common_genre_checkbox.value
        harmonic_checkbox = self.widgets.harmonic_checkbox.value
        similarity_checkbox = self.widgets.similarity_checkbox.value

        return common_genre_checkbox, harmonic_checkbox, similarity_checkbox

    def get_randomization_settings(self, b=None):
        settings = import_settings()["preferences"]["randomize"]
        random_choices = self.widgets.random_choices.value
        weighted_input = self.widgets.weighted_input.value

        random_output = settings["options"][random_choices]
        if random_choices == "Weighted":
            random_output = ast.literal_eval(weighted_input)

        return random_output

    def get_import_settings(self, b=None):
        playlist_import = self.widgets.reimport.value
        to_csv = self.widgets.to_csv.value
        to_spotify = self.widgets.to_spotify.value
        print_msg = self.widgets.print_msg.value
        print_plt = self.widgets.print_plt.value

        return playlist_import, to_csv, to_spotify, print_msg, print_plt

    def overwrite_settings_from_widgets(self, b=None):
        settings = import_settings(print_msg=True)

        common_genre_checkbox, harmonic_checkbox, similarity_checkbox = (
            self.get_models_settings()
        )
        random_output = self.get_randomization_settings()

        settings["models"]["common_text_score"]["applied"] = common_genre_checkbox
        settings["models"]["harmonic_keys"]["applied"] = harmonic_checkbox
        settings["models"]["nearest_neighbor"]["applied"] = similarity_checkbox

        settings["preferences"]["length_min"] = self.widgets.my_playlist_length.value
        settings["preferences"]["randomize"]["applied"] = random_output
        # preferences['preferred_order'] = preferred_order

        playlist_import, to_csv, to_spotify, print_msg, print_plt = (
            self.get_import_settings()
        )
        settings["import_from_spotify"] = playlist_import
        settings["export_to_csv"] = to_csv
        settings["export_to_spotify"] = to_spotify
        settings["print_msg"] = print_msg
        settings["print_plt"] = print_plt

        manual_path = import_settings()["paths"]["manual_input"]
        with open(manual_path, "w") as f:
            json.dump(settings, f, indent=4)
        print(f"{manual_path} saved!")

    # Before you save the JSON, save the settings on the widgets first
    def save_json_settings(self, b=None):
        new_data = self.overwrite_settings_from_widgets()
        new_data = json.loads(self.widgets.json_settings.value)
        manual_path = import_settings()["paths"]["manual_input"]
        with open(manual_path, "w") as f:
            json.dump(new_data, f, indent=4)
        print("Settings JSON saved!")

    def run_main_function(self, b=None):
        track_name, artist, album, my_playlist_name = self.get_info()
        if self.widgets.track_id is not None:
            input = self.widgets.track_id.value
        else:
            input = (track_name, artist, album)

        my_playlist = main_func(input, my_playlist_name)
        display(my_playlist)

    def lets_dj(self):
        display(self.widgets.get_widgets())
