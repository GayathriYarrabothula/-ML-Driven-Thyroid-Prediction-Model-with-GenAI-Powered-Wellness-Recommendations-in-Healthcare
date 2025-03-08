# Thyroid Prediction and Personalized Wellness Recommendations

This project aims to predict whether a person has **hypothyroidism, hyperthyroidism, or no thyroid disorder** using machine learning techniques. In addition to diagnosis, it provides **personalized wellness recommendations** to assist users in managing their thyroid health. These recommendations include:

- **Diet Plan:** A weekly meal plan tailored to the user's symptoms.
- **Exercise Videos:** Fetching relevant YouTube videos based on the diagnosed thyroid condition.
- **Doctor Recommendations:** Identifying six nearby thyroid specialists or hospitals for further consultation.

## Installation and Execution

Follow these steps to set up and run the project:

1. **Clone the Repository**  
   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. **Create Virtual Environment**  
   ```bash
   python -m venv venv

3. **Activate the Virtual Environment**  

   - **On Windows:**  
     ```bash
     .\venv\Scripts\activate
     ```
   - **On macOS/Linux:**  
     ```bash
     source venv/bin/activate
     ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt

4. **Run the Application**  
   ```bash
   streamlit run overalltest.py
