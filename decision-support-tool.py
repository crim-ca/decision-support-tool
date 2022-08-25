# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: title,-all
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
# ---

# + Imports and setup
import os
import param
import holoviews as hv
from holoviews.plotting.util import process_cmap
from holoviews import opts
import geoviews as gv
import panel as pn
import xarray as xr
import hvplot.xarray
from cartopy import crs
from pyproj import Proj, transform
import pandas as pd  # also needs xlrd installed
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex as th
import datetime as dt  # not available on Conda - access via PIP
import json

def selector_plus_custom_text(multi_select=False,grouped_lists=False,input_directory=None,input_file=None,selector_text=None,custom_text=None):
        # Open database from file and read each entry item into a dictionary
        with open(os.path.join(input_directory,input_file), "r") as j:
            item_list = json.loads(j.read())
        if grouped_lists:
            # Get basic list of system components.  Some fancy Python to get this into a list from nested dictionary entries.
            item_list = sum([item_list[c]["group"] for c in item_list], [])
        else:
            item_list=[s for s in item_list]
        # Provide selector that lets user 'construct' their list.
        if multi_select:
            selector=pn.widgets.CrossSelector(name=selector_text, value=[],options=item_list)
        else:
            selector=pn.widgets.Select(name=selector_text,options=item_list)
        return selector,pn.widgets.TextAreaInput(placeholder=custom_text)

general_input_directory = "."

with open(os.path.join(general_input_directory, "style.css")) as f:
    lines = f.readlines()
custom_css = "\n".join(lines)
pn.config.raw_css.append(custom_css)

hv.extension("bokeh")
gv.extension("bokeh")
pn.extension(raw_css=[custom_css],sizing_mode='stretch_width')

plot_width = 1200
plot_height = 1500
panel_options=dict(width=plot_width, width_policy='max', sizing_mode='stretch_both')

system_category="building"
template=pn.template.BootstrapTemplate(title='Canadian Centre for Climate Services '+system_category+' Decision Support Tool',
                                       favicon='images/logo.ico',
                                       logo='images/logo.ico')
# + Welcome stage
'''
This code provides a welcome and any/all practical and legal disclaimers/conditions of use that users should be aware of before continuing.
Applied as a modal to the app.
'''

system_input_directory = system_category.replace(" ", "_") + "_inputs"
jpg_pane = pn.pane.JPG(os.path.join(system_input_directory, "intro_header.jpg"),
                       width=plot_width)
with open(os.path.join(system_input_directory, "intro.txt")) as f:
     lines = f.readlines()
lines = "\n".join(lines)
introduction = pn.pane.Markdown(lines)

with open(os.path.join(general_input_directory, "disclaimer.txt")) as f:
    lines = f.readlines()
    lines = "\n".join(lines)
disclaimer = pn.pane.Markdown(lines)

welcome = pn.Column(jpg_pane,
                    introduction,
                    disclaimer,
                    **panel_options)

# + Core knowledge checklist stage
'''
Core knowledge checklist stage
This stage serves a set of general pre-learning resources.  These are intended to provide users with opportunity to gain some general - but important - climate change knowledge before they enter into the actual decision support tool process.  If new resources are added to master_general_resources_database.json file, they will automatically be displayed here.
'''

jpg_pane = pn.pane.JPG(os.path.join(general_input_directory, "images/core_knowledge.jpg"),width=plot_width)

t1 = pn.pane.Markdown( "### Before we begin, it is important that you are comfortable with some important concepts and programs related to use of future climate data in decision making!")
# Open general resources database and read each resource to dictionary
with open(os.path.join(general_input_directory, "master_general_resources_database.json"),
            "r") as j:
            general_resources = json.loads(j.read())
        # compile a list of markdown statements by iterating over dictionary
markdown_resource_links = [
    general_resources[s]["background"]
            + "<br/>["
            + s
            + "]("
            + general_resources[s]["url"]
            + '){:target="_blank"}'
            for s in general_resources]


knowledge_checklist=pn.Column(
            jpg_pane,
            t1,
            *markdown_resource_links,
            **panel_options)

# + Project definition stage
'''
Project definition stage
'''

