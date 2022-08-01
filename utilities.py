import os
import json
import panel as pn


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