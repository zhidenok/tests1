from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, MappedColumn
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, async_session
from sqlalchemy import BigInteger, String, ForeignKey

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)


class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = MappedColumn(String(30))


class Item(Base):
    __tablename__ = 'items'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = MappedColumn(String(30))
    price: Mapped[int] = MappedColumn()
    dicription: Mapped[str] = MappedColumn(String(130))
    category: Mapped[int] = MappedColumn(ForeignKey('categories.id'))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