class Project_Definition(param.Parameterized):

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("sector_type")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "site_info.jpg"),
            width=plot_width)
        
        self.t1 = pn.pane.Markdown(
            "## The first stage in understanding which climate data you need, is providing some basic information about your "
            + system_category
            + ".  Please fill in the following information, which will help curate specific climate data for you in subsequent steps of this tool.")

        self.t2 = pn.pane.Markdown(
            "What type of " + system_category + " are you assessing?" + 
            '  Select your building type from this list or define it yourself.')
        
        self.system_type_selector,self.system_type_manual_input=selector_plus_custom_text(multi_select=False,
            grouped_lists=True,
            input_directory=system_category.replace(" ", "_") + "_inputs",
            input_file='system_types.json',
            selector_text='',
            custom_text='Custom building type')
        
        # User provides a definition of system lifespan via manipulation of a slider

        self.t3 = pn.pane.Markdown(
            "What timeframe are you considering (past and future)? Make your selection based on the realistic stard and planned end of life of your "
            + system_category
            + ".")

        self.system_lifespan_widget = pn.widgets.DateRangeSlider(
            start=dt.datetime(1950, 1, 1),
            end=dt.datetime(2100, 1, 1),
            value=(dt.datetime(2021, 1, 1), dt.datetime(2061, 1, 1)),
            bar_color="#FF0000")

        self.t5 = pn.pane.Markdown("Where is your "+system_category+"?  Click on the (zoomable) map to provide the location.")

        #User provides location information via clicking on an interactive map display.
        self.x=0.
        self.y=0.
        self.stream = hv.streams.Tap(x=None, y=None)
        
    def map_constructor(self,x=0,y=0):
        map_background = gv.tile_sources.Wikipedia
        self.x=x
        self.y=y
        Canada_x_bounds=(-16000000,-5600000)
        Canada_y_bounds=(7500000,  15500000)
        location_point= gv.Points((x,y,'point'),vdims='Point',crs=crs.GOOGLE_MERCATOR)
        return (map_background*location_point).opts(opts.Points(global_extent=False,projection=crs.GOOGLE_MERCATOR,
                                          xlim=Canada_x_bounds,ylim=Canada_y_bounds, size=12, color='black', width=plot_width, height=int(plot_height))) #only Google Mercator allows interaction... too bad.  Would rather use Lambert Conformal which is most commonly used by StatsCan

    def map_view (self):
        mp=pn.bind(self.map_constructor,x=self.stream.param.x,y=self.stream.param.y)
        return hv.DynamicMap(mp)

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(system_type=param.String(),
                  system_lifespan=param.Tuple(),
                  system_location=param.List())
    
    def output(self):
        if self.system_type_manual_input.value != "":
            system_type = self.system_type_manual_input.value.lower()
        else:
            system_type = self.system_type_selector.value.lower()
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
            pn.WidgetBox(self.t2, self.system_type_selector,self.system_type_manual_input, css_classes=["custom-box"]),
            pn.WidgetBox(self.t3, self.system_lifespan_widget, css_classes=["custom-box"]),
            pn.WidgetBox(self.t5, self.map_view, css_classes=["custom-box"]))
            #**panel_options)

# + Component inventory stage
'''
2) Component inventory stage
To robustly understand climate impacts to and climate vulnerabilities of complex systems, they need to be broken down into major functional components and each component assessed separately. For example:

an airport could be vulnerable to climate impacts either to specific impacts to the runway, or specific impacts to the control tower
an ecosystem could be vulnerable to climate impacts either to a particular animal species, or a particular plant species High level component information gathered here is used to define one axis of a vulnerability ranking matrix that is manipulated be the user to self-develop an understanding of component vulnerability rankings.
'''

class Component_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type")

    # Develop database
    def __init__(self, **params):
        super().__init__(**params)
        self.t1 = pn.pane.Markdown( "### Next, think carefully about the basic elements of your " + str(self.system_type) + ".")
        self.t2 = pn.pane.Markdown("Please select the components from this list that are important aspects of your " + str(self.system_type) + ".")

        # Open hazards database and read each hazard item to dictionary
        self.system_input_directory = system_category.replace(" ", "_") + "_inputs"

        self.jpg_pane = pn.pane.JPG( os.path.join(self.system_input_directory, "components.jpg"), height=200)

        self.component_selector,self.component_manual_input=selector_plus_custom_text(multi_select=True,
                                                                                                grouped_lists=True,
                                                                                                input_directory=system_category.replace(" ", "_") + "_inputs",
                                                                                                input_file='component_database.json',
                                                                                                selector_text="Which " + self.system_type + " components would you like to include in this assessment?",
                                                                                                custom_text="Enter any number of additional " + self.system_type + " components, separated by commas, here.")

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(system_components=param.List())
    def output(self):
        system_components = self.component_selector.value
        if self.component_manual_input.value:
            system_components = (system_components + self.component_manual_input.value.replace(" ", "").split(","))
        return system_components

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            pn.WidgetBox(
                self.t2,
                self.component_selector,
                self.component_manual_input,
                css_classes=["custom-box"]),
            **panel_options)

