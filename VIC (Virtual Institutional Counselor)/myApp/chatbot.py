from sentence_transformers import SentenceTransformer
from langchain.prompts import PromptTemplate
from myApp.controllers.syllabus_controller import SyllabusController
from transformers import pipeline
from config.environment import get_database_url  # Changed this line
from langchain_ollama import ChatOllama
from myApp.models.chatbot_model import ChatbotService
import requests
import warnings
import time  # Add time import for sleep

class Chatbot:
    def __init__(self, timeout=45):  # Further increased timeout
        self.timeout = timeout
        self.is_ollama_available = False
        try:
            self.chatbot_service = ChatbotService()
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                self.embedding_model = SentenceTransformer('all-mpnet-base-v2', device='cpu')
            self.ollama_url = "http://localhost:11434/api/generate"
            self.model_name = "qwen2.5:1.5b"
            self.max_retries = 5  # Increased retries
            self.is_ollama_available = self._initialize_ollama()
        except Exception as e:
            print(f"Warning: Chatbot initialization error: {e}")
    
    def _initialize_ollama(self):
        """Initialize Ollama with retry logic"""
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting to connect to Ollama (attempt {attempt + 1}/{self.max_retries})...")
                response = requests.get(
                    'http://localhost:11434/api/tags',
                    timeout=30  # Increased timeout further
                )
                if response.status_code == 200:
                    print("Successfully connected to Ollama")
                    return True
                    
            except requests.exceptions.Timeout:
                wait_time = 2 ** attempt
                if attempt < self.max_retries - 1:
                    print(f"Connection attempt {attempt + 1} timed out. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Failed to establish connection to Ollama after multiple attempts")
                    return False
            except Exception as e:
                print(f"Warning: Ollama initialization error (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
        return False

    def _pull_model(self):
        """Pull the required model with extended timeout"""
        try:
            print(f"Pulling model {self.model_name}...")
            response = requests.post(
                'http://localhost:11434/api/pull',
                json={"name": self.model_name},
                timeout=600  # 10 minutes timeout for model pull
            )
            if response.status_code == 200:
                print(f"Successfully pulled model {self.model_name}")
            else:
                print(f"Failed to pull model: {response.status_code}")
        except Exception as e:
            print(f"Error pulling model: {e}")

    def process_question(self, question: str, user_id: str = "anonymous") -> dict:
        if not self.is_ollama_available:
            return {
                "error": "Ollama service is currently unavailable. Please try again later or contact support.",
                "fallback": True
            }
            
        try:
            # Add validation for empty/invalid questions
            if not question or len(question.strip()) < 3:
                return {"error": "Please provide a valid question"}
            
            # Check for existing answer first
            existing_answer = self.chatbot_service.get_existing_answer(question)
            if (existing_answer):
                print("Using existing answer from database")
                return {"answer": existing_answer}

            # If no existing answer, continue with normal processing
            question_embedding = self.embedding_model.encode(question).tolist()
            self.chatbot_service.insert_question(question, question_embedding, user_id)
            
            # Get relevant context from knowledge base
            context = self.chatbot_service.fetch_relevant_embeddings(question)
            
            # Create prompt with templates
            prompt = create_prompt(question, context)
            
            # Add retries for Ollama connection with increased timeouts
            max_retries = 5  # Increased from 3
            backoff_factor = 2
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    # Query Ollama
                    response = requests.post(
                        self.ollama_url,
                        json={
                            "model": self.model_name,  # Use the new model name
                            "prompt": prompt,
                            "stream": False,
                            "system": "You are VIC, a helpful academic counselor."
                        },
                        timeout=45  # Increased timeout
                    )
                    
                    if response.status_code == 200:
                        answer = response.json().get("response", "")
                        if answer:
                            self.chatbot_service.log_chat_interaction(user_id, question, answer)
                            return {"answer": answer, "success": True}
                        last_error = "Empty response from Ollama"
                        
                    elif response.status_code == 404:
                        print(f"Model {self.model_name} not found, attempting to pull...")
                        self._pull_model()
                        continue
                        
                    else:
                        last_error = f"Ollama error: {response.status_code}"
                        
                except requests.exceptions.Timeout:
                    wait_time = backoff_factor ** attempt
                    print(f"Request timed out. Retrying in {wait_time} seconds...")
                    if attempt == max_retries - 1:
                        return {
                            "error": "The service is experiencing high load. Please try again in a few minutes.",
                            "fallback": True
                        }
                    time.sleep(wait_time)
                    continue
                    
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    if attempt == max_retries - 1:
                        break
                    wait_time = backoff_factor ** attempt
                    print(f"Request failed. Retrying in {wait_time} seconds... ({last_error})")
                    time.sleep(wait_time)
                    continue

            return {
                "error": f"Service error: {last_error}",
                "fallback": True
            }
                
        except Exception as e:
            print(f"Error processing question: {e}")
            return {
                "error": "I'm having trouble processing your request. Please try again later.",
                "fallback": True
            }

    def store_knowledge(self, content: str, user_id: int) -> dict:
        """Store knowledge with user attribution"""
        try:
            # Generate embedding
            print(f"Generating embedding for knowledge from user {user_id}")
            embedding = self.embedding_model.encode(content).tolist()
            
            # Store in database with user attribution
            result = self.chatbot_service.store_knowledge(content, embedding, user_id)
            print(f"Knowledge base storage result: {result}")
            return result
            
        except Exception as e:
            print(f"Error in store_knowledge: {e}")
            raise Exception(f"Failed to store knowledge: {str(e)}")

# Keep existing template and helper functions

# Database setup
db_url = get_database_url()  # Changed this line
syllabus_controller = SyllabusController(db_url=db_url)

# Initialize the embedding model
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# Initialize the LLM
llm = ChatOllama(
    model="qwen2.5:1.5b",  # Changed model
    temperature=0.2,  # Lower temperature for more focused responses
    num_ctx=2048,    # Increased context window
    num_thread=4,    # Utilize multiple threads
    num_gpu=1,       # Enable GPU acceleration if available
    base_url="http://localhost:11434",
    timeout=45,      # Increased timeout
    streaming=True,  # Enable streaming for faster initial response
    cache=True,      # Enable response caching
    repeat_penalty=1.1,  # Slight penalty for repetition
    seed=42          # Consistent random seed
)

# Add caching decorator
from functools import lru_cache

# Cache embeddings for 1 hour (maxsize=128 most recent questions)
@lru_cache(maxsize=128, typed=True)
def get_question_embedding(question):
    return embedding_model.encode(question).tolist()

# Optimize get_relevant_context function
def get_relevant_context(question_embedding, top_n=2):
    """Fetch fragments based on embeddings with optimized search."""
    try:
        fragments = []
        
        # Get context from syllabus table with improved similarity search
        try:
            with psycopg2.connect(db_url) as conn:
                with conn.cursor() as cur:
                    # Convert embedding to proper format
                    embedding_list = question_embedding if isinstance(question_embedding, list) else question_embedding.tolist()
                    
                    # Perform similarity search with logging
                    query = """
                    WITH similar_chunks AS (
                        SELECT 
                            s.chunk,
                            c.cname,
                            c.ccode,
                            (s.embedding <=> %s) as distance
                        FROM syllabus s
                        JOIN class c ON s.courseid = c.cid
                        ORDER BY s.embedding <=> %s
                        LIMIT %s
                    )
                    SELECT 
                        chunk,
                        cname,
                        ccode,
                        distance
                    FROM similar_chunks
                    WHERE distance < 0.8
                    ORDER BY distance;
                    """
                    
                    print(f"Executing syllabus similarity search...")
                    cur.execute(query, (embedding_list, embedding_list, top_n))
                    results = cur.fetchall()
                    print(f"Found {len(results)} relevant chunks")
                    
                    for chunk, cname, ccode, distance in results:
                        context = f"From {cname} ({ccode}): {chunk}"
                        fragments.append(context)
                        print(f"Added chunk with similarity score: {1-distance:.2f}")
        except Exception as e:
            print(f"Error in syllabus search: {str(e)}")
        # ...existing code for other context sources...
        
        if not fragments:
            print("No relevant fragments found in any source")
            return ["No specific information found in syllabus or knowledge base."]
            
        print(f"Returning {len(fragments)} total fragments")
        return fragments[:top_n]
        
    except Exception as e:
        print(f"[ERROR] Context retrieval failed: {e}")
        return ["Context retrieval error."]

# Cache document retrieval for 1 hour
@lru_cache(maxsize=64, typed=True)
def get_cached_context(question_str):
    embedding = get_question_embedding(question_str)
    return get_relevant_context(embedding, top_n=3, question=question_str)

def truncate_documents(documents, max_chars=5000):
    """Truncate the documents to a specified number of characters."""
    return documents[:max_chars] + "..." if len(documents) > max_chars else documents

def keyword_based_fallback(question, fragments):
    """Fallback mechanism using keyword matching."""
    keywords = question.split()  # Extract keywords
    matched = [frag for frag in fragments if any(kw.lower() in frag.lower() for kw in keywords)]
    return matched[:5] if matched else ["No matching syllabus information found."]

def categorize_query(question):
    """Categorize the query type."""
    if "requisites" in question.lower() or "requirements" in question.lower():
        return "requisites"
    elif "textbooks" in question.lower():
        return "textbooks"
    elif "grades" in question.lower() or "evaluation" in question.lower():
        return "grades"
    elif "topics" in question.lower():
        return "topics"
    else:
        return "general"

def create_prompt(question, documents):
    """Create a prompt tailored to the query type."""
    query_type = categorize_query(question)

    base_template = """You are an academic assistant answering questions about course syllabi.
    Only use information from the provided syllabus documents.
    If information is not explicitly stated, say so clearly.
    
    Documents: {documents}
    Question: {question}
    
    Instructions:
    1. Search relevant syllabus sections
    2. Extract exact information (no inference)
    3. Format response clearly with course code/name
    4. State if information is missing
    5. Be concise and accurate
    
    Response format:
    - Start with course code and name
    - Use bullet points for lists
    - Include section reference
    
    Answer:"""

    # Replace the entire templates dict with specialized templates
    templates = {
        "requisites": base_template + """
            Focus on:
            - Prerequisites
            - Corequisites
            - Special conditions""",
            
        "textbooks": base_template + """
            Focus on:
            - Required textbooks
            - Authors and editions
            - ISBN if available""",
            
        "grades": base_template + """
            Focus on:
            - Grading components
            - Percentage breakdowns
            - Evaluation methods""",
            
        "topics": base_template + """
            Focus on:
            - Main course topics
            - Key concepts
            - Course objectives""",
            
        "general": base_template
    }

    return templates.get(query_type, templates["general"]).format(
        documents=truncate_documents(documents),
        question=question
    )

def verify_response(response, query_type):
    """Verify response meets requirements for query type"""
    if not response or len(response) < 20:
        return False
        
    required_elements = {
        "requisites": ["prerequisite", "require", "course"],
        "textbooks": ["book", "text", "author"],
        "grades": ["grade", "exam", "evaluation", "%"],
        "topics": ["topic", "cover", "include"]
    }
    
    if query_type in required_elements:
        return any(word in response.lower() for word in required_elements[query_type])
    return True

# Optimize chat function
@lru_cache(maxsize=256)  # Increased cache size
def chat(question: str, user_id: str = "anonymous"):
    """
    DEPRECATED: This function is only used for command-line testing.
    Production code should use the API endpoints.
    """
    print("Warning: Using local chat function instead of API endpoint")
    try:
        print(f"\nProcessing question from user {user_id}...")
        # Use cached embedding
        context_fragments = get_cached_context(question)
        
        if not context_fragments:
            return "I couldn't find relevant information in the syllabus database."

        # Limit context size and combine fragments
        documents = "\n".join(context_fragments)[:800]  # Reduced context size
        
        # Create prompt with system message and clear instructions
        messages = [
            {
                "role": "system",
                "content": "You are VIC, a concise academic counselor. Keep responses brief and focused."
            },
            {
                "role": "user",
                "content": f"Context:\n{documents}\nQuestion: {question}"
            }
        ]

        # Generate answer from the LLM
        result = llm.invoke(messages)
        answer = result.content.strip()[:500]  # Limit response length
        print(f"Generated answer for user {user_id}")

        return answer if len(answer) > 20 else "I don't have enough information to answer that question accurately."
        
    except Exception as e:
        print(f"[ERROR] Chat failed: {e}")
        return "I'm having trouble processing your question. Please try again."

if __name__ == "__main__":
    print("> Hi, my name is SSHarlie! I am your personal virtual academic counselor. \n"
          "> How can I help you for today? You can quit at any time by writing `q`.")

    while True:
        user_prompt = input("> ")
        if user_prompt.lower() == "q":
            print("> Bye, nice meeting you!")
            break
        else:
            answer = chat(user_prompt)
            print("> ", answer)

    # prompts = ["What are the requisites of Introduction to Computer Programming (CIIC 3015)?",
    # "What textbooks are used in Big Data Analytics?",
    # "How are grades divided in CIIC 4060?",
    # "List five topics in Bioinformatics Algorithms."]

    # for question in prompts:
    #     print(">", question)
    #     print(">", chat(question))