from os import environ
from flask_login import UserMixin
from sqlalchemy import Boolean, Integer, String, DateTime, UUID, create_engine, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, relationship
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

    pick_lists_requested = relationship('Pick_List', foreign_keys="Pick_List.requested_by_id", back_populates='requested_by')
    pick_lists_received = relationship('Pick_List',  foreign_keys="Pick_List.received_by_id", back_populates='received_by')
    pick_lists_delivered = relationship('Pick_List', foreign_keys="Pick_List.delivered_by_id", back_populates='delivered_by')
    comments = relationship('Comment', back_populates='user')
    change_logs = relationship('Change_Log', back_populates='user')
    scans = relationship('Scan', back_populates='user')

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
    description: Mapped[String] = mapped_column(String, nullable=True)
    manufacturer: Mapped[String] = mapped_column(String, nullable=True)
    part_number: Mapped[String] = mapped_column(String, nullable=True)
    serial_number: Mapped[String] = mapped_column(String, nullable=True)
    location: Mapped[String] = mapped_column(String, nullable=True) # link to foreign table
    owner: Mapped[String] = mapped_column(String, nullable=True)

    comments = relationship('Comment', back_populates='asset')
    change_logs = relationship('Change_Log', back_populates='asset')
    scans = relationship('Scan', back_populates='asset')
    pick_items = relationship('Pick_Item', back_populates='asset')

    def serialize(self):
        return { 
            "id": self.id,
            "description": self.description,
            "manufacturer": self.manufacturer, 
            "part_number": self.part_number,
            "serial_number": self.serial_number,
            "location": self.location,
            "owner": self.owner
        }

class Comment(db.Model):
    __tablename__ = "asset_comments"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('assets.id'))
    value: Mapped[String] = mapped_column(String)
    user_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('users.id'))
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    asset = relationship('Asset', back_populates='comments')
    user = relationship('User', back_populates='comments')

class Scan(db.Model):
    __tablename__ = "asset_scans"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('assets.id'))
    user_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('users.id'))
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    asset = relationship('Asset', back_populates='scans')
    user = relationship('User', back_populates='scans')

class Change_Log(db.Model):
    __tablename__ = "asset_change_logs"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('assets.id'))
    value: Mapped[String] = mapped_column(String)
    user_id: Mapped[Integer] = mapped_column(Integer, ForeignKey('users.id'))
    ts: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    asset = relationship('Asset', back_populates='change_logs')
    user = relationship('User', back_populates='change_logs')

class Pick_List(db.Model):
    __tablename__ = "pick_lists"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    requested_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    requested_by_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    delivered_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    delivered_by_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    received_by_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    received_by_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    items = relationship('Pick_Item', back_populates='pick_list')
    requested_by = relationship('User', foreign_keys="Pick_List.requested_by_id", back_populates='pick_lists_requested')
    delivered_by = relationship('User', foreign_keys="Pick_List.delivered_by_id", back_populates='pick_lists_delivered')
    received_by = relationship('User', foreign_keys="Pick_List.received_by_id", back_populates='pick_lists_received')

class Pick_Item(db.Model):
    __tablename__ = "pick_items"
    id: Mapped[int] = mapped_column(Identity(always=True), primary_key=True)
    pick_list_id: Mapped[int] = mapped_column(Integer, ForeignKey("pick_lists.id"), nullable=False)
    asset_id: Mapped[UUID] = mapped_column(UUID, ForeignKey('assets.id'))
    status: Mapped[String] = mapped_column(String, nullable=False) # waiting for picking, picked, waiting for delivery, delivered, waiting for receiving, received
    ts: Mapped[DateTime] = mapped_column(DateTime, onupdate=func.now(), server_default=func.now())

    pick_list = relationship('Pick_List', back_populates='items')
    asset = relationship('Asset', back_populates='pick_items')