# + Hazard inventory stages
'''
3) Hazard inventory stage
Once components of a system are defined, users need to think carefully about which hazards these components may be vulnerable to, today and in the future.  
High level component information gathered here is used to define one axis of a vulnerability ranking matrix that is manipulated be the user to self-develop an understanding of component vulnerability rankings.
'''
class Present_Hazard_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.

    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "present_hazard.jpg"), height=200)

        self.t1 = pn.pane.Markdown(
            "## Next, you need to think about *present-day* weather and climate hazards in your region.")

        self.t2 = pn.pane.Markdown(
            "Select any hazards that your "
            + self.system_type
            + " is vulnerable to, today.  Add any additional hazards that are not listed.")
        self.hazard_selector,self.hazard_manual_input=selector_plus_custom_text(multi_select=True,
                                                                                          grouped_lists=False,
                                                                                          input_directory=general_input_directory,
                                                                                          input_file='master_hazard_database.json',
                                                                                          selector_text="Which climate hazards is your " + self.system_type + " vulnerable to?",
                                                                                          custom_text="Enter any number of additional hazards, separated by commas, here.")

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(all_climate_hazards=param.List(),present_climate_hazards=param.List())
    def output(self):
        all_climate_hazards = self.hazard_selector.options
        present_climate_hazards = self.hazard_selector.value
        if self.hazard_manual_input.value:
            present_climate_hazards = (present_climate_hazards + self.hazard_manual_input.value.replace(" ", "").split(","))
        return all_climate_hazards,present_climate_hazards

    # Define Panel tab
    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            self.t2,
            self.hazard_selector,
            self.hazard_manual_input,
            **panel_options)

class Future_Hazard_Inventory(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    system_components = param.List()
    all_climate_hazards = param.List()
    present_climate_hazards = param.List()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type", "all_climate_hazards", "present_climate_hazards")
    def __init__(self, **params):
        super().__init__(**params)

        self.system_input_directory = system_category.replace(" ", "_") + "_inputs"
        self.jpg_pane = pn.pane.JPG(
            os.path.join(self.system_input_directory, "future_hazard.jpg"), height=200)

        self.t1 = pn.pane.Markdown(
            "## Now let's think about hazards that might emerge in the future because of climate change.")
        self.t2 = pn.pane.Markdown(
            "Consider the remaining hazards in the list.  Is there ANY chance that any of these hazards could impact your "
            + self.system_type
            + " in the future?"
            + " If so, let's add them to the list.")

        # Trim hazards list by previously selected hazards list
        self.potential_future_climate_hazards = [h for h in self.all_climate_hazards if h not in self.present_climate_hazards]

        # Provide selector that lets user select hazards that pertain to their system.
        self.climate_hazards_CrossSelector_widget = pn.widgets.CrossSelector(
            name="Which climate hazards might your "
            + self.system_type
            + " be vulnerable to in the future?",
            value=[],
            options=self.potential_future_climate_hazards)
        # Allow users to add arbitrary other compone hazards via text entry
        self.t3 = pn.pane.Markdown(
            "### Include other hazards that your "
            + self.system_type
            + " may be vulnerable to that are not in the list above.")
        self.climate_hazards_TextAreaInput_widget = pn.widgets.TextAreaInput(
            placeholder="Enter any number of additional hazards, separated by commas.")

    # Gather output of this Pipeline stage for next stages of Pipeline
    @param.output(net_climate_hazards=param.List())
    def output(self):
        net_climate_hazards = (self.present_climate_hazards
            + self.climate_hazards_CrossSelector_widget.value)
        if self.climate_hazards_TextAreaInput_widget.value:
            net_climate_hazards = (
                net_climate_hazards
                + self.climate_hazards_TextAreaInput_widget.value.replace(" ", "").split(","))
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
            **panel_options)

