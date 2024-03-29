# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# + tags=[]
#### Module loads and general setup

import os
import pathlib  # to do, convert all os-based path work to pathlib
import param
from bokeh.palettes import YlOrRd9
from bokeh.events import Tap
import holoviews as hv
from holoviews.plotting.util import process_cmap
from holoviews import opts
import hvplot.xarray
import geoviews as gv
import panel as pn
import xarray as xr
from cartopy import crs
from pyproj import Proj, transform
import pandas as pd  # also needs xlrd installed
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex as th
import datetime as dt  # not available on Conda - access via PIP
import json
from sklearn.neighbors import BallTree
from IPython import get_ipython
import panel as pn
from geopy.geocoders import Nominatim

general_input_directory = "."

with open(os.path.join(general_input_directory, "style.css")) as f:
    lines = f.readlines()
custom_css = "\n".join(lines)
pn.config.raw_css.append(custom_css)

hv.extension("bokeh")
gv.extension("bokeh")
pn.extension(raw_css=[custom_css])

# + tags=[]
# TODO: dynamically scale based on screen size
plot_width = 900
plot_height = 1500


class CRBCPI_class:
    def __init__(self):
        self.dT_levels = ["+0.5C", "+1.0C", "+1.5C", "+2.0C", "+2.5C", "+3.0C", "+3.5C"]
        self.CRBCPI_data = {
            self.dT_levels[0]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+0.5C_NBCC.xls"
            ),
            self.dT_levels[1]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+1.0C_NBCC.xls"
            ),
            self.dT_levels[2]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+1.5C_NBCC.xls"
            ),
            self.dT_levels[3]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+2.0C_NBCC.xls"
            ),
            self.dT_levels[4]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+2.5C_NBCC.xls"
            ),
            self.dT_levels[5]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+3.0C_NBCC.xls"
            ),
            self.dT_levels[6]: pd.read_excel(
                "https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+3.5C_NBCC.xls"
            ),
        }

        self.CRBCPI_dT_to_time = pd.DataFrame(
            [
                [2023, 2023, 2023, 2023],
                [2035, 2046, 2046, np.nan],
                [2047, 2070, 2070, np.nan],
                [2059, 2087, np.nan, np.nan],
                [2069, np.nan, np.nan, np.nan],
                [2080, np.nan, np.nan, np.nan],
                [2090, np.nan, np.nan, np.nan],
            ],
            index=self.dT_levels,
            columns=["RCP8.5", "RCP6.0", "RCP4.5", "RCP2.6"],
        )

        self.nn_finder = BallTree(
            np.vstack(
                (
                    np.deg2rad(self.CRBCPI_data["+0.5C"]["Latitude"].values),
                    np.deg2rad(self.CRBCPI_data["+0.5C"]["Longitude"].values),
                )
            ).swapaxes(1, 0),
            metric="haversine",
        )


CRBCPI = CRBCPI_class()


# -

# # Decision support tool core pipeline
#
# Each of the following Notebook sections encapsulate code for one step in a [Panels Pipeline](https://panel.holoviz.org/user_guide/Pipelines.html) flow, which defines the interactive user-driven decision support tool process.  As per Panels Pipeline architecture, each step is defined as a Python Parameterized class.

# ## Sector choice stage
#
# This stage allows user to define the sector they are interested in.

