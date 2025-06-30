# Fantasy-Environment-Generator
This project focuses on a Prompt Engineering and uses Gemini API. All code is written in Python and data is stored in JSON.
We can divide whole process into the 5 steps
## Step 1 - Iterate through JSON and choose properties
In the provided JSON there are categories that consist of properties.
For example we have:<br>
<pre><code>
  ...
  "Altitude/Elevation": [
      "Sea Level",
      "Lowlands",
      "Uplands",
      "Highlands",
      "Mountains",
      "High Plateau",
      "Subterranean",
      "Abyssal",
      "Floating Islands",
      "Sky-level"
    ],
  ...
</code></pre>
Where `Altitude/Elevation` is category and `Sea Level`, `Lowlands` , ... , `Sky-level` are properties. We iterate for the whole JSON and for each category we run `chooseProperty()`
## Step 2 - Use the model to create chance table
Now we will use the model to make a chance table that will tell us the most probable properties based on the given description. For example with the description: <br>
<pre><code>
Climate: Equatorial 
Foundational & Geological Parameters:
   Topography & Landforms: Volcanoes
   Altitude/Elevation: Lowlands, Sea Level
   Geology & Bedrock: Basalt
</code></pre>
and category:
<pre><code>
  ...
"Soil Type": [
      "Fertile Loam",
      "Rich Clay",
      "Sandy",
      "Silty",
      "Peat",
      "Chalky",
      "Saline",
      "Acidic",
      "Barren Rock",
      "Magically Enriched",
      "Cursed Earth",
      "Ash-covered",
      "Spore-choked",
      "Metallic Dust",
      "Glassy/Vitrified"
    ],
  ...
</code></pre>
Our chances will look like this:
<pre><code>
[
  { "value": "Ash-covered", "chance": 250 },
  { "value": "Barren Rock", "chance": 150 },
  { "value": "Magically Enriched", "chance": 120 },
  { "value": "Saline", "chance": 100 },
  { "value": "Acidic", "chance": 80 },
  { "value": "Rich Clay", "chance": 70 },
  { "value": "Fertile Loam", "chance": 60 },
  { "value": "Sandy", "chance": 50 },
  { "value": "Metallic Dust", "chance": 50 },
  { "value": "Glassy/Vitrified", "chance": 40 },
  { "value": "Silty", "chance": 30 },
  { "value": "Cursed Earth", "chance": 20 },
  { "value": "Spore-choked", "chance": 20 },
  { "value": "Peat", "chance": 5 },
  { "value": "Chalky", "chance": 5 },
  { "combination_value": 2 }
]
</code></pre>
where `combination_value` is the maximum properties we can combine, for example our soil can be `Ash-covered` and `Magically Enriched`. All chances will add up to 1000.
## Step 3 - Choose value and repeat
Now the program will just choose randomly a property based on the given chances, add it to the raw description and repeat until the end of JSON. When this happens it will save the text to `RawDescription.txt`.
## Step 4 - Make more detailed description
Now we give the model prompt to change our raw description to something easier to read and with more depth. This will save to `FinalDescription.txt`
## Step 5 - Convert it to HTML
We use the model again, this time to make a HTML website that has its text in two languages, English and Polish. This will save to `FinalDescription.html`
