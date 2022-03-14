
import json
from geopy.geocoders import Nominatim
import webbrowser
from textart import draw_stuff
import requests
import numpy as np
from sklearn.neighbors import BallTree
import pandas as pd
from collections import Counter


dT_levels=['+0.5C','+1.0C','+1.5C','+2.0C','+2.5C','+3.0C','+3.5C']

CRBCPI_data={dT_levels[0]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+0.5C_NBCC.xls"),
             dT_levels[1]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+1.0C_NBCC.xls"),
             dT_levels[2]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+1.5C_NBCC.xls"),
             dT_levels[3]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+2.0C_NBCC.xls"),
             dT_levels[4]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+2.5C_NBCC.xls"),
             dT_levels[5]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+3.0C_NBCC.xls"),
             dT_levels[6]:pd.read_excel("https://climate-scenarios.canada.ca/files/buildings_report/Appendix_1.2_NBCC/Appendix1.2_+3.5C_NBCC.xls")}

CRBCPI_dT_to_time=pd.DataFrame([[2023,2023,2023,2023],
                                [2035,2046,2046,np.nan],
                                [2047,2070,2070,np.nan],
                                [2059,2087,np.nan,np.nan],
                                [2069,np.nan,np.nan,np.nan],
                                [2080,np.nan,np.nan,np.nan],
                                [2090,np.nan,np.nan,np.nan]],
                                index=dT_levels,columns=['RCP8.5','RCP6.0','RCP4.5','RCP2.6'])

#SETUP FUNCTIONS

# Quick function to error-catch non-standard y/n responses
def yes_or_no(question):
    while True:
        reply = str(input(question+' (y/n): ')).lower().strip()
        if reply != "":
            if reply[0] == 'y':
                return True
            if reply[0] == 'n':
                return False
            else:
                print("Whoops - please enter 'y' or 'n'.")
                
# Quick function to error-catch non-standard y/n/u responses
def yes_or_no_unsure(question):
    while True:
        reply = str(input(question+' (y/n/u): ')).lower().strip()
        if reply != "":
            if reply[0] == 'y':
                return 1
            if reply[0] == 'n':
                return 0
            if reply[0] == 'u':
                return 2
            else:
                print("Whoops - please enter 'y' , 'n' or 'u'.")                

#%%
          
screen_clear="\033[H\033[J"

print(screen_clear)
draw_stuff("BVAT")
print ("\nREADY PLAYER ONE")
input("\nPress Enter to Begin...")


print(screen_clear)
print("WELCOME TO CLIMATEDATA.CA's INTERACTIVE VULNERABILITY ASSESSMENT TOOL FOR BUILDINGS")
print("\n")
print("This interactive tool is designed for engineers, architects, planners, and other professionals in the buildings sector.\n")
print("\nThe tool has two main goals:\n")
print("   GOAL 1 - Gain a better sense of how to select useful climate change information for building-specific climate change considerations, including risk assessments and long term planning.")
print("   GOAL 2 - Help find some  useful climate change information for your building")
print("\n")
print("You will be guided through the following 5 Steps:\n")
print("   STEP 1 - Provide basic information about your building")
print("   STEP 2 - Develop an inventory of building components and systems")
print("   STEP 3 - Identify the local weather and climate hazards that may matter for your building")
print("   STEP 4 - Explore the impacts of weather and climate hazards on building components and systems")
print("   STEP 5 - Summary report and next steps")
print("\nThis tool helps you select and source relevant climate change information for your building planning process.")
print("At the end of this tool's process, you will receive some important next steps to consider.\n")
print("\nThis process should take around 20 minutes to complete.")
input("Press Enter to continue...")

print(screen_clear)

