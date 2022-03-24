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

# + [markdown] tags=[]
# # Climate information and data decision support tool
#
# ![Toronto panorama](https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Sunset_Toronto_Skyline_Panorama_from_Snake_Island_Banner.jpg/1024px-Sunset_Toronto_Skyline_Panorama_from_Snake_Island_Banner.jpg)
#
# ## Background
#
# <img align="left" width="300" height="300" style="padding-right: 20px; padding-bottom: 20px;" src="https://i.cbc.ca/1.6252537.1637176843!/fileImage/httpImage/image.jpg_gen/derivatives/original_1180/abbotsford-flood-boat-highway-1.jpg">
#
# Climate information, specifically of future climate projections, is a crucial input to climate change risk assessments and subsequent adaptation planning.  However, decision makers often lack understanding of the decision framework underpins climate information data and use for practical use, and furthermore may not be capable of confidently identifying 'best in class' information and data sources.
#
# The tool encapsulated in this Jupyter Notebook is meant to aid users in 1) deciding which climate information would be useful for their climate change risk/adaptation work, and 2) providing access to user-specific well-vetted information and data.  In helping users in their initial climate information decision process, this tool implicitly guides users through the first key steps of a climate change risk/adaptation workflow, and furthermore provides them with useful links to real, user-relevant, decision-guided climate data and information.
#
# ## Decision Support Tool Design
#
# ### Conceptual Design
#
# #### Climate Change Impact, Risk, and Vulnerability Assessment Methods
#
# <img align="left" width="400" height="400" style="padding-right: 20px;" src="data/images/adaptation-cycle.png">
#
# Climate change information is most often used for impact, vulnerability and risk analyses in support of climate adaptation planning.  For this reason, the decision rules encapsulated in this decision support tool reflect fundamental elements of general vulnerability and risk assessment.  In particular, the first steps of general vulnerability and risk assessment (e.g. [ISO 31000:2018](https://www.iso.org/obp/ui/#iso:std:iso:31000:en)) are used to develop an understanding of the major components of a system in question, and the major impacts that may present risk to these components.  These principles form much of the basis of key climate change risk assessment frameworks in use today in Canada across multiple sectors, including engineering ([PIEVC](https://pievc.ca/)), community planning ([ICLEI BARC](https://icleicanada.org/barc-program/)), and this vulnerability and risk-relevant information and data sources is a second key outcome.
#
# #### Decision Support System Methods
#
# The decision rules and general design of this tool also adhers to [general principles of decision support systems](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.476.4750&rep=rep1&type=pdf) which generally target unstructured, poorly specified problems, combine user interaction and guidance with data access and retrieval functions, are easy and intuitive to use interactive; and are adaptable to changes in specific applications and decision making approaches.  Such tools help decision makers utilize data to solve unstructured problems - in this case, to perform climate impact, vulnerability and risk assessments.
#
# Production versions of this tool meet the following *conceptual* constraints (which must be satisfied in all future tool versions):
#
# 1. Adher to accepted impact, vulnerability and risk assessment principles (even if these principles are not explicitly stated to users)
# 2. Adher to decision support systems principles (even if these principles are not explicitly stated to users)
# 3. Remain flexible (ideally via input file changes and minimal/no code alteration) to application across arbitrary sectors, domains and systems
#
# ### Software Design
#
# This tool is currently written in Python, within a [Jupyter Notebook](https://jupyter.org/) environment.  It is fully version controlled using [Git](https://git-scm.com/), and [hosted on Github.com](https://github.com/ECCC-CCCS/decision-support-tool).  Hosting on the latter site allows - for example - easy localhost or truly web-based development testing using MyBinder.
#
# Within the Python framework, the tool currently relies heavily on the [Panels](https://panel.holoviz.org/) package, which "lets you create custom interactive web apps and dashboards by connecting user-defined widgets to plots, images, tables, or text."  In addition to Panels, the tool uses a selection of Holoviews ecosystem tools, as well as a suite of standard Python modules.  Panels-based apps can be rapidly developed and prototyped directly within a Jupyter Notebook environment, before being directly deployed as Python-based standalone apps.  The latter functionality is possible because Panel is developed on top of Bokeh, which provides access to a Tornado based web server ([Bokeh Server](https://docs.bokeh.org/en/latest/docs/user_guide/server.html)) that synchronizes data between the underlying Python environment and the BokehJS library running in the browser.
#
# The Python code that constitutes this tool has been carefully designed so that it is entirely agnostic to sector.  To apply the tool to a different sector/system, the developer only needs to alter a set of input files - not the code base itself.  Different sector-specific manifestations of the tool are tracked on separate Git branches within this repository.  They should all maintain, however, identical base .ipynb code bases, with the main branch existing as a common location to gather updates to this code, produced in the work of advancing sector-specific branch versions.
#
# Production versions of this tool meet the following *software* constraints (which must be satisfied in all future tool versions):
#
# 1. The tool must be natively Python-based for access to advanced visualization tools, and ease of prototyping and deployment
# 2. The tool must be entirely open source and version controlled
# 3. Web implementation of the tool must be low-latency and available on demand, and allow for simultaneous production and development
# 4. The base Python code must remain entirely sector-agnostic, and sector-specific instances of the tool need to be entirely manifested through changes to input files.
#
# ## Configuring and Running
#
# This Python Jupyter Notebook script enables the basic functionality of a building/climate change decision support tool.  It has been developed in a  local laptop environment using Anaconda-based Jupyter installation, on Python V3.7.  Use of other Python versions is certainly possible but not supported at present.  Note Python module dependencies - you will need to install these before executing this script successfully.
#
# Displaying the Notebook directly in-line in the Notebook is the fastest way to test the behaviour of the tool.  Deployment to MyBinder (via Github) is the fastest way to test a simple web-based deployment.
#
# ## In-line Documentation
#
# This code base provides extensive in-line documentation (in Markdown syntax) that describes how the implemented Python code addresses the conceptual and software constraints described above.  This in-line documentation should be considered the definitive documentation source for the tool.  Any substantial changes to the tool itself should be immediately reflected in this documentation.
#
# The code flow of this tool is organized around objects required to develop a Panel-based app.  In general, such apps can be organized via a range of methods (accordion expansions, tabs, etc.).  A tabs-based approach is chosen here to organize and present high-level sections of the tool.  As the content of each tab is developed sequentially 'in order of appearance' before being aggregated into the final app object, code can be read sequentially Within the core section of the tool (the Decision Support Tool tab), Panels Pipeline architecture is adopted in order to collect and pass user-provided impact and vulnerability information forward through a decision support system conceptual flow.
#
# Information inputs to the tool are, to the maximum extent possible, not hard-coded into the decision support tool code itself.  Instead, they are provided in input files (currently, .json files, which are ingested and used as dictionaries).
#
# #TODO statements are used throughout code to identify future work opportunities.

