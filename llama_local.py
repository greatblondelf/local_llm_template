from llama_cpp import Llama
import json


class LocalLLM:
    def __init__(self):
        self.llm = Llama.from_pretrained(
            repo_id="bartowski/Llama-3.2-1B-Instruct-GGUF",
            filename="Llama-3.2-1B-Instruct-IQ3_M.gguf",
            n_ctx=5000,
        )

    def output(self, input_prompt, output_json = False):
        try:
            response = None
            output = None
            if output_json:
                response = self.llm.create_chat_completion(
                    messages=[{"role": "user", "content": input_prompt}],
                    response_format={"type": "json_object"},
                )
                output = json.loads(response["choices"][0]["message"]["content"])
            else:
                response = self.llm.create_chat_completion(
                    messages=[{"role": "user", "content": input_prompt}],
                    response_format={"type": "text_object"},
                )
                output = str(response["choices"][0]["message"]["content"])
                
            print(f"\nFull LLM Response: {response}")
            return output
        except Exception as e:
            pass
        # If everything failed...
        print("\nNo working models, system error.")
        return {}
