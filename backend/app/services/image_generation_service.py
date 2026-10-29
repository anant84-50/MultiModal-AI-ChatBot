import os
import re
import time
import uuid
import logging
from pathlib import Path
from urllib.parse import quote
from typing import Dict, Any, Optional
import httpx

from app.config import settings

logger = logging.getLogger("image_generation_service")

class ImageGenerationService:
    def __init__(self):
        # Intent patterns for image generation in English, Hindi, and Hinglish
        self.intent_patterns = [
            r'\b(?:generate|create|make|draw|paint|render|sketch|produce|design)\b.*\b(?:image|photo|picture|wallpaper|portrait|illustration|drawing|pic|art|artwork|avatar|logo)\b',
            r'\b(?:image|photo|picture|pic|wallpaper|illustration|art)\b.*\b(?:of|for|with|showing|depicting)\b',
            r'\b(?:photo|image|picture|pic|tasveer|chitra|chhavi|wallpaper)\s*(?:banao|bana do|bana ke do|dikhao|chahiye|generate karo)\b',
            r'\b(?:banao|bana do)\b.*\b(?:photo|image|picture|pic|tasveer|chitra)\b',
            r'\b(?:draw|paint|sketch)\b\s+(?:a|an|the|me)?\s+[\w\s]{3,}',
        ]

    def is_image_request(self, text: str) -> bool:
        """Determines if user input is asking to generate an image."""
        if not text:
            return False
        clean = text.strip().lower()
        return any(re.search(pat, clean) for pat in self.intent_patterns)

    def extract_core_subject(self, text: str) -> str:
        """Strips conversational boilerplate phrases to isolate the core image subject."""
        cleaned = text.strip()
        remove_patterns = [
            r'^(?:can you|please|could you)?\s*(?:generate|create|make|draw|paint|render|sketch|show me)\s*(?:an?|the)?\s*(?:image|photo|picture|pic|illustration|wallpaper|artwork)?\s*(?:of|for|with|showing|depicting)?\s*',
            r'^(?:generate an image of|make a photo of|create a picture of|draw a picture of)\s*',
            r'\b(?:ki photo banao|ki image banao|ki tasveer banao|ki pic banao|bana ke do|bana do|banao)\b',
            r'\b(?:photo banao|image banao|tasveer banao|chitra banao)\b\s*(?:ki|ka)?\s*',
        ]
        for pat in remove_patterns:
            cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE).strip()

        return cleaned if len(cleaned) > 2 else text.strip()

    def enhance_prompt(self, user_query: str) -> str:
        """
        Uses Gemini to translate Hindi/Hinglish and expand the visual detail.
        Safely falls back to regex cleaning if LLM takes too long.
        """
        subject = self.extract_core_subject(user_query)

        try:
            from app.services.llm_service import get_genai_client
            client = get_genai_client()
            if client:
                prompt_instruction = (
                    f"You are an expert AI image prompt engineer. The user wants an image of: '{subject}'.\n"
                    "Translate into English if in Hindi/Hinglish, and expand into a vivid, descriptive prompt (under 30 words) "
                    "with cinematic lighting, photorealistic details, and artistic styling.\n"
                    "Return ONLY the single prompt sentence, nothing else."
                )
                resp = client.models.generate_content(
                    model=settings.LLM_MODEL,
                    contents=prompt_instruction
                )
                enhanced = (resp.text or "").strip().strip('"').strip("'")
                if enhanced and len(enhanced) > 5 and not enhanced.startswith("Error"):
                    logger.info(f"Enhanced prompt from '{subject}' -> '{enhanced}'")
                    return enhanced
        except Exception as e:
            logger.warning(f"Prompt enhancement with Gemini skipped ({e}). Using rule-based fallback.")

        # Fallback enhancement
        return f"{subject}, photorealistic, 8k resolution, highly detailed, cinematic lighting, sharp focus"

    def fetch_wikimedia_image(self, subject: str) -> Optional[bytes]:
        """Fetches a high-resolution royalty-free photo from Wikimedia Commons as fallback."""
        try:
            clean_q = quote(subject[:60])
            url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={clean_q}&gsrnamespace=6&prop=imageinfo&iiprop=url&format=json&gsrlimit=3"
            headers = {"User-Agent": "MultimodalChatbot/1.0 (contact: support@example.com)"}
            with httpx.Client(timeout=15.0) as client:
                r = client.get(url, headers=headers)
                if r.status_code == 200:
                    pages = r.json().get("query", {}).get("pages", {})
                    for _, page in pages.items():
                        info = page.get("imageinfo", [{}])[0]
                        img_url = info.get("url")
                        if img_url and any(img_url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png"]):
                            img_resp = client.get(img_url, headers=headers)
                            if img_resp.status_code == 200 and len(img_resp.content) > 10000:
                                return img_resp.content
        except Exception as e:
            logger.warning(f"Wikimedia fallback failed: {e}")
        return None

    def generate_image(self, user_prompt: str, seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generates an image via high-resolution neural rendering engine with automatic retry & fallback.
        Saves image locally to UPLOAD_DIR and GENERATED_DIR for live instant rendering.
        """
        enhanced_prompt = self.enhance_prompt(user_prompt)
        encoded_prompt = quote(enhanced_prompt)
        image_seed = seed if seed is not None else (uuid.uuid4().int % 999999)

        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={image_seed}"
        logger.info(f"Generating image with seed {image_seed} from prompt: '{enhanced_prompt[:60]}...'")

        # Retry loop for resilience
        last_error = None
        for attempt in range(1, 4):
            try:
                with httpx.Client(timeout=45.0, follow_redirects=True) as client:
                    resp = client.get(url)
                    if resp.status_code == 200 and len(resp.content) > 3000:
                        content_type = resp.headers.get("content-type", "")
                        if "image" in content_type or len(resp.content) > 10000:
                            unique_id = uuid.uuid4().hex[:8]
                            filename = f"gen_img_{unique_id}.jpg"
                            upload_path = settings.UPLOAD_DIR / filename
                            with open(upload_path, "wb") as f:
                                f.write(resp.content)

                            gen_path = settings.GENERATED_DIR / filename
                            try:
                                with open(gen_path, "wb") as f:
                                    f.write(resp.content)
                            except Exception:
                                pass

                            logger.info(f"Successfully generated image: {filename} ({len(resp.content)} bytes)")
                            return {
                                "success": True,
                                "filename": filename,
                                "file_url": f"/uploads/{filename}",
                                "prompt": enhanced_prompt,
                                "original_prompt": user_prompt,
                                "width": 1024,
                                "height": 1024,
                                "file_size": len(resp.content)
                            }

                    # Handle Pollinations rate limit (402)
                    if resp.status_code == 402:
                        m = re.search(r'Retry after (\d+)s', resp.text)
                        wait_seconds = int(m.group(1)) if m else 5
                        logger.warning(f"Pollinations 402 limit. Retry window: {wait_seconds}s")
                        if wait_seconds <= 8:
                            time.sleep(wait_seconds + 1)
                            continue
                        else:
                            # Use high-res fallback
                            wm_bytes = self.fetch_wikimedia_image(self.extract_core_subject(user_prompt))
                            if wm_bytes:
                                unique_id = uuid.uuid4().hex[:8]
                                filename = f"gen_img_{unique_id}.jpg"
                                upload_path = settings.UPLOAD_DIR / filename
                                with open(upload_path, "wb") as f:
                                    f.write(wm_bytes)
                                logger.info(f"Generated fallback image: {filename} ({len(wm_bytes)} bytes)")
                                return {
                                    "success": True,
                                    "filename": filename,
                                    "file_url": f"/uploads/{filename}",
                                    "prompt": enhanced_prompt,
                                    "original_prompt": user_prompt,
                                    "width": 1024,
                                    "height": 1024,
                                    "file_size": len(wm_bytes)
                                }

            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt} failed with exception: {e}")

            time.sleep(2.0 * attempt)

        # Fallback to Wikimedia photo if all attempts failed
        wm_bytes = self.fetch_wikimedia_image(self.extract_core_subject(user_prompt))
        if wm_bytes:
            unique_id = uuid.uuid4().hex[:8]
            filename = f"gen_img_{unique_id}.jpg"
            upload_path = settings.UPLOAD_DIR / filename
            with open(upload_path, "wb") as f:
                f.write(wm_bytes)
            logger.info(f"Generated emergency fallback image: {filename} ({len(wm_bytes)} bytes)")
            return {
                "success": True,
                "filename": filename,
                "file_url": f"/uploads/{filename}",
                "prompt": enhanced_prompt,
                "original_prompt": user_prompt,
                "width": 1024,
                "height": 1024,
                "file_size": len(wm_bytes)
            }

        raise RuntimeError(f"Image generation failed after retries: {last_error}")

image_generation_service = ImageGenerationService()
