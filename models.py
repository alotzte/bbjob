from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://root:BB123123!@188.72.107.89:5432/postgres"

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    middlename = Column(String)

class Features(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    sentmessages = Column(Integer)
    receivedmessages = Column(Integer)
    numberofrecipients = Column(Integer)
    bccmessages = Column(Integer)
    ccmessages = Column(Integer)
    messagesreadafterxhours = Column(Integer)
    daysbetweenreceiveandread = Column(Integer)
    messagesreplied = Column(Integer)
    charactersinoutgoingmessages = Column(Integer)
    messagesoutsideofworkhours = Column(Integer)
    ratioofreceivedtosent = Column(Float)
    bytesizeratioofreceivedtosent = Column(Float)
    unansweredquestions = Column(Integer)
    hasresume = Column(Boolean)
    interviewconducted = Column(Boolean)
    lastsalaryincrease = Column(Date)
    lastpromotion = Column(Date)
    termination_likelihood = Column(Float)
    totalworkingdays = Column(Integer)
    salary = Column(Float)
    education = Column(String)
    yearstopromotion = Column(Integer)
    ratioofpreviouscompaniestoworkingyears = Column(Float)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