# + Vulnerability screening stage
'''
4) Vulnerability screening stage
User-defined input regarding 1) project components and 2) potential climate hazards are combined in the following Pipeline tab into a 2-D heat map that represents a high level vulnerability screen. This heat map is dynamically user-defined (the number of vertical and horizontal elements is based on the number of project components and climate hazards, respectively). It is also interactive: users are prompted to set per-component/hazard vulnerabilities by clicking on individual heat map elements, to develop a heat map-based perspective on where greatest system vulnerabilities lie. This information is recorded and is a key input to the final tool summary.
'''

class Vulnerability_HeatMap(param.Parameterized):

    # Access information provided by user earlier in pipeline, either for direct use, or to carry forward for future use.
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
            width=plot_width)

        self.t1 = []
        self.t1.append(
            pn.pane.Markdown(
                "## Now the fun part: screening the impact of each hazard you identified, against each major component of your "
                + self.system_type.lower()
                + ".  This is crucial for prioritizing your climate data and information needs." ))
        self.t1.append(
            pn.pane.Markdown(
                "This matrix contains a box, for each combination of hazards (columns) and "
                + self.system_type.lower()
                + ' components (rows) that you identified. For each combination, think carefully about how vulnerable that component might be - today or in the future - to that climate hazard, across the scale from "no vulnerability" to "extreme vulnerability".'
                + "Click on the box one or more times to set that vulnerability level, for that hazard/component combination.  Then move on to the next box.  "
                + 'When you are done, step back and take a broad look at your completed "vulnerability heat map".  Does it match with your intuition about what your '
                + self.system_type.lower()+ " is sensitive to?"))

        # Define an xarray data array dimensioned by the # of hazards and # of components
        self.vulnerability_matrix = xr.DataArray(
            np.zeros((len(self.net_climate_hazards), len(self.system_components))),
            dims=["climate_hazards", "system_components"],
            coords=dict(climate_hazards=[ s.replace(" ", "\n") for s in self.net_climate_hazards],
                   system_components=[s.replace(" ", "\n") for s in self.system_components]),
            name="vulnerability")

        # Define a tap (mouse click) stream
        self.stream = hv.streams.Tap(x=None, y=None)

    colormap = "PuRd"

    # Define function that increments value of heatmap element by 1, each time it is clicked.  Loop back to initial value (zero) if maximum # of clicks exceeded
    def increment_map(self, hazards=None, components=None):
        if hazards and components:
            self.vulnerability_matrix.loc[{"climate_hazards": hazards, "system_components": components}] += 1
            if (self.vulnerability_matrix.loc[{"climate_hazards": hazards, "system_components": components}] > 5):
                self.vulnerability_matrix.loc[{"climate_hazards": hazards, "system_components": components}] = 0
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
            colorbar=False)
        return hm

    # Bind the increment map function to the output of the tap stream x and y values, wrap in a Holoviews DynamicMap object.
    def matrix_view(self):
        mp = pn.bind( self.increment_map,hazards=self.stream.param.x,components=self.stream.param.y)
        return hv.DynamicMap(mp)

    c = plt.cm.get_cmap("PuRd")
    ticks = (("extreme vulnerability", "white", th(c(1.0))),
        ("high vulnerability", "white", th(c(0.8))),
        ("substantial vulnerability", "white", th(c(0.6))),
        ("medium vulnerability", "black", th(c(0.4))),
        ("low vulnerability", "black", th(c(0.2))),
        ("no vulnerability", "black", th(c(0.0))))
    legend_box = pn.GridBox(
        *[pn.pane.HTML(
                entry[0],
                style={
                    "color": entry[1],
                    "background-color": entry[2],
                    "text-align": "center",
                    "border": "2px solid black",
                    "border-radius": "5px",
                    "padding": "10px",
                }, width=100,height=50)
            for entry in ticks], ncols=1)

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
            **panel_options)

# + Summary reporting stage
'''
5) Summary reporting stage
Provided with project definition, project component and climate hazard information, and after user-led vulnerability screening, the tool returns a graphical summary of user inputs and text-based summaries that:

Identifies the climate hazards that users rank as most consequential to system component vulnerabilities (based on axis-wise sums of the heatmap matrix)
Identifies the components that users indicate are most vulnerable (based on axis-wise sums of the heatmap matrix)
'''

