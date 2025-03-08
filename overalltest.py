import streamlit as st
import pickle
import numpy as np
import google.generativeai as genai
import requests
import geocoder
from googleapiclient.discovery import build

# Google Generative AI API key
GOOGLE_API_KEY = "AIzaSyAxTL8jZcTB1yXW1Jetzm4tsJXL3tQPPp8"
genai.configure(api_key=GOOGLE_API_KEY)

# YouTube Data API Key
YOUTUBE_API_KEY = "AIzaSyAxTL8jZcTB1yXW1Jetzm4tsJXL3tQPPp8"

# GoMaps.Pro API Key
PLACES_API_KEY = "AlzaSyOTgb6lUK5tL0ZKH_EAYOoNCTWIfwjLE5j"

# Load the Model
try:
    with open("xgb_model_final.pkl", "rb") as file:
        model = pickle.load(file)
except FileNotFoundError:
    st.error("The model file 'xgb_model_final.pkl' is not found.")
    st.stop()

# Declare global variables (default values)
age = None
sex = None
on_thyroxine = None
on_antithyroid_meds = None
sick = None
pregnant = None
thyroid_surgery = None
I131_treatment = None
lithium = None
goitre = None
tumor = None
hypopituitary = None
psych = None
TSH = None
T3 = None
TT4 = None
T4U = None
FTI = None

def validate(value, min_val, max_val):
    return min_val <= value <= max_val

def predict_thyroid_condition():
    global age, sex, on_thyroxine, on_antithyroid_meds, sick, pregnant, thyroid_surgery
    global I131_treatment, lithium, goitre, tumor, hypopituitary, psych, TSH, T3, TT4, T4U, FTI
    st.markdown("<h1>Predict Thyroid Condition</h1>", unsafe_allow_html=True)
    with st.container():
        st.subheader("Enter Your Health Details:")
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    # Initialize validation flags
    valid_inputs = True
    age = st.number_input("Enter Age", value=1, format="%d")
    if not validate(age, 1, 100):
        st.error("Enter a value between 1-120")
        valid_inputs = False
    sex = st.selectbox("Select Sex", ["Male", "Female"])
    on_thyroxine = st.selectbox("Are you on thyroxine?", ["No", "Yes"])
    on_antithyroid_meds = st.selectbox("Are you on antithyroid medications?", ["No", "Yes"])
    sick = st.selectbox("Are you sick?", ["No", "Yes"])
    pregnant = st.selectbox("Are you pregnant?", ["No", "Yes"])
    thyroid_surgery = st.selectbox("Have you undergone thyroid surgery?", ["No", "Yes"])
    I131_treatment = st.selectbox("Have you received I131 treatment?", ["No", "Yes"])
    lithium = st.selectbox("Are you taking lithium?", ["No", "Yes"])
    goitre = st.selectbox("Do you have goitre?", ["No", "Yes"])
    tumor = st.selectbox("Do you have a tumor?", ["No", "Yes"])
    hypopituitary = st.selectbox("Do you have hypopituitary condition?", ["No", "Yes"])
    psych = st.selectbox("Do you have any psychological condition?", ["No", "Yes"])
    TSH = st.number_input("Enter TSH level in mu/lit", value=0.4, format="%.2f")
    if not validate(TSH, 0.1, 10.0):
        st.error("Enter a value between 0.1-10 mu/lit")
        valid_inputs = False
    T3 = st.number_input("Enter T3 level in pmol/lit", value=1.5, format="%.2f")
    if not validate(T3, 1.0, 10.0):
        st.error("Enter a value between 1.0-10.0 pmol/lit")
        valid_inputs = False
    TT4 = st.number_input("Enter TT4 level in nmol/lit", value=58.0, format="%.2f")
    if not validate(TT4, 30.0, 200.0):
        st.error("Enter a value between 30-200 nmol/lit")
        valid_inputs = False
    T4U = st.number_input("Enter T4U level", value=0.8, format="%.2f")
    if not validate(T4U, 0.1, 3.0):
        st.error("Enter a value between 0.1-3.0")
        valid_inputs = False
    FTI = st.number_input("Enter FTI level", value=6.0, format="%.2f")
    if not validate(FTI, 2.0, 20.0):
        st.error("Enter a value between 2.0-20.0")
        valid_inputs = False

    # Convert categorical fields to numerical
    encoded_values = {
        "Male": 0, "Female": 1,
        "No": 0, "Yes": 1
    }

    sex_encoded = encoded_values[sex]
    on_thyroxine_encoded = encoded_values[on_thyroxine]
    on_antithyroid_meds_encoded = encoded_values[on_antithyroid_meds]
    sick_encoded = encoded_values[sick]
    pregnant_encoded = encoded_values[pregnant]
    thyroid_surgery_encoded = encoded_values[thyroid_surgery]
    I131_treatment_encoded = encoded_values[I131_treatment]
    lithium_encoded = encoded_values[lithium]
    goitre_encoded = encoded_values[goitre]
    tumor_encoded = encoded_values[tumor]
    hypopituitary_encoded = encoded_values[hypopituitary]
    psych_encoded = encoded_values[psych]

    predict_button = st.button("Predict Thyroid Condition", disabled=not valid_inputs)
    if predict_button:
        try:
            input_data = np.array([[age, sex_encoded, on_thyroxine_encoded, on_antithyroid_meds_encoded,
                                    sick_encoded, pregnant_encoded, thyroid_surgery_encoded, I131_treatment_encoded,
                                    lithium_encoded, goitre_encoded, tumor_encoded, hypopituitary_encoded,
                                    psych_encoded, TSH, T3, TT4, T4U, FTI]])
            st.session_state.prediction_result = model.predict(input_data)[0]
            if st.session_state.prediction_result == 1:
                st.header("Predicted Condition: Hypothyroid")
            elif st.session_state.prediction_result == 2:
                st.header("Predicted Condition: Hyperthyroid")
            else:
                st.header("Predicted Condition: No Thyroid")
                st.subheader("Congratulations! You do not have any thyroid condition.")
        except Exception as e:
            st.error(f"An error occurred during prediction: {e}")