print("CLIMATE DECISION SUPPORT TOOL DISCLAIMER AND RELEASE OF LIABILITY")
print('\nThis tool supports users in learning how to identify a subset of appropriate climate change information for building planning.  However, it is not an offical engineering design tool.  Users of this tool accept full responsibilty for expert judgement and professional standard of care in applying this and other climate change information to detailed project planning and engineering.  The authors of this tool accept no responsibilty for damage resulting from misuse of the datasets provided by this tool during project planning or execution.')
print('\nThis tool endeavours to summarize a selection of important building hazards and describe changes to these hazards resulting from climate change.  However, some hazards do not have reliable future information available, to the best knowledge of the authors of this tool, at this time.  The authors take no responsibility for negligent omission of consideration of such hazards in project planning or execution.')
print('\nThis tool is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and non infringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the tool.')
print("\nIn short, please combine the use of this tool with personal judgement, and full acceptance of liability and professional standard of care.")
input("\nPress Enter to begin...")

#%%
# CHECK USER'S BACKGROUND KNOWLEDGE
print(screen_clear)
draw_stuff("books")
print("\nCORE KNOWLEDGE CHECK-LIST\n")
print("Before we begin, it is important that you are comfortable with certain definitions and concepts related to climate models and future climate data.")

if yes_or_no("The amount of climate change we experience in the future depends on many factors, most notably future global emissions of greenhouse gases. Are you familiar with future climate scenarios, including the difference between RCP2.6, RCP4.5, and RCP8.5?\n >") is False:
    print("Here is a very short video that will quickly bring you up to speed. It is hightly recommended that you watch it before conitnuing.")
    url="https://climatedata.ca/resource/introduction-to-decision-making-using-climate-scenarios/"
    webbrowser.open(url,new=2,autoraise=False)

if yes_or_no("Climate data is best represented using a range of values, rather than a single number. Do you understand why this is the case?\n >") is False:
    print("Here is a very short video explaining why users should look at a range of model projections, rather than focus on a single value. It is highly recommeded that you take the time to watch it.")
    url="https://climatedata.ca/resource/understanding-ranges-in-climate-projections/"
    webbrowser.open(url,new=2,autoraise=False)
    
if yes_or_no("Have you used ClimateData.ca before, and are comfortable with navigating the map?\n>") is False:
    url="https://climatedata.ca/resource/how-to-navigate-variable-maps/"
    webbrowser.open(url,new=2,autoraise=False)
    
if yes_or_no("Are you familiar with the Government of Canada Climate-Resilience Buildings and Core Public Infrastructure program?") is False:
    url="https://www.infrastructure.gc.ca/plan/crbcpi-irccipb-eng.html"
    webbrowser.open(url,new=2,autoraise=False)

if yes_or_no("Are you familiar with the Government of Canada Climate Lens program?") is False:
    url="https://www.infrastructure.gc.ca/pub/other-autre/cl-occ-eng.html"
    webbrowser.open(url,new=2,autoraise=False)
    
if yes_or_no("Are you familiar with the Federation of Canadian Municipalities for Climate Innovation program?") is False:
    url="https://fcm.ca/en/programs/municipalities-climate-innovation-program/climate-change-adaptation"
    webbrowser.open(url,new=2,autoraise=False)    
     

input ("Press ENTER to continue...")
#%%
### PIEVC Step 1: PROJECT DEFINITION ###
print(screen_clear)
print("\n")
print("STEP 1: BASIC PROJECT DEFINITION")
print("\n")
draw_stuff('house')
print("\n")

print("What type of building are you designing, building, or operating?\n") # FYI
building_type=input(">")

if yes_or_no("Is this an existing building?\n >"):
    building_stage="existing"
    construction_date=input("When was your "+building_type+" constructed?\n >")
    if int(construction_date) < 2000:
        old_construction=True
        #TODO: based on old_construction flag, add a comment in final report generator.
        print("It looks like your building is at least 20 years old already!  Climate has changed significantly since then - you should assess whether your building is already at risk from change climate conditions!")
else:
    building_stage=input("OK, so what stage of the design/build process are you in?\n >")
    construction_date=input("And what's the anticipated final year of construction? \n >")

#TODO: see if possible to auto-specify standard design lives from NBCC or CSA S478 Building Durability

