import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytest
from unittest.mock import AsyncMock, patch
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from handlers import (
    cmd_start, catalog, category, item, story, owner,
    qwerty, multiply_by_ten, register, register_name, register_age, register_number
)
from handlers import Register, Deliver


# тест для команды /start
@pytest.mark.asyncio
async def test_start_command_with_new_user():
    """Проверяет, что создается новая запись в БД и отправляется приветствие"""
    with patch("database.requests.set_user", new_callable=AsyncMock) as mock_set_user:
        message = Message(from_user={'id': 12345})
        await cmd_start(message)
        mock_set_user.assert_called_once_with(12345)
        assert 'Добро пожаловать в магазин одежды!' in message.text

# тест для команды Каталог
@pytest.mark.asyncio
async def test_catalog():
    """Проверяет, что отправляется сообщение с меню категорий"""
    message = Message(text='Каталог')
    await catalog(message)
    assert 'Выберите пункт в меню!' in message.textcd

# тест для выбора категории
@pytest.mark.asyncio
async def test_category():
    """Проверяет, что отправляется сообщение с товарами выбранной категории"""
    callback = CallbackQuery(data='category_1')
    await category(callback)
    assert 'Вы выбрали категорию!' in callback.message.text

# тест для информации о товаре
@pytest.mark.asyncio
async def test_item():
    """Проверяет, что отправляется сообщение с информацией о товаре"""
    with patch("database.requests.get_item", new_callable=AsyncMock) as mock_get_item:
        mock_get_item.return_value = AsyncMock(name="Товар", dicription="Описание", price=1000)
        callback = CallbackQuery(data='item_1')
        await item(callback)
        assert 'Вы выбрали Товар!' in callback.message.text
        assert 'Название: Товар\nОписание: Описание\nЦена: 1000Р' in callback.message.text

# тест для команды "О нас"
@pytest.mark.asyncio
async def test_story():
    """Проверяет, что отправляется информация о компании"""
    message = Message(text='О нас')
    await story(message)
    assert 'Наша компания работает с 2013 года' in message.text

# тест для команды "Владелец"
@pytest.mark.asyncio
async def test_owner():
    """Проверяет, что отправляется информация о владельце"""
    message = Message(text='Владелец')
    await owner(message)
    assert 'Иванов Иван Иванович успешный предприниматель' in message.text

# тест для расчета стоимости доставки
@pytest.mark.asyncio
async def test_delivery_cost_calculation():
    """Проверяет, что стоимость товара умножается на коэффициент 1.1 и отображается корректно"""
    message = Message(text='1000')
    state = FSMContext()
    await multiply_by_ten(message, state)
    assert 'Цена: 1100 (включая стоимость доставки)' in message.text

# тест для некорректного ввода при расчете доставки
@pytest.mark.asyncio
async def test_delivery_cost_calculation_invalid_input():
    """Проверяет, что отправляется сообщение об ошибке при некорректном вводе"""
    message = Message(text='abc')
    state = FSMContext()
    await multiply_by_ten(message, state)
    assert "Пожалуйста, введите корректное число." in message.text

# тест для ввода отрицательной стоимости
@pytest.mark.asyncio
async def test_delivery_cost_calculation_invalid_negative():
    """Проверяет, что при вводе отрицательной стоимости отправляется сообщение об ошибке"""
    message = Message(text='-100')
    state = FSMContext()
    await multiply_by_ten(message, state)
    assert "Пожалуйста, введите корректное число." in message.text

# тест для регистрации пользователя
@pytest.mark.asyncio
async def test_register():
    """Проверяет, что начинается процесс регистрации с запроса имени пользователя"""
    message = Message(text='Регистрация')
    state = FSMContext()
    await register(message, state)
    assert 'Введите ваше имя' in message.text
    assert await state.get_state() == Register.name

# тест для ввода имени в процессе регистрации
@pytest.mark.asyncio
async def test_register_name():
    """Проверяет, что состояние меняется на запрос возраста после ввода имени"""
    message = Message(text='Иван')
    state = FSMContext()
    await register_name(message, state)
    assert 'Введите ваш возраст' in message.text
    assert await state.get_state() == Register.age

# тест для некорректного ввода возраста
@pytest.mark.asyncio
async def test_register_age_invalid():
    """Проверяет, что некорректный возраст не принимается"""
    message = Message(text='abc')
    state = FSMContext()
    await register_age(message, state)
    assert "Пожалуйста, введите корректный возраст." in message.text

# тест для ввода контактного номера в процессе регистрации
@pytest.mark.asyncio
async def test_register_number():
    """Проверяет, что сохраняется контактная информация"""
    message = Message(contact={'phone_number': '1234567890'})
    state = FSMContext()
    await register_number(message, state)
    data = await state.get_data()
    assert data['number'] == '1234567890'
    assert 'Ваше имя: Иван' in message.text