# + tags=[]
#### Module loads and general setup
import logging

import os
import pathlib  # to do, convert all os-based path work to pathlib
import param
from bokeh.palettes import YlOrRd9
from bokeh.events import Tap
import holoviews as hv
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
import panel as pn
from IPython import get_ipython

# other dependencies
# !pip install xlrd
# !pip install pre-commit
# !pre-commit install

hv.extension("bokeh")
gv.extension("bokeh")
pn.extension()

# + tags=[]
plot_width = 1000
plot_height = 1000


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

root_directory = "."
data_directory = "data"
general_directory = data_directory + "/general"
sectors_directory = data_directory + "/sectors"
images_directory =  data_directory + "/images"


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

        self.t1 = pn.pane.Markdown(
            "# This tool is designed to apply to a number of sectors (with more being added all the time!).  What sector are you interested in?"
        )
        self.system_category_widget = pn.widgets.Select(
            name="Select your sector!", options=["Building", "Contaminated Site"]
        )

    @param.output(system_category=param.String())
    def output(self):
        sector_type = self.system_category_widget.value.lower()
        logging.warning('Watch out!')  # will print a message to the console
        logging.info('I told you so')  # will not print anything
        return sector_type

    def panel(self):
        return pn.Column(self.t1, pn.WidgetBox(self.system_category_widget))


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
        # self.system_input_directory = "./sectors/" + self.system_category.replace(" ", "_") + "_inputs"
        self.system_input_directory = os.path.join(sectors_directory, self.system_category.replace(" ", "_") + "_inputs")
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
            os.path.join(root_directory, images_directory, "disclaimer.jpg"), height=200
        )
        with open(os.path.join(root_directory, data_directory, "disclaimer.txt")) as f:
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
# This stage serves a set of general pre-learning resources.  These are intended to provide users with opportunity to gain some general - but important - climate change knowledge before they enter into the actual decision support tool process.  If new resources are added to data/general/resources.json file, they will automatically be displayed here.