print("\nWhat is your "+building_type+"'s intended design life in years (intended service life before a major intervention is required (retrofit, modernize, demolish, etc.)?")
print("\nType 'help' if you are unsure how to determine your building's approximately design life.")
design_life=input(">")
while design_life=='help':
    print("You can find a description of standard building design lives in CSA S478. I'll open that resource for you now.")
    url="https://www.csagroup.org/store/product/CSA%20S478%3A19/?gclid=CjwKCAiAmrOBBhA0EiwArn3mfGwIl8Ll8Oa0BkkEPJgzrITQ8GeDn3M1tHu4inRLTxvgtjy3DHzkfRoCfeMQAvD_BwE"
    webbrowser.open(url,new=2,autoraise=False)
    print("\nWhat is your "+building_type+"'s intended design life in years (intended service life before a major intervention is required (retrofit, modernize, demolish, etc.)?")
    print("\nType 'help' if you are unsure how to determine your building's approximately design life.")
    design_life=input(">")
design_year=int(construction_date) + int(design_life)
decade=int(round(design_year,-1))
if decade <2030:
    print("Looks like your "+building_type+"'s expected design life is relatively short!\n")
    print("For relatively short-term design lives, you may want to consider applying recent observational weather and climate information, instead of future projections from climate models.\n")
    print("However, be careful using only past observations – some impacts are already quite different due to ongoing climate change. You may need expert opinion for this or use of climate model simulation resuts centred on the present day.\n")
    print("Keep these thoughts in mind in the context of your building's design life, as you continue with this exercise.\n")
if decade > 2070:
    if decade > 2100:
        print("NOTE: Just a heads up, I only have climate data that goes until the year 2100. Your building's design life exceeds this time frame. I'll just stick to showing you data from the 30-year period spanning 2071-2100.")
    decade=2070
    
# %%
## Get location

#if yes_or_no("Would you like me to look up your location from your latitude and longitude for you?\n >"):
geolocator = Nominatim(user_agent="example")
loc_address=str(input("Location of building site (full or partial address)? \n >"))
location = geolocator.geocode(loc_address)
latitude = location.latitude
longitude = location.longitude  

if not 41. <= latitude <= 84.:
    raise TypeError("Looks like your latitude is outside of Canada.  Can you re-check this?\n")
if not -142. <= longitude <= -.52:
    raise TypeError("Looks like your longitude is outside of Canada.  Can you re-check this?\n")

#find nearest CPI point (use CRBCPI_i to index climate data for this point, from CRBCPI data dictionary)
#Set up nearest neighbour search on the sphere
lat=np.deg2rad(CRBCPI_data["+0.5C"]["Latitude"].values)
lon=np.deg2rad(CRBCPI_data["+0.5C"]["Longitude"].values)
ball=BallTree(np.vstack((lat,lon)).swapaxes(1,0),metric="haversine")
CRBCPI_distance,CRBCPI_i=ball.query(np.deg2rad([[latitude,longitude]]),k=1)
CRBCPI_i=CRBCPI_i[0][0]


print("Your latitude is..." + str(latitude))
print("Your longitude is..." + str(longitude))

elev=float(input("\nHow far above sea level is your building (in meters)? \n >"))

## User's profession
professions=['Engineer','Architect','Owner/operator','Regulator','OTHER']
print("\nAnd finally, which of the following best describes your profession?\n")
counter=1
for p in professions:
    print("  " + str(counter) + ". " + p)
    counter+=1
userprof=input("Enter a number from 1 to " + str(counter-1) + " >")
users_profession=professions[int(userprof)-1]
if users_profession == "OTHER":
    users_profession=input("Please type in your profession >")


# %%
### PIEVC Step 2: DATA GATHERING ###

# TODO: 

print(screen_clear)
print("\n")
print("STEP 2: INVENTORY OF BUILDING SYSTEMS AND COMPONENTS")
print("\n")
print("Understanding climate change impacts to your building requires first developing a high-level catalog of your building's systems and components.")
print("\nWe'll use this catalog to assess how climate change could impact important aspects of your building in different ways.")
print("\nAnswer 'yes' to include any of the following Level 1 Major Group Elements in the analysis.")
print("\nYou will then be asked to identify Level 2 Components you wish to include in the analysis. Note, you'll need about 2 minutes of thinking per component, later in the process: ")

