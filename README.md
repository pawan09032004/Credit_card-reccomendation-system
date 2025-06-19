# Credit Card Advisor

A web-based, agent-powered credit card recommendation system that uses LLMs and tool integrations to guide users through a personalized Q&A journey and suggest the best-fit credit cards based on their preferences. 

## Demo Video

https://github.com/user-attachments/assets/5f1c3b9c-11cb-4f06-b13a-697b17f790e7

[Project Demo Video](https://www.youtube.com/watch?v=KY58OzIMGpg)

## Features

- AI-powered recommendation engine, utilizes Langchain and OpenAI API's gpt-4o-mini model
- Personalized card suggestions based on:
  - Monthly income
  - Age
  - Employment type
  - Spending patterns
- Detailed comparison of recommended cards
- Provides reasoning for each recommendation
- Reward type optimization
- User-friendly interface built with Streamlit

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **AI/ML**: LangChain, OpenAI GPT
- **Data Processing**: Python, Pandas
- **API**: RESTful architecture

## Installation

1. Clone the repository:
```bash
git clone https://github.com/manik1080/credit-card-advisor.git
cd credit-card-advisor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Add OpenAI API key:
   - Open `main.py`
   - Replace `YOUR_OPEN_API_KEY_HERE` with your actual OpenAI API key

## Usage

1. FastAPI backend:
```bash
uvicorn main:app
```

2. To start Streamlit frontend:
```bash
streamlit run streamlit_app.py
```
## **Steps:**
1. **Data Collection**: The `prepare_data.py` file consists of the code for dataset.
Looking for a website to scrape a dataset of 20+ Indian credit cards. Selected `https://select.finology.in/credit-card` as the source. Since the website lists only 15 per page and uses dynamic page loading, cards after the 15th card cannot be scraped using BeautifulSoup.
So, using the Network tab in the Inspect window, the JSON response consisting of all required information is seen in the response on clicking "Load More".
Card image is converted to base64, then encoded as ascii to upload to json file.

Next, we run `transform_data.py` to get the transformed data by parsing strings of data to extract information like reward rated, age range etc. used for finding eligibility of user for the card.

Using streamlit as frontend,
Users input their financial information and preferences through an intuitive interface.

The system uses Pydantic Models
- UserInput: Defines the raw fields accepted from the client (spending, age, income, employmentType, rewardType).
- StructuredInput: Mirrors those fields but adds validation:

2. **AI Processing**: The system uses LangChain and gpt-4o-mini to Structure and validate user inputs into json format and generate reasons for card choices. 

3. **Recommendation**: Cards are scored based on:
   - Age eligibility 
   - Reward type matching (matched by AI using spending habits)
   - Income eligibility
   - Employment type

5. **Results**: The final output displayed includes the top 5 recommended cards with details like eligibility criteria, required documents, reward rates etc.
An option to compare any of the cards also provided, along with AI-generated reasoning for each recommendation.

## Project Structure

- `streamlit_app.py`: Frontend interface
- `main.py`: FastAPI backend and recommendation engine
- `cards.json`: Original card dataset
- `response.txt`: The response taken from website's network tab in inspect window.
- `transformed_cards.json`: Processed card data
- `create_dataset.py`: Data scraping.
- `transform_dataset.py`: Create transformed dataset.
