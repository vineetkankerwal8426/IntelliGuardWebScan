from flask import Flask,jsonify,request
from flask_cors import CORS
import pickle
from pyppeteer import launch
import nest_asyncio
import asyncio
import nltk
import string
from nltk.stem import PorterStemmer
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from nltk.corpus import stopwords
import easyocr
from PIL import Image
from io import BytesIO
import time
 
app = Flask(__name__)
CORS(app)

model = pickle.load(open('model.pkl','rb'))
tfid = pickle.load(open('vectoriser.pkl','rb'))
categ_model = pickle.load(open('category_model.pkl','rb'))
categ_tfid = pickle.load(open('category_vectoriser.pkl','rb'))


def transform_text(text):
    # Convert the text to lowercase
    text = text.lower()

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Tokenize the text
    tokens = nltk.word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Stemming using Porter Stemmer
    porter = PorterStemmer()
    tokens = [porter.stem(word) for word in tokens]

    # Join the tokens back into a string
    processed_text = ' '.join(tokens)

    return processed_text



# Download NLTK resources (run only once)
nltk.download('stopwords')
nltk.download('punkt')


nest_asyncio.apply()

async def take_screenshot(url):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    # Navigate to the website
    driver.get(url)
    driver.maximize_window()
    driver.execute_script("document.body.style.zoom='80%'")  # Change the zoom level if needed

    # Wait for a short duration to allow content to load
    time.sleep(2)  # Increased wait time

    # Set the desired scroll height (adjust the value as needed)
    desired_scroll_height = 100

    # Set the scroll height using JavaScript
    driver.execute_script(f"window.scrollTo(0, {desired_scroll_height});")

    # Get the total height and width of the webpage
    total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
    total_width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
    
    # Set the initial scroll position
    current_scroll_position = desired_scroll_height

    # Set the viewport height to capture in each screenshot
    viewport_height = driver.execute_script("return window.innerHeight;")

    # Create an image to store the screenshot with full width
    full_screenshot = Image.new('RGB', (total_width, total_height))

    while current_scroll_position < total_height:
        # Take a screenshot of the current viewport
        screenshot = driver.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))

        # Paste the current screenshot into the full screenshot image
        full_screenshot.paste(screenshot, (0, current_scroll_position - desired_scroll_height))

        # Scroll down
        driver.execute_script(f"window.scrollTo(0, {current_scroll_position + viewport_height});")

        # Wait for a short duration to allow content to load
        time.sleep(0.5)  # Increased wait time

        # Update the scroll position
        current_scroll_position += viewport_height

    # Save the full screenshot with a custom filename
    full_screenshot.save('screenshot.png')
    driver.quit()
    reader = easyocr.Reader(['en'])
    results = reader.readtext('screenshot.png')
    # Concatenate all OCR results into a single string
    original_text = []
    for (_,text,_) in results:
        original_text.append(text)
    return original_text

    # Run the asyncio event loop
# url="https://www.amazon.in"
# asyncio.get_event_loop().run_until_complete(take_screenshot(url))



def predict(url):
    result = {}
    textList = asyncio.get_event_loop().run_until_complete(take_screenshot(url))
    trans_text=[]
    for i in textList:
        trans_text.append(transform_text(i))
    for i in range(len(textList)):
        vec = tfid.transform([trans_text[i]]).toarray()
        predict = model.predict(vec)
        if predict == 1:
            vec = categ_tfid.transform([trans_text[i]]).toarray()
            categ_predict = categ_model.predict(vec)
            category = ""
            if categ_predict==0:
                category += "forced action"
            elif categ_predict==1:
                category += "misdirection"
            elif categ_predict==2:
                category += "obstruction"
            elif categ_predict == 3:
                category += "scarcity"
            elif categ_predict == 4:
                category += "sneaking"
            elif categ_predict==5:
                category += "social proof"
            elif categ_predict ==6:
                category += "urgency"
            result[textList[i]] = category
        else:
            continue
    return result

@app.route('/',methods = ["POST"])
def home():
    data = request.json
    currentUrl = data.get("url",'')
    result = predict(currentUrl)
    return jsonify(result)

app.run()


