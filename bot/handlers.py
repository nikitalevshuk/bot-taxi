from datetime import datetime, time
import pytz
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, WorkSchedule
from .keyboards import (
    get_language_keyboard,
    get_country_keyboard,
    get_city_keyboard,
    get_main_menu_keyboard
)
from .constants import SUPPORTED_LANGUAGES, POLISH_CITIES
from .utils import parse_work_hours, calculate_non_working_hours

router = Router()

class RegistrationStates(StatesGroup):
    choosing_language = State()
    choosing_country = State()
    choosing_city = State()

class WorkScheduleStates(StatesGroup):
    entering_schedule = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession):
    user_id = message.from_user.id
    
    # Check if user exists
    existing_user = await session.execute(
        select(User).where(User.telegram_id == user_id)
    )
    if existing_user.scalar_one_or_none():
        await show_main_menu(message, session)
        return

    await state.set_state(RegistrationStates.choosing_language)
    await message.answer(
        "Please choose your language / Выберите язык:",
        reply_markup=get_language_keyboard()
    )

@router.callback_query(RegistrationStates.choosing_language)
async def process_language_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    language = callback.data
    if language not in SUPPORTED_LANGUAGES:
        await callback.answer("Invalid language selection")
        return

    await state.update_data(language=language)
    await state.set_state(RegistrationStates.choosing_country)
    await callback.message.edit_text(
        "Please select your country:",
        reply_markup=get_country_keyboard()
    )

@router.callback_query(RegistrationStates.choosing_country)
async def process_country_selection(
    callback: CallbackQuery,
    state: FSMContext
):
    country = callback.data
    await state.update_data(country=country)
    await state.set_state(RegistrationStates.choosing_city)
    await callback.message.edit_text(
        "Please select your city:",
        reply_markup=get_city_keyboard()
    )

@router.callback_query(RegistrationStates.choosing_city)
async def process_city_selection(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession
):
    city = callback.data
    if city not in POLISH_CITIES:
        await callback.answer("Invalid city selection")
        return

    user_data = await state.get_data()
    new_user = User(
        telegram_id=callback.from_user.id,
        language=user_data["language"],
        country=user_data["country"],
        city=city
    )
    
    session.add(new_user)
    await session.commit()
    
    await state.clear()
    await callback.message.edit_text(
        f"Registration complete! Your city: {city}",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("schedule"))
async def cmd_schedule(message: Message, state: FSMContext):
    await state.set_state(WorkScheduleStates.entering_schedule)
    await message.answer(
        "Please enter your work schedule for today in format:\n"
        "HH:MM-HH:MM[, HH:MM-HH:MM[, HH:MM-HH:MM]]\n"
        "Example: 09:00-11:00, 15:00-20:00"
    )

@router.message(WorkScheduleStates.entering_schedule)
async def process_schedule(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    try:
        schedules = parse_work_hours(message.text)
    except ValueError as e:
        await message.answer(str(e))
        return

    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user.scalar_one()

    # Check if schedule already exists for today
    tz = pytz.timezone('Europe/Warsaw')
    today = datetime.now(tz).date()
    existing_schedule = await session.execute(
        select(WorkSchedule)
        .where(WorkSchedule.user_id == user.id)
        .where(func.date(WorkSchedule.date) == today)
    )
    
    if existing_schedule.scalar_one_or_none():
        await message.answer(
            "You have already submitted your schedule for today. "
            "Please wait until tomorrow to submit a new schedule."
        )
        await state.clear()
        return

    schedule = WorkSchedule(
        user_id=user.id,
        date=today,
        start_time1=schedules[0][0],
        end_time1=schedules[0][1]
    )
    
    if len(schedules) > 1:
        schedule.start_time2 = schedules[1][0]
        schedule.end_time2 = schedules[1][1]
    
    if len(schedules) > 2:
        schedule.start_time3 = schedules[2][0]
        schedule.end_time3 = schedules[2][1]

    session.add(schedule)
    await session.commit()
    
    await state.clear()
    await message.answer("Your work schedule has been saved!")
    await show_city_stats(message, session)

@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession):
    await show_city_stats(message, session)

async def show_city_stats(message: Message, session: AsyncSession):
    user = await session.execute(
        select(User).where(User.telegram_id == message.from_user.id)
    )
    user = user.scalar_one()

    # Get total users in city
    total_users = await session.execute(
        select(func.count(User.id))
        .where(User.city == user.city)
    )
    total_users = total_users.scalar_one()

    # Calculate total non-working hours for the city
    tz = pytz.timezone('Europe/Warsaw')
    today = datetime.now(tz).date()
    
    city_schedules = await session.execute(
        select(WorkSchedule)
        .join(User)
        .where(User.city == user.city)
        .where(func.date(WorkSchedule.date) == today)
    )
    
    total_non_working_hours = sum(
        calculate_non_working_hours(schedule)
        for schedule in city_schedules.scalars()
    )

    await message.answer(
        f"Statistics for {user.city}:\n"
        f"Total users: {total_users}\n"
        f"Total non-working hours today: {total_non_working_hours:.1f}"
    )

async def show_main_menu(message: Message, session: AsyncSession):
    await message.answer(
        "Main Menu",
        reply_markup=get_main_menu_keyboard()
    )