# Initialize a list of building components that the user will grow interactively.
# This list will store component-specific hazards.
building_component_dict={}

# Load the master list of building components, from which a subset of user-specific building hazards is built.
with open('master_building_component_database.json', 'r') as j:
    master_building_component_dict = json.load(j)

for c in master_building_component_dict:
    if yes_or_no(c + " - " + master_building_component_dict[c]["description"]):
        for g in master_building_component_dict[c]["group"]:
            if yes_or_no("   " + g):
                building_component_dict[g]={"hazards":{}} #create a new building component dictionary item, containing a dictionary with an empty 'hazards' key

# Prompt the user to define the components of their building.  This list can be as long as needed.
print("\nAre there any other major structural or system components of your building and property that you'd like to include?\n")
print("For this exercise, let's try to keep to a high level here (12-15 components, maximum!).   Type 'done' when done.\n")

while True:
    token=input("->")
    if token != "done":
        building_component_dict[token]={"hazards":{}}  #create a new building component dictionary item, which itself is an empty dictionary
    else:
        break 

#%%

#STEP 3: UNDERSTAND HISTORICAL CLIMATE HAZARDS IN REGION
print(screen_clear)
print("\n")
print("STEP 3: WEATHER HAZARDS AND CLIMATE DATA")
print("\n")
draw_stuff("clouds")
print("\nNext, we need to identify the kinds of weather hazards your building's region is, or may become, susceptible to.")
print("\nYou'll contrast these weather hazards against your building components, to identify the hazards that appear most important, and help me curate a list of good information for you.")
print("\n")
input("Press ENTER to continue...")

# Initialize a blank list of weather hazards that the user will grow following a series of y/n questions:
hazard_dict={}

# Load the master list of climate hazards, from which a subset of user-specific building hazards is built,
with open('master_hazard_database.json', 'r') as j:
    master_hazard_dict = json.load(j)

print("\n")
#hard coding this option for now
do_vulnerability_ranking = True #yes_or_no("As part of this step, would you like to consider the relative level of vulnerability each building component has for each hazard, on a 'quick and dirty' 1-10 scale (1=trivially; 10=extremely)?  While this might make this exercise a few minutes longer, it will help me prioritize what climate information may be most important for you.")

#Dynamically generate a customized hazard_dict based on user prompts.

def provide_number(query,lower,upper):
    while True:
        n = input(query)
        if n.isnumeric() and lower <= int(n) <= upper:
            return int(n)
        else:
            print("     Whoops - please enter a number between "+str(lower)+"-"+str(upper)+".")

def update_componentwise_hazard_list(h,building_component_dict,do_vulnerability_ranking):
            for component in building_component_dict.keys():
                if yes_or_no(("Would your " + building_type.upper() + "'s " + component.upper()+ " be damaged during " +h.upper()+ " events? ->")) is True:
                    building_component_dict[component]["hazards"][h] = np.nan
                    if do_vulnerability_ranking:
                        building_component_dict[component]["hazards"][h] = provide_number("From 1 (slight) to 10 (complete collapse/loss), rank potential damage to "+component+" caused by "+h.upper()+" -> (1-10):",1,10)
            return building_component_dict
        