class Summary_Report_Hazard_Linkages(param.Parameterized):

    # Access information provided by user earlier in pipeline to provide a summary

    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    vulnerability_matrix = param.DataFrame()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_type", "system_lifespan", "system_location", "vulnerability_matrix")
    def __init__(self, **params):
        super().__init__(**params)

        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/report.jpg"),
            width=plot_width)

        self.t1 = pn.pane.Markdown(
            " ## Great work!  You've described your "
            + system_category
            + " components, identified climate hazards and screened the vulnerability of your "
            + system_category
            + " components.  These are important steps towards finding good climate data."
            + "Here's how climate hazards relate to the components of your "+self.system_type+".")

        self.hazard_cmap = process_cmap("YlOrRd",ncolors=len(self.vulnerability_matrix["climate_hazards"]))
        self.hazard_color_dict={h:self.hazard_cmap[n] for n,h in enumerate(self.vulnerability_matrix["climate_hazards"])}
        self.component_cmap = process_cmap("glasbey_dark",ncolors=len(self.vulnerability_matrix["system_components"]))
        self.component_color_dict={c:'black' for n,c in enumerate(self.vulnerability_matrix["system_components"])}  
        #self.component_color_dict={c:self.component_cmap[n] for n,c in enumerate(self.vulnerability_matrix["system_components"])}
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
        
        self.t2=pn.pane.Markdown("### *How does this infographic work?*\n"
                + "By summarizing the main climate hazards (on the left) linking these to the components of your "
                + self.system_type+ " (on the right), it helps you prioritize your climate data search, climate risk assessment and adaptation planning.  For example:\n"
                +" components with thicker bars are those that have greater present-day or potential future vulnerabilites to one (or more!) climate hazards.  You should focus on climate risk to these components.\n"
                +"Similarly, hazards with thicker bars are those that have the greatest potential to damage one or more aspects of your "+self.system_type+".  You should focus on understanding how climate change will affect these hazards.\n"
                + "**Pro tip: before you leave this stage, go back and confirm the component/hazard identification and vulnerability screening steps of this tool.  Question your original assumptions to make sure you're confident with these results!**")

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            self.t1,
            pn.WidgetBox(
                self.sankey, self.t2, width=plot_width, css_classes=["custom-box"]),
            **panel_options)

