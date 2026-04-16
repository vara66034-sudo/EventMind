import os
import re
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score


DATA_PATH = "vk_labeled_posts.csv"
ARTIFACT_DIR = "artifacts"
MODEL_PATH = os.path.join(ARTIFACT_DIR, "event_classifier.joblib")


def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = str(text)
    text = text.replace("&nbsp;", " ")
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\[club\d+\|[^\]]+\]", " ", text)
    text = re.sub(r"\[id\d+\|[^\]]+\]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig")

    # оставляем только нужные колонки
    needed = {"text", "label"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"В CSV нет колонок: {missing}")

    df = df[["text", "label"]].copy()
    df = df.dropna(subset=["text", "label"])

    df["text"] = df["text"].astype(str).map(clean_text)
    df["label"] = df["label"].astype(int)

    # убираем пустые тексты
    df = df[df["text"].str.len() > 0].copy()

    return df


def build_pipeline() -> Pipeline:
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True,
            )
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=2000,
                class_weight="balanced",
                random_state=42,
            )
        )
    ])


def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    df = load_data(DATA_PATH)

    print("Размер датасета:", len(df))
    print("Распределение классов:")
    print(df["label"].value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        random_state=42,
        stratify=df["label"],
    )

    model = build_pipeline()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    print("\nClassification report:")
    print(classification_report(y_test, y_pred, digits=4))

    print("Confusion matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("F1:", round(f1_score(y_test, y_pred), 4))

    # сохраним модель
    joblib.dump(model, MODEL_PATH)
    print(f"\nМодель сохранена: {MODEL_PATH}")

    # сохраним ошибки для ручного анализа
    error_df = pd.DataFrame({
        "text": X_test.values,
        "true_label": y_test.values,
        "pred_label": y_pred,
        "proba_event": y_proba,
    })
    error_df = error_df[error_df["true_label"] != error_df["pred_label"]]
    error_df.to_csv(os.path.join(ARTIFACT_DIR, "errors.csv"), index=False, encoding="utf-8-sig")
    print(f"Ошибки сохранены: {os.path.join(ARTIFACT_DIR, 'errors.csv')}")


if __name__ == "__main__":
    main()