# + tags=[]
class Sector_Definition(param.Parameterized):
    def __init__(self, **params):
        super().__init__(**params)

        with open(os.path.join(general_input_directory, "sector_choice.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)
        self.t1 = pn.pane.Markdown(self.lines)

        self.system_category_widget = pn.widgets.Select(
            options=["Building", "Contaminated Site"]
        )

    @param.output(system_category=param.String())
    def output(self):
        sector_type = self.system_category_widget.value.lower()
        return sector_type

    def panel(self):
        return pn.Column(
            self.t1,
            pn.WidgetBox(self.system_category_widget, css_classes=["custom-box"]),
        )


# -

# ## Introduction stage
#
# This stage provides a general introduction to the process that users will undergo, as they step through the tool.

# + tags=[]
class Introduction(param.Parameterized):

    # Define information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("sector_type")
    def __init__(self, **params):
        super().__init__(**params)
        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "intro_header.jpg"),
            width=plot_width,
        )
        with open(os.path.join(self.system_input_directory, "intro.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            pn.pane.Markdown(self.lines),
            width=plot_width,
            height=plot_height,
        )


# -

# ## Disclaimer stage
#
# This stage provides any/all practical and legal disclaimers/conditions of use that users should be aware of before continuing.

# + tags=[]
class Disclaimer(param.Parameterized):

    # Define information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()

    def __init__(self, **params):
        super().__init__(**params)
        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/disclaimer.jpg"), height=200
        )
        with open(os.path.join(general_input_directory, "disclaimer.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            pn.pane.Markdown(self.lines),
            width=plot_width,
            height=plot_height,
            name="Disclaimer",
        )


# TODO: add a 'Do you accept these conditions of use?' button that opens access to remainder of app.
# -

# ## Core knowledge checklist stage
#
# This stage serves a set of general pre-learning resources.  These are intended to provide users with opportunity to gain some general - but important - climate change knowledge before they enter into the actual decision support tool process.  If new resources are added to master_general_resources_database.json file, they will automatically be displayed here.

# + tags=[]
class Core_Knowledge_Checklist(param.Parameterized):

    # Define information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()

    def __init__(self, **params):
        super().__init__(**params)
        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/core_knowledge.jpg"),
            width=plot_width,
        )
        self.t1 = pn.pane.Markdown(
            "# Before we begin, it is important that you are comfortable with some important concepts and programs related to use of future climate data in decision making!"
        )
        # Open general resources database and read each resource to dictionary
        with open(
            os.path.join(
                general_input_directory, "master_general_resources_database.json"
            ),
            "r",
        ) as j:
            self.general_resources = json.loads(j.read())
        # compile a list of markdown statements by iterating over dictionary
        self.markdown_resource_links = [
            self.general_resources[s]["background"]
            + "<br/>["
            + s
            + "]("
            + self.general_resources[s]["url"]
            + '){:target="_blank"}'
            for s in self.general_resources
        ]

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            *self.markdown_resource_links,  # splatted list of markdown statements
            width=plot_width,
            height=plot_height
        )


# -

# ## Project definition stage
#
# A key first step in any climate change impact/vulnerability assessment, is a clear-eyed and objective statement of the system ('project') in question.  Project definition information is gathered here and is used to focus summary information and data extractions for the user on (for example) relevant time frames and locations.

# + tags=[]
class Project_Definition(param.Parameterized):

    # Define information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("sector_type")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "site_info.jpg"),
            width=plot_width,
        )
        self.t1 = pn.pane.Markdown(
            "# The first stage in understanding which climate data you need, is providing some basic information about your "
            + self.system_category
            + "!"
        )
        self.t11 = pn.pane.Markdown(
            "## Please fill in the following information, which will help curate specific climate data for you in subsequent steps of this tool."
        )

        self.t2 = pn.pane.Markdown(
            "### What type of " + self.system_category + " are you assessing?"
        )

        # User provides an open-ended (typed) definition of system type.
        self.system_type_widget = pn.widgets.TextInput(
            placeholder="Enter " + self.system_category + " type here..."
        )

        # User provides a definition of system lifespan via manipulation of a slider

        self.t3 = pn.pane.Markdown(
            "### What timeframe (past and future) do you need to make decisions on, with respect to your "
            + self.system_category
            + "?"
        )

        self.system_lifespan_widget = pn.widgets.DateRangeSlider(
            start=dt.datetime(1950, 1, 1),
            end=dt.datetime(2100, 1, 1),
            value=(dt.datetime(2021, 1, 1), dt.datetime(2061, 1, 1)),
            bar_color="#FF0000",
        )

        self.t4 = pn.pane.Markdown(
            "Please enter the location of your "
            + self.system_category.replace("_", " ")
            + ", or use the map below to select a location manually."
        )
        # note: I want to chanve 'value' to 'placeholder' below, but doing so messes everything up...
        self.system_address_widget = pn.widgets.TextInput(
            placeholder="Type full or partial address here...", value=""
        )
        self.geocode_button = pn.widgets.Button(name="🔍", width=100)

        latitude = -8677300
        longitude = 9012300
        location = "empty"

        self.t5 = pn.pane.Markdown(
            "### Click on this zoomable map to provide the location of your "
            + self.system_category
            + ".  Be patient, it may take a moment for your point to appear on the map."
        )
        # User provides location information via clicking on an interactive map display.
        self.x = -8677300
        self.y = 9012300
        self.stream = hv.streams.Tap(x=None, y=None)
        self.geocodeflag = 0

        def b(event):
            geolocator = Nominatim(user_agent="example")
            address = self.system_address_widget.value
            location = geolocator.geocode(address)
            latitude = location.latitude
            longitude = location.longitude
            proj1 = Proj("epsg:4326", preserve_units=False)
            proj2 = Proj("epsg:3785", preserve_units=False)
            outProj = Proj(init="epsg:3857")
            inProj = Proj(init="epsg:4326")
            x1 = longitude
            y1 = latitude
            x2, y2 = transform(inProj, outProj, x1, y1)
            self.x = x2
            self.y = y2
            self.geocodeflag = 1
            self.stream.update(x=x2)

        self.geocode_button.on_click(b)

    # TO DO: inherit location information from geocode function, plot dot automatically
    def map_constructor(self, x, y):
        map_background = gv.tile_sources.CartoLight

        Canada_x_bounds = (-15807400, -5677300)
        Canada_y_bounds = (8012300, 11402300)
        if self.geocodeflag == 0:
            self.x = -8677300
            self.y = 9012300
            location_point = gv.Points(
                (x, y, "point"), vdims="Point", crs=crs.GOOGLE_MERCATOR
            )
        else:
            location_point = gv.Points(
                (self.x, self.y, "point"), vdims="Point", crs=crs.GOOGLE_MERCATOR
            )
        self.geocodeflag = 0
        return (map_background * location_point).opts(
            opts.Points(
                global_extent=False,
                xlim=Canada_x_bounds,
                ylim=Canada_y_bounds,
                width=700,
                height=550,
                size=12,
                color="black",
            )
        )

    def map_view(self):
        mp = pn.bind(self.map_constructor, x=self.stream.param.x, y=self.stream.param.y)
        return hv.DynamicMap(mp)

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(
        system_type=param.String(),
        system_lifespan=param.Tuple(),
        system_location=param.List(),
    )
    def output(self):
        system_type = self.system_type_widget.value.lower()
        system_lifespan = self.system_lifespan_widget.value
        proj1 = Proj("epsg:4326", preserve_units=False)
        proj2 = Proj("epsg:3785", preserve_units=False)
        system_location = [transform(proj2, proj1, self.x, self.y)]
        return system_type, system_lifespan, system_location

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            self.t11,
            pn.WidgetBox(self.t2, self.system_type_widget, css_classes=["custom-box"]),
            pn.WidgetBox(
                self.t3, self.system_lifespan_widget, css_classes=["custom-box"]
            ),
            pn.WidgetBox(
                self.t4,
                pn.Row(self.system_address_widget, self.geocode_button),
                css_classes=["custom-box"],
            ),
            pn.WidgetBox(self.t5, self.map_view, css_classes=["custom-box"]),
            width=plot_width,
            height=plot_height,
        )