def resource_help(h, hazard_dict):
    print("\nOkay thanks for telling me that you were unsure. I have some resources that might help. Take a look, then I'll ask the question again.\n")
    if hazard_dict[h]["resources"]: #if there is actually a dictionary of resources available, proceed -
        for resource,resource_details in hazard_dict[h]["resources"].items():
            print("\n")
            print("    --->Resource: "+resource.upper()+"<---")
            print("    Information on "+h.upper()+" is available from "+resource_details["source"]+".")
            print("    This "+resource_details["type"]+" "+resource_details["description"])
            if resource_details["source"]=="ClimateData.ca":
                if yes_or_no("    Would you like me to open a map in your web browser, where you can access data for your location for different future scenarios?"):
                    url=(resource_details["URL"]+str(latitude)+","+str(longitude)+",12&geo-select=&var="+resource_details["var"]+"&var-group="+resource_details["group"]+"&mora="+resource_details["season"]+"&rcp=rcp85&decade="+str(decade)+"s&sector=")
                    webbrowser.open(url,new=0,autoraise=False)
            elif resource_details["source"]=="The Climate Resilient Buildings and Core Public Infrastructure Project":
                location=CRBCPI_data["+0.5C"]["Location"][np.squeeze(CRBCPI_i)]
                proximity="{x:.0f}".format(x=np.squeeze(CRBCPI_distance)*6378.) # convert distance from radians to kilometers, format for rounded-value printing
                print("    In addition to regional information, it appears there is data available for "+location +", around "+proximity+" km away from your  site.")
                if yes_or_no("    Would you like me to open the CRBCPI report section on "+resource+", where you can read more about how to use this information?"):
                    url=(resource_details["URL"])
                    webbrowser.open(url,new=0,autoraise=False)
            else:
                if yes_or_no("    Would you like me to open a website where you can read more about this?"):
                    url=(resource_details["URL"])
                    webbrowser.open(url,new=0,autoraise=False)
    else:
        print("    Sorry, I don't have any information for: "+h.upper()+" quite yet.  Please give the CCCS Service Desk a call (1-833-517-0376) to request some one-on-one help!")
        if yes_or_no("    Would you like me to open the CCCS Service Desk website?"):   
            url=("https://climate-change.canada.ca/support-desk/Index")
            webbrowser.open(url,new=0,autoraise=False)
                

