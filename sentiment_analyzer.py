import pandas as pd
from transformers import pipeline, BertForSequenceClassification, BertTokenizer
import torch
from typing import List, Optional


class SentimentAnalyzer:
    """Class for analyzing sentiment in textual data using pretrained transformer models."""

    sentiment_mapping = {
        'Neutral': 0,
        'Positive': 1,
        'Negative': -1
    }

    def __init__(self, default_model_name: str = 'yiyanghkust/finbert-tone', default_batch_size: int = 8):
        """
        Initializes the SentimentAnalyzer with default model parameters.

        :param default_model_name: The default transformer model name to use if no custom model is specified.
        :param default_batch_size: The batch size to use for processing text data in batches.
        """
        self.default_model_name = default_model_name
        self.default_batch_size = default_batch_size

    @staticmethod
    def split_content(text: str, limit: int) -> List[str]:
        """
        Splits the given text into smaller chunks if it exceeds the specified length limit.

        :param text: The text content to be split.
        :param limit: The maximum length of each text chunk.
        :return: A list of text chunks.
        """
        return [text[i:i + limit] for i in range(0, len(text), limit)] if len(text) > limit else [text]

    def _load_model_and_tokenizer(self, model_path: Optional[str] = None):
        """
        Loads the transformer model and tokenizer from the specified path or default model.

        :param model_path: The path to the pretrained model. If None, the default model is used.
        :return: A tuple containing the model and tokenizer.
        """
        if model_path:
            model = BertForSequenceClassification.from_pretrained(model_path, force_download=True)
            tokenizer = BertTokenizer.from_pretrained(model_path, force_download=True)
        else:
            model = BertForSequenceClassification.from_pretrained(self.default_model_name, force_download=True)
            tokenizer = BertTokenizer.from_pretrained(self.default_model_name, force_download=True)

        return model, tokenizer

    def analyze(self, data: pd.DataFrame, length_limit: int = 500, enable_cuda: bool = False, model_choice: int = None,
                batch_size: Optional[int] = None) -> float:
        """
        Analyzes sentiment in the provided DataFrame using a transformer model.

        :param data: A DataFrame containing text data for analysis.
        :param length_limit: The character limit for text chunks to prevent truncation by the model.
        :param enable_cuda: Enables GPU usage if CUDA is available.
        :param model_choice: Specifies which model to use (0, 1, or None for the default model).
        :param batch_size: The batch size for processing text data. Uses default if not specified.
        :return: The overall sentiment score.
        """
        # Validate input DataFrame
        if 'Content' not in data.columns:
            raise ValueError("The input DataFrame must contain a 'Content' column.")

        # Validate model choice
        if model_choice not in [0, 1, None]:
            raise ValueError("Invalid model selection. Choose either 0, 1, or leave it as None for the default model.")

        # Determine device to use
        device = 0 if enable_cuda and torch.cuda.is_available() else -1
        print(f"Using {'CUDA/GPU' if device == 0 else 'CPU'} for computation.")

        # Load the appropriate model and tokenizer
        if model_choice == 0:
            model_path = "Nor8ix/finbert_hand_sentiment_model_press"
        elif model_choice == 1:
            model_path = "Nor8ix/finbert_hand_sentiment_model_news"
        else:
            model_path = None  # Use the default model

        model, tokenizer = self._load_model_and_tokenizer(model_path)

        # Set up the sentiment analysis pipeline
        sentiment_pipeline = pipeline(
            task="sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            batch_size=batch_size if batch_size is not None else self.default_batch_size,
            device=device
        )

        # Prepare the data
        df = data.copy()
        df['article_id'] = df.index
        df['content_chunks'] = df['Content'].apply(lambda x: self.split_content(x, length_limit))
        df = df.explode('content_chunks').reset_index(drop=True)

        # Perform sentiment analysis
        predictions = sentiment_pipeline(df['content_chunks'].tolist())
        df['prediction'] = [pred['label'] for pred in predictions]
        df['sentiment'] = df['prediction'].map(self.sentiment_mapping)
        article_sentiment = df.groupby('article_id')['sentiment'].mean().reset_index()
        article_sentiment['sentiment_label'] = article_sentiment['sentiment'].apply(lambda x: 1 if x > 0.33 else
                                                                                    (-1 if x < -0.33 else 0))
        overall_sentiment = article_sentiment['sentiment'].mean()

        return overall_sentiment
