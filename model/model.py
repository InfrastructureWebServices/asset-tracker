from os import environ
from flask_login import UserMixin
from sqlalchemy import Boolean, Integer, String, DateTime, UUID
from sqlalchemy import create_engine, MetaData, text, insert, Table
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.schema import Identity
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4

engine = create_engine(environ['SQLALCHEMY_DATABASE_URI'], echo=True)
SessionFactory = sessionmaker(engine)

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    mobile_number: Mapped[String] = mapped_column(String, unique=True)
    first_name: Mapped[String] = mapped_column(String)
    last_name: Mapped[String] = mapped_column(String)

class Verification_Session(db.Model):
    __tablename__ = "verification_sessions"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    mobile_number: Mapped[String] = mapped_column(String, unique=True, nullable=False)
    existing_user: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    code: Mapped[String] = mapped_column(String, nullable=False)
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    active: Mapped[Boolean] = mapped_column(Boolean, nullable=False, default=True)

class Asset(db.Model):
    __tablename__ = "assets"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[String] = mapped_column(String, nullable=True)
    manufacturer: Mapped[String] = mapped_column(String, nullable=True)
    part_number: Mapped[String] = mapped_column(String, nullable=True)
    serial_number: Mapped[String] = mapped_column(String, nullable=True)
    location: Mapped[String] = mapped_column(String, nullable=True) # link to foreign table
    owner: Mapped[String] = mapped_column(String, nullable=True)

class Comments(db.Model):
    __tablename__ = "asset_comments"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID)
    value: Mapped[String] = mapped_column(String)
    user_id: Mapped[Integer] = mapped_column(String)
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class Scans(db.Model):
    __tablename__ = "asset_scans"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID)
    user_id: Mapped[Integer] = mapped_column(String)
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

class Change_Log(db.Model):
    __tablename__ = "asset_change_log"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID)
    value: Mapped[String] = mapped_column(String)
    user_id: Mapped[Integer] = mapped_column(String)
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

