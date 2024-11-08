class User:
    """
    Reference:
        Telegram User Class: https://core.telegram.org/bots/api#user
    
    """
    id: str
    is_bot: bool
    first_name: str
    last_name: str | None
    username: str | None
    language_code: str | None
    
    def __init__(self, id: str, is_bot: bool, first_name: str, last_name: str | None = None, username: str | None = None, language_code: str | None = None) -> None:
        self.id = id
        self.is_bot = is_bot
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
    
    def eval(self):
        return {k: v for k, v in {
            "id": self.id,
            "is_bot": self.is_bot,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code
        }.items() if v is not None}
        
    def __str__(self) -> str:
        return f"User {self.first_name} {self.last_name} ({self.id})"

class Chat:
    """
    Reference:
        Telegram Chat Class: https://core.telegram.org/bots/api#chat
    """
    
    id: str
    type: str
    title: str | None
    username: str | None
    first_name: str | None
    last_name: str | None
        
    def __init__(self, id: str, type: str, title: str | None = None, username: str | None = None, first_name: str | None = None, last_name: str | None = None) -> None:
        self.id = id
        self.type = type
        self.title = title
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        
    def eval(self):
        return {k: v for k, v in {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name
            
        }.items() if v is not None}
    
    def __str__(self) -> str:
        return f"Chat {self.title} ({self.id})"
    
class Message:
    """
    Reference:
        Telegram Message Class: https://core.telegram.org/bots/api#message
    """

    message_id: str
    date: int
    text: str | None
    
    def __init__(self, message_id: str, from_user: User | None, chat: Chat | None, date: int, text: str | None = None) -> None:
        self.message_id = message_id
        self.from_user = from_user
        self.chat = chat
        self.date = date
        self.text = text
    
    def eval(self):
        return {k: v for k, v in {
            "message_id": self.message_id,
            "from_user": None if self.from_user is None else self.from_user.eval(),
            "chat": None if self.chat is None else self.chat.eval(),
            "date": self.date,
            "text": self.text
        }.items() if v is not None}
        
    def __str__(self) -> str:
        return f"Message {self.message_id} from {self.from_user} in {self.chat}"