from langchain_community.chat_message_histories import PostgresChatMessageHistory
from langchain_core.messages import BaseMessage
import json
from langchain_core.messages import (
    BaseMessage,
    message_to_dict,
    messages_from_dict,
)
from typing import List

class LimitedPostgresChatMessageHistory(PostgresChatMessageHistory):
    def __init__(self, connection_string: str, session_id: str):
        super().__init__(connection_string=connection_string, session_id=session_id)
        self._max_messages = 4  # Define the limit as a class variable

    @property
    def messages(self) -> List[BaseMessage]:  # type: ignore
        """Retrieve the messages from PostgreSQL"""
        query = (
            f"SELECT message FROM {self.table_name} WHERE session_id = %s ORDER BY id DESC LIMIT %s;"
        )
        self.cursor.execute(query, (self.session_id, self._max_messages))
        items = [record["message"] for record in self.cursor.fetchall()]
        messages = messages_from_dict(items)
        messages = messages[::-1]
        return messages