for h in master_hazard_dict.keys():
    his_freq=0
    fut_freq=0
    his_unsure=0
    fut_unsure=0
    if h != "other":
        print(screen_clear)
        #draw_stuff(h)
        print(h.upper())
        print("---------------------------------------------------------------------------")
        print("\n"+master_hazard_dict[h]["impact_statement"])
        print("\n"+master_hazard_dict[h]["direction_statement"])
        print("---------------------------------------------------------------------------")
        his_question = yes_or_no_unsure("Histrically, is your " + building_type.upper() + " exposed to potentially damaging " + h.upper() + " events? (Y=yes, N=no, U=unsure)")
        if his_question != 0:
            hazard_dict[h]=master_hazard_dict[h]
            while his_question == 2:
                his_freq=0
                resource_help(h, hazard_dict)
                his_question = yes_or_no_unsure("So, what do you think now? Histrically, is your " + building_type.upper() + " exposed to potentially damaging " + h.upper() + " events? (Y=yes, N=no, U=unsure)")
                if his_question == 2:
                    print("\nThat's okay if still you don't know. Let's assume the answer is yes for now, and we can come back to this later.")
                    his_question = 1
                    his_unsure = 1
            if his_question == 1:
                print("\nBased on your experience, approximately how often does a potentially damaging " + h.upper() + " event occur?")
                print("1. multiple times per year")
                print("2. once per year")
                print("3. once every 2 to 5 years")
                print("4. once every 5 to 10 years")
                print("5. less than once every 10 years")
                his_freq=provide_number("Enter a number from 1 to 5 >",1,5)
                fut_quest="\nDo you expect damaging " + h.upper() + " events will become MORE frequent as the climate continues to change? (Y=yes, N=no, U=unsure"
                fut_freq=yes_or_no_unsure(fut_quest) 
            else:
                his_freq=999 #code to note that this hazard does occur historically
                fut_quest="\nWhat about in the future? Do you think your "+building_type+" could experience "+h.upper() + " events because of climate change or other factors? (Y=yes, N=no, U=unsure)"
                fut_freq=yes_or_no_unsure(fut_quest)
            while fut_freq ==2:
                resource_help(h, hazard_dict)
                fut_freq=yes_or_no_unsure("I'll aks my question one more time: " + fut_quest)
                if fut_freq == 2:
                    fut_freq=1
                    fut_unsure=1
                    print("\nThat's okay if you still don't know. It can be very difficult to know how future weather hazards will change in the future. Let's just assume the answer is yes for now; better safe than sorry!")
            damage_flag=1
            if his_freq == 999:
                if fut_freq == 0:
                    #does not occur at all
                    damage_flag=0
            if damage_flag==1:
                print("\nFinally, I need to understand how this hazard can potentially damage your "+building_type.upper()+".")
                building_component_dict=update_componentwise_hazard_list(h,building_component_dict,do_vulnerability_ranking)   
                hazard_dict[h]["his_freq"]=his_freq
                hazard_dict[h]["fut_freq"]=fut_freq
                hazard_dict[h]["his_unsure"]=his_unsure
                hazard_dict[h]["fut_unsure"]=fut_unsure
        else:
            fut_quest="\nWhat about in the future? Do you think your "+building_type+" could experience "+h.upper() + " events because of climate change or other factors? (Y=yes, N=no, U=unsure)"
            emerging=yes_or_no_unsure(fut_quest)
            his_freq=999  #code to note that this hazard does occur historically
            if emerging != 0:
                hazard_dict[h]=master_hazard_dict[h]
                while emerging == 2:
                    resource_help(h,hazard_dict)
                    emerging=yes_or_no_unsure("I'll ask my question one more time: " + fut_quest)
                    if emerging == 2:
                        emerging=1
                        fut_unsure=1
                        print("\nThat's okay if you still don't know. It can be very difficult to know how future weather hazards will change in the future. Let's just assume the answer is yes for now; better safe than sorry!")
                    fut_freq=emerging
                if emerging == 1:
                    fut_freq=emerging
                    print("\nI need to understand how this hazard can potentially damage your "+building_type+".")
                    building_component_dict=update_componentwise_hazard_list(h,building_component_dict,do_vulnerability_ranking)
                    hazard_dict[h]["his_freq"]=his_freq
                    hazard_dict[h]["fut_freq"]=fut_freq
                    hazard_dict[h]["his_unsure"]=his_unsure
                    hazard_dict[h]["fut_unsure"]=fut_unsure 
            
    else:
        print(screen_clear)
        print("ANYTHING I FORGOT?")
        print("---------------------------------------------------------------------------")
        print("\nAre there any other weather hazards you want to tell me about before we continue?  Please enter these hazards below (or type 'done' if you are done)")
        while True:
            token=input("->")
            if token != "done":
                hazard_dict.update({token:master_hazard_dict[h]})  #Get user-inputted hazard and assign default 'other' hazard information to new, user-defined hazard.  
                building_component_dict=update_componentwise_hazard_list(token,building_component_dict,do_vulnerability_ranking)    
            else:
                break
print(screen_clear)


# %% 

print(screen_clear)
print("\n")
print("STEP 4: SUMMARY REPORT")
print("\n")

print("IN CONSIDERING POTENTIAL CLIMATE HAZARDS FOR EACH COMPONENT OF YOUR BUILDING, YOU HAVE STARTED ON YOUR WAY TO INTEGRATE CLIMATE CHANGE CONSIDERATIONS INTO BUILDING PLANNING.\n")
print("LET ME SUMMARIZE YOUR RESULTS, AND TRY TO POINT YOU TO SOME POTENTIAL SOURCES OF GOOD PAST AND FUTURE CLIMATE INFORMATION THAT IS RELEVANT TO YOUR BUILDING,\n")

sep="\n->"

# Estimate component(s) with most/least vulnerabilities by summing up numerical rankings for all hazards for each component.
aggregate_hazard_list=Counter()
for component,per_component_hazard_dict in building_component_dict.items():
    building_component_dict[component]["total_hazard_sum"]=0
    for hazard,rankval in per_component_hazard_dict["hazards"].items():
        building_component_dict[component]["total_hazard_sum"] += rankval #This just adds 'NaNs' to the sum, if do_vulnerability_ranking == False
        aggregate_hazard_list.update([hazard])

