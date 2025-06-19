import os
os.environ["OPENAI_API_KEY"] = "YOUR_OPEN_API_KEY_HERE"
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field, validator
from typing import List, Literal
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOpenAI
import json
import re

# Initialize FastAPI app
app = FastAPI()

with open("transformed_cards.json", "r") as f:
    dataset = json.load(f)["dataset"]

user_spending = 0
class UserInput(BaseModel):
    spending: int
    age: int
    income: int
    employmentType: Literal['salaried', 'self-employed']
    rewardType: Literal['Reward Points', 'Shopping', 'Lifestyle', 'Business', 'Travel', 'Cashback', 'Dining', 'Rewards', 'Lounge', 'Fuel']

class StructuredInput(BaseModel):
    rewardType: str = Field(..., description="Reward type category")
    spending: int
    age: int
    income: int
    employmentType: str

    @validator("rewardType")
    def validate_reward(cls, v):
        valid_rewards = {'Reward Points', 'Shopping', 'Lifestyle', 'Business', 'Travel', 'Cashback', 'Dining', 'Rewards', 'Lounge', 'Fuel'}
        if v not in valid_rewards:
            raise ValueError("Invalid reward type")
        return v

    @validator("employmentType")
    def format_employment(cls, v):
        v = v.lower()
        if "salaried" in v:
            return "salaried"
        elif "self" in v or "business" in v:
            return "self-employed"
        else:
            raise ValueError("Invalid employment type")

def is_eligible(card, user: UserInput):
    return user.income >= card["minMonthlyIncome"]

def score_card(card, user: UserInput):
    score = 0
    if user.rewardType.lower() in card["rewardType"].lower():
        score += 50
    if user.employmentType.lower() in card["employmentType"].lower():
        score += 20
    if isinstance(card.get("rewardRate"), list):
        if card.get("rewardRate"):
            score += max(card.get("rewardRate"))*10
    
    #score -= (card.get("annualFee") + card.get("joiningFee"))//1000
    return score

# Use ChatOpenAI for chat models
llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

reason_template = PromptTemplate.from_template("""
Create a response in JSON style with the following fields stating positive reasons for choosing the card:
{{'reasons': [{{"<cardName>": "<reason>"}}, {{"<cardName>": "<reason>"}} ...]}}
When user input was:
{response}
And chosen cards are:
{chosen}

output should have this structure: {{'reasons': <List of dicts>}}
""")

parse_template = PromptTemplate.from_template("""
We got user input as: {response}

Rewrite this in the format:
{{
    "rewardType": <choose the most suitable one from {{"Reward Points", "Shopping", ...}}>,
    "spending": <(integer) how much the user spends on that reward>,
    "age": <integer>,
    "income": <integer>,
    "employmentType": <'salaried' or 'self-employed'>
}}

Example:
Input: {{"spending": "I spend about 6000 on fuel and 500 on dining", "Age": "I am 21", "employmentType": "I have a business", "monthlyIncome": "50000"}}
Output: {{"rewardType": "Fuel", "spending": 6000, "age": 21, "income": 50000, "employmentType": "self-employed"}}
""")

# Use RunnableSequence (prompt | llm) instead of LLMChain
parse_chain = parse_template | llm
reason_chain = reason_template | llm

def extract_json_from_response(response_text):
    start = response_text.find("{")
    end   = response_text.rfind("}") + 1
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in response_text")
    json_block = response_text[start:end]
    return json.loads(json_block)

# ---------------- FastAPI Endpoint ----------------

@app.post("/parse-input")
def parse_user_input(response: dict = Body(...)):
    global user_spending
    raw_response = parse_chain.invoke({"response": response})
    # print(response)
    # print("Raw_Response: ", raw_response)
    raw = raw_response.content if hasattr(raw_response, 'content') else raw_response
    try:
        parsed = extract_json_from_response(raw)
        user_input = UserInput(**parsed)
        user_spending = user_input.spending
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parsing failed: {str(e)}")
    # print("converted to: ", user_input.dict())
    return {"structured_input": user_input.dict()}

@app.post("/recommend")
def recommend_cards(user: UserInput):
    global user_spending
    eligible_cards = [card for card in dataset if is_eligible(card, user)]
    # print('len(eligible_cards): ', len(eligible_cards))
    if not eligible_cards:
        raise HTTPException(status_code=404, detail="No eligible cards found.")
    scored_cards = sorted(eligible_cards, key=lambda card: score_card(card, user), reverse=True)
    top_cards = scored_cards[:5]
    # print("Top Cards:", top_cards)
    reasons = reason_chain.invoke({
        "response": user.dict(),
        "chosen": [{
            "cardName": card["cardName"],
            "minMonthlyIncome": card["minMonthlyIncome"],
            "rewardType": card["rewardType"],
            "rewardRate": card["rewardRate"],
            "joiningFee": card["joiningFee"],
            "annualFee": card["annualFee"],
            "features": card["features"],
            "eligibility": card["eligibility"],
            "userSpending": user_spending
        } for card in top_cards]
    })
    print(reasons.content)
    print(extract_json_from_response(reasons.content))
    return {
        "cards": top_cards,
        "reasons": extract_json_from_response(reasons.content if hasattr(reasons, 'content') else reasons)['reasons']
    }
