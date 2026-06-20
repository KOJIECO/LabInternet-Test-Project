import json
import logging
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client_configured = False
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.client_configured = True
                logger.info("Google Gemini API successfully configured.")
            except Exception as e:
                logger.error(f"Failed to configure Gemini client: {e}")
        else:
            logger.warning("GEMINI_API_KEY is not set. Service running in fallback mode.")

    async def analyze_message(self, name: str, message: str) -> dict:
        if not self.client_configured:
            logger.info("Using local fallback analyzer (Gemini is not configured).")
            return self._get_fallback_analysis(message)
            
        prompt = f"""
        Вы — интеллектуальный AI-ассистент разработчика. Проанализируйте следующее сообщение от пользователя по имени "{name}":
        ---
        {message}
        ---
        
        Верните строго JSON-объект со следующими полями без какого-либо дополнительного текста, markdown-разметки или backticks (```json):
        {{
            "sentiment": "positive" | "neutral" | "negative",
            "category": "job_offer" | "question" | "partnership" | "spam" | "other",
            "suggested_reply": "Ваш вежливый, персонализированный ответ пользователю на русском языке"
        }}
        
        Особенно важно:
        - В поле "sentiment" должно быть ровно одно из слов: positive, neutral, negative.
        - В поле "category" должно быть ровно одно из слов: job_offer (предложение работы/вакансия), question (вопрос по проекту/технологиям), partnership (сотрудничество/партнерство), spam (реклама/спам), other (другое).
        - В поле "suggested_reply" сгенерируйте вежливый ответ от лица разработчика (Eduard), поблагодарите за обращение и напишите уместный ответ в зависимости от категории и тональности сообщения. Пишите лаконично и профессионально.
        """
        
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            
            result_text = response.text.strip()
            if result_text.startswith("```"):
                result_text = result_text.strip("`").replace("json\n", "", 1).strip()
                
            data = json.loads(result_text)
            
            sentiment = data.get("sentiment", "neutral").lower()
            if sentiment not in ["positive", "neutral", "negative"]:
                sentiment = "neutral"
                
            category = data.get("category", "other").lower()
            if category not in ["job_offer", "question", "partnership", "spam", "other"]:
                category = "other"
                
            suggested_reply = data.get("suggested_reply", "Спасибо за ваше сообщение!")
            
            logger.info(f"Gemini analysis successful: sentiment={sentiment}, category={category}")
            return {
                "sentiment": sentiment,
                "category": category,
                "suggested_reply": suggested_reply
            }
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}. Activating fallback analysis.")
            return self._get_fallback_analysis(message)

    def _get_fallback_analysis(self, message: str) -> dict:
        msg_lower = message.lower()
        
        if any(w in msg_lower for w in ["работа", "вакансия", "оффер", "hr", "резюме", "собеседование", "hiring", "job", "vacancy"]):
            category = "job_offer"
        elif any(w in msg_lower for w in ["сотрудничество", "партнер", "проект", "коллаборация", "partnership", "collaboration"]):
            category = "partnership"
        elif any(w in msg_lower for w in ["крипта", "битки", "заработок", "казино", "продвижение", "реклама", "seo", "купить"]):
            category = "spam"
        elif any(w in msg_lower for w in ["как", "почему", "вопрос", "стек", "технологии", "question", "how", "why"]):
            category = "question"
        else:
            category = "other"
            
        positive_words = ["круто", "отлично", "нравится", "супер", "класс", "молодец", "хорошо", "great", "nice", "awesome"]
        negative_words = ["плохо", "ужасно", "фигня", "дерьмо", "отстой", "криво", "bad", "terrible", "worst"]
        
        pos_count = sum(1 for w in positive_words if w in msg_lower)
        neg_count = sum(1 for w in negative_words if w in msg_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
        elif neg_count > pos_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        replies = {
            "job_offer": "Здравствуйте! Большое спасибо за предложение о работе. Я обязательно ознакомлюсь с деталями и свяжусь с вами в ближайшее время для обсуждения.",
            "partnership": "Приветствую! Тема сотрудничества мне очень интересна. Буду рад обсудить возможности совместной работы подробнее. Напишу вам в ближайшее время.",
            "spam": "Спасибо за ваше сообщение. Реклама и спам-предложения рассматриваются в индивидуальном порядке.",
            "question": "Здравствуйте! Спасибо за ваш вопрос. Я подготовлю подробный ответ и отправлю его вам на почту в течение дня.",
            "other": "Здравствуйте! Спасибо за обращение. Я получил ваше сообщение и свяжусь с вами в ближайшее время."
        }
        
        return {
            "sentiment": sentiment,
            "category": category,
            "suggested_reply": replies.get(category, "Спасибо за ваше обращение! Я свяжусь с вами в ближайшее время.")
        }

ai_service = AIService()
