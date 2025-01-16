# myApp.models.chatbot_model.py
import psycopg2
from psycopg2.extras import Json, execute_values, RealDictCursor
import requests
import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
from datetime import datetime  # Add this import
from config.local_config import LocalConfig
from config.heroku_config import DatabaseConfig

load_dotenv()

class ChatbotService:
    MAX_CONTEXT_LENGTH = 2000  # Maximum context character length for Ollama

    def __init__(self):
        """Initialize with database configuration."""
        self.ollama_api_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434/api/chat')
        
        # Get database URL from different sources
        self.db_url = None
        
        # Try getting URL from environment first
        self.db_url = os.getenv('DATABASE_URL')
        
        # Try local config if no environment URL
        if not self.db_url:
            try:
                self.local_config = LocalConfig()
                self.db_url = getattr(self.local_config, 'DATABASE_URL', None)
                if not self.db_url:
                    self.db_url = self.local_config.get_db_url()
            except Exception as e:
                print(f"Local config initialization failed: {e}")

        # Final fallback to direct import
        if not self.db_url:
            try:
                from config.local_config import DATABASE_URL
                self.db_url = DATABASE_URL
            except:
                pass

        if not self.db_url:
            raise Exception("No database URL available - Please check your configuration")

        # Ensure proper URL format
        if self.db_url.startswith("postgres://"):
            self.db_url = self.db_url.replace("postgres://", "postgresql://", 1)

        # Test connection
        self._test_connection()

    def _test_connection(self):
        """Test database connection on startup"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT current_database();")
                    db_name = cur.fetchone()[0]
                    print(f"Successfully connected to database: {db_name}")
            
            # Test Ollama connection
            response = requests.get('http://localhost:11434/api/tags')
            if response.status_code == 200:
                print("Successfully connected to Ollama")
            
        except Exception as e:
            print(f"Warning: Service initialization error: {e}")

    def get_db_connection(self):
        """Get database connection."""
        return psycopg2.connect(self.db_url)

    def execute_query(self, query, params=None):
        """Execute query with enhanced error handling and logging."""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    conn.commit()
                    if cur.description:
                        return cur.fetchall()
                    return None
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise

    def fetch_relevant_embeddings(self, question: str, limit: int = 5) -> List[Dict]:
        """Fetch relevant embeddings from database."""
        print("\n=== Fetching Relevant Embeddings ===")
        query = """
            WITH question_embedding AS (
                SELECT embedding
                FROM questions
                WHERE question = %s
            )
            SELECT 
                content,
                1 - (embedding <=> (SELECT embedding FROM question_embedding)) as similarity
            FROM knowledge_base
            WHERE EXISTS (SELECT 1 FROM question_embedding)
            ORDER BY similarity DESC
            LIMIT %s
        """
        params = (question, limit)
        
        try:
            rows = self.execute_query(query, params)
            if rows:
                embeddings = [{"content": row[0], "similarity": row[1]} for row in rows]
                return embeddings[:limit]
            return []
        except Exception as e:
            print(f"[DB-002] Database error while fetching embeddings: {str(e)}")
            return []

    def log_chat_interaction(self, user_id: str, question: str, answer: str) -> bool:
        """Log chat interactions to both databases."""
        print("\n=== Database Operation: Logging Chat ===")
        query = """
            INSERT INTO chat_logs (user_id, question, answer, timestamp)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id;
        """
        params = (user_id, question, answer)
        
        try:
            results = self.execute_query(query, params)
            return bool(results)
        except Exception as e:
            print(f"ERROR logging chat: {str(e)}")
            return False

    def query_ollama(self, question: str, context: List[Dict]) -> str:
        """Send a question with context to Ollama API and get the response."""
        try:
            # Prepare context string from relevant embeddings
            context_str = "\n".join([item["content"] for item in context])

            # Trim context if it exceeds the maximum length
            if len(context_str) > self.MAX_CONTEXT_LENGTH:
                context_str = context_str[:self.MAX_CONTEXT_LENGTH] + "..."

            prompt = f"""
            The following context is extracted from the knowledge base:

            {context_str}

            Question: {question}
            Please answer the question as accurately as possible using the provided context.
            """

            response = requests.post(
                self.ollama_api_url,
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response received from the model.")
            else:
                raise Exception(f"[API-001] Ollama API error: {response.status_code} {response.text}")
                
        except requests.RequestException as e:
            raise Exception(f"[API-002] Error querying Ollama API: {str(e)}")

    def get_answer_from_ollama(self, question: str, user_id: str = "anonymous") -> Dict[str, str]:
        """
        Get answer from Ollama and log the interaction.
        
        Args:
            question (str): The user's question
            user_id (str): Identifier for the user (default: anonymous)
            
        Returns:
            Dict[str, str]: The chatbot's response.
        """
        try:
            relevant_context = self.fetch_relevant_embeddings(question)
            answer = self.query_ollama(question, relevant_context)
            
            # Log the interaction
            self.log_chat_interaction(user_id, question, answer)
            
            return {"answer": answer}
            
        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error: {str(e)}. Please try again later."
            }

    def insert_question(self, question: str, embedding: list, user_id: str) -> int:
        """Store question with embedding in both databases."""
        print("\n=== Database Operation: Inserting Question ===")
        query = """
            INSERT INTO questions (question, embedding, user_id, timestamp)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            RETURNING id;
        """
        params = (question, embedding, user_id)
        
        try:
            results = self.execute_query(query, params)
            return results[0][0] if results else None
        except Exception as e:
            print(f"ERROR inserting question: {str(e)}")
            raise

    def log_interaction(self, user_id: str, question: str, response: str, timestamp: datetime):
        """Log chat interaction in chat_logs table."""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO chat_logs (user_id, question, response, timestamp)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, question, response, timestamp))
        except Exception as e:
            print(f"Failed to log interaction: {str(e)}")

    def store_knowledge(self, content: str, embedding: list, user_id: int, tags: list = None, priority: str = "Medium", source: str = "Manual Entry") -> dict:
        """Store knowledge in database."""
        print("\n=== Database Operation: Storing Knowledge ===")
        query = """
            INSERT INTO knowledge_base (content, embedding, created_by, tags, priority, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (content, embedding, user_id, tags, priority, source)
        
        try:
            result = self.execute_query(query, params)
            if result:
                knowledge_id = result[0][0]
                return {"id": knowledge_id, "message": "Knowledge stored successfully"}
            raise Exception("Failed to store knowledge in database")
        except Exception as e:
            print(f"ERROR storing knowledge: {str(e)}")
            raise

    def get_existing_answer(self, question: str) -> Optional[str]:
        """Get existing answer if question has been asked before."""
        print("\n=== Checking for existing answer ===")
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Look for most recent answer to similar question
                    cur.execute("""
                        SELECT cl.answer, cl.timestamp
                        FROM questions q
                        JOIN chat_logs cl ON q.question = cl.question
                        WHERE q.question = %s
                        ORDER BY cl.timestamp DESC
                        LIMIT 1;
                    """, (question,))
                    
                    result = cur.fetchone()
                    if result:
                        print(f"Found existing answer from {result[1]}")
                        return result[0]
                    print("No existing answer found")
                    return None
                    
        except Exception as e:
            print(f"Error checking for existing answer: {e}")
            return None

    def get_all_knowledge(self) -> list:
        """Retrieve all knowledge entries"""
        try:
            with self.get_db_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute("""
                        SELECT 
                            k.id, 
                            k.content, 
                            k.created_at::text,  -- Convert to text
                            k.updated_at::text,  -- Convert to text
                            k.tags,
                            k.priority,
                            k.source,
                            u.username as created_by
                        FROM knowledge_base k
                        LEFT JOIN users u ON k.created_by = u.id
                        ORDER BY k.created_at DESC
                    """)
                    results = cursor.fetchall()
                    # Convert results to list of dicts with proper datetime handling
                    entries = []
                    for row in results:
                        entry = dict(row)
                        # Ensure created_at and updated_at are strings
                        entry['created_at'] = str(entry['created_at']) if entry['created_at'] else None
                        entry['updated_at'] = str(entry['updated_at']) if entry['updated_at'] else None
                        entries.append(entry)
                    return entries
        except Exception as e:
            print(f"Error getting knowledge: {e}")
            return []

    def delete_knowledge(self, entry_id: int) -> bool:
        """Delete a knowledge entry"""
        try:
            # Use get_db_connection instead of direct psycopg2 connection
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM knowledge_base WHERE id = %s", (entry_id,))
                    conn.commit()  # Add commit
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting knowledge: {e}")
            return False

    def update_knowledge(self, entry_id: int, content: str, tags: list = None, priority: str = None) -> bool:
        """Update a knowledge entry"""
        try:
            # Use get_db_connection instead of direct psycopg2 connection
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    # Update multiple fields
                    cursor.execute("""
                        UPDATE knowledge_base 
                        SET content = %s,
                            tags = %s,
                            priority = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (content, tags, priority, entry_id))
                    conn.commit()  # Add commit
                    return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating knowledge: {e}")
            return False

class ChatbotModel:
    def __init__(self, db_url):
        self.db_url = db_url

    def insert_knowledge(self, content, embedding):
        """Insert a new knowledge entry into the database."""
        try:
            with psycopg2.connect(self.db_url) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO knowledge_base (content, embedding)
                        VALUES (%s, %s)
                        RETURNING id
                        """,
                        (content, embedding)
                    )
                    knowledge_id = cur.fetchone()[0]
                    return {"id": knowledge_id, "message": "Knowledge stored successfully"}
        except psycopg2.errors.UniqueViolation:
            raise ValueError("This content already exists in the knowledge base")
        except Exception as e:
            raise RuntimeError(f"Database error: {str(e)}")