# -

# ## 2) Component inventory stage
#
# To robustly understand climate impacts to and climate vulnerabilities of complex systems, they need to be broken down into major functional components and each component assessed separately.  For example:
# - an airport could be vulnerable to climate impacts either to specific impacts to the runway, or specific impacts to the control tower  
# - an ecosystem could be vulnerable to climate impacts either to a particular animal species, or a particular plant species
# High level component information gathered here is used to define one axis of a vulnerability ranking matrix that is manipulated be the user to self-develop an understanding of component vulnerability rankings.

# + tags=[]
class Component_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_category", "system_type")

    # Develop database
    def __init__(self, **params):
        super().__init__(**params)
        self.t1 = pn.pane.Markdown(
            "# Next, think carefully about the basic elements of your "
            + str(self.system_type)
            + "."
        )
        self.t2 = pn.pane.Markdown(
            "### Please select the components from this list that are important aspects of your "
            + str(self.system_type)
            + "."
        )

        # Open hazards database and read each hazard item to dictionary
        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"

        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "components.jpg"), height=200
        )

        with open(
            os.path.join(self.system_input_directory, "component_database.json"), "r"
        ) as j:
            self.components = json.loads(j.read())
        # Get basic list of system components.  Some fancy Python to get this into a list from nested dictionary entries.
        self.system_components = sum(
            [self.components[c]["group"] for c in self.components], []
        )
        # Provide selector that lets user 'construct' their system.
        # TODO: generalize this to allow for arbitrary input component files, for arbitrary systems
        self.system_components_CrossSelector_widget = pn.widgets.CrossSelector(
            name="Which "
            + self.system_category
            + " components would you like to include in this assessment?",
            value=[],
            options=self.system_components,
        )
        # Allow users to add arbitrary other components via text entry
        self.t3 = pn.pane.Markdown(
            "### Feel free to include other components of your "
            + self.system_type
            + ", that are not in the list above."
        )
        self.system_components_TextAreaInput_widget = pn.widgets.TextAreaInput(
            placeholder="Enter any number of "
            + self.system_category
            + " components, separated by commas..."
        )

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(system_components=param.List())
    def output(self):
        system_components = self.system_components_CrossSelector_widget.value
        if self.system_components_TextAreaInput_widget.value:
            system_components = (
                system_components
                + self.system_components_TextAreaInput_widget.value.replace(
                    " ", ""
                ).split(",")
            )
        return system_components

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            pn.WidgetBox(
                self.t2,
                self.system_components_CrossSelector_widget,
                css_classes=["custom-box"],
            ),
            pn.WidgetBox(
                self.t3,
                self.system_components_TextAreaInput_widget,
                css_classes=["custom-box"],
            ),
            width=plot_width,
            height=plot_height,
        )


# -

