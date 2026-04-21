import logging
from tagging.db import DBManager
from tagging.pipeline import TaggingPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventMind-Worker")


def main():
    db = DBManager()
    pipeline = TaggingPipeline()

    logger.info("Starting EventMind Autotagging process...")

    # 1. Читаем данные из Neon
    events = db.get_unprocessed_events()

    if not events:
        logger.info("No new events to process.")
        return

    for event in events:
        id = event['id']
        logger.info(f"Processing event ID: {id}")

        # 2. Очистка, Теггирование и Эмбеддинги (внутри pipeline.py)
        # Мы передаем словарь с title и description
        processed_data = pipeline.process_event(event)

        # 3. Сохраняем результат обратно в Neon
        # Добавляем проверку, что processed_data не None
        if processed_data is not None and processed_data.get("tags"):
            try:
                db.update_event_data(
                    id=id,
                    tags=processed_data["tags"],
                    embedding=processed_data["embedding"]
                )
                logger.info(f"Successfully updated event {id}")
            except Exception as e:
                logger.error(f"Failed to save event {id}: {e}")
        else:
            logger.warning(f"No relevant tags found for event {id}. Skipping update.")


if __name__ == "__main__":
    main()
