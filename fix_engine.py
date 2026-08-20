import re

with open('./backend/app/ilrmf/engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
skip = False
skip_until_empty = False

i = 0
while i < len(lines):
    line = lines[i]

    # Skip self._groq_client = None
    if 'self._groq_client = None' in line:
        i += 1
        continue

    # Skip groq_client property block
    if '@property' in line and i + 1 < len(lines) and 'def groq_client' in lines[i + 1]:
        i += 1
        while i < len(lines) and 'return self._groq_client' not in lines[i]:
            i += 1
        i += 1  # skip the return line too
        continue

    # Skip _call_groq method
    if 'async def _call_groq' in line:
        i += 1
        while i < len(lines) and '"Groq API Error:' not in lines[i]:
            i += 1
        i += 1  # skip the return line
        continue

    # Replace gemini_model property
    if '@property' in line and i + 1 < len(lines) and 'def gemini_model' in lines[i + 1]:
        out.append('    @property\n')
        out.append('    def gemini_client(self):\n')
        out.append('        if self._gemini_model is None:\n')
        out.append('            try:\n')
        out.append('                from google import genai\n')
        out.append('                self._gemini_model = genai.Client(api_key=settings.GEMINI_API_KEY)\n')
        out.append('                logger.info(f"Gemini client initialized ({settings.GEMINI_MODEL})")\n')
        out.append('            except Exception as e:\n')
        out.append('                logger.error(f"Gemini init failed: {e}")\n')
        out.append('        return self._gemini_model\n')
        i += 1
        while i < len(lines) and 'return self._gemini_model' not in lines[i]:
            i += 1
        i += 1
        continue

    # Replace _call_ai method
    if 'async def _call_ai' in line:
        out.append('    async def _call_ai(self, prompt: str) -> dict:\n')
        out.append('        """Route to Gemini AI provider."""\n')
        out.append('        result = await self._call_gemini(prompt)\n')
        out.append('        return result\n')
        i += 1
        while i < len(lines) and 'async def _call_gemini' not in lines[i]:
            i += 1
        continue

    # Replace _call_gemini method
    if 'async def _call_gemini' in line:
        out.append('    async def _call_gemini(self, prompt: str) -> dict:\n')
        out.append('        """Call Google Gemini via google-genai v2.x API."""\n')
        out.append('        from google import genai\n')
        out.append('        last_error = None\n')
        out.append('        for attempt in range(3):\n')
        out.append('            try:\n')
        out.append('                client = self.gemini_client\n')
        out.append('                if client is None:\n')
        out.append('                    raise RuntimeError("Gemini client not initialized \u2014 check GEMINI_API_KEY")\n')
        out.append('\n')
        out.append('                response = await asyncio.to_thread(\n')
        out.append('                    client.models.generate_content,\n')
        out.append('                    model=settings.GEMINI_MODEL,\n')
        out.append('                    contents=prompt,\n')
        out.append('                    config=genai.types.GenerateContentConfig(\n')
        out.append('                        temperature=0.1,\n')
        out.append('                        max_output_tokens=16000,\n')
        out.append('                    ),\n')
        out.append('                )\n')
        out.append('\n')
        out.append('                raw = response.text.strip() if response.text else ""\n')
        out.append('                if not raw:\n')
        out.append('                    raise ValueError("Empty response from Gemini")\n')
        out.append('\n')
        out.append('                parsed = self._parse_json(raw)\n')
        out.append('                logger.info(f"Gemini OK: attempt={attempt + 1} chars={len(raw)}")\n')
        out.append('                return {"success": True, "data": parsed}\n')
        out.append('            except Exception as e:\n')
        out.append('                last_error = f"{type(e).__name__} - {str(e)}"\n')
        out.append('                logger.warning(f"Gemini attempt {attempt + 1} failed: {last_error}")\n')
        out.append('                if attempt < 2:\n')
        out.append('                    await asyncio.sleep(1.5 ** attempt)\n')
        out.append('\n')
        out.append('        logger.error(f"Gemini failed after 3 attempts: {last_error}")\n')
        out.append('        return {"success": False, "error": f"Gemini API Error: {last_error}"}\n')
        i += 1
        while i < len(lines) and 'async def _call_groq' not in lines[i]:
            i += 1
        continue

    out.append(line)
    i += 1

with open('./backend/app/ilrmf/engine.py', 'w', encoding='utf-8') as f:
    f.writelines(out)

print('Done!')
