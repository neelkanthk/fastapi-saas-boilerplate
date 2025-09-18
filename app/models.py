from app.config.database import Base
from sqlalchemy import Column, INTEGER, VARCHAR, TEXT, BOOLEAN, TIMESTAMP, ForeignKey, Enum, JSON, Float
from sqlalchemy.orm import relationship


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, primary_key=True, nullable=False)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    password = Column(VARCHAR(255), nullable=False)
    is_verified = Column(BOOLEAN, nullable=False, server_default='false')
    refresh_token = Column(VARCHAR(255), nullable=True)
    refresh_token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)

    profile = relationship('UserProfile', uselist=False, backref='user', cascade='all, delete-orphan')
    subscriptions = relationship('Subscription', uselist=False, backref='user', cascade='all, delete-orphan')
    notifications = relationship('Notification', backref='user', cascade='all, delete-orphan')


class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    full_name = Column(VARCHAR(255), nullable=True)
    country = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)


class UserVerificationToken(Base):
    __tablename__ = 'user_verification_token'
    id = Column(INTEGER, primary_key=True, nullable=False)
    user_id = Column(INTEGER, nullable=False)
    type = Column(Enum('new_signup', 'password_reset', name='user_verification_request_type_enum'), nullable=False)
    token = Column(VARCHAR(255), nullable=True)
    token_expiry = Column(TIMESTAMP(timezone=True), nullable=True)
    is_verified = Column(BOOLEAN, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)


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


class Analytics(Base):
    __tablename__ = 'analytics'

    id = Column(INTEGER, primary_key=True, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, server_default='now()')

    # User metrics
    total_users = Column(INTEGER, nullable=False)
    active_users_daily = Column(INTEGER, nullable=False)
    active_users_weekly = Column(INTEGER, nullable=False)
    active_users_monthly = Column(INTEGER, nullable=False)
    pro_users = Column(INTEGER, nullable=False)
    free_users = Column(INTEGER, nullable=False)

    # Domain metrics
    total_domains = Column(INTEGER, nullable=False)
    verified_domains = Column(INTEGER, nullable=False)
    pending_domains = Column(INTEGER, nullable=False)

    # Scan metrics
    total_scans = Column(INTEGER, nullable=False)
    scans_today = Column(INTEGER, nullable=False)
    scans_this_week = Column(INTEGER, nullable=False)
    scans_this_month = Column(INTEGER, nullable=False)
    average_scan_duration = Column(Float, nullable=True)
    failed_scans_count = Column(INTEGER, nullable=False)
    scan_success_rate = Column(Float, nullable=True)

    # Report metrics
    total_reports = Column(INTEGER, nullable=False)
    average_performance_score = Column(Float, nullable=True)
    average_seo_score = Column(Float, nullable=True)
    average_accessibility_score = Column(Float, nullable=True)
    average_best_practices_score = Column(Float, nullable=True)
    average_security_score = Column(Float, nullable=True)
    average_pwa_score = Column(Float, nullable=True)

    # API Usage metrics
    total_lighthouse_api_calls = Column(INTEGER, nullable=False)
    total_openai_api_calls = Column(INTEGER, nullable=False)
    average_openai_response_time = Column(Float, nullable=True)

    # Business metrics
    total_revenue = Column(Float, nullable=False)
    mrr = Column(Float, nullable=False)  # Monthly Recurring Revenue
    conversion_rate = Column(Float, nullable=True)
    churn_rate = Column(Float, nullable=True)

    # System metrics
    average_response_time = Column(Float, nullable=True)
    error_count = Column(INTEGER, nullable=False)

    # Detailed breakdowns (JSON columns for flexibility)
    user_geographic_distribution = Column(JSON, nullable=True)
    scan_type_distribution = Column(JSON, nullable=True)
    error_distribution = Column(JSON, nullable=True)
    subscription_distribution = Column(JSON, nullable=True)