# ## 3) Hazard inventory stage
#
# Once components of a system are defined, users need to think carefully about which hazards these components may be vulnerable to, today and in the future.  
# High level component information gathered here is used to define one axis of a vulnerability ranking matrix that is manipulated be the user to self-develop an understanding of component vulnerability rankings.

# + tags=[]
class Present_Hazard_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "present_hazard.jpg"), height=200
        )

        self.t1 = pn.pane.Markdown(
            "# Next, you need to think about *present-day* weather and climate hazards in your region."
        )

        self.t2 = pn.pane.Markdown(
            "## Select any hazards that your "
            + self.system_type
            + " is vulnerable to, today.  Add any additional hazards that are not listed."
        )

        # Open hazards database and read each hazard item to dictionary
        with open(
            os.path.join(general_input_directory, "master_hazard_database.json"), "r"
        ) as j:
            self.full_hazards_dict = json.loads(j.read())
        self.all_climate_hazards = [s for s in self.full_hazards_dict]
        # Provide selector that lets user select hazards that pertain to their system.
        self.climate_hazards_CrossSelector_widget = pn.widgets.CrossSelector(
            name="Which climate hazards is your "
            + self.system_type
            + " is vulnerable to?",
            value=[],
            options=self.all_climate_hazards,
        )
        # Allow users to add arbitrary other component hazards via text entry
        self.t3 = pn.pane.Markdown(
            "### Include other hazards that your "
            + self.system_type
            + " is vulnerable to that are not in the list above."
        )
        self.climate_hazards_TextAreaInput_widget = pn.widgets.TextAreaInput(
            placeholder="Enter other hazards, separated by commas."
        )

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(present_climate_hazards=param.List())
    def output(self):
        present_climate_hazards = self.climate_hazards_CrossSelector_widget.value
        if self.climate_hazards_TextAreaInput_widget.value:
            present_climate_hazards = (
                present_climate_hazards
                + self.climate_hazards_TextAreaInput_widget.value.replace(
                    " ", ""
                ).split(",")
            )
        return present_climate_hazards

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            self.t2,
            self.climate_hazards_CrossSelector_widget,
            self.t3,
            self.climate_hazards_TextAreaInput_widget,
            width=plot_width,
            height=plot_height,
        )


# + tags=[]
class Future_Hazard_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()
    present_climate_hazards = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type", "present_climate_hazards")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "future_hazard.jpg"), height=200
        )

        self.t1 = pn.pane.Markdown(
            "# Now let's think about hazards that might emerge in the future because of climate change.")
        self.t2 = pn.pane.Markdown(
            "## Consider the remaining hazards in the list.  Is there ANY chance that any of these hazards could impact your "
            + self.system_type
            + " in the future?"
            + " If so, let's add them to the list."
        )

        # Re-open hazards database and read each hazard item to dictionary
        with open(
            os.path.join(general_input_directory, "master_hazard_database.json"), "r"
        ) as j:
            self.full_hazards_dict = json.loads(j.read())
        self.all_climate_hazards = [s for s in self.full_hazards_dict]

        # Trim list by previously selected hazards list
        self.potential_future_climate_hazards = [
            h for h in self.all_climate_hazards if h not in self.present_climate_hazards
        ]

        # Provide selector that lets user select hazards that pertain to their system.
        self.climate_hazards_CrossSelector_widget = pn.widgets.CrossSelector(
            name="Which climate hazards might your "
            + self.system_type
            + " be vulnerable to in the future?",
            value=[],
            options=self.potential_future_climate_hazards,
        )
        # Allow users to add arbitrary other compone hazards via text entry
        self.t3 = pn.pane.Markdown(
            "### Include other hazards that your "
            + self.system_type
            + " may be vulnerable to that are not in the list above."
        )
        self.climate_hazards_TextAreaInput_widget = pn.widgets.TextAreaInput(
            placeholder="Enter other hazards, separated by commas."
        )

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(net_climate_hazards=param.List())
    def output(self):
        net_climate_hazards = (
            self.present_climate_hazards
            + self.climate_hazards_CrossSelector_widget.value
        )
        if self.climate_hazards_TextAreaInput_widget.value:
            net_climate_hazards = (
                net_climate_hazards
                + self.climate_hazards_TextAreaInput_widget.value.replace(
                    " ", ""
                ).split(",")
            )
        return net_climate_hazards

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            self.t2,
            self.climate_hazards_CrossSelector_widget,
            self.t3,
            self.climate_hazards_TextAreaInput_widget,
            width=plot_width,
            height=plot_height,
        )


# + [markdown] tags=[]
# ## 4) Vulnerability screening stage
#
# User-defined input regarding 1) project components and 2) potential climate hazards are combined in the following Pipeline tab into a 2-D heat map that represents a high level vulnerability screen.   This heat map is dynamically user-defined (the number of vertical and horizontal elements is based on the number of project components and climate hazards, respectively).  It is also interactive: users are prompted to set per-component/hazard vulnerabilities by clicking on individual heat map elements, to develop a heat map-based perspective on where greatest system vulnerabilities lie.  This information is recorded and is a key input to the final tool summary.

