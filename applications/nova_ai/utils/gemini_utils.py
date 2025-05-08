from google import genai
from google.genai import types
from google.ai.generativelanguage_v1beta.types import content

import os
import dotenv
import json
dotenv.load_dotenv()
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def upload_and_cache_topic(path, system_instruction):
    file_obj = client.files.upload(
        file=path,
        config={"mime_type": "application/pdf"}
    )
    # cache = client.caches.create(
    #     model="gemini-1.5-flash-8b",
    #     config=types.CreateCachedContentConfig(
    #     contents=[file_obj]
    #     )
    # )
    # client.caches.delete(name = cache.name)

    cache = client.caches.create(
        model="gemini-1.5-flash-8b",
        config=types.CreateCachedContentConfig(
            system_instruction=system_instruction,
            contents=[file_obj]
        )
    )
    return cache.name  # Cached content ID

def ask_question(file_id, question, role="If the document is not relevant to the question, say 'I don't know'."):
    config = types.GenerateContentConfig(
        cached_content=file_id,
        # system_instruction=[role],
    )
    guard = """
    You are an educational chatbot designed to help grade 3 children learn only about the topic in the provided document.

    Strict instructions:
    1. Do not answer any questions that are not directly related to the content of the document.
    2. If the question is about another topic, even if it's educational, respond: "I'm here to help you learn only about the topic we're studying right now. Let's stay focused!"
    3. Use simple, age-appropriate language suitable for children.
    4. If the document does not contain enough information to answer the question, respond with: "Hmm, I couldn't find that in our study material. Let's try a different question from this topic!"
    5. Be encouraging and friendly but always guide the learner back to the topic of the document.
    6. Never include information from outside the uploaded material.

    Also:
    After you answer a question, inspire the child to be more curious! Suggest related questions or offer to explain more parts of the topic. For example, say:
    - "Would you like to learn more about this part?"
    - "This is interesting, right? Want to go deeper?"
    - "There's more to discover — ask me another question about this topic!"

    """
    question = f"{guard} {question}"
    response = client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=[question],
        config=config
    )
    return response.text

def get_summary(file_id):
    question = "Summarize the key points of the document in a fun and simple way for kids to revise. If the topic is too dry, make it fun by maybe creating a story or a game."
    config = types.GenerateContentConfig(
        cached_content=file_id,
        # system_instruction=[role],
    )
    # question = f"{role} {question}"
    response = client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=[question],
        config=config
    )
    return response.text

def generate_quiz(file_id):
    question = "Create 10 multiple-choice questions (with 4 options each) and answers from this content. Make it kid-friendly."
    config = types.GenerateContentConfig(
        cached_content=file_id,
        # system_instruction=[role],
    )
    # question = f"{role} {question}"
    response = client.models.generate_content(
        model="gemini-1.5-flash-8b",
        contents=[question],
        config=config
    )
    return response.text

def generate_flashcards_from_cache(cache_id):
    # The model prompt to generate flashcards from the document
    prompt = """
    Generate a list of flashcards based on the content of this document.
    Each flashcard should have a "Question" and an "Answer".
    Return the output strictly as a JSON object in the following format:

    {
        "Question": ["...question1...", "...question2...", "..."],
        "Answer": ["...answer1...", "...answer2...", "..."]
    }

    Make sure the number of questions and answers match.
    """
    # generation_config = {
    #     "response_schema": content.Schema(
    #         type=content.Type.OBJECT,
    #         properties={
    #             "Question": content.Schema(
    #                 type=content.Type.ARRAY,
    #                 items=content.Schema(type=content.Type.STRING),
    #             ),
    #             "Answer": content.Schema(
    #                 type=content.Type.ARRAY,
    #                 items=content.Schema(type=content.Type.STRING),
    #             ),
    #         },
    #         required=["Question", "Answer"]
    #     ),
    #     "response_mime_type": "application/json",
    # }


    # Create the configuration for content generation
    config = types.GenerateContentConfig(
        cached_content=cache_id,  # Use the cached content from previous uploads
        # generation_config=generation_config
    )

    # Request content generation from the model
    response = client.models.generate_content(
        model="gemini-1.5-flash-8b",  # Use the appropriate model
        contents=[prompt],
        config=config
    )
    # print(response)
    # Check if the response is valid JSON    
    try:
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]  # Remove the leading ```json
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]  # Remove the trailing ```

        parsed_json = json.loads(raw_text)
        return parsed_json
    except json.JSONDecodeError:
        print("❌ Could not parse JSON from Gemini response.")
        print("Raw response:", response.text)
        return None