def generate_diet_plan():
    try:
        input_prompt = f"""I need a personalized weekly diet plan for a patient with Thyroid Condition: {'Hypothyroid' if st.session_state.prediction_result == 1 else 'Hyperthyroid'}. Here are their medical details:
        Age: {age}
        Sex: {sex}
        On Thyroxine: {on_thyroxine}
        On Antithyroid Medications: {on_antithyroid_meds}
        Sick: {sick}
        Pregnant: {pregnant}
        Thyroid Surgery History: {thyroid_surgery}
        I131 Treatment: {I131_treatment}
        Lithium Medication History: {lithium}
        Goitre: {goitre}
        Tumor History: {tumor}
        Hypopituitary Condition: {hypopituitary}
        Psychological Condition: {psych}
        TSH Level: {TSH} mu/lit
        T3 Level: {T3} pmol/lit
        TT4 Level: {TT4} nmol/lit
        T4U Level: {T4U}
        FTI (Free Thyroxine Index): {FTI}
        Requirements for the diet plan:
        1. The diet should support thyroid function based on the patient’s condition (Thyroid Condition: {'Hypothyroid' if st.session_state.prediction_result == 1 else 'Hyperthyroid'}).
        2. Include foods to consume and foods to avoid specific to their condition.
        3. Ensure proper nutrient balance, focusing on iodine, selenium, zinc, vitamin D, iron, and other essential nutrients.
        4. Provide a detailed daily meal plan for one week (Breakfast, Lunch, Dinner, and Snacks).
        5. Avoid any foods that may interfere with thyroid medications (e.g., goitrogens in raw cruciferous vegetables, excessive soy, caffeine, etc.).
        6. If the patient has specific conditions like pregnancy, history of thyroid surgery, or goitre, adjust recommendations accordingly."""
        with st.spinner("Generating diet plan..."):
            model = genai.GenerativeModel("gemini-1.5-pro-latest")
            response = model.generate_content([input_prompt])
            st.subheader("Personalized Diet Plan")
            st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred while generating the diet plan: {e}")

def fetch_exercise_videos():
    try:
        condition = "Hypothyroid" if st.session_state.prediction_result == 1 else "Hyperthyroid"
        search_query = f"Best yoga exercises for {condition} treatment"

        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=search_query,
            part="snippet",
            maxResults=5,
            type="video"
        )
        response = request.execute()

        st.subheader(f"Top 5 Exercise Videos for {condition}")
        for item in response["items"]:
            video_title = item["snippet"]["title"] 
            video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            st.write(f"[{video_title}]({video_url})")
    except Exception as e:
        st.error(f"An error occurred while fetching exercise videos: {e}")

