from app.config.database import Base
from sqlalchemy import Column, INTEGER, VARCHAR, TEXT, BOOLEAN, TIMESTAMP, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class User(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, primary_key=True, nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    is_verified = Column(BOOLEAN, nullable=False, server_default='false')
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    profile = relationship('UserProfile', uselist=False, backref='user', cascade='all, delete-orphan')
    subscription = relationship('Subscription', uselist=False, backref='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', backref='user', cascade='all, delete-orphan')
    sessions = relationship('UserSession', backref="user", cascade='all, delete-orphan')

    def user(self, id: int):
        return self if self.id == id else None


class UserSession(Base):
    __tablename__ = 'user_sessions'
    id = Column(INTEGER, nullable=False, primary_key=True)
    user_id = Column(INTEGER, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    refresh_token = Column(VARCHAR(255), nullable=True)
    refresh_token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    device_info = Column(VARCHAR(255), nullable=True)
    ip_address = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = Column(VARCHAR(255), nullable=True)
    country = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)


class UserVerificationToken(Base):
    __tablename__ = 'user_verification_tokens'
    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    type = Column(Enum('new_signup', 'password_reset', name='user_verification_request_type_enum'), nullable=False)
    token = Column(VARCHAR(255), nullable=True)
    token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    is_used = Column(BOOLEAN, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    def is_valid(self, type: str):
        if (
            self.type == type
            and self.is_used == False
            and self.token_expiry > datetime.now(timezone.utc)
        ):
            return True
        else:
            return False

    def invalidate(self):
        self.is_used = True
        self.token = None
        self.updated_at = datetime.now(timezone.utc)
        return self


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    sub_type = Column(Enum('free', 'pro', name='subscription_type_enum'), nullable=False, server_default='free')
    status = Column(Enum('active', 'inactive', 'canceled', 'past_due', name='subscription_status_enum'),
                    nullable=False, server_default='inactive')
    start_date = Column(TIMESTAMP(timezone=True), nullable=True)
    end_date = Column(TIMESTAMP(timezone=True), nullable=True)
    max_domains = Column(INTEGER, nullable=False, server_default='1')
    max_scans_per_month = Column(INTEGER, nullable=False, server_default='5')

    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)


class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    message = Column(VARCHAR(255), nullable=False)
    is_read = Column(BOOLEAN, nullable=False, server_default='false')
    is_sent = Column(BOOLEAN, nullable=False, server_default='false')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)


class Jobs(Base):
    __tablename__ = 'jobs'
    id = Column(INTEGER, primary_key=True, nullable=False)
    priority = Column(INTEGER, nullable=False, server_default='0')
    retries = Column(INTEGER, nullable=False, server_default='0')
    max_retries = Column(INTEGER, nullable=False, server_default='3')
    last_error = Column(TEXT, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')


class FailedJobs(Base):
    __tablename__ = 'failed_jobs'
    id = Column(INTEGER, primary_key=True, nullable=False)
    job_id = Column(INTEGER, ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False)
    error_message = Column(TEXT, nullable=True)
    failed_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
