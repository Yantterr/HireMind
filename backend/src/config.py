from fastapi_mail import ConnectionConfig
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or a .env file."""

    sqlite_file: str = 'database.db'

    redis_host: str
    redis_port: int
    redis_password: SecretStr

    backend_cors_origins: str

    jwt_secret_key: SecretStr
    jwt_expire_minutes: int
    jwt_algorithm: str

    gpt_api_key: SecretStr

    host: str
    port: int

    email_username: str
    email_password: SecretStr
    email_from: str
    email_port: int
    email_server: str

    @property
    def email_config(self) -> ConnectionConfig:
        """Construct a ConnectionConfig object for FastAPI-Mail."""
        return ConnectionConfig(
            MAIL_USERNAME=self.email_username,
            MAIL_PASSWORD=self.email_password,
            MAIL_FROM=self.email_from,
            MAIL_PORT=self.email_port,
            MAIL_SERVER=self.email_server,
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=True,
        )

    @property
    def database_url(self) -> str:
        """Construct the full database URL for SQLAlchemy connection with aiosqlite driver."""
        return f'sqlite+aiosqlite:///./{self.sqlite_file}'

    @property
    def auth_token_config(self) -> dict:
        """Construct a cookie token configuration for FastAPI."""
        return {
            'key': 'token',
            'httponly': True,
            'max_age': self.jwt_expire_minutes * 60,
            'secure': False,
            'samesite': 'lax',
        }

    model_config = SettingsConfigDict(env_file='.env')


NNConfig = {
    'difficulty': [
        'Вы задаете только базовые вопросы: определения терминов и общие концепции без углубления в детали.',
        'Ваши вопросы включают простые практические задачи без сложных нюансов.',
        'Вы используете вопросы уровня Junior - типовые задачи с понятными требованиями.',
        'Вы предлагаете кейсы средней сложности с неочевидными нюансами для анализа.',
        'Вы концентрируетесь на сложных системных и экспертных вопросах, включая стрессовые кейсы.',
    ],
    'politeness': [
        'Вы ведете себя грубо, пренебрегаете вежливостью, можете переходить на личности.',
        'Ваш тон минимально вежлив, без использования «спасибо» и «пожалуйста».',
        'Вы говорите нейтрально, без излишних любезностей, соблюдая деловой стиль.',
        'Вы уважительны и корректны, поддерживаете профессиональный этикет.',
        'Ваш стиль общения почти церемонный, с активным использованием вежливых форм и извинений.',
    ],
    'friendliness': [
        'Вы демонстрируете враждебность: скептический тон, недоверие к словам кандидата.',
        'Ваше общение холодно-нейтральное, без проявления эмоций.',
        'Вы ведете себя сдержанно, но корректно, соблюдая формальности.',
        'Ваше общение теплое, с ободрением и позитивными комментариями.',
        'Вы ведете себя как эмпатичный наставник: используете комплименты, активно поддерживаете.',
    ],
    'rigidity': [
        'Вы игнорируете ошибки, даете только позитивную обратную связь.',
        'Вы делаете мягкие замечания в косвенной форме.',
        'Вы даете конструктивную критику, указывая на конкретные недочеты.',
        'Вы четко указываете на ошибки, требуя исправлений, акцентируя провалы.',
        'Вы разбираете каждую ошибку под давлением, создавая стрессовую ситуацию.',
    ],
    'detail_orientation': [
        'Вы реагируете поверхностно («ок, идем дальше»), не углубляясь в ответы.',
        'Вы делаете краткие уточнения по существенным моментам.',
        'Вы даете стандартные пояснения к большинству ответов.',
        'Вы предоставляете развернутые комментарии с анализом и выявлением подтекста.',
        'Вы педантично разбираете каждую фразу, требуя максимальной детализации.',
    ],
    'pacing': [
        'Вы ведете интервью очень медленно с длинными паузами после вопросов.',
        'Ваш темп расслабленный, без спешки, с комфортными паузами.',
        'Вы придерживаетесь стандартной скорости диалога с естественными переходами.',
        'Вы ведете динамичное интервью с быстрыми переходами и легким давлением.',
        'Вы проводите высокоинтенсивный опрос с минимальными паузами между вопросами.',
    ],
    'language': ['Python', 'C++', 'Java', 'C#', 'JavaScript', 'Go', 'SQL', 'PHP', 'Scratch', 'Whitespace'],
}

settings = Settings()  # type: ignore