def fetch_nearby_locations():
    g = geocoder.ip('me')
    latitude, longitude = g.latlng  # Extract latitude and longitude
    radius = 10000  # 10 km radius
    hospital_types = ['thyroid+specialist', 'endocrinologist']
    headers = {"Accept": "application/json"}
    location_results = []
    unique_place_ids = set()  # To track unique locations and avoid duplicates
    for hospital_type in hospital_types:
        url = f"https://maps.gomaps.pro/maps/api/place/textsearch/json?location={latitude},{longitude}&query={hospital_type}&radius={radius}&type=hospital&language=en&region=in&key={PLACES_API_KEY}"
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data['results']) > 0:
                for place in data['results']:
                    place_id = place.get('place_id', '')
                    
                    # Avoid duplicates and limit results to 6 unique places
                    if place_id not in unique_place_ids and len(location_results) < 6:
                        name = place.get('name', 'No name available')
                        address = place.get('formatted_address', 'No address available')
                        google_maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                        
                        location_results.append({
                            'name': name,
                            'address': address,
                            'google_maps_link': google_maps_link
                        })
                        
                        unique_place_ids.add(place_id)  # Add to the set to track unique places
            else:
                location_results.append({
                    'name': f"No {hospital_type} found",
                    'address': '',
                    'google_maps_link': ''
                })
        else:
            st.error(f"Failed to fetch {hospital_type}. Status code: {response.status_code}")
        
        # Stop searching if we've already found 6 unique locations
        if len(location_results) >= 6:
            break
    return location_results
# Streamlit Page Config
st.set_page_config(page_title="Thyroid Health Assistant", layout="wide")

# CSS for Styling
st.markdown("""
    <style>
        body { font-family: 'Arial', sans-serif; background-color: #f4f7f9; font-size: 18px;}
        .main-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #2c3e50; text-align: center; }
        .stButton > button { background-color: #3498db; color: white; border-radius: 8px; padding: 10px 16px; font-size: 16px; border: none; font-size: 18px; }
        .stButton > button:hover { background-color: #2980b9; transform: scale(1.05); transition: 0.2s ease-in-out; }
    </style>
""", unsafe_allow_html=True)

# Navigation Sidebar
page = st.sidebar.radio("Go to", ["🏠 Home", "🔍 Predict Thyroid", "📍 Nearby Doctors"])

# Home Page
if page == "🏠 Home":
    st.markdown("<h2>ML-Driven Thyroid Prediction Model and GenAI-Powered Wellness Recommendations</h2>", unsafe_allow_html=True)

    # Features Section
    st.markdown("""
    ## 🔍 Features:
    - *Thyroid Condition Prediction*: Input your health details, and our AI model will predict whether you have a thyroid condition.
    - *Personalized Diet Plans*: Get AI-generated diet recommendations tailored to your thyroid condition.
    - *Exercise Video Recommendations*: Find the best exercises for managing thyroid conditions with YouTube videos.
    - *Nearby Doctors and Hospitals*: Locate thyroid specialists and endocrinologists near you.
    """, unsafe_allow_html=True)

    # How to Use Section
    st.markdown("""
    ## 📌 How to Use:
    1. *Predict Thyroid*: Click on "🔍 Predict Thyroid" in the sidebar and enter your health details.
    2. *Get a Diet Plan*: If diagnosed with thyroid issues, a "Get Diet Plan" button will appear. Click it to receive a customized diet plan.
    3. *Watch Exercise Videos*: If diagnosed, you’ll also see a "Watch Exercise Videos" button. Click it to access guided exercises for managing thyroid health.
    4. *Find Nearby Doctors*: Use the "📍 Nearby Doctors" section to locate specialists in your area.
    """, unsafe_allow_html=True)

    st.write("Navigate using the sidebar to explore these features!")


# Predict Thyroid Page
elif page == "🔍 Predict Thyroid":
    predict_thyroid_condition()

    # Show options based on prediction
    if st.session_state.prediction_result in [1, 2]:  # Hypothyroid or Hyperthyroid
        # Generate diet plan button
        if st.button("Generate Diet Plan"):
            generate_diet_plan()

        # Exercise videos button
        if st.button("Show Exercise Videos"):
            fetch_exercise_videos()

# Nearby Doctors Page
elif page == "📍 Nearby Doctors":
    st.markdown("<h1>Find Nearby Doctors</h1>", unsafe_allow_html=True)
    if "location_results" not in st.session_state:
        st.session_state.location_results = []

    # Button to trigger location fetch
    if st.button("Find Nearby Doctors and Hospitals"):
        with st.spinner("Fetching nearby locations..."):
            st.session_state.location_results = fetch_nearby_locations()

        # Display results
        if st.session_state.location_results:
            for location in st.session_state.location_results:
                st.write(f"*Name:* {location['name']}")
                st.write(f"*Address:* {location['address']}")
                if location['google_maps_link']:
                    st.write(f"[Google Maps Link]({location['google_maps_link']})")
                st.write("---")