# %%
if do_vulnerability_ranking:
    # iterate over building components, and get indice list corresponding to most-hazard-impacted, to least.
    ranks=[]
    for component in building_component_dict:
        ranks.append(building_component_dict[component]["total_hazard_sum"])
    sortrank=sorted(ranks, reverse=True)
    
    j = 0
    print("\n")
    print("Frist, this is what I heard from you in regards to historical and future weather hazards in your region:\n")
    for h in hazard_dict:
        j+=1
        summary_statement=""
        components_impacted = ""
        #historical statement
        if hazard_dict[h]["his_unsure"] == 0:
            if hazard_dict[h]["his_freq"] != 999:
                if hazard_dict[h]["his_freq"] == 1: 
                    his_choice ="frequenly, potentially multiple times per year"
                elif hazard_dict[h]["his_freq"] == 2:
                    his_choice="frequently, approximatley once per year"
                elif hazard_dict[h]["his_freq"] == 3:
                    his_choice="roughly once every 2 to 5 years"
                elif hazard_dict[h]["his_freq"] == 4:
                    his_choice="relatively infrequently, roughly once every 5 to 10 years"
                elif hazard_dict[h]["his_freq"] == 5:
                    his_choice="infrequently, less than once every 10 years"
                summary_statement+=(str(j) + ". Based on your experience, " + h.upper() + " events occur " + his_choice + ".")
            elif hazard_dict[h]["his_freq"] == 0:
                summary_statement+=(str(j) + ". You indicated your were unsure if " + h.upper() + " occurs historically in your region. I hope the resources I supplied you with helped." )
            elif hazard_dict[h]["his_freq"] == 999:
                summary_statement+=(str(j) + ". You indicated that, historically, " + h.upper() + " events do not occur in your region.")
        else:
            summary_statement+=(str(j) + ". You indicated your were unsure if " + h.upper() + " occurs historically in your region, even after reviewing the resources I had on file." )
        
        #future statement
        if hazard_dict[h]["fut_unsure"] == 0:
            if hazard_dict[h]["fut_freq"] == 0:
                summary_statement+=(" However, you indicated too that, based on what you've read or heard, " + h.upper() + " events are NOT likely to occur more frequently in the future. To me, this reads: if you are well adapted to this hazard now, you might not need to do anything extra to account for " + h.upper() + " events in the future. But certaintly don't quote me on that!")
            elif hazard_dict[h]["fut_freq"] == 1:
                if hazard_dict[h]["his_freq"] != 999:
                    summary_statement+=(" Critically, you then indicated that " + h.upper() + " events are likely to occur MORE frequenlty in the coming decades due to climate change.")
                else:
                    summary_statement+=(" However, you then told me that " + h.upper() + " events could become an emerging hazard in the future due to climate change.")
            elif hazard_dict[h]["fut_freq"] ==2:
                summary_statement+=(" You indicated to me earlier that you were unsure whether " +h.upper()+" events will occur more frequently in the future. I hope the resources I supplied you with helped, but its all too often that we don't have all the answers about future hazards. Don't let this stop you.")
        else:
            summary_statement+=(" You indicated to me earlier that you were unsure whether " +h.upper()+" events will occur more frequently in the future. I hope the resources I supplied you with helped a bit, but its all too often that we don't have all the answers about future hazards. Don't let this stop you; proactive action in the face of uncertainty is key.")
       
        
        #sloppy, I know... pre-loop thorugh the dict to simply count the number of matching items. So I can do grammar below...
        c=0        
        for component,per_component_hazard_dict in building_component_dict.items():
            for rankval in per_component_hazard_dict["hazards"].items():
                if rankval[0]==h:
                    c=c+1
        cc=0
        for component,per_component_hazard_dict in building_component_dict.items():
            for rankval in per_component_hazard_dict["hazards"].items():
                if rankval[0]==h:
                    ranking=building_component_dict[component]["hazards"][h]
                    if ranking < 3:
                        damage="slight"
                    if ranking >= 3:
                        if ranking <= 5:
                            damage="light to medium"
                    if ranking > 5:
                        if ranking <= 7:
                            damage="medium to heavy"
                    if ranking > 7:
                        damage="potentially catastrophic"
                    cc=cc+1
                    if c > 2:  #list need commas
                        if cc < c:
                            components_impacted += damage + " damage to " + component + ", "    
                        else:
                            components_impacted += "and " + damage + " damage to " + component
                    elif c == 2:  #list doesn't need a comma, just an and
                        if cc < c:
                            components_impacted += damage + " damage to " + component
                        else:
                            components_impacted += " and " + damage + " damage to " + component
                    elif c == 1: #list only has one component, no comma and ands required ;)
                        components_impacted+=damage + " damage to " + component
                    
        if components_impacted == "":
            summary_statement+= (" I thought it was interesting to note that " + h.upper() + " events do not seem to impact your " + building_type.upper()+"'s components, so maybe this insn't a hazard you should focus on this time around.")
        else:
            summary_statement+=(" Importantly, " + h.upper() + " events can potentially impact your " + building_type.upper()+ " by causing " + components_impacted + ".")

        print("\n"+summary_statement)
        
    print("\nNext, based on your entries, I have tried to rank your building's components from MOST to LEAST vulnerable:\n")
    j = 0
    for i in range(len(sortrank)):
        if i+j < len(sortrank):
            flag = 0
            for component in building_component_dict:
                if building_component_dict[component]["total_hazard_sum"] == sortrank[i+j]:
                    if flag != 1:
                        print("  "+str(i+j+1)+".  "+component)
                    else:
                        print("  "+str(i+j+1)+". (tie)  " + component)
                        j += 1
                    flag = 1
    print("\nIt might make sense to focus most on understanding climate change risks to the components nearer the top of this list during your building planning work.")

