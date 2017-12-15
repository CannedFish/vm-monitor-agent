CREATE TABLE IF NOT EXISTS MESSAGES (
  uuid TEXT,
  container_id TEXT,
  object_id TEXT,
  orig_name TEXT,
  content_type TEXT,
  local_path TEXT,
  timestramp TimeStamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
