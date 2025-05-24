# services/preset_manager.py
from google.cloud import firestore
from datetime import datetime, timezone # Используем timezone-aware datetime
from config import db, logger # Используем db (клиент Firestore) и logger из config.py

PRESETS_COLLECTION = "chartgenius_user_presets" # Название коллекции в Firestore

def save_preset(user_id: str, preset_name: str, settings: dict) -> tuple[bool, str]:
    if not user_id:
        logger.error("Save preset failed: user_id is missing.")
        return False, "Ошибка: ID пользователя не найден."
    if not preset_name:
        logger.error("Save preset failed: preset_name is missing.")
        return False, "Ошибка: Имя пресета не может быть пустым."
    if not db:
        logger.error("Save preset failed: Firestore client (db) is not available.")
        return False, "Ошибка: База данных не доступна."

    try:
        # Создаем ID документа, комбинируя user_id и имя пресета (санитизированное)
        # Это гарантирует, что имя пресета уникально для пользователя
        sanitized_preset_name = "".join(c if c.isalnum() or c in ['_','-'] else '_' for c in preset_name.strip())
        if not sanitized_preset_name:
             logger.error("Save preset failed: sanitized preset_name is empty.")
             return False, "Ошибка: Имя пресета содержит недопустимые символы или пустое после очистки."

        doc_id = f"user_{user_id}_preset_{sanitized_preset_name.lower()}"
        
        preset_data = {
            "user_id": user_id,
            "preset_name": preset_name.strip(), # Сохраняем оригинальное имя для отображения
            "sanitized_name": sanitized_preset_name.lower(), # Для возможного поиска/индексации
            "settings": settings,
            "created_at": datetime.now(timezone.utc), # Используем timezone-aware UTC
            "updated_at": datetime.now(timezone.utc)
        }
        # Используем set с merge=True, чтобы обновить, если существует, или создать новый.
        # Если нужно строгое "создать или перезаписать полностью", то merge=False или просто set без merge.
        # Для "сохранить или обновить", set(data, merge=True) или update(data) подходят.
        # Просто set() перезапишет документ, если он существует.
        db.collection(PRESETS_COLLECTION).document(doc_id).set(preset_data)
        logger.info(f"Preset '{preset_name}' for user '{user_id}' saved successfully with doc_id '{doc_id}'.")
        return True, f"Пресет '{preset_name}' успешно сохранен!"
    except Exception as e:
        logger.error(f"Error saving preset '{preset_name}' for user '{user_id}': {e}", exc_info=True)
        return False, f"Ошибка при сохранении пресета: {str(e)}"

def load_user_presets_list(user_id: str) -> list[dict]:
    if not user_id or not db:
        return []
    
    presets_options = []
    try:
        presets_query = db.collection(PRESETS_COLLECTION).where("user_id", "==", user_id).order_by("preset_name").stream()
        for preset_doc in presets_query:
            preset_data = preset_doc.to_dict()
            # Для value в Dropdown лучше использовать что-то уникальное, если preset_name могут повторяться
            # Но если мы гарантируем уникальность preset_name для пользователя (через doc_id), то можно и preset_name
            presets_options.append({'label': preset_data.get("preset_name"), 'value': preset_doc.id}) # Используем doc_id как value
        logger.info(f"Loaded {len(presets_options)} presets for user '{user_id}'.")
        return presets_options
    except Exception as e:
        logger.error(f"Error loading presets list for user '{user_id}': {e}", exc_info=True)
        return []

def load_preset_settings(doc_id: str) -> dict | None: # Принимаем doc_id вместо user_id и preset_name
    if not doc_id or not db:
        return None
    try:
        doc_ref = db.collection(PRESETS_COLLECTION).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            preset_data = doc.to_dict()
            logger.info(f"Settings for preset_doc_id '{doc_id}' loaded successfully.")
            return preset_data.get("settings")
        else:
            logger.warning(f"Preset with doc_id '{doc_id}' not found.")
            return None
    except Exception as e:
        logger.error(f"Error loading settings for preset_doc_id '{doc_id}': {e}", exc_info=True)
        return None

def delete_preset(doc_id: str) -> bool: # Принимаем doc_id
    if not doc_id or not db:
        return False
    try:
        db.collection(PRESETS_COLLECTION).document(doc_id).delete()
        logger.info(f"Preset with doc_id '{doc_id}' deleted successfully.")
        return True
    except Exception as e:
        logger.error(f"Error deleting preset_doc_id '{doc_id}': {e}", exc_info=True)
        return False