l_sorted=aggregate_hazard_list.most_common()

max_len=min(3,len(l_sorted))
print("\nFinally, the top climate hazards that potentially impact the most components of you " + building_type.upper()+ " appear to be (in no specific order):\n")
for h in range(max_len):
    print("->"+l_sorted[h][0])
print("\nIt might make sense to focus most on these hazards during data gathering for your building planning work.\n")

input ("Press ENTER to continue")
print(screen_clear)

# %%

print("\n")
print("STEP 5: NEXT STEPS")
print("\n")

print("\n")
input("Let's summarize what you've done here - AND - what you still need to do to ensure your building's climate resiliency! (press ENTER to continue)\n")
input("1) You described your building's basics, including expected lifetime and major components... (press ENTER to continue)\n")
input("2) You identified some h present and future climate hazards for your region... (press ENTER to continue)\n")
input("3) You thought about which climate hazards could impact each of your building's components... (press ENTER to continue)\n")
input("4) You developed a summary that prioritized major hazards and identified some promising climate information for each one... (ENTER to continue)\n")
input("Your next tasks are: (ENTER to continue)\n")
input("5) Get this climate information and develop a tailored climate change summary report for your building... (ENTER to continue)\n")
input("6) Use this report to understand how the likelihood and severity of each hazard will change in the future... (ENTER to continue)\n")
input("7) Undertake impact, vulnerability or risk assessments for present and future conditions if you want to understand how these will change for each of your components over time due to climate change... (ENTER to continue)\n")
input("8) Consider developing adaptation plans and actions to ensure your building's resilience, now and in the future! (ENTER to continue)\n")

print("\n")
print("Well done, and good luck with using this climate information and training to increase your building's resilience to climate change!")
email_address=input("Enter your email address to receive a brief report that summarizes the results of this decision support tool!") #FYI
#TODO: generate an email or PDF-based send-out report.
input("When you're ready to say goodbye, press ENTER!")

print(screen_clear)
draw_stuff('wizard_end')
print ("POOF! ALL DONE")


#%%


    
