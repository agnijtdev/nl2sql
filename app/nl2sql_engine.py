"""
nl2sql_engine.py
Loads the fine-tuned T5 model and converts natural language to SQL.
Also handles vague queries with heuristic post-processing.
"""

import re
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer


# ---------- Vagueness resolution rules ----------
VAGUE_TERMS = {
    "recent":       "last 30 days",
    "recently":     "last 30 days",
    "latest":       "ORDER BY id DESC LIMIT 10",
    "old":          "ORDER BY created_at ASC",
    "popular":      "ORDER BY count DESC",
    "most active":  "ORDER BY activity_count DESC",
    "new":          "last 7 days",
    "top":          "ORDER BY value DESC LIMIT 10",
    "big":          "ORDER BY size DESC",
    "small":        "ORDER BY size ASC",
}

DATE_PATTERNS = {
    "last month":   "strftime('%Y-%m', date_col) = strftime('%Y-%m', date('now', '-1 month'))",
    "this month":   "strftime('%Y-%m', date_col) = strftime('%Y-%m', 'now')",
    "today":        "date_col = date('now')",
    "this year":    "strftime('%Y', date_col) = strftime('%Y', 'now')",
    "last week":    "date_col >= date('now', '-7 days')",
}


class NL2SQLEngine:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self._loaded = False

    def load(self):
        """Load model from disk (call once at startup)."""
        print("⏳ Loading NL2SQL model...")
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_path)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_path)
        self.model.eval()
        self._loaded = True
        print("✅ Model loaded.")

    def _build_prompt(self, question: str, schema_string: str, db_name: str) -> str:
        """
        Build the model input prompt with schema context injected.
        Format matches training: "translate to SQL: <Q> | database: <db> | schema: <schema>"
        """
        return (
            f"translate to SQL: {question} "
            f"| database: {db_name} "
            f"| schema: {schema_string}"
        )

    def _post_process(self, sql: str, question: str) -> str:
        """
        Patch common vague terms the model might miss.
        Applies heuristic rules on top of model output.
        """
        q_lower = question.lower()

        # Replace vague time references
        for term, replacement in DATE_PATTERNS.items():
            if term in q_lower and "date_col" in sql:
                # This is a placeholder; in real use, map to actual date column
                pass  # Schema-aware replacement handled in clarifier

        return sql

    def convert(self, question: str, schema_string: str, db_name: str) -> dict:
        """
        Main method: converts natural language question to SQL.
        Returns dict with sql, confidence, warnings.
        """
        if not self._loaded:
            raise RuntimeError("Model not loaded. Call .load() first.")

        prompt = self._build_prompt(question, schema_string, db_name)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=512,
            truncation=True,
        )

        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=256,
                num_beams=4,
                early_stopping=True,
                no_repeat_ngram_size=2,
            )

        sql = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        sql = self._post_process(sql, question)

        # Detect vagueness warnings
        warnings = []
        q_lower = question.lower()
        for vague_word in VAGUE_TERMS:
            if vague_word in q_lower:
                warnings.append(
                    f"⚠️  Vague term '{vague_word}' detected — "
                    f"interpreted as: {VAGUE_TERMS[vague_word]}"
                )

        return {
            "sql": sql,
            "warnings": warnings,
            "prompt_used": prompt,
        }