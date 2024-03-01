from collections import defaultdict
from typing import List

import torch
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class QuestionIntent(BaseModel):
    """The request model for creating an annotation."""
    input: str
    intent: str
    output: str


class MismatchedIntents(BaseModel):
    """The mismatched intents of the annotation."""
    questionPair: List[str] = []
    """The question pair of the annotation."""
    intent1: str = ""
    """The intent1 of the annotation."""
    intent2: str = ""
    """The intent2 of the annotation."""
    answer1: str = ""
    """The answer1 of the annotation."""
    answer2: str = ""
    """The answer2 of the annotation."""
    lineNumbers: List[int] = []
    """The line numbers of the annotation."""


class SimilarIntents(BaseModel):
    """The similar intents of the annotation."""
    intentPair: List[str] = []
    """The intent pair of the annotation."""


class SimilarQuestionIntent(BaseModel):
    """The response model for a list of data annotations."""
    mismatchedIntents: List[MismatchedIntents] = []
    similarIntents: List[SimilarIntents] = []


class DatasetsModel:
    """The datasets model."""

    def __init__(self, model_path: str = "", device: str = ""):
        """Construct a new model."""
        if not model_path:
            model_path = "uer/sbert-base-chinese-nli"
        self.model_path = model_path

        if not device:
            # 如果是mac系统，使用mps
            if "mac" in torch.__file__:
                device = "mps"
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"

        self.device = device
        self.model = SentenceTransformer(model_name_or_path=model_path, device=device)

    async def analyze_similar_questions_and_intents(self, data: List[QuestionIntent], similarity_threshold: float = 0.9,
                                                    intent_similarity_threshold: float = 0.9) -> SimilarQuestionIntent:
        """Analyze similar questions and intents."""

        all_query = []
        all_intents = []
        all_answers = []
        indices = []

        for i, item in enumerate(data):
            questions = item.input[1:-1].split(',')
            questions = [q.strip() for q in questions]
            intents = item.intent
            answers = item.output
            for q in questions:
                all_query.append(q)
            for _ in range(len(questions)):
                all_intents.append(intents)
                all_answers.append(answers)
                indices.append(i)
            i += 1

        sentence_embeddings = self.model.encode(all_query)
        cosine_score = cosine_similarity(sentence_embeddings)
        similar_indices = np.argwhere(cosine_score >= similarity_threshold)
        intent_question = defaultdict(list)

        for row, col in similar_indices:
            if row < col:
                intent1 = all_intents[row]
                intent2 = all_intents[col]
                if intent1 != intent2:  # 不考虑同一个意图的情况
                    question1 = all_query[row]
                    question2 = all_query[col]
                    answer1 = all_answers[row]
                    answer2 = all_answers[col]
                    intent_question[tuple((intent1, intent2))].append({
                        "question_pair": [question1, question2],
                        "intent1": intent1,
                        "intent2": intent2,
                        "answer1": answer1,
                        "answer2": answer2,
                        "line_numbers": [indices[row], indices[col]]
                    })

        # 比较相似问题的意图是否相似
        similar_intents: List[SimilarIntents] = []
        intents_ = [intent for intent_pair in intent_question.keys()
                    for intent in intent_pair]
        if intents_:
            sentence_embeddings = self.model.encode(intents_)
            for i in range(0, len(sentence_embeddings), 2):
                intent_sim = cosine_similarity([sentence_embeddings[i]], [
                    sentence_embeddings[i + 1]])[0][0]
                if intent_sim > intent_similarity_threshold:
                    intent_sim = float(intent_sim)

                    similar_intents.append(SimilarIntents(intent_pair=[intents_[i], intents_[i + 1]]))

        return SimilarQuestionIntent(similarIntents=similar_intents,
                                     mismatchedIntents=[v for pairs in intent_question.values() for v in pairs])