# + tags=[]
class Vulnerability_HeatMap(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()
    net_climate_hazards = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type", "system_components", "net_climate_hazards")
    def __init__(self, **params):
        super().__init__(**params)

        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/vulnerability.jpg"),
            width=plot_width,
        )

        self.t1 = []
        self.t1.append(
            pn.pane.Markdown(
                "# Now the fun part: screening the impact of each hazard you identified, against each major component of your "
                + self.system_type.lower()
                + ".  This is crucial for prioritizing your climate data and information needs."
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                "This matrix contains a box, for each combination of hazards (columns) and "
                + self.system_type.lower()
                + " components (rows) that you identified."
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                'For each combination, think carefully about how vulnerable that component might be - today or in the future - to that climate hazard, across the scale from "no vulnerability" to "extreme vulnerability".'
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                "Click on the box one or more times to set that vulnerability level, for that hazard/component combination.  Then move on to the next box!"
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                'When you are done, step back and take a broad look at your completed "vulnerability heat map".  Does it match with your intuition about what your '
                + self.system_type.lower()
                + " is sensitive to?  If so: on to the final step!"
            )
        )

        # Define an xarray data array dimensioned by the # of hazards and # of components
        self.vulnerability_matrix = xr.DataArray(
            np.zeros((len(self.net_climate_hazards), len(self.system_components))),
            dims=["climate_hazards", "system_components"],
            coords=dict(
                climate_hazards=[
                    s.replace(" ", "\n") for s in self.net_climate_hazards
                ],
                system_components=[
                    s.replace(" ", "\n") for s in self.system_components
                ],
            ),
            name="vulnerability",
        )

        # Define a tap (mouse click) stream
        self.stream = hv.streams.Tap(x=None, y=None)

    colormap = "PuRd"

    # Define function that increments value of heatmap element by 1, each time it is clicked.  Loop back to initial value (zero) if maximum # of clicks exceeded
    def increment_map(self, hazards=None, components=None):
        if hazards and components:
            self.vulnerability_matrix.loc[
                {"climate_hazards": hazards, "system_components": components}
            ] += 1
            if (
                self.vulnerability_matrix.loc[
                    {"climate_hazards": hazards, "system_components": components}
                ]
                > 5
            ):
                self.vulnerability_matrix.loc[
                    {"climate_hazards": hazards, "system_components": components}
                ] = 0
            self.stream.reset()

        # Update heatmap matrix with vulnerability matrix values provided by user
        hm = self.vulnerability_matrix.hvplot.heatmap(
            x="climate_hazards",
            y="system_components",
            C="vulnerability",
            cmap=self.colormap,
            clim=(0, 5),
            rot=45,
            min_height=500,
            min_width=500,
            grid=True,
            framewise=True,
            responsive=True,
        ).opts(
            toolbar=None,
            tools=[],
            xlabel="Climate Hazard",
            ylabel=self.system_type.title() + " Component",
            fontsize={"ticks": "10pt", "ylabel": "20px", "xlabel": "20px"},
            gridstyle={"grid_line_color": "black"},
            colorbar=False,
        )
        return hm

    # Bind the increment map function to the output of the tap stream x and y values, wrap in a Holoviews DynamicMap object.
    def matrix_view(self):
        mp = pn.bind(
            self.increment_map,
            hazards=self.stream.param.x,
            components=self.stream.param.y,
        )
        return hv.DynamicMap(mp)

    c = plt.cm.get_cmap("PuRd")
    ticks = (
        ("extreme vulnerability", "white", th(c(1.0))),
        ("high vulnerability", "white", th(c(0.8))),
        ("substantial vulnerability", "white", th(c(0.6))),
        ("medium vulnerability", "black", th(c(0.4))),
        ("low vulnerability", "black", th(c(0.2))),
        ("no vulnerability", "black", th(c(0.0))),
    )
    legend_box = pn.GridBox(
        *[
            pn.pane.HTML(
                entry[0],
                style={
                    "color": entry[1],
                    "background-color": entry[2],
                    "text-align": "center",
                    "border": "2px solid black",
                    "border-radius": "5px",
                    "padding": "10px",
                },
                width=100,
                height=50,
            )
            for entry in ticks
        ],
        ncols=1,
    )

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(vulnerability_matrix=param.DataFrame())
    def output(self):
        vulnerability_matrix = self.vulnerability_matrix.to_dataframe().reset_index() #convert to Pandas tidy-like datafram
        vulnerability_matrix = vulnerability_matrix[vulnerability_matrix["vulnerability"] > 0] #exclude zero-vulnerabilities 
        return vulnerability_matrix

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            *self.t1,
            pn.Row(self.matrix_view, self.legend_box),
            width=plot_width,
            height=plot_height,
        )