# + tags=[]
class Core_Knowledge_Checklist(param.Parameterized):

    # Define information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()

    def __init__(self, **params):
        super().__init__(**params)
        self.jpg_pane = pn.pane.JPG(
            os.path.join(root_directory, images_directory, "core_knowledge.jpg"),
            width=plot_width,
        )
        self.t1 = pn.pane.Markdown(
            "# Before we begin, it is important that you are comfortable with some important concepts and programs related to use of future climate data in decision making!"
        )
        # Open general resources database and read each resource to dictionary
        with open(
            os.path.join(
                root_directory, general_directory, "resources.json"
            ),
            "r",
        ) as j:
            self.general_resources = json.loads(j.read())
        # compile a list of markdown statements by iterating over dictionary
        self.markdown_resource_links = [
            "**"
            + self.general_resources[s]["background"]
            + "**<br/>["
            + s
            + "]("
            + self.general_resources[s]["url"]
            + '){:target="_blank"}'
            for s in self.general_resources
        ]

    def panel(self):
        return pn.Column(
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
            "### Click on this zoomable map to provide the location of your "
            + self.system_category
            + ".  Be patient, it may take a moment for your point to appear on the map."
        )
        # User provides location information via clicking on an interactive map display.
        self.x = 0.0
        self.y = 0.0
        self.stream = hv.streams.Tap(x=None, y=None)

    def map_constructor(self, x=0, y=0):
        map_background = gv.tile_sources.Wikipedia
        self.x = x
        self.y = y
        Canada_x_bounds = (-15807400, -5677300)
        Canada_y_bounds = (8012300, 11402300)
        self.x = -8677300
        self.y = 9012300
        location_point = gv.Points(
            (x, y, "point"), vdims="Point", crs=crs.GOOGLE_MERCATOR
        )
        return (map_background * location_point).opts(
            opts.Points(
                global_extent=False,
                xlim=Canada_x_bounds,
                ylim=Canada_y_bounds,
                width=500,
                height=475,
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
            self.t1,
            self.t11,
            pn.WidgetBox(self.t2, self.system_type_widget),
            pn.WidgetBox(self.t3, self.system_lifespan_widget),
            pn.WidgetBox(self.t4, self.map_view),
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
        # self.system_input_directory =  "./sectors/" + self.system_category.replace(" ", "_") + "_inputs"
        self.system_input_directory = os.path.join(sectors_directory, self.system_category.replace(" ", "_") + "_inputs")


        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "components.jpg"), height=200
        )

        with open(
            os.path.join(self.system_input_directory, "components.json"), "r"
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
            pn.WidgetBox(self.t2, self.system_components_CrossSelector_widget),
            pn.WidgetBox(self.t3, self.system_components_TextAreaInput_widget),
            width=plot_width,
            height=plot_height,
        )


# -

