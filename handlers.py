
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery

from database import requests as rq
import keyboards as kb

router = Router()


class Register(StatesGroup):
    name = State()
    age = State()
    number = State()


class Deliver(StatesGroup):
    status = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.answer('Добро пожаловать в магазин одежды!', reply_markup=kb.main)


@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите пункт в меню!', reply_markup=await kb.categories())


@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию!')
    await callback.message.answer('Выберите товар по категории!',
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])

    await callback.answer('Вы выбрали Товар!')
    await callback.message.answer(
        f'Название: {item_data.name}\nОписание: {item_data.dicription}\nЦена: {item_data.price}Р',
        reply_markup=await kb.back_to_main())


@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('Возвращаемся на главную!')
    await callback.message.answer('Добро пожаловать на главную!', reply_markup=kb.main)


@router.message(F.text == 'О нас')
async def story(message: Message):
    await message.answer(
        'Наша компания работает с 2013 года, и обслуживает более 30000 покупателей ежегодно. Наши товары проходят проверку на оригинальность и брак!',
        reply_markup=await kb.back_to_main())


@router.message(F.text == 'Владелец')
async def owner(message: Message):
    await message.answer(
        'Иванов Иван Иванович успешный предприниматель, который начал свою предпринимательскую деятельность в 2005 году, тогда он открыл свой первый магазин!',
        reply_markup=await kb.back_to_main())


@router.message(F.text == 'Рассчитать стоимость доставки с комиссией')
async def qwerty(message: Message, state: FSMContext):
    await message.answer(
        f'Пожалуйста, введите стоимость товара (вы можете его выбрать во вклаке "католог" и мы сможем посчитать окончательную цену товара с учетом доставки',
        reply_markup=await kb.back_to_main())
    await state.set_state(Deliver.status)


@router.message(Deliver.status)
async def multiply_by_ten(message: Message, state: FSMContext):
    if message.text.isdigit():
        number = int(message.text)
        result = str(number * 1.10)[0:-2]
        await message.reply(f"Цена: {result} (включая стоимость доставки)",reply_markup=await kb.back_to_main())
        await state.clear()
    else:
        await message.reply("Пожалуйста, введите корректное число.")



@router.message(F.text == 'Регистрация')
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer('Введите ваше имя')


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.age)
    await message.answer("Введите ваш возраст")


@router.message(Register.age)
async def register_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(Register.number)
    await message.answer("Введите ваш номер телефона", reply_markup=kb.get_number)


@router.message(Register.number)
async def register_number(message: Message, state: FSMContext):
    if message.contact:
        number = message.contact.phone_number
    else:
        number = message.text

    await state.update_data(number=number)
    data = await state.get_data()

    name = data.get("name", "Не указано")  # значение, если ключ отсутствует
    age = data.get("age", "Не указано")
    number = data.get("number", "Не указано")

    await message.answer(
        f'Ваше имя: {name}\nВаш возраст: {age}\nВаш контактный номер телефона: {number}',
        reply_markup=await kb.back_to_main())
    await state.clear()