# -

# ## 5) Summary reporting stage
#
# Provided with project definition, project component and climate hazard information, and after user-led vulnerability screening, the tool returns a graphical summary of user inputs and text-based summaries that:
# - Identifies the climate hazards that users rank as most consequential to system component vulnerabilities (based on axis-wise sums of the heatmap matrix)
# - Identifies the components that users indicate are most vulnerable (based on axis-wise sums of the heatmap matrix)
#
# Following this summary, the tool uses the provided resource links for each climate hazard relevant to system components, to develop a curated list of climate resources that are specific to the needs identified by the user.
#

# + tags=[]
class Summary_Report_Hazard_Linkages(param.Parameterized):

    # Access information provided by user earlier in pipeline to provide a summary
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    vulnerability_matrix = param.DataFrame()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends(
        "system_category",
        "system_type",
        "system_lifespan",
        "system_location",
        "vulnerability_matrix",
    )
    def __init__(self, **params):
        super().__init__(**params)

        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/report.jpg"),
            width=plot_width)

        self.t1 = pn.pane.Markdown(
            " # Great work!  You've described your "
            + self.system_category
            + " components, identified climate hazards and screened the vulnerability of your "
            + self.system_category
            + " components.  These are important steps towards finding good climate data."
        )

        self.t2=pn.pane.Markdown("# Here's how climate hazards relate to the components of your "+self.system_type+".\n")

        self.hazard_cmap = process_cmap("YlOrRd",ncolors=len(self.vulnerability_matrix["climate_hazards"]))
        self.hazard_color_dict={h:self.hazard_cmap[n] for n,h in enumerate(self.vulnerability_matrix["climate_hazards"])}
        self.component_cmap = process_cmap("glasbey_dark",ncolors=len(self.vulnerability_matrix["system_components"]))
        self.component_color_dict={c:self.component_cmap[n] for n,c in enumerate(self.vulnerability_matrix["system_components"])}
        self.sankey_cmap={**self.hazard_color_dict,**self.component_color_dict} #https://www.geeksforgeeks.org/python-merging-two-dictionaries/
        
        # Make a Sankey flow graphic that maps hazards to components
        self.sankey = hv.Sankey(self.vulnerability_matrix, label="")
        self.sankey.opts(edge_color='climate_hazards',
            node_color='climate_hazards',
            width=plot_width,
            toolbar=None,
            tools=[],
            show_values=False,
            label_position="outer",
            label_text_font_size='15pt',
            cmap=self.sankey_cmap,
            node_sort=True)
        
        self.t22=pn.pane.Markdown("### How does this infographic work?\n"
                + "By summarizing the main climate hazards (on the left) linking these to the components of your "
                + self.system_type+ " (on the right), it helps you prioritize your climate data search and - as a result - your climate risk assessment and adaptation planning.  For example:\n"
                +" components with thicker bars are those that have greater present-day or potential future vulnerabilites to one (or more!) climate hazards.  You may want to focus first on assessments of climate risk to these components.\n"
                +"Similarly, hazards with thicker bars are those that have the greatest potential to damage one or more aspects of your "+self.system_type+".  You may want to focus most energy on finding good climate change information for these hazards.\n"
                + "**Pro tip: before you leave this stage of the tool, go back and refine the component/hazard identification and vulnerability screening steps of this tool, to remake this infographic a few times.  Question your original assumptions!"
                + "Climate adaptation work is best done iteratively and a great first iteration is improving your confidence in the relationship between present and future climate hazards, and the components of your "+self.system_type+".**")

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            pn.WidgetBox(
                self.t2, self.sankey, self.t22, width=plot_width, css_classes=["custom-box"]
            ),
            width=plot_width,
            height=plot_height,
        )
    
    