# ## 3) Hazard inventory stage
#
# Once components of a system are defined, users need to think carefully about which hazards these components may be vulnerable to, today and in the future.
# High level component information gathered here is used to define one axis of a vulnerability ranking matrix that is manipulated be the user to self-develop an understanding of component vulnerability rankings.

# + tags=[]
class Hazard_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type")

    # Open hazards database and read each hazard item to dictionary
    def __init__(self, **params):
        super().__init__(**params)

        # self.system_input_directory =  "./sectors/" + self.system_category.replace(" ", "_") + "_inputs"
        self.system_input_directory = os.path.join(sectors_directory, self.system_category.replace(" ", "_") + "_inputs")

        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "hazard.jpg"), height=200
        )

        self.t1 = pn.pane.Markdown(
            "# Next, you need to think about the important weather and climate hazards in your region."
        )

        self.t2 = pn.pane.Markdown(
            "## Please select any hazards that your "
            + self.system_type
            + " is, or may become, vulnerable to.  Add any additional hazards that are not listed."
        )
        super().__init__(**params)
        with open(
            os.path.join(root_directory, general_directory, "hazards.json"), "r"
        ) as j:
            self.full_hazards_dict = json.loads(j.read())
        self.climate_hazards = [s for s in self.full_hazards_dict]
        # Provide selector that lets user select hazards that pertain to their system.
        self.climate_hazards_CrossSelector_widget = pn.widgets.CrossSelector(
            name="Which climate hazards is your "
            + self.system_type
            + " potentially vulnerable to, if the hazard occurred now or in the future?",
            value=[],
            options=self.climate_hazards,
        )
        # Allow users to add arbitrary other compone hazards via text entry
        self.t3 = pn.pane.Markdown(
            "### Include other hazards that your "
            + self.system_type
            + " may be vulnerable to that are not in the list above."
        )
        self.climate_hazards_TextAreaInput_widget = pn.widgets.TextAreaInput(
            placeholder="Enter any other hazards you would like to include in this evaluation, separated by commas..."
        )

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(climate_hazards=param.List())
    def output(self):
        climate_hazards = self.climate_hazards_CrossSelector_widget.value
        if self.climate_hazards_TextAreaInput_widget.value:
            climate_hazards = (
                climate_hazards
                + self.climate_hazards_TextAreaInput_widget.value.replace(
                    " ", ""
                ).split(",")
            )
        return climate_hazards

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            pn.WidgetBox(self.t2, self.climate_hazards_CrossSelector_widget),
            pn.WidgetBox(self.t3, self.climate_hazards_TextAreaInput_widget),
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
    climate_hazards = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type", "system_components", "climate_hazards")
    def __init__(self, **params):
        super().__init__(**params)

        self.t1 = []
        self.t1.append(
            pn.pane.Markdown(
                "# Next, the fun part: screening the impact of each hazard you identified, against each major component of your "
                + self.system_type.lower()
                + ".  This is crucial for prioritizing your climate data and information needs."
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                "## This matrix contains a box, for each combination of hazards (columns) and "
                + self.system_type.lower()
                + " components (rows) that you identified."
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                '## For each combination, think carefully about how vulnerable that component might be - today or in the future - to that climate hazard, across the scale from "no vulnerability" to "extreme vulnerability".'
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                "## Click on the box one or more times to set that vulnerability level, for that hazard/component combination.  Then move on to the next box!"
            )
        )
        self.t1.append(
            pn.pane.Markdown(
                '## When you are done, step back and take a broad look at your completed "vulnerability heat map".  Does it match with your intuition about what your '
                + self.system_type.lower()
                + " is sensitive to?  If so: on to the final step!"
            )
        )

        # Define an xarray data array dimensioned by the # of hazards and # of components
        self.vulnerability_matrix = xr.DataArray(
            np.zeros((len(self.climate_hazards), len(self.system_components))),
            dims=["climate_hazards", "system_components"],
            coords=dict(
                climate_hazards=self.climate_hazards,
                system_components=self.system_components,
            ),
            name="vulnerability",
        )

        # Define a tap (mouse click) stream
        self.stream = hv.streams.Tap(x=None, y=None)

    colormap = "magma"

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
            show_grid=True,
            framewise=True,
            responsive=True,
        )
        hm.opts(
            toolbar=None,
            tools=[],
            xlabel="Climate Hazard",
            ylabel=self.system_type.title() + " Component",
            fontsize={"ticks": "15pt", "ylabel": "20px", "xlabel": "20px"},
            gridstyle={"grid_line_color": "white"},
            show_grid=True,
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

    c = plt.cm.get_cmap("magma_r")
    ticks = (
        ("extreme vulnerability", "black", th(c(0.0))),
        ("high vulnerability", "black", th(c(0.2))),
        ("substantial vulnerability", "black", th(c(0.4))),
        ("medium vulnerability", "white", th(c(0.6))),
        ("low vulnerability", "white", th(c(0.8))),
        ("no vulnerability", "white", th(c(1.0))),
    )
    legend_title = pn.pane.HTML("<h1>This is an HTML pane</h1>")
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
    @param.output(
        vulnerability_matrix=param.DataFrame()
    )  # to do, make a true xarray param class
    def output(self):
        vulnerability_matrix = self.vulnerability_matrix.to_dataframe().reset_index()
        return vulnerability_matrix

    # Define Panel tab
    def panel(self):
        return pn.Column(
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
class Summary_Report(param.Parameterized):

    # Access information provided by user earlier in pipeline to provide a summary
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()
    climate_hazards = param.List()
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

        self.t1 = pn.pane.Markdown(
            " # Great work!  Describing your "
            + self.system_category
            + " components, identifying potential hazards and then screen the vulnerability of your "
            + self.system_category
            + " components to each hazard, provides some excellent insights that will help you find good climate data."
        )

        self.t2 = pn.pane.Markdown(
            "# Linking components, hazards, and vulnerabilities: a visual breakdown\n"
            "This infographic summarizes the main climate hazards to your "
            + self.system_type
            + ".  "
            "On the left are the hazards you identified.  On the right are the components of your "
            + self.system_type
            + ".  "
            "Grey bars reflect the hazard/component vulnerabilities you identified.  "
            "Larger hazards are those which your "
            + self.system_type
            + " components are particularly vulnerable to - these are represented by thicker bars.  "
            "Components with thicker bars are the more vulnerable components of your "
            + self.system_type
            + ".  "
            "This visualization helps you decide which hazards you may want spend more time investigating.  "
            "It also highlights which parts of your "
            + self.system_type
            + " may be most vulnerable to climate change - these are perhaps components where adaptation should be prioritized.  "
            "Feel free to try refining your components, hazards, and vulnerability screening heatmap a few times - thinking about climate change vulnerabilities is an iterative process.  "
        )

        self.t3 = pn.pane.Markdown(
            "# Prioritizing key hazards and components: a ranked list\n"
            "Ranking hazards in terms of their impact on your "
            + self.system_type
            + " helps you prioritize efforts to find climate information and data.  "
            "The hazards you identified as most important to your "
            + self.system_type
            + " are ranked below.  Most influential hazards appear first.  "
            "For each hazard, a curated initial go-to list of good climate information information and data resources is provided.  "
            "You should explore these resources first, as you build understanding of climate change impacts to your "
            + self.system_type
            + ".  "
        )

        # Build list of hazards, that start with biggest hazards.  Make text red for higher impact hazards; scale to blacker and smaller.
        self.hazards = self.prioritized_hazards.index.values.tolist()
        self.fontsize = np.linspace(15, 10, num=len(self.hazards))
        self.fontcolor = [(r, 0, 0) for r in np.linspace(255, 0, num=len(self.hazards))]
        self.statement_list = []

        with open(
            os.path.join(root_directory, general_directory, general_directory, "hazards.json"), "r"
        ) as j:
            self.full_hazards_dict = json.loads(j.read())

        self.hazard_panels = []  # list of per hazard WidgetPanes

        # find nearest CPI point (use CRBCPI_i to index climate data for this point, from CRBCPI data dictionary)
        # Set up nearest neighbour search on the sphere
        self.CRBCPI_distance, self.CRBCPI_i = CRBCPI.nn_finder.query(
            np.deg2rad([[self.lat, self.lon]]), k=1
        )
        self.CRBCPI_i = self.CRBCPI_i[0][0]

        for n, h in enumerate(self.hazards):
            self.hazard_details = []  # list of items for each WidgetPane
            # self.widget_details.append('<h2 style="color:rgb'+str(self.fontcolor[n])+';">'+str(n+1)+') '+h.capitalize()+'</h2>')

            if h in self.full_hazards_dict:
                self.hazard_details.append(
                    "## "
                    + self.full_hazards_dict[h]["impact_statement"][
                        self.system_category.replace(" ", "_")
                    ]
                    + "  "
                    + self.full_hazards_dict[h]["direction_statement"]
                )
                self.hazard_details.append(
                    "## "
                    + self.full_hazards_dict[h]["direction_confidence"]
                    + "  "
                    + self.full_hazards_dict[h]["magnitude_confidence"]
                )
                self.hazard_details.append(
                    "## Here are some "
                    + h
                    + " resources you should consider exploring:"
                )

                for resource, resource_details in self.full_hazards_dict[h][
                    "resources"
                ].items():

                    self.resource_items = []

                    self.resource_items.append(
                        "### Information and/or data on "
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
                            "###  Click here to explore this data in more detail for your location: ["
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
                            "### In addition to regional information, it appears there is data available for "
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
                self.hazard_details.append(
                    "### Please contact the [Canadian Centre for Climate Services Support Desk](https://www.canada.ca/en/environment-climate-change/services/climate-change/canadian-centre-climate-services.html) to help find information on how "
                    + h
                    + " may change in the future with climate change!"
                )

            self.hazard_panels.append(
                pn.Column(*self.hazard_details, name=h.capitalize(), width=plot_width)
            )

        self.vulnerability_matrix = self.vulnerability_matrix[
            self.vulnerability_matrix["vulnerability"] > 0
        ]
        # Make a Sankey flow graphic that maps hazards to components
        self.sankey = hv.Sankey(self.vulnerability_matrix, label="")
        self.sankey.opts(  # edge_color='system_components',
            # node_color='climate_hazards',
            cmap="tab20",
            width=plot_width,
            toolbar=None,
            tools=[],
            show_values=False,
            label_position="outer",
        )

    def panel(self):
        return pn.Column(
            self.t1,
            pn.WidgetBox(self.t2, self.sankey, width=plot_width),
            pn.WidgetBox(self.t3, pn.Accordion(*self.hazard_panels, width=plot_width)),
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
        # self.system_input_directory "./sectors/" + self.system_category.replace(" ", "_") + "_inputs"
        self.system_input_directory = os.path.join(sectors_directory, self.system_category.replace(" ", "_") + "_inputs")

        # Open general resources database and read each resource to dictionary
        with open(os.path.join(self.system_input_directory, "next_steps.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)

    def panel(self):
        return pn.Column(
            pn.pane.Markdown(self.lines), width=plot_width, height=plot_height
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
pipeline.add_stage(name="Hazard Inventory", stage=Hazard_Inventory)
pipeline.add_stage(name="Vulnerability Heat Map", stage=Vulnerability_HeatMap)
pipeline.add_stage(name="Summary Report", stage=Summary_Report)
pipeline.add_stage(name="Next Steps", stage=Next_Steps)

if debug_flag:
    DST_core = pn.Column(
        pipeline, width=plot_width, height=plot_height, name="Decision Support Tool"
    )
else:
    DST_core = pn.Column(
        pipeline.buttons,
        pipeline.stage,
        width=plot_width,
        height=plot_height,
        name="Decision Support Tool",
    )

# + tags=[]
DST_core.servable()
# -




