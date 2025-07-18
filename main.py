import google.generativeai as genai
import json
import random
import time
genai.configure(api_key="YOUR_API_KEY")


#Creates a cumulative chance table from a list of chances
def makeChanceTable(chanceList):
    chanceList = sorted(chanceList, key=lambda x: x[1])
    cumulative = 0
    newList = []
    for value, chance in chanceList:
        if chance == 0:
            continue
        cumulative += chance
        newList.append([value, cumulative])
    return newList
# Chooses a random property or properties from the given JSON string based on the chances provided
def chooseRandomProperty(data_string):
   
    # Extract the JSON string from the input data_string
    start_index = data_string.find('[')
    end_index = data_string.rfind(']') + 1
    if start_index == -1 or end_index == 0:
        return "None"
    json_string = data_string[start_index:end_index]
    data = json.loads(json_string)

    #Extract values, chances and combination value from the JSON to a list
    valuesAndChances = []
    combination_value = 1
    for item in data:
        if 'value' in item and 'chance' in item:
            valuesAndChances.append([item['value'], item['chance']])
        else:
            combination_value = random.randint(1,int(item['combination_value']))
    
    #Draw answer/s based on the chances
    answers = []
    for _ in range(combination_value):
        chancesList = makeChanceTable(valuesAndChances)

        random_value = random.randint(0, chancesList[len(chancesList) - 1][1] - 1)
        for i in range(len(chancesList)):
            if random_value < chancesList[i][1]:
                answers.append(chancesList[i][0])
                valuesAndChances = [x for x in valuesAndChances if x[0] != chancesList[i][0]]
                break
    return ', '.join(answers) if answers else "None"


def create_model(model_name="models/gemini-2.5-flash", temperature=1.0, top_p=0.95, max_tokens=4096):
    generation_config = genai.types.GenerationConfig(
        temperature=temperature,
        top_p=top_p,
        max_output_tokens=max_tokens,
    )
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config
    )

def chooseProperty(data, description):
    # Wait for a few seconds to avoid rate limiting
    time.sleep(4.5) 

    prompt = """
Im creating a environment for a fantasy world and i need your help distributing probability chances. Here is the current description of the world \n""" + description + """
I need you to create a probability table based on the given description and new properties that is logically consistent with the current description of the world. I want you to distribute the chances based on the probability property being coherent with the given description, meaning that the most probable properties will have the biggest chance. Also give me "combination_value" which is the number of maximum properties that can be present at once, meaning if it is possible to choose more than one property for the environment for example you could have a: snow and hail in cold environments, try to keep this value low and do not set it to more than >= 3.All chances should add to 1000, if there is no chance for property to occur set its chance to 0 . You should only answer in the JSON and it should be in the following JSOM format:
[
    { "value": "property1", "chance": x1 },
    { "value": "property2", "chance": x2 },
    { "value": "property3", "chance": x3 },
    { "value": "property4", "chance": x4 },
    { "value": "property5", "chance": x5 },
    { "combination_value": "y1"},
]
New propoperties: """ + data
    #Model setup
    try:
        model = create_model(model_name="models/gemini-2.5-flash-lite-preview-06-17", max_tokens=1024) 
        response = model.generate_content(prompt)
        return chooseRandomProperty(response.text)
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return "None"

# Creates a final description based on the raw description provided
def createFinalDescription(rawDescription):
    prompt = """
You are a master world-builder and descriptive writer, akin to authors like Tolkien or Le Guin. Your task is to synthesize the following raw data points into a rich, evocative, and cohesive description of a fantasy environment.
Do not simply list the properties. Instead, weave them together into immersive prose, focusing on sensory details and the overall mood. Follow this specific structure for your description:
Structure to Follow:
Opening Paragraph: The First Impression. Start with a broad, atmospheric overview. Establish the most defining features of the environment, such as the perpetual twilight, the overall climate, and the first things a visitor would see and feel. Set the scene and the mood.
Paragraph 2: The Ground Beneath Your Feet. Focus on the landscape and geology. Describe the topography (swamps, lowlands) and what the ground is made of (basalt, petrified wood, silty soil). Seamlessly integrate the "Unnatural Formations" (Crystalline Spires) into this description, highlighting how they contrast or interact with the natural landscape.
Paragraph 3: Life in the Gloom - Flora. Describe the dominant plant life. Focus on the unique characteristics provided: the size and scale of the mangrove-like trees, their luminosity in response to sound or magic, and their reflective qualities. Mention the precipitation (spore fall, mist) as an interaction with the flora. Hint at the danger (poisonous properties).
Paragraph 4: Unseen Dangers - Fauna & Soundscape. Paint a picture of the animal life without necessarily showing the creatures directly. Describe the predator-heavy ecosystem. Convey the sense of being watched by solitary hunters and packs using camouflage and venom. Integrate the soundscape here—explain how the muffled sounds and erratic winds contribute to the tension and feeling of danger.
Paragraph 5: Whispers of the Past. Describe the signs of history and sapient influence. Weave in the presence of the ancient monoliths and the feeling that the land is currently inhabited by spirits and monsters rather than mortals. Connect this to the ancient, magical aura of the location.
Concluding Sentence: The Sensory Summary. End with a single, powerful sentence that encapsulates the core experience of the environment, focusing on a key sense like smell (petrichor, brine) or the overall feeling of the place.
Raw Data: \n"""+ rawDescription + """
"""

    #Model setup
    try:
        model = create_model(model_name="models/gemini-2.5-flash", max_tokens= 8194, temperature=1.1)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return "Error occurred during generation."
    