class Summary_Report_Curated_Data(param.Parameterized):

    # Access information provided by user earlier in pipeline to provide a summary
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    vulnerability_matrix = param.DataFrame()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends(
        "system_category",
        "system_type",
        "system_lifespan",
        "system_location",
        "vulnerability_matrix",
    )
    
    def __init__(self, **params):
        super().__init__(**params)

        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/report.jpg"),
            width=plot_width)

        self.lat = self.system_location[0][0]
        self.lon = self.system_location[0][1]

        # Get sorted hazards list
        self.prioritized_hazards = (
            self.vulnerability_matrix.groupby("climate_hazards")["vulnerability"]
            .sum()
            .to_frame()
            .sort_values("vulnerability", ascending=False)
        )

        self.prioritized_components = (
            self.vulnerability_matrix.groupby("system_components")["vulnerability"]
            .sum()
            .to_frame()
            .sort_values("vulnerability", ascending=False)
        )

        self.t3=[]
        self.t3.append(pn.pane.Markdown(
            "# Here is a list of climate information and data resources, curated for you.\n"
            "This list is based on the hazards *you* identified, and is ranked in terms of their impact on your "+ self.system_type
            + " - according to your own assessment.  Most influential hazards appear first."
            +"If you expand each hazard item, you will find a go-to list of best-in-class climate information and data resources, curated by the Canadian Centre for Climate Services.  "
            +"Explore these resources first, to kick-start your understanding of present and future climate  impacts to your "
            + self.system_type+ "!"
        ))

        self.dT = dt.date.today().year - self.system_lifespan[0].year
        if self.dT > 20.0:
            self.t3.append(
                pn.pane.Markdown(
                    "**Pro tip: It looks like your "
                    + self.system_type
                    + " is already "
                    + str(int(self.dT))
                    + " years old.  "
                    + "Climate has already changed quite a bit in this time!  In your climate change planning, be sure to consider that your "
                    + self.system_type
                    + " has already experienced a significant amount of change in the severity and frequency of hazards you've identified!**"
                )
            )

        # Build list of hazards, that start with biggest hazards.  Make text red for higher impact hazards; scale to blacker and smaller.
        self.hazards = self.prioritized_hazards.index.values.tolist()
        self.fontsize = np.linspace(15, 10, num=len(self.hazards))
        self.fontcolor = [(r, 0, 0) for r in np.linspace(255, 0, num=len(self.hazards))]
        self.statement_list = []

        with open(
            os.path.join(general_input_directory, "master_hazard_database.json"), "r"
        ) as j:
            self.full_hazards_dict = json.loads(j.read())

        self.hazard_panels = []  # list of per hazard WidgetPanes

        # find nearest CPI point (use CRBCPI_i to index climate data for this point, from CRBCPI data dictionary)
        # Set up nearest neighbour search on the sphere
        self.CRBCPI_distance, self.CRBCPI_i = CRBCPI.nn_finder.query(
            np.deg2rad([[self.lat, self.lon]]), k=1
        )
        self.CRBCPI_i = self.CRBCPI_i[0][0]

        for n, h_formatted in enumerate(self.hazards):
            h = h_formatted.replace("\n", " ")
            self.hazard_details = []  # list of items for each hazard WidgetPane
            if h in self.full_hazards_dict:
                # set header image
                self.fname = os.path.join(
                    general_input_directory,
                    "images",
                    "cropped_hazard_images",
                    h.replace(" ", "-") + ".jpg",
                )
                self.hazard_jpg_pane = pn.pane.JPG(
                    self.fname, width=int(plot_width * 0.9)
                )  # this has to have same name as hazard, with exception of spaces (which get replaced by '-' as per replace code)width=plot_width,

                # build up hazard-specific reporting box
                self.hazard_details.append(
                    self.full_hazards_dict[h]["impact_statement"][
                        self.system_category.replace(" ", "_")
                    ]
                    + "  "
                    + self.full_hazards_dict[h]["direction_statement"]
                )
                self.hazard_details.append(
                    self.full_hazards_dict[h]["direction_confidence"]
                    + "  "
                    + self.full_hazards_dict[h]["magnitude_confidence"]
                )
                self.hazard_details.append(
                    "Click below to explore these best-in-class, Canadian-focussed "
                    + h
                    + "/climate change resources."
                )

                for resource, resource_details in self.full_hazards_dict[h][
                    "resources"
                ].items():
                    self.resource_items = []
                    self.resource_items.append(
                        "Information and/or data on "
                        + h
                        + " is available from "
                        + resource_details["source"]
                        + ".  This "
                        + resource_details["type"]
                        + " "
                        + resource_details["description"]
                    )
                    if resource_details["source"] == "ClimateData.ca":
                        self.url = (
                            resource_details["url"]
                            + str(self.lat)
                            + ","
                            + str(self.lon)
                            + ",8&geo-select=&var="
                            + resource_details["var"]
                            + "&var-group="
                            + resource_details["group"]
                            + "&mora="
                            + resource_details["season"]
                            + "&rcp=rcp85&decade="
                            + str(2070)
                            + "s&sector="
                        )
                        self.resource_items.append(
                            "  Click here to explore this data in more detail for your location: ["
                            + resource
                            + "]("
                            + self.url
                            + '){:target="_blank"}'
                        )
                    elif (
                        resource_details["source"]
                        == "The Climate Resilient Buildings and Core Public Infrastructure Project"
                    ):
                        self.location = CRBCPI.CRBCPI_data["+0.5C"]["Location"][
                            np.squeeze(self.CRBCPI_i)
                        ]
                        self.proximity = "{x:.0f}".format(
                            x=np.squeeze(self.CRBCPI_distance) * 6378.0
                        )  # convert distance from radians to kilometers, format for rounded-value printing
                        self.resource_items.append(
                            "In addition to regional information, it appears there is data available for "
                            + self.location
                            + ", around "
                            + self.proximity
                            + " km away from your site."
                        )
                        self.url = resource_details["url"]
                        self.resource_items.append(
                            "###  Click here to explore this data in more detail: ["
                            + resource
                            + "]("
                            + self.url
                            + ")"
                        )
                    else:
                        self.url = resource_details["url"]
                        self.resource_items.append(
                            "###  Click here to explore this information in more detail: ["
                            + resource
                            + "]("
                            + self.url
                            + ")"
                        )

                    self.hazard_details.append(
                        pn.WidgetBox(*self.resource_items, width=int(plot_width * 0.9))
                    )
            else:
                #TODO determine which picture to use if no hazard pic exists.
                self.fname=os.path.join(general_input_directory, "images","cropped_hazard_images","generic.jpg")
                self.hazard_jpg_pane = pn.pane.JPG(self.fname,width=int(plot_width* 0.9))
                self.hazard_details.append("### Please contact the [Canadian Centre for Climate Services Support Desk](https://www.canada.ca/en/environment-climate-change/services/climate-change/canadian-centre-climate-services.html) to help find information on how "
                    +h+ " may change in the future with climate change!")
            self.hazard_panels.append(pn.Column(self.hazard_jpg_pane,*self.hazard_details, name=h.capitalize(), width=plot_width))

        self.vulnerability_matrix = self.vulnerability_matrix[self.vulnerability_matrix["vulnerability"] > 0]

        self.hazard_cmap = process_cmap("YlOrRd",ncolors=len(self.vulnerability_matrix["climate_hazards"]))
        self.hazard_color_dict={h:self.hazard_cmap[n] for n,h in enumerate(self.vulnerability_matrix["climate_hazards"])}
        self.component_cmap = process_cmap("glasbey_dark",ncolors=len(self.vulnerability_matrix["system_components"]))
        self.component_color_dict={c:self.component_cmap[n] for n,c in enumerate(self.vulnerability_matrix["system_components"])}
        self.sankey_cmap={**self.hazard_color_dict,**self.component_color_dict} #https://www.geeksforgeeks.org/python-merging-two-dictionaries/

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            pn.WidgetBox(
                *self.t3,
                pn.Accordion(*self.hazard_panels, width=plot_width),
                css_classes=["custom-box"],
            ),
            width=plot_width,
            height=plot_height,
        )


