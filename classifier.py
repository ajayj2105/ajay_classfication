import streamlit as st
from groq import Groq
from prompts import SYSTEM_PROMPT

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

MODEL = "openai/gpt-oss-120b"

def classify_po(po_description:str,Supplier:str="Not provided"):
  user_prompt = f"""
  PO Description: {po_description}
  Supplier: {Supplier}
  """
  Response = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    temperature=0.0,
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

  )
  return Response.choices[0].message.content