# Creates a self-contained HTML file with the generated description in English and Polish
def createHTMLVersion(description):
    prompt = """
You are an expert front-end developer and a skilled translator. Your task is to create a single, self-contained HTML file that displays a rich text description in two languages, English and Polish, with a functional language switcher.
Follow these instructions precisely:
1. HTML Structure:
Create a standard HTML5 document (<!DOCTYPE html>, <html>, etc.).
Inside the <body>, create a container for the language-switching buttons.
Below the buttons, create two main <div> containers for the text:
One for the English version with the ID english-text.
One for the Polish version with the ID polish-text.
The English text should be visible by default when the page loads. The Polish text should be hidden.
2. CSS Styling:
Embed the provided CSS code directly into the <head> section of the HTML file, inside <style> tags. Do not link to an external stylesheet.
3. Content and Translation:
Take the provided English Description and place it inside the <div id="english-text"> container. Use appropriate HTML tags for structure (e.g., <h1>, <h2>, <p>).
Translate the entire English description accurately into Polish.
Place the translated Polish text inside the <div id="polish-text"> container, using the same HTML structure as the English version.
4. JavaScript Functionality:
Create two buttons: one labeled "English" and one labeled "Polish".
Write the necessary JavaScript to control the visibility of the text containers.
Place this JavaScript inside a <script> tag at the end of the <body>.
When the "English" button is clicked: The <div id="english-text"> should be displayed, and the <div id="polish-text"> should be hidden.
When the "Polish" button is clicked: The <div id="polish-text"> should be displayed, and the <div id="english-text"> should be hidden.
Summary of Deliverable: A single .html file containing the HTML structure, the embedded CSS, the English and translated Polish text, and the JavaScript for the language switcher.
Assets to Use:
CSS Styles to Use:
Generated css
<style>
    body {
      background-color: #111;
      color: #e6e6e6;
      font-family: 'Georgia', serif;
      line-height: 1.7;
      padding: 2em;
      max-width: 900px;
      margin: auto;
    }
    h1 {
      color: #a8ffb0;
      font-size: 2.4em;
      border-bottom: 2px solid #a8ffb0;
      padding-bottom: 0.2em;
      margin-bottom: 0.6em;
    }
    h2 {
      color: #b4ffa6;
      font-size: 1.6em;
      margin-top: 2em;
    }
    p {
      margin: 1em 0;
    }
    .language-switcher {
      margin-bottom: 2em;
    }
    .language-switcher button {
      background-color: #333;
      color: #a8ffb0;
      border: 1px solid #a8ffb0;
      padding: 0.5em 1em;
      cursor: pointer;
      font-family: sans-serif;
      margin-right: 0.5em;
      transition: background-color 0.3s;
    }
    .language-switcher button:hover {
      background-color: #4c8a52;
    }
</style>
(Note: I have taken the liberty of adding styles for the language switcher buttons to ensure they match the aesthetic).
English Description to Use (and Translate):""" + description 

    #Model setup
    try:
        model = create_model(model_name="models/gemini-2.5-flash", temperature=1.1, max_tokens=8194)
        response = model.generate_content(prompt)
        filename = "FinalDescription.html"
        open(filename, "w", encoding="utf-8").write(response.text)
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
        lines = lines[1:-1]
        with open(filename, "w", encoding="utf-8") as file:
            file.writelines(lines)

    except Exception as e:
        print(f"An error occurred during generation: {e}")
        return "Error occurred during generation."
with open('EnvironmentData.json', 'r', encoding='utf-8') as plik:
    dane = json.load(plik)

possibleClimate = ["Equatorial","Tropical","Sub-tropical","Temperate","Sub-arctic","Arctic","Polar"]
description = f"Climate: {random.choice(possibleClimate)} \n"
allPropertySum = 0
propertiesDone = 0
for category in dane:
    for property in dane[category]:
        allPropertySum += 1

for category in dane:
    description += f"{category}:\n"
    for property in dane[category]:
        values = dane[category][property]  
        dataText = ", ".join(values)        

        print(f"Generating chances for property: {property} " + f"[{round((propertiesDone/allPropertySum)*100, 2)}]%")
        result = chooseProperty(dataText, description)
        description += f"   {property}: {result}\n"
        propertiesDone += 1
    description += "\n"

print("Creating final description...")
final_description = createFinalDescription(description)
open("FinalDescription.txt", "w", encoding="utf-8").write(final_description)
open("RawDescription.txt", "w", encoding="utf-8").write(description)
print("Converting to HTML file...")
createHTMLVersion(final_description)
print("HTML file created successfully.")
