from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship

from otto.api.models.base import Base
from otto.ryu.intent_engine.intent_processor_agent_tools import create_tool_list


class ToolCalls(Base):
    __tablename__ = "tool_calls"

    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String(200), unique=True, nullable=False)

    outcomes = relationship('CalledTools', back_populates='tool_call', cascade='all, delete-orphan')

    @staticmethod
    def populate_tool_calls() -> None:
        """
        Method to populate the ToolCalls table. First obtains the currently available tool
        calls, and checks whether they are already inputted into the tool_calls table. 
        If they are not, they will be added.
        """
        engine = create_engine("mysql+pymysql://root:root@127.0.0.1:3306/authentication_db")
        session = Session(engine)
        available_tools = [tool.name for tool in create_tool_list()]

        registered_tools = session.execute(select(ToolCalls.name)).scalars().all()

        tools_to_add = [ToolCalls(name=tool) for tool in available_tools if
	                tool not in registered_tools]
        if tools_to_add:
           session.add_all(tools_to_add)

           session.commit()

        session.close()

