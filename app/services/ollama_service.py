"""
Ollama LLM Client Integration for Enterprise NL2SQL
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional
import structlog
from app.config import settings

logger = structlog.get_logger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama LLM server"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
    def health_check(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")
            return False
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models in Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {str(e)}")
            return []
    
    def generate_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate completion using Ollama model"""
        
        try:
            # Convert OpenAI-style messages to Ollama prompt format
            prompt = self._convert_messages_to_prompt(messages)
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": min(max_tokens, 256),  # Further reduced for faster inference
                    "stop": ["</sql>", "\n\n", "```"],
                    "num_ctx": 1024,  # Smaller context for faster processing
                    "num_thread": 4   # Use multiple threads for inference
                }
            }
            
            logger.info(f"Sending request to Ollama: model={model}, prompt_length={len(prompt)}")
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60  # Reduced timeout for faster model
            )
            response.raise_for_status()
            
            if stream:
                return self._handle_streaming_response(response)
            else:
                result = response.json()
                return {
                    "choices": [{
                        "message": {
                            "content": result.get("response", ""),
                            "role": "assistant"
                        }
                    }],
                    "usage": {
                        "prompt_tokens": result.get("prompt_eval_count", 0),
                        "completion_tokens": result.get("eval_count", 0),
                        "total_tokens": result.get("prompt_eval_count", 0) + result.get("eval_count", 0)
                    }
                }
                
        except Exception as e:
            logger.error(f"Ollama generation failed: {str(e)}")
            raise Exception(f"Failed to generate completion: {str(e)}")
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to a single prompt"""
        prompt_parts = []
        
        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    def _handle_streaming_response(self, response) -> Dict[str, Any]:
        """Handle streaming response from Ollama"""
        full_response = ""
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    if "response" in data:
                        full_response += data["response"]
                    if data.get("done", False):
                        break
                except json.JSONDecodeError:
                    continue
        
        return {
            "choices": [{
                "message": {
                    "content": full_response,
                    "role": "assistant"
                }
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }


class OllamaLLMService:
    """Service wrapper for Ollama LLM functionality"""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = None):
        # Use the base_url from environment or default to localhost
        if base_url is None:
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        self.client = OllamaClient(base_url)
        self.model_name = model_name
        
        try:
            self._check_model_availability()
        except Exception as e:
            logger.warning(f"Ollama initialization warning: {str(e)}")
            # Don't fail completely, just log the warning
    
    def _check_model_availability(self):
        """Check if the specified model is available"""
        if not self.client.health_check():
            raise Exception("Ollama server is not running. Please start Ollama first.")
        
        available_models = self.client.list_models()
        model_names = [model.get("name", "") for model in available_models]
        
        if self.model_name not in model_names:
            logger.warning(f"Model {self.model_name} not found. Available models: {model_names}")
            if model_names:
                self.model_name = model_names[0]
                logger.info(f"Using first available model: {self.model_name}")
            else:
                raise Exception("No models available in Ollama. Please pull a model first.")
    
    def generate_sql(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 2000
    ) -> str:
        """Generate SQL using Ollama model"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = self.client.generate_completion(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response["choices"][0]["message"]["content"]
            return generated_text.strip()
            
        except Exception as e:
            logger.error(f"SQL generation failed with Ollama: {str(e)}")
            raise Exception(f"Failed to generate SQL: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "provider": "ollama",
            "model_name": self.model_name,
            "server_status": self.client.health_check(),
            "available_models": [model.get("name") for model in self.client.list_models()]
        }


# Factory function to create LLM service based on configuration
def create_llm_service() -> Any:
    """Create appropriate LLM service based on configuration"""
    
    llm_provider = getattr(settings, 'LLM_PROVIDER', 'openai').lower()
    
    if llm_provider == 'ollama':
        model_name = getattr(settings, 'OLLAMA_MODEL', 'llama3.1:8b')
        return OllamaLLMService(model_name)
    else:
        # Default to OpenAI
        from openai import OpenAI
        return OpenAI(api_key=settings.OPENAI_API_KEY)


# For backward compatibility
def get_ollama_service() -> OllamaLLMService:
    """Get Ollama service instance"""
    return OllamaLLMService()