# + Summary_Report_Curated_Data
'''
Provide resource links for each climate hazard relevant to system components, to develop a curated list of climate resources that are specific to the needs identified by the user.
'''
class Summary_Report_Curated_Data(param.Parameterized):

    # Access information provided by user earlier in pipeline to provide a summary
    system_category = param.String()
    system_type = param.String()
    system_lifespan = param.Tuple()
    system_location = param.List()
    vulnerability_matrix = param.DataFrame()

    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_category", "system_type", "system_lifespan", "system_location", "vulnerability_matrix")
    
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
            .sort_values("vulnerability", ascending=False))

        self.prioritized_components = (
            self.vulnerability_matrix.groupby("system_components")["vulnerability"]
            .sum()
            .to_frame()
            .sort_values("vulnerability", ascending=False))

        self.t3=[]
        self.t3.append(pn.pane.Markdown(
            "## Here is a list of climate information and data resources, curated for you.\n"
            "This list is based on the hazards *you* identified, and is ranked in terms of their impact on your "+ self.system_type
            + " - according to your own assessment.  Most influential hazards appear first.  "
            +"If you expand each hazard item, you will find a go-to list of best-in-class climate information and data resources, curated by the Canadian Centre for Climate Services.  "
            +"Explore these resources first, to kick-start your understanding of present and future climate  impacts to your "
            + self.system_type+ "!"))

        self.dT = dt.date.today().year - self.system_lifespan[0].year
        if self.dT > 20.0:
            self.t3.append(
                pn.pane.Markdown(
                    "**Pro tip: It looks like your " + self.system_type + " is already " + str(int(self.dT)) + " years old.  "
                    + "Climate has already changed quite a bit in this time!  In your climate change planning, be sure to consider that your "
                    + self.system_type + " has already experienced a significant amount of change in the severity and frequency of hazards you've identified!**"))

        # Build list of hazards, that start with biggest hazards.  Make text red for higher impact hazards; scale to blacker and smaller.
        self.hazards = self.prioritized_hazards.index.values.tolist()
        self.fontsize = np.linspace(15, 10, num=len(self.hazards))
        self.fontcolor = [(r, 0, 0) for r in np.linspace(255, 0, num=len(self.hazards))]
        self.statement_list = []

        with open(os.path.join(general_input_directory, "master_hazard_database.json"), "r") as j:
            self.full_hazards_dict = json.loads(j.read())

        self.hazard_panels = []  # list of per hazard WidgetPanes

        for n, h_formatted in enumerate(self.hazards):
            h = h_formatted.replace("\n", " ")
            self.hazard_details = []  # list of items for each hazard WidgetPane
            if h in self.full_hazards_dict:
                # set header image
                self.fname = os.path.join(
                    general_input_directory,
                    "images",
                    "cropped_hazard_images",
                    h.replace(" ", "-") + ".jpg")
                self.hazard_jpg_pane = pn.pane.JPG(
                    self.fname, width=int(plot_width * 0.9))  # this has to have same name as hazard, with exception of spaces (which get replaced by '-' as per replace code)width=plot_width,

                # build up hazard-specific reporting box
                self.hazard_details.append(self.full_hazards_dict[h]["impact_statement"][
                    system_category.replace(" ", "_")]+ "  " + self.full_hazards_dict[h]["direction_statement"] +
                    self.full_hazards_dict[h]["direction_confidence"] + "  " + self.full_hazards_dict[h]["magnitude_confidence"] +
                    "**Click below to explore these best-in-class, Canadian-focussed " + h + "/climate change resources.**")

                for resource, resource_details in self.full_hazards_dict[h]["resources"].items():
                    self.resource_items = []
                    self.resource_items.append(
                        "Information and/or data on "
                        + h
                        + " is available from "
                        + resource_details["source"]
                        + ".  This "
                        + resource_details["type"]
                        + " "
                        + resource_details["description"])
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
                            + "s&sector=")
                    elif resource_details["source"] == "PCIC Design Value Explorer":
                        self.url= resource_details["url"] + resource_details["var"]
                    else:
                        self.url = resource_details["url"]
                    self.resource_items.append(
                        "### Click here to explore this information in more detail: ["
                        + resource+ "](" + self.url + '){:target="_blank"}')
                    self.hazard_details.append(
                        pn.WidgetBox(*self.resource_items, width=int(plot_width * 0.9)))
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
                css_classes=["custom-box"]),**panel_options)

# + Next_Steps
'''
Next steps stage
This stage serves a jumping off point for users to understand what their next steps are. This text is intended to align users to basics of risk assessment, followed by adaptation (if their risk assessment thinking indicates that an 'unacceptable' risk threshold will be crossed.
'''

class Next_Steps(param.Parameterized):

    system_category = param.String()
    # State dependence of code in this Pipeline block, to previously-entered information from previous blocks.
    @param.depends("system_category")
    
    def __init__(self, **params):
        super().__init__(**params)
        
        self.jpg_pane = pn.pane.JPG(
            os.path.join(general_input_directory, "images/report.jpg"),
            width=plot_width)
        
        self.system_input_directory = system_category.replace(" ", "_") + "_inputs"
        # Open general resources database and read each resource to dictionary
        with open(os.path.join(self.system_input_directory, "next_steps.txt")) as f:
            self.lines = f.readlines()
        self.lines = "\n".join(self.lines)

    def panel(self):
        return pn.Column(
            self.jpg_pane,
            pn.pane.Markdown(self.lines),
            **panel_options)

# + Build pipeline

debug_flag = True
pipeline = pn.pipeline.Pipeline(inherit_params=True, debug=debug_flag)
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
        name="Decision Support Tool")
else:
    DST_core = pn.Column(
        pipeline.stage,
        pipeline.buttons,
        width=plot_width,
        height=plot_height,
        name="Decision Support Tool")

# + Deploy
main_panel_widget = pn.widgets.RadioBoxGroup(name="", 
                                          options=['Welcome',
                                                   'Knowledge Checklist',
                                                   'Decision Support Tool'])

@pn.depends(main_panel_widget_value=main_panel_widget)
def main_panel(main_panel_widget_value):
    if main_panel_widget_value == 'Welcome':
        return welcome
    elif main_panel_widget_value == 'Knowledge Checklist':
        return knowledge_checklist
    elif main_panel_widget_value == 'Decision Support Tool':
        return DST_core
    
template.sidebar.append(pn.Column(main_panel_widget))
template.main.append(pn.Column(main_panel))
template.open_modal()
template.servable()
template.show()