# -

# ## Next steps stage
# This stage serves a jumping off point for users to understand what their next steps are. This text is intended to align users to basics of risk assessment, followed by adaptation (if their risk assessment thinking indicates that an 'unacceptable' risk threshold will be crossed.

# + tags=[]
class Next_Steps(param.Parameterized):

    system_category = param.String()
    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_category")
    
    def __init__(self, **params):
        super().__init__(**params)
        
        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/report.jpg"),
            width=plot_width)
        
        self.system_input_directory = self.system_category.replace(" ", "_") + "_inputs"
        # Open general resources database and read each resource to dictionary
        with open(os.path.join(self.system_input_directory, "next_steps.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            pn.pane.Markdown(self.lines),
            width=plot_width, 
            height=plot_height
        )


# + tags=[]
debug_flag = False

pipeline = pn.pipeline.Pipeline(inherit_params=True, debug=debug_flag)

pipeline.add_stage(name="Sector Definition", stage=Sector_Definition)
pipeline.add_stage(name="Introduction", stage=Introduction)
pipeline.add_stage(name="Disclaimer", stage=Disclaimer)
pipeline.add_stage(name="Core Knowledge Checklist", stage=Core_Knowledge_Checklist)
pipeline.add_stage(name="Project Definition", stage=Project_Definition)
pipeline.add_stage(name="Component Inventory", stage=Component_Inventory)
pipeline.add_stage(name="Present Hazard Inventory", stage=Present_Hazard_Inventory)
pipeline.add_stage(name="Future Hazard Inventory", stage=Future_Hazard_Inventory)
pipeline.add_stage(name="Vulnerability Heat Map", stage=Vulnerability_HeatMap)
pipeline.add_stage(name="Summary Report: Hazard Linkages", stage=Summary_Report_Hazard_Linkages)
pipeline.add_stage(name="Summary Report: Curated Data", stage=Summary_Report_Curated_Data)
pipeline.add_stage(name="Next Steps", stage=Next_Steps)

if debug_flag:
    DST_core = pn.Column(
        pipeline,
        width=plot_width,
        height=plot_height,
        name="Decision Support Tool",
    )
else:
    DST_core = pn.Column(
        pipeline.buttons,
        pipeline.stage,
        width=plot_width,
        height=plot_height,
        name="Decision Support Tool",
    )

DST_core.servable()
# -


